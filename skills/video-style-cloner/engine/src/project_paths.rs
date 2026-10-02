//! Project paths used for destructive rendering operations must stay beneath the configured root.
use anyhow::{Context, Result};
use std::path::{Path, PathBuf};

pub fn validate_slug(slug: &str) -> Result<()> {
    validate_identifier(slug, "project slug")
}

pub fn validate_identifier(value: &str, label: &str) -> Result<()> {
    anyhow::ensure!(
        !value.is_empty() && value.len() <= 128
            && value.as_bytes()[0].is_ascii_alphanumeric()
            && value.bytes().all(|b| b.is_ascii_alphanumeric() || b == b'-' || b == b'_'),
        "Invalid {}: use 1-128 ASCII letters, digits, hyphens or underscores, starting with a letter or digit", label
    );
    Ok(())
}

/// A caller may intentionally configure a symlinked projects root. Below that root,
/// reject all symlinks, including dangling links, before reading or mutating a project.
pub fn project_dir(projects_dir: &str, slug: &str) -> Result<PathBuf> {
    validate_slug(slug)?;
    std::fs::create_dir_all(projects_dir).context("Cannot create projects root")?;
    let root = std::fs::canonicalize(projects_dir).context("Cannot resolve projects root")?;
    let project = root.join(slug);
    check_tree(&project)?;
    Ok(project)
}

pub fn check_tree(path: &Path) -> Result<()> {
    let metadata = match std::fs::symlink_metadata(path) {
        Ok(metadata) => metadata,
        Err(error) if error.kind() == std::io::ErrorKind::NotFound => return Ok(()),
        Err(error) => {
            return Err(error).with_context(|| format!("Cannot inspect {}", path.display()))
        }
    };
    anyhow::ensure!(
        !metadata.file_type().is_symlink(),
        "Project path contains a symlink: {}",
        path.display()
    );
    if metadata.is_dir() {
        let entries = match std::fs::read_dir(path) {
            Ok(entries) => entries,
            Err(error) if error.kind() == std::io::ErrorKind::NotFound => return Ok(()),
            Err(error) => {
                return Err(error).with_context(|| format!("Cannot inspect {}", path.display()))
            }
        };
        for entry in entries {
            match entry {
                Ok(entry) => check_tree(&entry.path())?,
                Err(error) if error.kind() == std::io::ErrorKind::NotFound => continue,
                Err(error) => return Err(error.into()),
            }
        }
    }
    Ok(())
}
