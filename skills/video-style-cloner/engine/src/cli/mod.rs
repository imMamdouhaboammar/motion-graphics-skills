use clap::{Parser, Subcommand};

#[derive(Parser)]
#[command(
    name = "reelmimic",
    about = "ReelMimic Rust Orchestration Engine — style-clone any video",
    version,
    propagate_version = true
)]
pub struct Cli {
    #[command(subcommand)]
    pub command: Commands,

    /// Log level: error, warn, info, debug, trace
    #[arg(long, global = true, default_value = "info", env = "REELMIMIC_LOG")]
    pub log_level: String,

    /// Output JSON logs (for CI / agent consumption)
    #[arg(long, global = true)]
    pub json_logs: bool,
}

#[derive(Subcommand)]
pub enum Commands {
    /// Run the full pipeline: analyse → plan → produce → review → assemble
    Run(RunArgs),

    /// Analyse a reference video and produce STYLE.md only
    Analyse(AnalyseArgs),

    /// Resume a previously paused project
    Resume(ResumeArgs),

    /// List all projects under the projects/ directory
    Projects,

    /// Check that all required runtime tools are installed
    Doctor,
}

#[derive(clap::Args, Debug)]
pub struct RunArgs {
    /// Reference video: local file path or URL (YouTube, direct link)
    #[arg(short, long)]
    pub reference: String,

    /// Creative brief: what the new video should be about
    #[arg(short, long)]
    pub brief: String,

    /// Project slug (auto-generated if omitted)
    #[arg(short, long)]
    pub slug: Option<String>,

    /// Target duration in seconds
    #[arg(long, default_value = "30")]
    pub duration: u32,

    /// Aspect ratio: 16x9, 9x16, 1x1
    #[arg(long, default_value = "16x9")]
    pub aspect: String,

    /// Path to audio file (optional)
    #[arg(long)]
    pub audio: Option<String>,

    /// Path to lyrics text file (optional)
    #[arg(long)]
    pub lyrics: Option<String>,

    /// Skip human approval gate (auto-approve storyboard)
    #[arg(long)]
    pub auto_approve: bool,

    /// Projects root directory
    #[arg(long, default_value = "projects")]
    pub projects_dir: String,

    /// Skills root directory
    #[arg(long)]
    pub skills_dir: Option<String>,
}

#[derive(clap::Args, Debug)]
pub struct AnalyseArgs {
    /// Reference video: local file path or URL
    #[arg(short, long)]
    pub reference: String,

    /// Output directory for analysis artifacts
    #[arg(short, long, default_value = "analysis")]
    pub out: String,
}

#[derive(clap::Args, Debug)]
pub struct ResumeArgs {
    /// Project slug to resume
    pub slug: String,

    /// Explicitly approve the reviewed plan.json and continue production
    #[arg(long)]
    pub approve_storyboard: bool,

    /// Projects root directory
    #[arg(long, default_value = "projects")]
    pub projects_dir: String,
}
