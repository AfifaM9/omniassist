# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Calendar Versioning](https://calver.org/).

## [v2026.3]

### Added
- Added a slash-command framework to the CLI with a `/help` command that renders available commands in a Rich table
- Added an unknown-command handler that warns on unrecognized slash commands and points users to `/help`
- Added `tests/test_cli.py` covering slash-command matching, quit patterns, and edge cases
- Added GitHub Actions CI workflow (`.github/workflows/ci.yml`) running the pytest suite on Python 3.11
- Added GitHub Actions Lint workflow (`.github/workflows/lint.yml`) running `ruff check`
- Added status badges (CI, Lint, Python, License, Version) to the README
- Added a "Before vs. After" section and an "Other" checkbox to the PR template

### Changed
- Bumped version to 2026.3 across `config/config.yml`, `main.py`, `interfaces/cli.py`, `interfaces/api/server.py`, and `mcp_tools/search_tools.py` (User-Agent)
- Expanded the supported-version table in `SECURITY.md` from 2026.2 to 2026.3
- Reworked the README directory tree to reflect the full current structure (adapters, API server, `web_fetch.py`, requirements files) and dropped the stale `.env` / `venv` entries
- Documented `/help` in the README's usage section and linked `LICENSE.txt` in the License section

### Removed
- Removed redundant project scaffolding entries from the README tree (local `.env` and `venv/` directories)

## [v2026.2] - 2026-08-04

### Added
- Added `/help` command to display available slash commands

### Removed
- Removed catastrophic commands that could cause data loss or system damage

## [v2026.1]

### Added
- Initial Release

[v2026.3]: https://github.com/AfifaM9/omniassist/compare/v2026.2...v2026.3
[v2026.2]: https://github.com/AfifaM9/omniassist/compare/v2026.1...v2026.2
[v2026.1]: https://github.com/AfifaM9/omniassist/tree/v2026.1
