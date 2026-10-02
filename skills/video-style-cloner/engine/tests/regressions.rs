use reelmimic_engine::{agents::dispatch_parallel_production, executor, models::*};
use std::sync::Arc;
#[tokio::test]
async fn parses_nested_analyzer_report_without_audio() {
    let dir = tempfile::tempdir().unwrap();
    let script = dir.path().join("analyze.py");
    std::fs::write(&script, r#"import json,sys,os
out=sys.argv[sys.argv.index('--out')+1]
json.dump({'video':{'duration':2.5,'fps':24,'width':640,'height':360},'pacing':{'mean_shot_s':2.5},'audio':{'present':False},'shot_details':[{'shot':1,'start':0,'end':2.5,'camera':{'kind':['static'],'pace':'still'},'look':{'brightness':0.4,'contrast':0.2,'dark_ratio':0.1,'colourfulness':0.3,'dominant':['#123456']}}],'look_summary':{'low_key_shots':0,'moving_camera_shots':0,'mean_brightness':0.4,'camera_kinds':['static']}},open(os.path.join(out,'report.json'),'w'))
"#).unwrap();
    let config = EngineConfig {
        analyse_script: script.to_str().unwrap().into(),
        ..Default::default()
    };
    let analysis = executor::run_analysis("dummy", dir.path().to_str().unwrap(), &config)
        .await
        .unwrap();
    assert_eq!(analysis.duration_s, 2.5);
    assert_eq!(analysis.resolution, [640, 360]);
    assert!(analysis.silent);
    assert_eq!(analysis.shot_details[0].dominant_colors, vec!["#123456"]);
}
fn project() -> Project {
    Project {
        slug: "test".into(),
        created_at: chrono::Utc::now(),
        reference: VideoRef::LocalFile("unused".into()),
        brief: "test".into(),
        duration_s: 1,
        aspect: AspectRatio::Landscape,
        audio: None,
        lyrics_file: None,
        auto_approve: false,
        state: ProjectState::AwaitingApproval,
        analysis: None,
        style: None,
        storyboard: None,
        segments: vec![],
    }
}
#[tokio::test]
async fn paused_project_does_not_start_analysis_or_production() {
    let dir = tempfile::tempdir().unwrap();
    let config = EngineConfig {
        projects_dir: dir.path().to_str().unwrap().into(),
        analyse_script: "missing.py".into(),
        ..Default::default()
    };
    let (pipeline, _) = reelmimic_engine::pipeline::Pipeline::new(config);
    let mut p = project();
    pipeline.run(&mut p).await.unwrap();
    assert_eq!(p.state, ProjectState::AwaitingApproval);
    assert!(!dir.path().join("test/build").exists());
}
#[tokio::test]
async fn absent_producer_cannot_approve_empty_frames() {
    let dir = tempfile::tempdir().unwrap();
    let config = Arc::new(EngineConfig {
        projects_dir: dir.path().to_str().unwrap().into(),
        ..Default::default()
    });
    let seg = Segment {
        id: "A".into(),
        shot_ids: vec![1],
        engine: "general-video".into(),
        state: SegmentState::Pending,
        frames_dir: None,
        review_result: None,
        fix_rounds: 0,
    };
    let (tx, _rx) = tokio::sync::mpsc::channel(256);
    let result = dispatch_parallel_production(&project(), vec![seg], config, tx).await;
    assert!(result.is_err());
}

#[test]
fn real_renderer_review_assembly_and_custom_resume() {
    let dir = tempfile::tempdir().unwrap();
    let root = dir.path().join("test");
    std::fs::create_dir_all(&root).unwrap();
    let example = std::path::Path::new(env!("CARGO_MANIFEST_DIR")).join("examples/smoke-project");
    for name in ["render_segment.py", "review_segment.py", "review_final.py"] {
        std::fs::copy(example.join(name), root.join(name)).unwrap();
    }
    let plan = serde_json::json!({"logline":"Technical test card", "colour_arc":"test pattern", "motif":"test", "required_inputs":[],"approved":false,
 "shots":[{"id":7,"beats":24,"transition_in":"cut","event":"test card","reaction":"none","ref_shot":1,"ref_what":"test","camera":{"move":"static","focal":"wide","fill":1.0,"region":"full","depth_of_field":"deep","angle_start":0,"angle_end":0},"notes":null}]});
    std::fs::write(
        root.join("plan.json"),
        serde_json::to_string(&plan).unwrap(),
    )
    .unwrap();
    std::fs::write(
        root.join("project.json"),
        serde_json::to_string(&project()).unwrap(),
    )
    .unwrap();
    let cli = env!("CARGO_BIN_EXE_reelmimic");
    let pause = std::process::Command::new(cli)
        .args([
            "resume",
            "test",
            "--projects-dir",
            dir.path().to_str().unwrap(),
        ])
        .output()
        .unwrap();
    assert!(
        pause.status.success(),
        "{}",
        String::from_utf8_lossy(&pause.stderr)
    );
    assert!(!root.join("build").exists());
    let run = std::process::Command::new(cli)
        .args([
            "resume",
            "test",
            "--projects-dir",
            dir.path().to_str().unwrap(),
            "--approve-storyboard",
        ])
        .output()
        .unwrap();
    assert!(
        run.status.success(),
        "stdout={} stderr={}",
        String::from_utf8_lossy(&run.stdout),
        String::from_utf8_lossy(&run.stderr)
    );
    let saved: Project =
        serde_json::from_str(&std::fs::read_to_string(root.join("project.json")).unwrap()).unwrap();
    assert_eq!(saved.state, ProjectState::Complete);
    assert_eq!(saved.segments[0].shot_ids, vec![7]);
    assert_eq!(
        executor::frame_sequence(&root.join("build/frames/assembled"))
            .unwrap()
            .len(),
        24
    );
    assert!(std::fs::metadata(root.join("out/final.mp4")).unwrap().len() > 1000);
    // A failing final reviewer must prevent Complete even when assembly succeeds.
    std::fs::write(
        root.join("review_final.py"),
        "import json\nprint(json.dumps({'passed':False,'score':0,'failures':[]}))\n",
    )
    .unwrap();
    let mut retry = saved;
    retry.state = ProjectState::StoryboardDraft;
    std::fs::write(
        root.join("project.json"),
        serde_json::to_string(&retry).unwrap(),
    )
    .unwrap();
    let failure = std::process::Command::new(cli)
        .args([
            "resume",
            "test",
            "--projects-dir",
            dir.path().to_str().unwrap(),
        ])
        .output()
        .unwrap();
    assert!(!failure.status.success());
    let saved: Project =
        serde_json::from_str(&std::fs::read_to_string(root.join("project.json")).unwrap()).unwrap();
    assert_ne!(saved.state, ProjectState::Complete);
}

#[tokio::test]
async fn resumes_each_preproduction_state_to_approval() {
    for state in [
        ProjectState::Analysing,
        ProjectState::AudioAnalysis,
        ProjectState::StyleRouting,
        ProjectState::StoryboardDraft,
    ] {
        let dir = tempfile::tempdir().unwrap();
        let config = EngineConfig {
            projects_dir: dir.path().to_str().unwrap().into(),
            analyse_script: "must-not-repeat-completed-analysis.py".into(),
            ..Default::default()
        };
        let (pipeline, _rx) = reelmimic_engine::pipeline::Pipeline::new(config);
        let mut p = project();
        p.state = state.clone();
        p.analysis = Some(executor::parse_analysis_report(r#"{"video":{"duration":1,"fps":24,"width":160,"height":90},"audio":{"present":false},"pacing":{"mean_shot_s":1},"shot_details":[]}"#).unwrap());
        p.style = Some(StyleSelection {
            style_name: "test".into(),
            engine: "general-video".into(),
            medium: "2d-painted".into(),
            priority: 1,
            score: 5.0,
            why: "test".into(),
            is_downgrade: false,
        });
        pipeline
            .run(&mut p)
            .await
            .unwrap_or_else(|error| panic!("Could not resume {state:?}: {error}"));
        assert_eq!(p.state, ProjectState::AwaitingApproval);
        assert!(!dir.path().join("test/build").exists());
    }
}

#[test]
fn bundled_style_registry_has_painted_engine() {
    let config = EngineConfig::default();
    for script in [
        &config.analyse_script,
        &config.align_lyrics_script,
        &config.compare_script,
    ] {
        assert!(
            std::path::Path::new(script).is_file(),
            "Script not found: {script}"
        );
    }
    let styles = reelmimic_engine::router::load_style_registry(&config.skills_dir).unwrap();
    assert!(styles
        .iter()
        .any(|s| s.name == "painted-animation" && s.engine == "painted-animation"));
}

#[tokio::test]
async fn intake_analysis_routes_bundled_styles_then_pauses() {
    let dir = tempfile::tempdir().unwrap();
    let script = dir.path().join("analyze.py");
    std::fs::write(&script, r#"import json,sys,os
out=sys.argv[sys.argv.index('--out')+1]
json.dump({'video':{'duration':1,'fps':24,'width':160,'height':90},'pacing':{'mean_shot_s':1},'audio':{'present':False},'shot_details':[]},open(os.path.join(out,'report.json'),'w'))
"#).unwrap();
    let config = EngineConfig {
        projects_dir: dir.path().to_str().unwrap().into(),
        analyse_script: script.to_str().unwrap().into(),
        ..Default::default()
    };
    let (pipeline, _rx) = reelmimic_engine::pipeline::Pipeline::new(config);
    let mut p = project();
    p.state = ProjectState::Intake;
    pipeline.run(&mut p).await.unwrap();
    assert_eq!(p.state, ProjectState::AwaitingApproval);
    assert_eq!(p.style.unwrap().style_name, "painted-animation");
    assert!(dir.path().join("test/analysis/report.json").is_file());
    assert!(!dir.path().join("test/build").exists());
}

#[test]
fn audio_only_and_pacing_beats_convert_without_inventing_video() {
    let result = executor::parse_analysis_report(r#"{"video":{"duration":30,"fps":null,"width":null,"height":null},"audio":{"present":true,"silent":false,"bpm":120,"beats":[0,0.5,1],"phase_inverted":true,"noise_floor_db":-52},"pacing":{"mean_shot_s":null},"shot_details":[]}"#).unwrap();
    assert_eq!(result.resolution, [0, 0]);
    assert_eq!(result.fps, 0.0);
    assert_eq!(result.bpm, Some(120.0));
    assert_eq!(result.beat_times, vec![0.0, 0.5, 1.0]);
    assert!(!result.silent);
    assert!(result.phase_inverted);
    assert!(result.shot_details.is_empty());
}

#[tokio::test]
async fn segment_qa_rejects_critical_empty_and_corrupt_output() {
    for mode in ["empty", "corrupt", "critical"] {
        let dir = tempfile::tempdir().unwrap();
        let root = dir.path().join("test");
        std::fs::create_dir_all(&root).unwrap();
        std::fs::write(root.join("plan.json"), r#"{"shots":[{"id":1,"beats":24}]}"#).unwrap();
        if mode == "critical" {
            std::fs::copy(
                std::path::Path::new(env!("CARGO_MANIFEST_DIR"))
                    .join("examples/smoke-project/render_segment.py"),
                root.join("render_segment.py"),
            )
            .unwrap();
        } else {
            let source = if mode == "empty" {
                "pass"
            } else {
                "import pathlib,sys\npathlib.Path(sys.argv[sys.argv.index('--frames')+1],'frame_000001.png').write_bytes(b'corrupt')"
            };
            std::fs::write(root.join("render_segment.py"), source).unwrap();
        }
        std::fs::write(root.join("review_segment.py"),"import json\nprint(json.dumps({'passed':True,'score':5,'failures':[{'category':'visual','item':'Missing character','severity':'Critical'}]}))").unwrap();
        let config = EngineConfig {
            projects_dir: dir.path().to_str().unwrap().into(),
            max_fix_rounds: 0,
            ..Default::default()
        };
        let (tx, _rx) = tokio::sync::mpsc::channel(256);
        let seg = Segment {
            id: "A".into(),
            shot_ids: vec![1],
            engine: "general-video".into(),
            state: SegmentState::Pending,
            frames_dir: None,
            review_result: None,
            fix_rounds: 0,
        };
        let result =
            dispatch_parallel_production(&project(), vec![seg], Arc::new(config.clone()), tx).await;
        if mode == "critical" {
            let segments = result.unwrap();
            assert!(matches!(
                segments[0].state,
                SegmentState::ReviewFailed { .. }
            ));
            let (pipeline, _) = reelmimic_engine::pipeline::Pipeline::new(config);
            let mut p = project();
            p.segments = segments;
            assert!(pipeline.phase_assemble(&mut p).await.is_err());
            assert!(!root.join("out/final.mp4").exists());
        } else {
            assert!(result.is_err(), "Mode {mode} approved invalid output");
        }
    }
}
