# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/2.0.0/),
and this project adheres to [Calendar Versioning](https://calver.org/).

## [v2026.7] - 2026-10-21

*Release "2026.7 \"Eton Mass\"".*

### Added
- **OCR tooling** (`mcp_tools/ocr_tool.py`): `ocr_image`, `ocr_pdf`, and `ocr_languages`, backed by the host Tesseract binary and invoked as a subprocess so no Python binding is required. Handles images, multi-page PDFs (via `pdftoppm`), language-pack validation, and blank/unreadable inputs.
- **Long-term semantic memory** (`memory/vector_store.py`): a persisted vector index with `add_document`, `search`, `get_document`, `save`, `load`, and `clear`. Uses `sentence-transformers` when available and falls back to a deterministic hashing embedder otherwise; vectors are recomputed automatically when the backend changes.
- Agent memory integration: completed turns are stored and relevant notes are recalled into the system prompt. New `recall()` and `remember()` methods, plus `OMNIASSIST_MEMORY_DIR` to relocate storage.
- `/memory` CLI command showing the embedding backend, storage path, document count, and recent notes.
- Test suites `tests/test_agent_loop.py`, `tests/test_memory.py`, and `tests/test_ocr_tool.py` (125 tests total, up from 68).

### Fixed
- **Tool calls never executed.** `core/agent.py` dispatched to `self.router.execute(...)`, but `TaskRouter` only defines `route()`. The `hasattr` guard silently degraded every tool call to the literal string `"Executed <tool>"`, so no tool ever ran. Tool calls now dispatch through `MCPToolRegistry.execute_tool`, and results are fed back to the model until it produces a final answer.
- **Automatic function calling bypassed the agent loop.** `google-genai` enables it by default, executing tools inside the SDK where they were invisible to `last_tool_log` and to memory. It is now explicitly disabled so there is a single, observable execution path.
- **Multi-turn tool conversations were malformed.** The model's function-call turn was not preserved before appending results, and `max_iterations` was loaded but unused. The loop now appends the model turn, honours `max_iterations`, and reports when the cap is reached.
- Memory turn identifiers were off by one (`turn-1` for the first exchange).

### Changed
- Bumped version to 2026.7 across `config/config.yml`, `main.py`, `interfaces/cli.py`, `interfaces/api/server.py`, `mcp_tools/search_tools.py` (User-Agent), and `README.md`.
- Added `python-dotenv` to `requirements.txt`; `.env` was previously never loaded because the dependency was undeclared.
- README corrected: tool calls are documented as routing through the MCP registry rather than `core/router.py`, and the test tree now lists all suites.

## [v2026.6] - 2026-10-19

*Release "2026.6 \"Dirt Cake\"".*

### Changed
- **Model hierarchy refreshed.** Primary model is now `gemini-3.6-flash-lite`; `gemini-3.5-flash-lite` and the previous chain follow as fallbacks (`gemini-3.6-flash-lite` -> `gemini-3.5-flash-lite` -> `gemini-3.1-flash-lite` -> `gemini-3-flash` -> `gemini-2.5-flash` -> `gemini-2.5-flash-lite` -> `gemma-4-31B-it` -> `gemma-4-26B-A4B-it`).
- Bumped version to 2026.6 across `config/config.yml`, `main.py`, `interfaces/cli.py`, `interfaces/api/server.py`, and `mcp_tools/search_tools.py` (User-Agent).

## [v2026.4] - 2026-09-13

### Changed
- Bumped version to 2026.4 across `config/config.yml`, `main.py`, `interfaces/cli.py`, `interfaces/api/server.py`, `mcp_tools/search_tools.py` (User-Agent), `README.md`, and `SECURITY.md`
- Expanded the supported-version table in `SECURITY.md` from 2026.3 to 2026.4
- Reworked the model fallback chain to try the primary model first and automatically move on to the next fallback when a model call fails (primary: `gemini-3.5-flash-lite` → `gemini-3.1-flash-lite` → `gemini-3-flash` → `gemini-2.5-flash` → `gemini-2.5-flash-lite` → `gemma-4-31B-it` → `gemma-4-26B-A4B-it`)

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

[v2026.6]: https://github.com/AfifaM9/omniassist/tree/v2026.6
[v2026.4]: https://github.com/AfifaM9/omniassist/compare/v2026.3...v2026.4
[v2026.3]: https://github.com/AfifaM9/omniassist/compare/v2026.2...v2026.3
[v2026.2]: https://github.com/AfifaM9/omniassist/compare/v2026.1...v2026.2
[v2026.1]: https://github.com/AfifaM9/omniassist/tree/v2026.1
