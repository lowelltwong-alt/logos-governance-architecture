mod internal_links;
mod reports;

use crate::internal_links::{run_check, InternalLinksInput};
use std::env;
use std::path::PathBuf;

struct ParsedInternalLinks {
    input: InternalLinksInput,
    json: bool,
}

fn main() {
    let args = env::args().skip(1).collect::<Vec<_>>();
    if args.is_empty() {
        print_usage();
        std::process::exit(2);
    }

    let command = &args[0];
    let result = match command.as_str() {
        "internal-links" => parse_internal_links(&args[1..]).map(|parsed| {
            let report = run_check(parsed.input);
            emit_report(&report, parsed.json);
            report.is_pass()
        }),
        _ => Err(format!("unknown command: {}", command)),
    };

    match result {
        Ok(true) => {}
        Ok(false) => std::process::exit(1),
        Err(message) => {
            eprintln!("{}", message);
            print_usage();
            std::process::exit(2);
        }
    }
}

fn parse_internal_links(args: &[String]) -> Result<ParsedInternalLinks, String> {
    let mut root =
        env::current_dir().map_err(|exc| format!("cannot resolve current dir: {}", exc))?;
    let mut all_markdown = false;
    let mut json = false;
    let mut paths = Vec::new();

    let mut index = 0;
    while index < args.len() {
        match args[index].as_str() {
            "--root" => {
                index += 1;
                let Some(value) = args.get(index) else {
                    return Err("--root requires a path".to_string());
                };
                root = PathBuf::from(value);
            }
            "--all-markdown" => all_markdown = true,
            "--json" => json = true,
            flag if flag.starts_with('-') => return Err(format!("unknown flag: {}", flag)),
            path => paths.push(PathBuf::from(path)),
        }
        index += 1;
    }

    Ok(ParsedInternalLinks {
        input: InternalLinksInput {
            root,
            all_markdown,
            paths,
        },
        json,
    })
}

fn emit_report(report: &reports::CheckReport, json: bool) {
    if json {
        println!("{}", report.to_json());
    } else if report.is_pass() {
        println!("{}", report.message);
    } else {
        for detail in &report.details {
            println!("FAIL {}", detail);
        }
    }
}

fn print_usage() {
    eprintln!(
        "Usage: logos_governance_fast_validators internal-links [--root PATH] [--all-markdown] [--json] [PATH ...]"
    );
}
