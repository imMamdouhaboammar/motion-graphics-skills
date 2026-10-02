use serde::{Deserialize, Serialize};

// ─── Core domain types ───────────────────────────────────────────────────────

/// Unique identifier for a production job
pub type JobId = uuid::Uuid;

/// A video production project
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Project {
    pub slug: String,
    pub created_at: chrono::DateTime<chrono::Utc>,
    pub reference: VideoRef,
    pub brief: String,
    pub duration_s: u32,
    pub aspect: AspectRatio,
    pub audio: Option<String>,
    pub lyrics_file: Option<String>,
    pub auto_approve: bool,
    pub state: ProjectState,
    pub analysis: Option<AnalysisResult>,
    pub style: Option<StyleSelection>,
    pub storyboard: Option<Storyboard>,
    pub segments: Vec<Segment>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum VideoRef {
    LocalFile(String),
    Url(String),
}

impl VideoRef {
    pub fn as_str(&self) -> &str {
        match self {
            VideoRef::LocalFile(p) => p,
            VideoRef::Url(u) => u,
        }
    }
}

#[derive(Debug, Clone, Copy, Serialize, Deserialize, PartialEq, Eq)]
pub enum AspectRatio {
    Landscape, // 16:9
    Portrait,  // 9:16
    Square,    // 1:1
}

impl AspectRatio {
    pub fn from_str(s: &str) -> Self {
        match s {
            "9x16" | "9:16" => Self::Portrait,
            "1x1" | "1:1" => Self::Square,
            _ => Self::Landscape,
        }
    }

    pub fn ffmpeg_scale(&self) -> &'static str {
        match self {
            Self::Landscape => "1920:1080",
            Self::Portrait => "1080:1920",
            Self::Square => "1080:1080",
        }
    }
}

// ─── Pipeline State Machine ───────────────────────────────────────────────────

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
pub enum ProjectState {
    Intake,
    Analysing,
    StyleRouting,
    AudioAnalysis,
    StoryboardDraft,
    AwaitingApproval,
    Producing { segment: usize, total: usize },
    Assembling,
    FinalReview,
    Complete,
    Failed(String),
}

impl std::fmt::Display for ProjectState {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            Self::Intake => write!(f, "intake"),
            Self::Analysing => write!(f, "analysing"),
            Self::StyleRouting => write!(f, "style-routing"),
            Self::AudioAnalysis => write!(f, "audio-analysis"),
            Self::StoryboardDraft => write!(f, "storyboard-draft"),
            Self::AwaitingApproval => write!(f, "awaiting-approval"),
            Self::Producing { segment, total } => write!(f, "producing [{}/{}]", segment, total),
            Self::Assembling => write!(f, "assembling"),
            Self::FinalReview => write!(f, "final-review"),
            Self::Complete => write!(f, "complete"),
            Self::Failed(msg) => write!(f, "failed: {}", msg),
        }
    }
}

// ─── Analysis types ───────────────────────────────────────────────────────────

/// Output of analyze.py
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AnalysisResult {
    pub duration_s: f64,
    pub fps: f32,
    pub resolution: [u32; 2],
    pub bpm: Option<f64>,
    pub beat_times: Vec<f64>,
    pub avg_shot_length_s: f64,
    pub avg_shot_length_beats: f64,
    pub silent: bool,
    pub phase_inverted: bool,
    pub noise_floor_db: Option<f64>,
    pub look_summary: LookSummary,
    pub transitions: Vec<String>,
    pub shot_details: Vec<ShotDetail>,
}

#[derive(Debug, Clone, Default, Serialize, Deserialize)]
#[serde(default)]
pub struct LookSummary {
    pub low_key_shots: f64,
    pub moving_camera_shots: f64,
    pub mean_brightness: f64,
    pub camera_kinds: Vec<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ShotDetail {
    pub id: u32,
    pub start_s: f64,
    pub end_s: f64,
    pub duration_s: f64,
    pub duration_beats: f64,
    pub camera_move: String,
    pub camera_speed: String,
    pub brightness: f32,
    pub contrast: f32,
    pub shadow_ratio: f32,
    pub saturation: f32,
    pub dominant_colors: Vec<String>,
    pub transition_out: String,
}

// ─── Style routing types ──────────────────────────────────────────────────────

/// Medium classification (must match STYLE.md frontmatter)
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq, Hash)]
pub enum Medium {
    Painted2D,
    Cel2D,
    Pixel2D,
    Crayon2D,
    Paper2D,
    Lineart2D,
    Vector2D,
    LiveAction,
    Other(String),
}

