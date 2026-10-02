use crate::models::{Medium, StyleSelection};
use anyhow::{Context, Result};
use std::path::Path;
use tracing::{debug, info, warn};

/// Frontmatter parsed from a style/*.md file
#[derive(Debug, Clone)]
pub struct StyleDef {
    pub name: String,   // filename without .md
    pub engine: String, // engine skill name
    pub medium: Medium,
    pub priority: u8,
    pub body: String, // raw markdown body (identification features etc.)
}

/// Parse all style/*.md files from the skill directory
pub fn load_style_registry(skills_dir: &str) -> Result<Vec<StyleDef>> {
    let skills_path = Path::new(skills_dir);
    let bundled = skills_path.parent().unwrap_or(skills_path).join("styles");
    // Load bundled definitions first. Local/legacy entries with the same name override them.
    let paths = [bundled, skills_path.join("video-clone/styles")];
    let mut styles = std::collections::BTreeMap::new();
    for styles_path in paths {
        if !styles_path.is_dir() {
            continue;
        }
        let entries = std::fs::read_dir(&styles_path)
            .with_context(|| format!("Cannot read styles dir: {:?}", styles_path))?;
        for entry in entries {
            let entry = entry?;
            let path = entry.path();
            if path.extension().map(|e| e == "md").unwrap_or(false) {
                let name = path.file_stem().unwrap().to_string_lossy().to_string();
                if name.starts_with('_') {
                    debug!("Skipping template file: {}", name);
                    continue;
                }

                let content = std::fs::read_to_string(&path)
                    .with_context(|| format!("Cannot read style file: {:?}", path))?;

                if let Some(def) = parse_style_frontmatter(&name, &content) {
                    // Only include styles whose engine skill exists
                    let engine_skill_path = Path::new(skills_dir).join(&def.engine);
                    if engine_skill_path.exists() {
                        styles.insert(name, def);
                    } else {
                        warn!(
                            "Skipping style '{}' — engine skill '{}' not installed",
                            name, def.engine
                        );
                    }
                }
            }
        }
    }
    info!("Loaded {} styles from merged registries", styles.len());
    Ok(styles.into_values().collect())
}

fn parse_style_frontmatter(name: &str, content: &str) -> Option<StyleDef> {
    // Parse YAML frontmatter between --- delimiters
    let stripped = content.trim_start_matches("---\n");
    let (fm_end, body_start) = stripped.find("\n---").map(|i| (i, i + 4))?;
    let frontmatter = &stripped[..fm_end];
    let body = stripped[body_start..].trim().to_string();

    let mut engine = String::new();
    let mut medium = Medium::Other("unknown".to_string());
    let mut priority: u8 = 5;

    for line in frontmatter.lines() {
        let line = line.trim();
        if let Some(v) = line.strip_prefix("engine:") {
            engine = v.trim().trim_matches('"').to_string();
        } else if let Some(v) = line.strip_prefix("medium:") {
            medium = Medium::from_str(v.trim().trim_matches('"'));
        } else if let Some(v) = line.strip_prefix("priority:") {
            priority = v.trim().parse().unwrap_or(5);
        }
    }

    if engine.is_empty() {
        return None;
    }

    Some(StyleDef {
        name: name.to_string(),
        engine,
        medium,
        priority,
        body,
    })
}

/// Score a style against the reference analysis
/// Returns 0.0 - 10.0
fn score_style(
    style: &StyleDef,
    ref_medium: &Medium,
    _analysis_json: Option<&serde_json::Value>,
) -> f32 {
    let mut score: f32 = 0.0;

    // Medium match is mandatory for base score
    if &style.medium == ref_medium {
        score += 7.0;
    } else {
        // Partial credit for related mediums (lineart ↔ vector, painted ↔ crayon)
        let partial = matches!(
            (&style.medium, ref_medium),
            (Medium::Lineart2D, Medium::Vector2D)
                | (Medium::Vector2D, Medium::Lineart2D)
                | (Medium::Painted2D, Medium::Crayon2D)
                | (Medium::Crayon2D, Medium::Painted2D)
        );
        if partial {
            score += 3.0;
        }
    }

    // Registries use priorities on a 0-100 scale. Keep their bonus within three
    // points so it cannot outweigh exact medium (7) or related medium (3).
    score += (style.priority.min(100) as f32 / 100.0) * 3.0;

    score.min(10.0)
}

