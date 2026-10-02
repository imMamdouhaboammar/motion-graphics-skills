use crate::{agents::dispatch_parallel_production, executor, models::*, router};
use anyhow::{Context, Result};
use std::path::Path;
use std::sync::Arc;
use tokio::sync::mpsc;
use tracing::{info, warn};

/// Full end-to-end pipeline runner
pub struct Pipeline {
    pub config: Arc<EngineConfig>,
    pub event_tx: mpsc::Sender<String>,
}

impl Pipeline {
    pub fn new(config: EngineConfig) -> (Self, mpsc::Receiver<String>) {
        let (tx, rx) = mpsc::channel(256);
        (
            Self {
                config: Arc::new(config),
                event_tx: tx,
            },
            rx,
        )
    }

    /// Run all phases for a project in sequence
    pub async fn run(&self, project: &mut Project) -> Result<()> {
        crate::project_paths::project_dir(&self.config.projects_dir, &project.slug)?;
        self.emit(&project.slug, "pipeline", "Starting full pipeline")
            .await;

        if project.state == ProjectState::Complete {
            return Ok(());
        }
        // Each persisted preproduction state resumes at its earliest unfinished phase.
        let next_phase = match project.state {
            ProjectState::Intake | ProjectState::Analysing => 1,
            ProjectState::AudioAnalysis => 2,
            ProjectState::StyleRouting => 3,
            ProjectState::StoryboardDraft
                if !project.storyboard.as_ref().is_some_and(|s| s.approved) =>
            {
                4
            }
            _ => 5,
        };
        if next_phase <= 1 && project.analysis.is_none() {
            self.phase_analyse(project).await?;
        }
        if next_phase <= 2 {
            self.phase_audio(project).await?;
        }
        if next_phase <= 3 && project.style.is_none() {
            self.phase_route(project).await?;
        }
        if next_phase <= 4 {
            self.phase_storyboard(project).await?;
        }
        if project.state == ProjectState::AwaitingApproval {
            self.emit(
                &project.slug,
                "storyboard",
                "Paused. Author plan.json and resume with --approve-storyboard after reviewing it.",
            )
            .await;
            return Ok(());
        }
        anyhow::ensure!(
            project.storyboard.as_ref().is_some_and(|s| s.approved),
            "Production requires an explicitly approved storyboard"
        );
        self.phase_produce(project).await?;
        self.phase_assemble(project).await?;
        self.phase_final_review(project).await?;

        project.state = ProjectState::Complete;
        self.emit(&project.slug, "pipeline", "✅ Pipeline complete")
            .await;

        self.persist_project(project)?;
        Ok(())
    }

    // ─── Phase 0+1: Analyse ──────────────────────────────────────────────────

    pub async fn phase_analyse(&self, project: &mut Project) -> Result<()> {
        project.state = ProjectState::Analysing;
        self.persist_project(project)?;
        self.emit(&project.slug, "analyse", "Analysing reference video")
            .await;

        let out_dir = format!("{}/{}/analysis", self.config.projects_dir, project.slug);
        let analysis =
            executor::run_analysis(project.reference.as_str(), &out_dir, &self.config).await?;

        // Check audio flags
        if analysis.silent {
            warn!("⚠️  Reference video audio is SILENT. Re-record with system audio enabled.");
        }
        if analysis.phase_inverted {
            warn!("⚠️  Phase-inverted audio detected. Audio quality may be limited.");
        }

        project.analysis = Some(analysis);
        self.persist_project(project)?;
        Ok(())
    }

    // ─── Phase 3: Audio (optional) ───────────────────────────────────────────

    pub async fn phase_audio(&self, project: &mut Project) -> Result<()> {
        let audio_path = match &project.audio {
            Some(p) => p.clone(),
            None => return Ok(()), // silent video
        };

        project.state = ProjectState::AudioAnalysis;
        self.persist_project(project)?;
        self.emit(&project.slug, "audio", "Analysing audio file")
            .await;

        let out_dir = format!(
            "{}/{}/analysis/song",
            self.config.projects_dir, project.slug
        );
        let _audio_analysis = executor::run_analysis(&audio_path, &out_dir, &self.config).await?;

        // Prepare clipped audio for production
        let clip_out = format!(
            "{}/{}/assets/clip.m4a",
            self.config.projects_dir, project.slug
        );
        std::fs::create_dir_all(format!(
            "{}/{}/assets",
            self.config.projects_dir, project.slug
        ))?;

        executor::prepare_audio_clip(
            &audio_path,
            0.0,
            project.duration_s,
            &clip_out,
            &self.config,
        )
        .await?;

        // Align lyrics if provided
        if let Some(lyrics_path) = &project.lyrics_file {
            let out_lrc = format!(
                "{}/{}/analysis/lyrics/subs.lrc",
                self.config.projects_dir, project.slug
            );
            std::fs::create_dir_all(Path::new(&out_lrc).parent().unwrap())?;
            executor::align_lyrics(&audio_path, lyrics_path, &out_lrc, &self.config).await?;
        }

        self.persist_project(project)?;
        Ok(())
    }

