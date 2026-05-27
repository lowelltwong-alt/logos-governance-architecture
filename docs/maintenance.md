# Maintenance

This file contains operational maintenance instructions that should not clutter the public README.

## Maintenance runs

For long cleanup/buildout cycles, use the staged operations script:

- Script: `scripts/overnight_maintenance.sh`
- Stages:
  1. metadata lint and normalization
  2. cross-reference validation
  3. link validation
  4. report generation
- Checkpoints: stage completion markers are written to the generated runtime path `logs/overnight/checkpoints` so interrupted runs can resume safely.
- Logs: timestamped run logs are written to the generated runtime path `logs/overnight`.
- Reports: timestamped summaries are written to `reports/`.

## Common commands

```bash
# Normal run (resumable)
./scripts/overnight_maintenance.sh

# Preview normalization only (no writes)
./scripts/overnight_maintenance.sh --dry-run

# Treat warnings as failures
./scripts/overnight_maintenance.sh --strict

# Re-run all stages even if checkpoints exist
./scripts/overnight_maintenance.sh --force
```

## Example long run

Use either `nohup` or `tmux` for long sessions:

```bash
nohup ./scripts/overnight_maintenance.sh --strict > logs/overnight/nohup_$(date -u +"%Y%m%dT%H%M%SZ").out 2>&1 &
```

Or inside `tmux`:

```bash
tmux new -s overnight-maintenance './scripts/overnight_maintenance.sh --strict'
```

## AI-agent note

Before running maintenance commands, verify that `scripts/overnight_maintenance.sh` exists in the local checkout. If it does not exist, report the missing script rather than inventing a replacement command.
