use crate::{executor, models::*};
use anyhow::{Context, Result};
use std::{path::Path, sync::Arc};
use tokio::{
    process::Command,
    sync::{mpsc, Semaphore},
};

/// Project adapters are real subprocesses. A reviewer is launched separately for every round.
pub async fn dispatch_parallel_production(
    project: &Project,
    segments: Vec<Segment>,
    config: Arc<EngineConfig>,
    event_tx: mpsc::Sender<String>,
) -> Result<Vec<Segment>> {
    crate::project_paths::project_dir(&config.projects_dir, &project.slug)?;
    for segment in &segments {
        crate::project_paths::validate_identifier(&segment.id, "segment ID")?;
    }
    anyhow::ensure!(
        !segments.is_empty(),
        "Storyboard contains no production segments"
    );
    anyhow::ensure!(
        config.max_parallel_agents > 0,
        "max_parallel_agents must be positive"
    );
    let semaphore = Arc::new(Semaphore::new(
        config.max_parallel_agents.min(segments.len()),
    ));
    let mut handles = Vec::new();
    for segment in segments {
        let sem = Arc::clone(&semaphore);
        let cfg = Arc::clone(&config);
        let slug = project.slug.clone();
        let tx = event_tx.clone();
        handles.push(tokio::spawn(async move {
            let _permit = sem.acquire().await?;
            produce_segment(segment, &slug, cfg, tx).await
        }));
    }
    // Join every task even if one fails, so no renderer continues after returning an error.
    let mut results = Vec::new();
    let mut failure = None;
    for handle in handles {
        match handle.await {
            Ok(Ok(segment)) => results.push(segment),
            Ok(Err(error)) => {
                failure.get_or_insert(error);
            }
            Err(error) => {
                failure.get_or_insert(anyhow::Error::from(error));
            }
        }
    }
    if let Some(error) = failure {
        return Err(error);
    }
    Ok(results)
}

async fn produce_segment(
    mut segment: Segment,
    slug: &str,
    config: Arc<EngineConfig>,
    tx: mpsc::Sender<String>,
) -> Result<Segment> {
    let project = crate::project_paths::project_dir(&config.projects_dir, slug)?;
    let frames = project.join("build/frames").join(&segment.id);
    let producer = project.join("render_segment.py");
    let reviewer = project.join("review_segment.py");
    anyhow::ensure!(
        producer.is_file(),
        "Missing renderer adapter {}. See engine/README.md",
        producer.display()
    );
    anyhow::ensure!(
        reviewer.is_file(),
        "Missing independent reviewer adapter {}",
        reviewer.display()
    );
    let plan = project.join("plan.json");
    let fixes = project
        .join("build")
        .join(format!("fixes_{}.json", segment.id));
    for round in 0..=config.max_fix_rounds {
        segment.state = SegmentState::Producing;
        let _ = tx
            .send(format!(
                "[{}] Rendering segment {} round {}",
                slug, segment.id, round
            ))
            .await;
        crate::project_paths::check_tree(&project)?;
        // Each pass must produce fresh frames. Old output must never stand in for a failed render.
        if frames.exists() {
            std::fs::remove_dir_all(&frames)?;
        }
        std::fs::create_dir_all(&frames)?;
        let mut command = Command::new(&config.python_bin);
        command
            .arg(&producer)
            .arg("--project")
            .arg(&project)
            .arg("--plan")
            .arg(&plan)
            .arg("--segment")
            .arg(&segment.id)
            .arg("--engine")
            .arg(&segment.engine)
            .arg("--shot-ids")
            .arg(
                segment
                    .shot_ids
                    .iter()
                    .map(u32::to_string)
                    .collect::<Vec<_>>()
                    .join(","),
            )
            .arg("--frames")
            .arg(&frames);
        if round > 0 {
            command.arg("--fixes").arg(&fixes);
        }
        let status = command
            .status()
            .await
            .context("Failed to launch segment renderer")?;
        anyhow::ensure!(status.success(), "Segment {} renderer failed", segment.id);
        crate::project_paths::check_tree(&project)?;
        executor::validate_frames(&frames, &config).await?;
        segment.frames_dir = Some(frames.to_string_lossy().into());
        segment.state = SegmentState::AwaitingReview;
        let review = run_review(&reviewer, &project, Some(&segment), &frames, &config).await?;
        let passed = review.passed
            && review.score.is_finite()
            && review.score >= config.qa_pass_threshold
            && !review
                .failures
                .iter()
                .any(|f| f.severity == QaSeverity::Critical);
        segment.review_result = Some(review.clone());
        if passed {
            segment.state = SegmentState::Approved;
            return Ok(segment);
        }
        if round == config.max_fix_rounds {
            segment.state = SegmentState::ReviewFailed {
                reason: format!("QA failed after {} fixes", round),
            };
            return Ok(segment);
        }
        std::fs::write(&fixes, serde_json::to_string_pretty(&review)?)?;
        segment.fix_rounds += 1;
    }
    unreachable!()
}

/// Reviewer stdout must be a ReviewResult JSON object. Diagnostics belong on stderr.
pub async fn run_review(
    script: &Path,
    project: &Path,
    segment: Option<&Segment>,
    artifact: &Path,
    config: &EngineConfig,
) -> Result<ReviewResult> {
    anyhow::ensure!(
        script.is_file(),
        "Missing reviewer adapter {}",
        script.display()
    );
    let mut command = Command::new(&config.python_bin);
    command
        .arg(script)
        .arg("--project")
        .arg(project)
        .arg("--plan")
        .arg(project.join("plan.json"));
    if let Some(segment) = segment {
        command
            .arg("--segment")
            .arg(&segment.id)
            .arg("--shot-ids")
            .arg(
                segment
                    .shot_ids
                    .iter()
                    .map(u32::to_string)
                    .collect::<Vec<_>>()
                    .join(","),
            )
            .arg("--frames")
            .arg(artifact);
    } else {
        command.arg("--video").arg(artifact);
    }
    let output = command
        .output()
        .await
        .context("Failed to launch independent reviewer")?;
    anyhow::ensure!(
        output.status.success(),
        "Reviewer failed: {}",
        String::from_utf8_lossy(&output.stderr)
    );
    serde_json::from_slice(&output.stdout).context("Reviewer stdout must contain ReviewResult JSON")
}