    // ─── Phase 2: Style routing ──────────────────────────────────────────────

    pub async fn phase_route(&self, project: &mut Project) -> Result<()> {
        project.state = ProjectState::StyleRouting;
        self.persist_project(project)?;
        self.emit(&project.slug, "route", "Selecting production style")
            .await;

        let styles = router::load_style_registry(&self.config.skills_dir)
            .context("Failed to load style registry")?;

        // Determine medium from analysis (default to painted if unknown)
        let _analysis = project
            .analysis
            .as_ref()
            .context("Analysis must complete before routing")?;

        // Detect medium from STYLE.md (written by analyse phase)
        // In practice the agent writes STYLE.md; we read it here
        let style_md_path = format!(
            "{}/{}/analysis/STYLE.md",
            self.config.projects_dir, project.slug
        );
        let detected_medium =
            read_medium_from_style_md(&style_md_path).unwrap_or(Medium::Painted2D);

        let selection = router::route_style(&styles, &detected_medium, None, None)
            .context("Style routing failed")?;

        // Warn on downgrade
        if selection.is_downgrade {
            warn!(
                "⚠️  Reference is 3D/live-action. Reproducing in 2D style '{}'. \
                Rhythm, camera, composition, and mood will be matched.",
                selection.style_name
            );
        }

        info!(
            "Style selected: {} → engine: {}",
            selection.style_name, selection.engine
        );
        self.emit(
            &project.slug,
            "route",
            &format!(
                "Style: {} → engine: {}",
                selection.style_name, selection.engine
            ),
        )
        .await;

        project.style = Some(selection);
        self.persist_project(project)?;
        Ok(())
    }

    // ─── Phase 4: Storyboard ─────────────────────────────────────────────────

    pub async fn phase_storyboard(&self, project: &mut Project) -> Result<()> {
        project.state = ProjectState::StoryboardDraft;
        self.persist_project(project)?;
        self.emit(&project.slug, "storyboard", "Generating storyboard")
            .await;

        let plan_path = Path::new(&self.config.projects_dir)
            .join(&project.slug)
            .join("plan.json");
        if plan_path.exists() {
            project.storyboard = Some(
                serde_json::from_str(&std::fs::read_to_string(&plan_path)?)
                    .context("plan.json must contain a Storyboard object")?,
            );
        }
        project.state = ProjectState::AwaitingApproval;
        self.persist_project(project)?;
        if project.auto_approve {
            self.approve_storyboard(project)?;
        } else {
            self.emit(&project.slug, "storyboard", "Awaiting storyboard approval. Create/review STORYBOARD.md and plan.json, then resume --approve-storyboard.").await;
        }

        self.persist_project(project)?;
        Ok(())
    }

    /// Called only by explicit CLI approval or the requested auto-approve mode.
    pub fn approve_storyboard(&self, project: &mut Project) -> Result<()> {
        crate::project_paths::project_dir(&self.config.projects_dir, &project.slug)?;
        anyhow::ensure!(
            project.state == ProjectState::AwaitingApproval,
            "Project is not awaiting storyboard approval"
        );
        let root = Path::new(&self.config.projects_dir).join(&project.slug);
        let mut storyboard: Storyboard = serde_json::from_str(
            &std::fs::read_to_string(root.join("plan.json"))
                .context("Write a complete plan.json before approving")?,
        )?;
        anyhow::ensure!(
            !storyboard.shots.is_empty(),
            "Storyboard must contain shots"
        );
        let mut ids = std::collections::HashSet::new();
        for shot in &storyboard.shots {
            anyhow::ensure!(
                shot.id > 0 && ids.insert(shot.id),
                "Shot IDs must be positive and unique"
            );
        }
        anyhow::ensure!(
            storyboard
                .required_inputs
                .iter()
                .all(|i| i.provided || i.skipped),
            "Resolve required inputs before approving"
        );
        storyboard.approved = true;
        std::fs::write(
            root.join("plan.json"),
            serde_json::to_string_pretty(&storyboard)?,
        )?;
        project.storyboard = Some(storyboard);
        project.state = ProjectState::StoryboardDraft;
        self.persist_project(project)
    }

