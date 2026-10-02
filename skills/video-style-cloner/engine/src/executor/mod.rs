use crate::models::{AnalysisResult, EngineConfig};
use anyhow::{Context, Result};
use std::path::Path;
use tokio::process::Command;
use tracing::{debug, info};

/// Run analyze.py on a reference video/URL and return parsed AnalysisResult
pub async fn run_analysis(
    reference: &str,
    out_dir: &str,
    config: &EngineConfig,
) -> Result<AnalysisResult> {
    let script = &config.analyse_script;
    let python = &config.python_bin;

    info!("Running analysis: {} → {}", reference, out_dir);
    std::fs::create_dir_all(out_dir)
        .with_context(|| format!("Cannot create output dir: {}", out_dir))?;

    let status = Command::new(python)
        .args([script.as_str(), reference, "--out", out_dir])
        .status()
        .await
        .with_context(|| format!("Failed to spawn analyze.py with python={}", python))?;

    if !status.success() {
        anyhow::bail!(
            "analyze.py exited with code {:?}. Check that Python deps are installed.",
            status.code()
        );
    }

    // Read the report.json produced by analyze.py
    let report_path = Path::new(out_dir).join("report.json");
    let raw = std::fs::read_to_string(&report_path).with_context(|| {
        format!(
            "analyze.py did not produce report.json at {:?}",
            report_path
        )
    })?;

    let result = parse_analysis_report(&raw)
        .with_context(|| "Failed to parse report.json from analyze.py")?;

    info!(
        "Analysis complete: {:.1}s, {} shots, BPM={:?}",
        result.duration_s,
        result.shot_details.len(),
        result.bpm
    );

    Ok(result)
}

/// Run align_lyrics.py to timestamp-align user-provided lyrics text
pub async fn align_lyrics(
    audio_path: &str,
    lyrics_path: &str,
    out_lrc: &str,
    config: &EngineConfig,
) -> Result<()> {
    info!("Aligning lyrics: {} + {}", audio_path, lyrics_path);

    let status = Command::new(&config.python_bin)
        .args([
            config.align_lyrics_script.as_str(),
            audio_path,
            lyrics_path,
            "--out",
            out_lrc,
        ])
        .status()
        .await
        .with_context(|| "Failed to spawn align_lyrics.py")?;

    if !status.success() {
        anyhow::bail!("align_lyrics.py failed. Verify faster-whisper is installed.");
    }

    info!("Lyrics aligned → {}", out_lrc);
    Ok(())
}

/// Trim audio to target length, normalize loudness, add fades
pub async fn prepare_audio_clip(
    input: &str,
    start_s: f64,
    duration_s: u32,
    out: &str,
    config: &EngineConfig,
) -> Result<()> {
    let fade_start = (duration_s as f64 - 2.0).max(0.0);
    let af = format!(
        "loudnorm=I=-14:TP=-1.5,afade=t=in:d=0.08,afade=t=out:st={:.2}:d=2",
        fade_start
    );

    info!(
        "Preparing audio clip: {} → {} ({} s)",
        input, out, duration_s
    );

    let status = Command::new(&config.ffmpeg_bin)
        .args([
            "-y",
            "-ss",
            &start_s.to_string(),
            "-t",
            &duration_s.to_string(),
            "-i",
            input,
            "-af",
            &af,
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            out,
        ])
        .status()
        .await
        .with_context(|| "Failed to spawn ffmpeg for audio preparation")?;

    if !status.success() {
        anyhow::bail!("FFmpeg audio preparation failed");
    }

    Ok(())
}

