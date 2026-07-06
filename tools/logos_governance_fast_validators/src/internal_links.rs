use crate::reports::CheckReport;
use regex::Regex;
use std::fs;
use std::path::{Path, PathBuf};
use std::time::Instant;

const CHECK_NAME: &str = "internal_links";
const SKIP_PREFIXES: [&str; 6] = ["http://", "https://", "mailto:", "tel:", "data:", "#"];
const VALID_BACKTICK_SUFFIXES: [&str; 6] = [".md", ".yaml", ".yml", ".json", ".py", ".sh"];

#[derive(Debug, Clone)]
pub struct InternalLinksInput {
    pub root: PathBuf,
    pub all_markdown: bool,
    pub paths: Vec<PathBuf>,
}

pub fn run_check(input: InternalLinksInput) -> CheckReport {
    let started = Instant::now();
    let files = markdown_files(&input);
    let mut failures = Vec::new();

    for markdown in &files {
        let text = match fs::read_to_string(markdown) {
            Ok(text) => text,
            Err(exc) => {
                failures.push(format!(
                    "{}: unreadable markdown file: {}",
                    display_path(markdown, &input.root),
                    exc
                ));
                continue;
            }
        };

        for target in iter_targets(&text) {
            if !path_exists(markdown, &target, &input.root) {
                failures.push(format!(
                    "{}: missing local target '{}'",
                    display_path(markdown, &input.root),
                    target
                ));
            }
        }
    }

    let elapsed = started.elapsed();
    if failures.is_empty() {
        CheckReport::pass(
            CHECK_NAME,
            elapsed,
            format!(
                "Internal link validation passed ({} markdown files).",
                files.len()
            ),
        )
    } else {
        CheckReport::fail(
            CHECK_NAME,
            elapsed,
            format!(
                "Internal link validation failed ({} failures across {} markdown files).",
                failures.len(),
                files.len()
            ),
            failures,
        )
    }
}

fn markdown_files(input: &InternalLinksInput) -> Vec<PathBuf> {
    let mut files = if !input.paths.is_empty() {
        input
            .paths
            .iter()
            .map(|path| resolve_cli_path(&input.root, path))
            .collect::<Vec<_>>()
    } else if input.all_markdown {
        collect_markdown_files(&input.root)
    } else {
        vec![input.root.join("README.md")]
    };

    files.retain(|path| path.extension().is_some_and(|suffix| suffix == "md") && path.exists());
    files.sort_by(|left, right| left.to_string_lossy().cmp(&right.to_string_lossy()));
    files
}

fn resolve_cli_path(root: &Path, path: &Path) -> PathBuf {
    if path.is_absolute() {
        path.to_path_buf()
    } else {
        root.join(path)
    }
}

fn collect_markdown_files(root: &Path) -> Vec<PathBuf> {
    let mut files = Vec::new();
    visit_markdown_files(root, &mut files);
    files
}

fn visit_markdown_files(path: &Path, files: &mut Vec<PathBuf>) {
    let Ok(entries) = fs::read_dir(path) else {
        return;
    };

    for entry in entries.flatten() {
        let entry_path = entry.path();
        if entry_path.is_dir() {
            visit_markdown_files(&entry_path, files);
        } else if entry_path.extension().is_some_and(|suffix| suffix == "md") {
            files.push(entry_path);
        }
    }
}

fn iter_targets(text: &str) -> Vec<String> {
    let markdown_link_re = Regex::new(r"\[[^\]]*\]\(([^)]+)\)").expect("valid markdown link regex");
    let backtick_re = Regex::new(r"`([^`]+)`").expect("valid backtick regex");
    let mut targets = Vec::new();

    for captures in markdown_link_re.captures_iter(text) {
        if let Some(target) = captures.get(1) {
            targets.push(target.as_str().to_string());
        }
    }

    for captures in backtick_re.captures_iter(text) {
        if let Some(target) = captures.get(1) {
            let reference = target.as_str();
            if looks_like_local_path(reference) {
                targets.push(reference.to_string());
            }
        }
    }

    targets
}