/// Select the best matching style for the reference video
pub fn route_style(
    styles: &[StyleDef],
    detected_medium: &Medium,
    analysis_json: Option<&serde_json::Value>,
    user_override: Option<&str>,
) -> Result<StyleSelection> {
    // User override takes precedence
    if let Some(override_name) = user_override {
        if let Some(style) = styles
            .iter()
            .find(|s| s.name == override_name || s.engine == override_name)
        {
            info!("User override: routing to style '{}'", style.name);
            return Ok(StyleSelection {
                style_name: style.name.clone(),
                engine: style.engine.clone(),
                medium: format!("{:?}", style.medium),
                priority: style.priority,
                score: 10.0,
                why: format!("User explicitly requested '{}'", override_name),
                is_downgrade: false,
            });
        }
        warn!(
            "User override '{}' not found in registry; falling back to auto-routing",
            override_name
        );
    }

    // Is the reference a 2D medium we can match directly?
    let is_downgrade = !detected_medium.is_2d();

    // Filter to 2D styles only (3D track is disabled)
    let candidates: Vec<_> = styles.iter().filter(|s| s.medium.is_2d()).collect();

    if candidates.is_empty() {
        anyhow::bail!("No 2D styles found in registry. Check skills/video-clone/styles/");
    }

    // Score and rank
    let mut scored: Vec<(&StyleDef, f32)> = candidates
        .iter()
        .map(|s| (*s, score_style(s, detected_medium, analysis_json)))
        .collect();

    scored.sort_by(|a, b| b.1.partial_cmp(&a.1).unwrap_or(std::cmp::Ordering::Equal));

    let (best, score) = scored[0];

    let why = if &best.medium == detected_medium {
        format!(
            "Matched medium {:?} with score {:.1}",
            detected_medium, score
        )
    } else {
        format!(
            "No exact medium match for {:?}; closest 2D style is '{}' ({:?}), score {:.1}",
            detected_medium, best.name, best.medium, score
        )
    };

    info!(
        "Style routed: {} → engine: {} (score: {:.1})",
        best.name, best.engine, score
    );

    Ok(StyleSelection {
        style_name: best.name.clone(),
        engine: best.engine.clone(),
        medium: format!("{:?}", best.medium),
        priority: best.priority,
        score,
        why,
        is_downgrade,
    })
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_parse_frontmatter() {
        let content = r#"---
engine: painted-animation
medium: 2d-painted
priority: 9
---
# Style body
Some content here.
"#;
        let def = parse_style_frontmatter("painted-animation", content).unwrap();
        assert_eq!(def.engine, "painted-animation");
        assert_eq!(def.medium, Medium::Painted2D);
        assert_eq!(def.priority, 9);
    }

    #[test]
    fn test_route_prefers_matching_medium() {
        let styles = vec![
            StyleDef {
                name: "painted-animation".to_string(),
                engine: "painted-animation".to_string(),
                medium: Medium::Painted2D,
                priority: 9,
                body: String::new(),
            },
            StyleDef {
                name: "pixel-art".to_string(),
                engine: "pixel-art".to_string(),
                medium: Medium::Pixel2D,
                priority: 7,
                body: String::new(),
            },
        ];

        let sel = route_style(&styles, &Medium::Painted2D, None, None).unwrap();
        assert_eq!(sel.style_name, "painted-animation");
    }

    #[test]
    fn test_user_override() {
        let styles = vec![StyleDef {
            name: "pixel-art".to_string(),
            engine: "pixel-art".to_string(),
            medium: Medium::Pixel2D,
            priority: 7,
            body: String::new(),
        }];

        let sel = route_style(&styles, &Medium::Painted2D, None, Some("pixel-art")).unwrap();
        assert_eq!(sel.style_name, "pixel-art");
    }
}