/// Assemble final MP4 from frames directory + audio
pub async fn assemble_video(
    frames_dir: &str,
    audio_path: Option<&str>,
    fps: f32,
    aspect_scale: &str,
    out: &str,
    config: &EngineConfig,
) -> Result<()> {
    info!("Assembling final video → {}", out);

    let frame_pattern = format!("{}/frame_%06d.png", frames_dir);
    let mut args: Vec<String> = vec![
        "-y".to_string(),
        "-framerate".to_string(),
        fps.to_string(),
        "-start_number".to_string(),
        "1".to_string(),
        "-i".to_string(),
        frame_pattern,
    ];

    if let Some(audio) = audio_path {
        args.extend(["-i".to_string(), audio.to_string()]);
    }

    args.extend([
        "-c:v".to_string(),
        "libx264".to_string(),
        "-preset".to_string(),
        "slow".to_string(),
        "-crf".to_string(),
        "18".to_string(),
        "-vf".to_string(),
        format!("scale={}", aspect_scale),
        "-pix_fmt".to_string(),
        "yuv420p".to_string(),
    ]);

    if audio_path.is_some() {
        args.extend([
            "-c:a".to_string(),
            "copy".to_string(),
            "-shortest".to_string(),
        ]);
    }

    args.push(out.to_string());

    let status = Command::new(&config.ffmpeg_bin)
        .args(&args)
        .status()
        .await
        .with_context(|| "Failed to spawn ffmpeg for assembly")?;

    if !status.success() {
        anyhow::bail!("FFmpeg video assembly failed");
    }

    info!("Video assembled: {}", out);
    Ok(())
}

/// Extract a single frame at a given timestamp for QA inspection
pub async fn extract_frame(
    video_path: &str,
    timestamp_s: f64,
    out_jpg: &str,
    config: &EngineConfig,
) -> Result<()> {
    debug!("Extracting frame at {}s → {}", timestamp_s, out_jpg);

    let status = Command::new(&config.ffmpeg_bin)
        .args([
            "-y",
            "-ss",
            &timestamp_s.to_string(),
            "-i",
            video_path,
            "-vframes",
            "1",
            "-q:v",
            "2",
            out_jpg,
        ])
        .status()
        .await?;

    if !status.success() {
        anyhow::bail!("FFmpeg frame extraction failed at {}s", timestamp_s);
    }

    Ok(())
}

/// Run compare.py to score rendered shots against reference
pub async fn compare_shots(
    ref_sheet: &str,
    frames_dir: &str,
    plan_json: &str,
    threshold: f32,
    config: &EngineConfig,
) -> Result<Vec<(u32, f32)>> {
    // (shot_id, score)
    info!(
        "Running shot comparison: ref={} frames={}",
        ref_sheet, frames_dir
    );

    let output = Command::new(&config.python_bin)
        .args([
            config.compare_script.as_str(),
            "--ref",
            ref_sheet,
            "--out",
            frames_dir,
            "--shot-map",
            plan_json,
            "--threshold",
            &threshold.to_string(),
            "--json",
        ])
        .output()
        .await
        .with_context(|| "Failed to spawn compare.py")?;

    if !output.status.success() {
        let err = String::from_utf8_lossy(&output.stderr);
        anyhow::bail!("compare.py failed: {}", err);
    }

    let stdout = String::from_utf8_lossy(&output.stdout);
    let scores: Vec<(u32, f32)> =
        serde_json::from_str(&stdout).with_context(|| "Failed to parse compare.py JSON output")?;

    Ok(scores)
}

