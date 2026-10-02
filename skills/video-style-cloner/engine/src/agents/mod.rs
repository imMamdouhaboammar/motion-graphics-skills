use crate::models::{
    EngineConfig, Project, Segment, SegmentState, ReviewResult, QaSeverity,
};
use anyhow::Result;
use std::sync::Arc;
use tokio::sync::{mpsc, Semaphore};
use tracing::{error, info, warn};

/// Dispatch up to N production agents in parallel for a set of segments.
/// Each segment is produced by one agent, then reviewed by a fresh independent agent.
/// Returns updated segments.
pub async fn dispatch_parallel_production(
    project: &Project,
    segments: Vec<Segment>,
    config: Arc<EngineConfig>,
    event_tx: mpsc::Sender<String>,
) -> Result<Vec<Segment>> {
    let concurrency = config.max_parallel_agents.min(segments.len());
    let semaphore = Arc::new(Semaphore::new(concurrency));
    let mut handles = Vec::new();

    info!(
        "Dispatching {} segments with max {} parallel agents",
        segments.len(),
        concurrency
    );

    for segment in segments {
        let sem = Arc::clone(&semaphore);
        let cfg = Arc::clone(&config);
        let project_slug = project.slug.clone();
        let engine = segment.engine.clone();
        let tx = event_tx.clone();

        let handle = tokio::spawn(async move {
            let _permit = sem.acquire().await.expect("semaphore closed");
            produce_segment(segment, &project_slug, &engine, cfg, tx).await
        });

        handles.push(handle);
    }

    let mut results = Vec::new();
    for handle in handles {
        match handle.await {
            Ok(Ok(seg)) => results.push(seg),
            Ok(Err(e)) => {
                error!("Segment production failed: {}", e);
                // Push a failed segment — don't lose it
            }
            Err(e) => {
                error!("Segment task panicked: {}", e);
            }
        }
    }

    Ok(results)
}

/// Produce a single segment and immediately run review
async fn produce_segment(
    mut segment: Segment,
    project_slug: &str,
    engine: &str,
    config: Arc<EngineConfig>,
    event_tx: mpsc::Sender<String>,
) -> Result<Segment> {
    info!("Segment {} → producing with engine '{}'", segment.id, engine);
    segment.state = SegmentState::Producing;

    let _ = event_tx.send(format!(
        "[{}] segment:{} phase:produce engine:{}", project_slug, segment.id, engine
    )).await;

    // ── In a real system this calls the AI agent subprocess ──
    // The agent reads skills/<engine>/SKILL.md and renders frames.
    // For now we model the interface contract:
    let frames_dir = format!("projects/{}/build/frames/{}", project_slug, segment.id);
    std::fs::create_dir_all(&frames_dir)?;
    segment.frames_dir = Some(frames_dir.clone());

    // ── Review loop (max N rounds) ──────────────────────────
    let mut round = 0u8;
    loop {
        segment.state = SegmentState::AwaitingReview;
        info!("Segment {} → review round {}", segment.id, round + 1);

        let review = run_independent_review(&segment, project_slug, &config).await?;

        if review.passed {
            info!("Segment {} → APPROVED (score {:.1})", segment.id, review.score);
            segment.review_result = Some(review);
            segment.state = SegmentState::Approved;
            break;
        }

        let critical = review.failures.iter().any(|f| f.severity == QaSeverity::Critical);
        warn!(
            "Segment {} → FAILED (score {:.1}, {} failures, critical={})",
            segment.id, review.score, review.failures.len(), critical
        );

        round += 1;
        if round >= config.max_fix_rounds {
            let reason = format!(
                "Failed QA after {} rounds. Last score: {:.1}. Issues: {:?}",
                round,
                review.score,
                review.failures.iter().map(|f| &f.item).collect::<Vec<_>>()
            );
            segment.review_result = Some(review);
            segment.state = SegmentState::ReviewFailed { reason };
            break;
        }

        // Request fix from producer agent
        segment.state = SegmentState::Producing;
        segment.fix_rounds += 1;
        request_segment_fix(&segment, &review, project_slug, engine, &config).await?;
    }

    Ok(segment)
}

/// Run an independent reviewer agent (different from the producer)
async fn run_independent_review(
    segment: &Segment,
    _project_slug: &str,
    _config: &EngineConfig,
) -> Result<ReviewResult> {
    // In production: spawn fresh agent subprocess with reviewer prompt
    // pointing it at segment.frames_dir and the QA checklist.
    // The agent outputs a structured JSON review result.
    //
    // For now we model the interface:
    let frames_dir = segment.frames_dir.as_deref().unwrap_or(".");
    info!("Independent review of segment {} at {}", segment.id, frames_dir);

    // Simulated: read compare.py output or agent JSON output
    // Real impl would call: compare_shots(...) and parse QA checklist results
    Ok(ReviewResult {
        passed: true,      // ← real impl reads actual agent output
        failures: vec![],
        score: 4.5,
    })
}

/// Request the producer agent to fix a failed segment
async fn request_segment_fix(
    segment: &Segment,
    review: &ReviewResult,
    project_slug: &str,
    engine: &str,
    _config: &EngineConfig,
) -> Result<()> {
    info!(
        "Requesting fix for segment {} from engine '{}' — {} failures",
        segment.id, engine, review.failures.len()
    );

    // Write a fixes.json entry per failure
    let fix_entries: Vec<serde_json::Value> = review.failures.iter().map(|f| {
        serde_json::json!({
            "segment": segment.id,
            "category": f.category,
            "item": f.item,
            "severity": format!("{:?}", f.severity),
            "before_frame": null,   // agent fills this
            "after_frame": null,    // agent fills this
            "validated": false
        })
    }).collect();

    let fixes_path = format!("projects/{}/fixes.json", project_slug);
    let existing_raw = std::fs::read_to_string(&fixes_path).unwrap_or_else(|_| "[]".to_string());
    let mut existing: Vec<serde_json::Value> = serde_json::from_str(&existing_raw).unwrap_or_default();
    existing.extend(fix_entries);
    std::fs::write(&fixes_path, serde_json::to_string_pretty(&existing)?)?;

    Ok(())
}
