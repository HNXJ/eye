# Policy GAMMA v1.0
Target: Generalized Regex Policy Set
This repository contains scripts and configurations for optimizing Gemini CLI policies using a regex-based architecture, replacing granular literal matching for improved performance and maintainability.

## Architecture
- **Policy Optimizer:** `policy_optimizer.py` script to generate generalized regex rules.
- **Configuration:** `auto-saved.toml` managed by the script.
- **Documentation:** README and config files for clarity.

## Rules
- **Absolute Integrity:** Generalized policies will NOT allow `rm` on `*.dat`, `*.abf`, or `*.nwb` file extensions.
- **Shell Wildcards:** `run_shell_command` with `.*` is allowed for primary development commands, but current `$PWD` verification is mandatory.
- **Network Scoping:** Network access is limited unless explicitly specified.
