use crate::models::EngineConfig;
use anyhow::Result;
use tokio::process::Command;

pub async fn run_doctor(config: &EngineConfig) -> Result<()> {
    println!("\n🩺 ReelMimic Engine — Runtime Doctor\n");

    check_tool("Python 3", &config.python_bin, &["--version"]).await;
    check_tool("FFmpeg", &config.ffmpeg_bin, &["-version"]).await;
    check_tool("Node.js", &config.node_bin, &["--version"]).await;
    check_tool("yt-dlp", "yt-dlp", &["--version"]).await;

    // Check Python packages
    check_python_pkg(&config.python_bin, "yt_dlp").await;
    check_python_pkg(&config.python_bin, "faster_whisper").await;
    check_python_pkg(&config.python_bin, "cv2").await;
    check_python_pkg(&config.python_bin, "librosa").await;

    // Check skill scripts exist
    check_file("analyze.py", &config.analyse_script);
    check_file("align_lyrics.py", &config.align_lyrics_script);
    check_file("fetch_assets.py", &config.fetch_assets_script);
    check_file("compare.py", &config.compare_script);

    // Check skills directory
    check_dir("skills/", &config.skills_dir);
    check_dir("skills/video-clone/", &format!("{}/video-clone", config.skills_dir));

    println!("\n✅ Doctor complete. Fix any ❌ items above before running.\n");
    Ok(())
}

async fn check_tool(name: &str, bin: &str, args: &[&str]) {
    let result = Command::new(bin).args(args).output().await;
    match result {
        Ok(out) if out.status.success() => {
            let ver = String::from_utf8_lossy(&out.stdout);
            let ver = ver.lines().next().unwrap_or("").trim();
            println!("  ✅ {:<20} {}", name, ver);
        }
        _ => {
            println!("  ❌ {:<20} NOT FOUND — install required", name);
        }
    }
}

async fn check_python_pkg(python: &str, pkg: &str) {
    let result = Command::new(python)
        .args(["-c", &format!("import {}; print('ok')", pkg)])
        .output()
        .await;
    match result {
        Ok(out) if out.status.success() => {
            println!("  ✅ python:{:<16} installed", pkg);
        }
        _ => {
            println!("  ❌ python:{:<16} NOT INSTALLED — pip install {}", pkg, pkg.replace('_', "-"));
        }
    }
}

fn check_file(name: &str, path: &str) {
    if std::path::Path::new(path).exists() {
        println!("  ✅ script:{:<16} {}", name, path);
    } else {
        println!("  ❌ script:{:<16} NOT FOUND at {}", name, path);
    }
}

fn check_dir(name: &str, path: &str) {
    if std::path::Path::new(path).is_dir() {
        println!("  ✅ dir:{:<20} {}", name, path);
    } else {
        println!("  ❌ dir:{:<20} NOT FOUND at {}", name, path);
    }
}