/// Convert the analyzer's nested measurements into the engine's normalized model.
pub fn parse_analysis_report(raw: &str) -> Result<AnalysisResult> {
    use serde::Deserialize;
    #[derive(Deserialize)]
    struct Video {
        duration: f64,
        fps: Option<f32>,
        width: Option<u32>,
        height: Option<u32>,
    }
    #[derive(Deserialize, Default)]
    struct Audio {
        #[serde(default)]
        present: bool,
        #[serde(default)]
        silent: bool,
        #[serde(default)]
        phase_inverted: bool,
        bpm: Option<f64>,
        #[serde(default)]
        beats: Vec<f64>,
        noise_floor_db: Option<f64>,
    }
    #[derive(Deserialize)]
    struct Pacing {
        mean_shot_s: Option<f64>,
        mean_shot_beats: Option<f64>,
    }
    #[derive(Deserialize)]
    struct Camera {
        kind: Vec<String>,
        pace: String,
    }
    #[derive(Deserialize)]
    struct Look {
        brightness: f32,
        contrast: f32,
        dark_ratio: f32,
        colourfulness: f32,
        dominant: Vec<String>,
    }
    #[derive(Deserialize)]
    struct Shot {
        shot: u32,
        start: f64,
        end: f64,
        camera: Camera,
        look: Look,
    }
    #[derive(Deserialize)]
    struct Report {
        video: Video,
        audio: Audio,
        pacing: Pacing,
        #[serde(default)]
        look_summary: crate::models::LookSummary,
        shot_details: Vec<Shot>,
    }
    let report: Report = serde_json::from_str(raw)?;
    let shots = report
        .shot_details
        .into_iter()
        .map(|s| crate::models::ShotDetail {
            id: s.shot,
            start_s: s.start,
            end_s: s.end,
            duration_s: s.end - s.start,
            duration_beats: report
                .audio
                .bpm
                .map(|b| (s.end - s.start) * b / 60.0)
                .unwrap_or(0.0),
            camera_move: s.camera.kind.join("/"),
            camera_speed: s.camera.pace,
            brightness: s.look.brightness,
            contrast: s.look.contrast,
            shadow_ratio: s.look.dark_ratio,
            saturation: s.look.colourfulness,
            dominant_colors: s.look.dominant,
            transition_out: "unknown".into(),
        })
        .collect();
    Ok(AnalysisResult {
        duration_s: report.video.duration,
        fps: report.video.fps.unwrap_or(0.0),
        resolution: [
            report.video.width.unwrap_or(0),
            report.video.height.unwrap_or(0),
        ],
        bpm: report.audio.bpm,
        beat_times: report.audio.beats,
        avg_shot_length_s: report.pacing.mean_shot_s.unwrap_or(0.0),
        avg_shot_length_beats: report.pacing.mean_shot_beats.unwrap_or(0.0),
        silent: !report.audio.present || report.audio.silent,
        phase_inverted: report.audio.phase_inverted,
        noise_floor_db: report.audio.noise_floor_db,
        look_summary: report.look_summary,
        transitions: vec![],
        shot_details: shots,
    })
}

/// Require a nonempty, contiguous PNG sequence numbered from one.
pub fn frame_sequence(dir: &Path) -> Result<Vec<std::path::PathBuf>> {
    let mut frames: Vec<_> = std::fs::read_dir(dir)?
        .filter_map(|e| e.ok())
        .map(|e| e.path())
        .filter(|p| p.extension().is_some_and(|e| e == "png"))
        .collect();
    frames.sort();
    anyhow::ensure!(
        !frames.is_empty(),
        "No rendered PNG frames in {}",
        dir.display()
    );
    for (i, path) in frames.iter().enumerate() {
        let expected = format!("frame_{:06}.png", i + 1);
        anyhow::ensure!(
            path.file_name().and_then(|s| s.to_str()) == Some(expected.as_str()),
            "Invalid frame sequence at {}: expected {}",
            path.display(),
            expected
        );
        anyhow::ensure!(
            std::fs::metadata(path)?.len() > 0,
            "Empty frame {}",
            path.display()
        );
    }
    Ok(frames)
}

pub async fn validate_frames(dir: &Path, config: &EngineConfig) -> Result<()> {
    frame_sequence(dir)?;
    let status = Command::new(&config.ffmpeg_bin)
        .args(["-v", "error", "-xerror", "-start_number", "1", "-i"])
        .arg(dir.join("frame_%06d.png"))
        .args(["-f", "null", "-"])
        .status()
        .await?;
    anyhow::ensure!(
        status.success(),
        "Rendered frame sequence cannot be decoded: {}",
        dir.display()
    );
    Ok(())
}
