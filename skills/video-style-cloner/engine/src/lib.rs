// reelmimic-engine — Rust orchestration engine
// Coordinates the full ReelMimic video style cloner pipeline:
// Ingest → Analyse → Style Route → Multi-agent Production → QA → Assemble

pub mod cli;
pub mod config;
pub mod models;
pub mod router;
pub mod pipeline;
pub mod agents;
pub mod executor;

pub use anyhow::Result;