impl Medium {
    pub fn from_str(s: &str) -> Self {
        match s {
            "2d-painted" => Self::Painted2D,
            "2d-cel" => Self::Cel2D,
            "2d-pixel" => Self::Pixel2D,
            "2d-crayon" => Self::Crayon2D,
            "2d-paper" => Self::Paper2D,
            "2d-lineart" => Self::Lineart2D,
            "2d-vector" => Self::Vector2D,
            "live-action" => Self::LiveAction,
            other => Self::Other(other.to_string()),
        }
    }

    pub fn is_2d(&self) -> bool {
        !matches!(self, Self::LiveAction | Self::Other(_))
    }
}

/// Result of style routing
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct StyleSelection {
    pub style_name: String,
    pub engine: String,
    pub medium: String,
    pub priority: u8,
    pub score: f32,
    pub why: String,
    pub is_downgrade: bool, // true if ref is 3D/live-action but we're doing 2D
}

// ─── Storyboard types ─────────────────────────────────────────────────────────

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Storyboard {
    pub logline: String,
    pub colour_arc: String,
    pub motif: String,
    pub shots: Vec<PlannedShot>,
    pub required_inputs: Vec<RequiredInput>,
    pub approved: bool,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PlannedShot {
    pub id: u32,
    pub beats: u32,
    pub transition_in: String,
    pub event: String,
    pub reaction: String,
    pub ref_shot: u32,
    pub ref_what: String,
    pub camera: CameraSpec,
    pub notes: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CameraSpec {
    pub r#move: String,
    pub focal: String,
    pub fill: f32,
    pub region: String,
    pub depth_of_field: String,
    pub angle_start: i32,
    pub angle_end: i32,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RequiredInput {
    pub name: String,
    pub description: String,
    pub provided: bool,
    pub skipped: bool,
}

// ─── Production segment types ─────────────────────────────────────────────────

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Segment {
    pub id: String,
    pub shot_ids: Vec<u32>,
    pub engine: String,
    pub state: SegmentState,
    pub frames_dir: Option<String>,
    pub review_result: Option<ReviewResult>,
    pub fix_rounds: u8,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
pub enum SegmentState {
    Pending,
    Producing,
    AwaitingReview,
    ReviewFailed { reason: String },
    Approved,
    Failed(String),
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ReviewResult {
    pub passed: bool,
    pub failures: Vec<QaFailure>,
    pub score: f32,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct QaFailure {
    pub category: String,
    pub item: String,
    pub severity: QaSeverity,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
pub enum QaSeverity {
    Critical, // blocks — character integrity, no fix = retry
    Minor,    // log + continue
}

// ─── Fix evidence types ───────────────────────────────────────────────────────

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct FixRecord {
    pub shot_id: u32,
    pub description: String,
    pub before_frame: String,
    pub after_frame: String,
    pub validated: bool,
    pub timestamp: chrono::DateTime<chrono::Utc>,
}

// ─── Asset log ────────────────────────────────────────────────────────────────

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AssetRecord {
    pub filename: String,
    pub source: String,
    pub author: String,
    pub licence: AssetLicence,
    pub url: Option<String>,
    pub notes: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum AssetLicence {
    Cc0,
    CcBy,
    CcByNc,
    RoyaltyFree,
    UserProvided,
    Unknown,
}

impl std::fmt::Display for AssetLicence {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            Self::Cc0 => write!(f, "CC0"),
            Self::CcBy => write!(f, "CC-BY"),
            Self::CcByNc => write!(f, "CC-BY-NC"),
            Self::RoyaltyFree => write!(f, "Royalty-free"),
            Self::UserProvided => write!(f, "User-provided"),
            Self::Unknown => write!(f, "⚠️ Licence unconfirmed"),
        }
    }
}

// ─── Engine configuration ─────────────────────────────────────────────────────

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct EngineConfig {
    pub projects_dir: String,
    pub skills_dir: String,
    pub python_bin: String,
    pub ffmpeg_bin: String,
    pub node_bin: String,
    pub max_parallel_agents: usize,
    pub max_fix_rounds: u8,
    pub qa_pass_threshold: f32,
    pub analyse_script: String,
    pub align_lyrics_script: String,
    pub fetch_assets_script: String,
    pub compare_script: String,
}

impl EngineConfig {
    /// Shared configuration application for run and resume.
    pub fn apply_skills_dir(&mut self, skills: Option<String>) {
        if let Some(skills) = skills {
            self.skills_dir = skills;
            if std::env::var_os("REELMIMIC_SCRIPTS").is_none() {
                let scripts = std::path::Path::new(&self.skills_dir).join("video-clone/scripts");
                self.analyse_script = scripts.join("analyze.py").to_string_lossy().into();
                self.align_lyrics_script = scripts.join("align_lyrics.py").to_string_lossy().into();
                self.fetch_assets_script = scripts.join("fetch_assets.py").to_string_lossy().into();
                self.compare_script = scripts.join("compare.py").to_string_lossy().into();
            }
        }
    }
}

impl Default for EngineConfig {
    fn default() -> Self {
        let skills = if std::path::Path::new(".claude/skills/video-clone").is_dir() {
            std::path::PathBuf::from(".claude/skills")
        } else {
            std::path::Path::new(env!("CARGO_MANIFEST_DIR")).join("../skills")
        };
        let scripts = std::env::var_os("REELMIMIC_SCRIPTS")
            .map(std::path::PathBuf::from)
            .unwrap_or_else(|| skills.join("video-clone/scripts"));
        Self {
            projects_dir: "projects".to_string(),
            skills_dir: skills.to_string_lossy().into(),
            python_bin: "python3".to_string(),
            ffmpeg_bin: "ffmpeg".to_string(),
            node_bin: "node".to_string(),
            max_parallel_agents: 6,
            max_fix_rounds: 3,
            qa_pass_threshold: 4.0,
            analyse_script: scripts.join("analyze.py").to_string_lossy().into(),
            align_lyrics_script: scripts.join("align_lyrics.py").to_string_lossy().into(),
            fetch_assets_script: scripts.join("fetch_assets.py").to_string_lossy().into(),
            compare_script: scripts.join("compare.py").to_string_lossy().into(),
        }
    }
}

// ─── Pipeline event (for observability) ──────────────────────────────────────

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PipelineEvent {
    pub timestamp: chrono::DateTime<chrono::Utc>,
    pub project_slug: String,
    pub phase: String,
    pub message: String,
    pub data: Option<serde_json::Value>,
}

impl PipelineEvent {
    pub fn new(slug: &str, phase: &str, msg: &str) -> Self {
        Self {
            timestamp: chrono::Utc::now(),
            project_slug: slug.to_string(),
            phase: phase.to_string(),
            message: msg.to_string(),
            data: None,
        }
    }

    pub fn with_data(mut self, data: serde_json::Value) -> Self {
        self.data = Some(data);
        self
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_aspect_ratio_parsing_and_scaling() {
        assert_eq!(AspectRatio::from_str("16x9"), AspectRatio::Landscape);
        assert_eq!(AspectRatio::from_str("9x16"), AspectRatio::Portrait);
        assert_eq!(AspectRatio::from_str("9:16"), AspectRatio::Portrait);
        assert_eq!(AspectRatio::from_str("1x1"), AspectRatio::Square);
        assert_eq!(AspectRatio::from_str("unknown"), AspectRatio::Landscape);

        assert_eq!(AspectRatio::Landscape.ffmpeg_scale(), "1920:1080");
        assert_eq!(AspectRatio::Portrait.ffmpeg_scale(), "1080:1920");
        assert_eq!(AspectRatio::Square.ffmpeg_scale(), "1080:1080");
    }

    #[test]
    fn test_medium_2d_validation() {
        assert!(Medium::from_str("2d-painted").is_2d());
        assert!(Medium::from_str("2d-cel").is_2d());
        assert!(Medium::from_str("2d-pixel").is_2d());
        assert!(!Medium::from_str("live-action").is_2d());
        assert!(!Medium::from_str("3d-photoreal").is_2d());
    }

    #[test]
    fn test_project_state_display() {
        assert_eq!(ProjectState::Intake.to_string(), "intake");
        assert_eq!(
            ProjectState::Producing {
                segment: 1,
                total: 3
            }
            .to_string(),
            "producing [1/3]"
        );
        assert_eq!(
            ProjectState::Failed("timeout".into()).to_string(),
            "failed: timeout"
        );
    }
}
