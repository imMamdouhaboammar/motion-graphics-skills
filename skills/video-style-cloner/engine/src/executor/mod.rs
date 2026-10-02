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
    let raw = std::fs::read_to_string(&report_path)
        .with_context(|| format!("analyze.py did not produce report.json at {:?}", report_path))?;

    let result: AnalysisResult = serde_json::from_str(&raw)
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

    info!("Preparing audio clip: {} → {} ({} s)", input, out, duration_s);

    let status = Command::new(&config.ffmpeg_bin)
        .args([
            "-y",
            "-ss", &start_s.to_string(),
            "-t", &duration_s.to_string(),
            "-i", input,
            "-af", &af,
            "-c:a", "aac",
            "-b:a", "192k",
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
        "-framerate".to_string(), fps.to_string(),
        "-i".to_string(), frame_pattern,
    ];

    if let Some(audio) = audio_path {
        args.extend(["-i".to_string(), audio.to_string()]);
    }

    args.extend([
        "-c:v".to_string(), "libx264".to_string(),
        "-preset".to_string(), "slow".to_string(),
        "-crf".to_string(), "18".to_string(),
        "-vf".to_string(), format!("scale={}", aspect_scale),
        "-pix_fmt".to_string(), "yuv420p".to_string(),
    ]);

    if audio_path.is_some() {
        args.extend(["-c:a".to_string(), "copy".to_string(), "-shortest".to_string()]);
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
            "-ss", &timestamp_s.to_string(),
            "-i", video_path,
            "-vframes", "1",
            "-q:v", "2",
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
) -> Result<Vec<(u32, f32)>> {  // (shot_id, score)
    info!("Running shot comparison: ref={} frames={}", ref_sheet, frames_dir);

    let output = Command::new(&config.python_bin)
        .args([
            config.compare_script.as_str(),
            "--ref", ref_sheet,
            "--out", frames_dir,
            "--shot-map", plan_json,
            "--threshold", &threshold.to_string(),
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
    let scores: Vec<(u32, f32)> = serde_json::from_str(&stdout)
        .with_context(|| "Failed to parse compare.py JSON output")?;

    Ok(scores)
}
