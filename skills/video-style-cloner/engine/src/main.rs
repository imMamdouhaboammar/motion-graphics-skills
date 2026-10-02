use anyhow::Result;
use clap::Parser;
use reelmimic_engine::{
    cli::{Cli, Commands},
    config::run_doctor,
    models::{AspectRatio, EngineConfig, Project, ProjectState, VideoRef},
    pipeline::Pipeline,
};
use tracing::info;
use tracing_subscriber::EnvFilter;
use uuid::Uuid;

#[tokio::main]
async fn main() -> Result<()> {
    let cli = Cli::parse();

    // Initialize logging
    let filter = EnvFilter::try_new(&cli.log_level).unwrap_or_else(|_| EnvFilter::new("info"));

    if cli.json_logs {
        tracing_subscriber::fmt()
            .json()
            .with_env_filter(filter)
            .init();
    } else {
        tracing_subscriber::fmt()
            .with_env_filter(filter)
            .with_target(false)
            .compact()
            .init();
    }

    match cli.command {
        Commands::Doctor => {
            let config = EngineConfig::default();
            run_doctor(&config).await?;
        }

        Commands::Projects => {
            let projects_dir = "projects";
            if !std::path::Path::new(projects_dir).exists() {
                println!("No projects directory found.");
                return Ok(());
            }
            println!("\n📽  Projects:\n");
            for entry in std::fs::read_dir(projects_dir)? {
                let entry = entry?;
                let slug = entry.file_name().to_string_lossy().to_string();
                let state_file = entry.path().join("project.json");
                if state_file.exists() {
                    let raw = std::fs::read_to_string(&state_file)?;
                    let proj: serde_json::Value = serde_json::from_str(&raw)?;
                    let state = proj["state"].as_str().unwrap_or("unknown");
                    println!("  • {:<24} {}", slug, state);
                } else {
                    println!("  • {}", slug);
                }
            }
            println!();
        }

        Commands::Analyse(args) => {
            let config = EngineConfig::default();
            reelmimic_engine::executor::run_analysis(&args.reference, &args.out, &config).await?;
            println!("✅ Analysis complete → {}", args.out);
        }

        Commands::Resume(args) => {
            let config = EngineConfig {
                projects_dir: args.projects_dir.clone(),
                ..EngineConfig::default()
            };
            let project_path = format!("{}/{}/project.json", config.projects_dir, args.slug);
            let raw = std::fs::read_to_string(&project_path)
                .map_err(|_| anyhow::anyhow!("Project '{}' not found", args.slug))?;
            let mut project: Project = serde_json::from_str(&raw)?;
            info!(
                "Resuming project '{}' from state: {}",
                project.slug, project.state
            );
            let (pipeline, mut events) = Pipeline::new(config);
            tokio::spawn(async move {
                while let Some(ev) = events.recv().await {
                    println!("  {}", ev);
                }
            });
            if args.approve_storyboard {
                pipeline.approve_storyboard(&mut project)?;
            }
            pipeline.run(&mut project).await?;
        }

        Commands::Run(args) => {
            // Build slug
            let slug = args.slug.unwrap_or_else(|| {
                let id = Uuid::new_v4().to_string();
                id[..8].to_string()
            });

            // Determine reference type
            let reference = if args.reference.starts_with("http") {
                VideoRef::Url(args.reference.clone())
            } else {
                VideoRef::LocalFile(args.reference.clone())
            };

            // Build config
            let mut config = EngineConfig {
                projects_dir: args.projects_dir.clone(),
                ..EngineConfig::default()
            };
            if let Some(skills) = args.skills_dir {
                config.skills_dir = skills;
                if std::env::var_os("REELMIMIC_SCRIPTS").is_none() {
                    let scripts =
                        std::path::Path::new(&config.skills_dir).join("video-clone/scripts");
                    config.analyse_script = scripts.join("analyze.py").to_string_lossy().into();
                    config.align_lyrics_script =
                        scripts.join("align_lyrics.py").to_string_lossy().into();
                    config.fetch_assets_script =
                        scripts.join("fetch_assets.py").to_string_lossy().into();
                    config.compare_script = scripts.join("compare.py").to_string_lossy().into();
                }
            }

            // Build project
            let mut project = Project {
                slug: slug.clone(),
                created_at: chrono::Utc::now(),
                reference,
                brief: args.brief.clone(),
                duration_s: args.duration,
                aspect: AspectRatio::from_str(&args.aspect),
                audio: args.audio,
                lyrics_file: args.lyrics,
                auto_approve: args.auto_approve,
                state: ProjectState::Intake,
                analysis: None,
                style: None,
                storyboard: None,
                segments: vec![],
            };

            println!("\n🎬 ReelMimic Engine");
            println!("   Project:  {}", slug);
            println!("   Reference: {}", args.reference);
            println!("   Brief:    {}", args.brief);
            println!("   Duration: {}s  Aspect: {}\n", args.duration, args.aspect);

            let (pipeline, mut events) = Pipeline::new(config);

            // Print pipeline events
            tokio::spawn(async move {
                while let Some(ev) = events.recv().await {
                    println!("  ▶ {}", ev);
                }
            });

            pipeline.run(&mut project).await?;

            if project.state == ProjectState::AwaitingApproval {
                println!("Paused for storyboard approval. Resume {} --projects-dir {} --approve-storyboard after reviewing plan.json", slug, args.projects_dir);
                return Ok(());
            }

            // Final summary
            let out_path = format!("{}/{}/out/final.mp4", args.projects_dir, slug);
            println!("\n✅ Complete!");
            println!("   Output: {}", out_path);
        }
    }

    Ok(())
}