fn looks_like_local_path(text: &str) -> bool {
    let candidate = text.trim().trim_matches('"').trim_matches('\'');
    if candidate.is_empty()
        || candidate.contains(' ')
        || candidate.contains('<')
        || candidate.contains('>')
    {
        return false;
    }
    if starts_with_skip_prefix(candidate) {
        return false;
    }
    if candidate.starts_with("./") || candidate.starts_with("../") {
        return true;
    }
    if !candidate.contains('/') {
        return false;
    }
    VALID_BACKTICK_SUFFIXES
        .iter()
        .any(|suffix| candidate.ends_with(suffix))
        || candidate.ends_with('/')
}

fn normalize_target(raw: &str) -> String {
    let mut target = raw.trim().trim_matches('"').trim_matches('\'').to_string();
    if target.starts_with('<') && target.ends_with('>') {
        target = target[1..target.len() - 1].trim().to_string();
    }
    if let Some((prefix, _)) = target.split_once('#') {
        target = prefix.to_string();
    }
    if let Some((prefix, _)) = target.split_once('?') {
        target = prefix.to_string();
    }
    target.trim().to_string()
}

fn path_exists(base_file: &Path, raw_target: &str, root: &Path) -> bool {
    let target = normalize_target(raw_target);
    if target.is_empty() || starts_with_skip_prefix(&target) {
        return true;
    }

    let candidates = if target.starts_with('/') {
        vec![root.join(target.trim_start_matches('/'))]
    } else {
        vec![
            base_file
                .parent()
                .unwrap_or_else(|| Path::new(""))
                .join(&target),
            root.join(&target),
        ]
    };
    candidates.iter().any(|candidate| candidate.exists())
}

fn starts_with_skip_prefix(text: &str) -> bool {
    SKIP_PREFIXES.iter().any(|prefix| text.starts_with(prefix))
}

fn display_path(path: &Path, root: &Path) -> String {
    path.strip_prefix(root)
        .unwrap_or(path)
        .to_string_lossy()
        .replace('\\', "/")
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::fs::{create_dir_all, write};

    fn fixture_root(name: &str) -> PathBuf {
        let root = std::env::temp_dir().join(format!(
            "logos_governance_fast_validators_{}_{}",
            name,
            std::process::id()
        ));
        let _ = fs::remove_dir_all(&root);
        create_dir_all(&root).expect("fixture root should be created");
        root
    }

    #[test]
    fn passes_valid_markdown_links_and_backtick_paths() {
        let root = fixture_root("pass");
        create_dir_all(root.join("docs")).expect("docs fixture should be created");
        write(
            root.join("README.md"),
            "[ok](docs/target.md)\n`docs/config.yaml`\n",
        )
        .expect("README fixture should be written");
        write(root.join("docs/target.md"), "target").expect("target fixture should be written");
        write(root.join("docs/config.yaml"), "key: value\n")
            .expect("yaml fixture should be written");

        let report = run_check(InternalLinksInput {
            root,
            all_markdown: false,
            paths: Vec::new(),
        });

        assert!(report.is_pass());
        assert_eq!(
            report.message,
            "Internal link validation passed (1 markdown files)."
        );
    }

    #[test]
    fn reports_missing_markdown_link_target() {
        let root = fixture_root("fail");
        write(root.join("README.md"), "[missing](docs/missing.md)\n")
            .expect("README fixture should be written");

        let report = run_check(InternalLinksInput {
            root,
            all_markdown: false,
            paths: Vec::new(),
        });

        assert!(!report.is_pass());
        assert_eq!(
            report.details,
            vec!["README.md: missing local target 'docs/missing.md'"]
        );
    }

    #[test]
    fn skips_external_links_and_fragments() {
        let root = fixture_root("skip");
        write(
            root.join("README.md"),
            "[web](https://example.com)\n[anchor](#local)\n",
        )
        .expect("README fixture should be written");

        let report = run_check(InternalLinksInput {
            root,
            all_markdown: false,
            paths: Vec::new(),
        });

        assert!(report.is_pass());
    }
}