    // ─── Phase 5: Production ─────────────────────────────────────────────────

    pub async fn phase_produce(&self, project: &mut Project) -> Result<()> {
        crate::project_paths::project_dir(&self.config.projects_dir, &project.slug)?;
        let engine = project
            .style
            .as_ref()
            .map(|s| s.engine.clone())
            .unwrap_or_else(|| "general-video".to_string());

        // Build segments (2-5 shots per segment, max 6 parallel)
        let storyboard = project
            .storyboard
            .as_ref()
            .context("Storyboard is required")?;
        anyhow::ensure!(storyboard.approved, "Storyboard is not approved");
        let segments = build_segments(storyboard.shots.len(), &engine, project);
        let seg_count = segments.len();

        project.state = ProjectState::Producing {
            segment: 0,
            total: seg_count,
        };
        self.emit(
            &project.slug,
            "produce",
            &format!(
                "Dispatching {} segments across up to {} agents",
                seg_count, self.config.max_parallel_agents
            ),
        )
        .await;

        let updated = dispatch_parallel_production(
            project,
            segments,
            Arc::clone(&self.config),
            self.event_tx.clone(),
        )
        .await?;

        // Collect failures
        let failures: Vec<_> = updated
            .iter()
            .filter(|s| matches!(s.state, SegmentState::ReviewFailed { .. }))
            .collect();

        let failed_count = failures.len();
        project.segments = updated;
        self.persist_project(project)?;
        anyhow::ensure!(
            failed_count == 0,
            "{} segments failed QA. Assembly blocked",
            failed_count
        );
        Ok(())
    }

    // ─── Phase: Assemble ─────────────────────────────────────────────────────

    pub async fn phase_assemble(&self, project: &mut Project) -> Result<()> {
        project.state = ProjectState::Assembling;
        self.persist_project(project)?;
        self.emit(&project.slug, "assemble", "Assembling final video")
            .await;

        let frames_dir = format!(
            "{}/{}/build/frames/assembled",
            self.config.projects_dir, project.slug
        );
        let out_dir = format!("{}/{}/out", self.config.projects_dir, project.slug);
        std::fs::create_dir_all(&out_dir)?;

        anyhow::ensure!(!project.segments.is_empty(), "No segments to assemble");
        let assembled = Path::new(&frames_dir);
        if assembled.exists() {
            std::fs::remove_dir_all(assembled)?;
        }
        std::fs::create_dir_all(assembled)?;
        let mut index = 1usize;
        for segment in &project.segments {
            anyhow::ensure!(
                segment.state == SegmentState::Approved,
                "Segment {} has not passed QA",
                segment.id
            );
            let source = segment
                .frames_dir
                .as_ref()
                .context("Approved segment has no frames")?;
            executor::validate_frames(Path::new(source), &self.config).await?;
            for frame in executor::frame_sequence(Path::new(source))? {
                std::fs::copy(frame, assembled.join(format!("frame_{:06}.png", index)))?;
                index += 1;
            }
        }
        anyhow::ensure!(
            index - 1 == project.duration_s as usize * 24,
            "Rendered frame count {} does not match target {} seconds at 24 FPS",
            index - 1,
            project.duration_s
        );

        let audio_clip = format!(
            "{}/{}/assets/clip.m4a",
            self.config.projects_dir, project.slug
        );
        let audio_arg = if Path::new(&audio_clip).exists() {
            Some(audio_clip.as_str())
        } else {
            None
        };

        let out_mp4 = format!("{}/final.mp4", out_dir);
        let scale = project.aspect.ffmpeg_scale();

        executor::assemble_video(&frames_dir, audio_arg, 24.0, scale, &out_mp4, &self.config)
            .await?;

        info!("Assembly complete: {}", out_mp4);
        self.emit(&project.slug, "assemble", &format!("✅ {}", out_mp4))
            .await;
        Ok(())
    }

    // ─── Phase: Final Review ─────────────────────────────────────────────────

    pub async fn phase_final_review(&self, project: &mut Project) -> Result<()> {
        project.state = ProjectState::FinalReview;
        self.persist_project(project)?;
        self.emit(
            &project.slug,
            "final-review",
            "Running final cross-segment review",
        )
        .await;

        let root = Path::new(&self.config.projects_dir).join(&project.slug);
        let video = root.join("out/final.mp4");
        let status = tokio::process::Command::new(&self.config.ffmpeg_bin)
            .args(["-v", "error", "-xerror", "-i"])
            .arg(&video)
            .args(["-f", "null", "-"])
            .status()
            .await?;
        anyhow::ensure!(status.success(), "Final video cannot be decoded");
        let review = crate::agents::run_review(
            &root.join("review_final.py"),
            &root,
            None,
            &video,
            &self.config,
        )
        .await?;
        std::fs::write(
            root.join("out/final-review.json"),
            serde_json::to_string_pretty(&review)?,
        )?;
        anyhow::ensure!(
            review.passed
                && review.score.is_finite()
                && review.score >= self.config.qa_pass_threshold
                && !review
                    .failures
                    .iter()
                    .any(|f| f.severity == QaSeverity::Critical),
            "Final QA failed"
        );
        Ok(())
    }

    // ─── Helpers ─────────────────────────────────────────────────────────────

    async fn emit(&self, slug: &str, phase: &str, msg: &str) {
        let line = format!("[{}] [{}] {}", slug, phase, msg);
        info!("{}", line);
        let _ = self.event_tx.send(line).await;
    }

    fn persist_project(&self, project: &Project) -> Result<()> {
        crate::project_paths::project_dir(&self.config.projects_dir, &project.slug)?;
        let path = format!("{}/{}/project.json", self.config.projects_dir, project.slug);
        std::fs::create_dir_all(Path::new(&path).parent().unwrap())?;
        let json = serde_json::to_string_pretty(project)?;
        std::fs::write(&path, json)?;
        Ok(())
    }
}

// ─── Helpers ─────────────────────────────────────────────────────────────────

fn build_segments(shot_count: usize, engine: &str, project: &Project) -> Vec<Segment> {
    // Group shots into segments of 2-5 shots
    const SHOTS_PER_SEGMENT: usize = 4;
    let shot_ids: Vec<u32> = project
        .storyboard
        .as_ref()
        .map(|s| s.shots.iter().map(|s| s.id).collect())
        .unwrap_or_else(|| (1..=(shot_count as u32)).collect());
    let chunks: Vec<Vec<u32>> = shot_ids
        .chunks(SHOTS_PER_SEGMENT)
        .map(|c| c.to_vec())
        .collect();

    chunks
        .into_iter()
        .enumerate()
        .map(|(i, ids)| Segment {
            id: format!("{}", (b'A' + i as u8) as char),
            shot_ids: ids,
            engine: engine.to_string(),
            state: SegmentState::Pending,
            frames_dir: None,
            review_result: None,
            fix_rounds: 0,
        })
        .collect()
}

fn read_medium_from_style_md(path: &str) -> Option<Medium> {
    let content = std::fs::read_to_string(path).ok()?;
    // Look for a line starting with "2d-" or "live-action" in the Medium section
    for line in content.lines() {
        let line = line.trim().to_lowercase();
        for prefix in &[
            "2d-painted",
            "2d-cel",
            "2d-pixel",
            "2d-crayon",
            "2d-paper",
            "2d-lineart",
            "2d-vector",
            "live-action",
        ] {
            if line.contains(prefix) {
                return Some(Medium::from_str(prefix));
            }
        }
    }
    None
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_build_segments_partitioning() {
        let proj = Project {
            slug: "test-slug".into(),
            created_at: chrono::Utc::now(),
            reference: VideoRef::LocalFile("test.mp4".into()),
            brief: "test brief".into(),
            duration_s: 30,
            aspect: AspectRatio::Landscape,
            audio: None,
            lyrics_file: None,
            auto_approve: true,
            state: ProjectState::Intake,
            analysis: None,
            style: None,
            storyboard: None,
            segments: vec![],
        };

        // 10 shots should yield 3 segments (4 + 4 + 2)
        let segments = build_segments(10, "painted-animation", &proj);
        assert_eq!(segments.len(), 3);
        assert_eq!(segments[0].id, "A");
        assert_eq!(segments[0].shot_ids, vec![1, 2, 3, 4]);
        assert_eq!(segments[1].id, "B");
        assert_eq!(segments[1].shot_ids, vec![5, 6, 7, 8]);
        assert_eq!(segments[2].id, "C");
        assert_eq!(segments[2].shot_ids, vec![9, 10]);
    }

    #[test]
    fn test_read_medium_from_text() {
        let dir = tempfile::tempdir().unwrap();
        let file_path = dir.path().join("STYLE.md");
        std::fs::write(&file_path, "# Style\n## Medium\n2d-cel (anime)\n").unwrap();

        let medium = read_medium_from_style_md(file_path.to_str().unwrap());
        assert_eq!(medium, Some(Medium::Cel2D));
    }
}
