# OmniAssist 🚀

![CI](https://img.shields.io/badge/CI-Active-green)
![Lint](https://img.shields.io/badge/Lint-Active-green)
![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Version](https://img.shields.io/github/v/tag/AfifaM9/omniassist?label=version)

Operationalized Multi-Agent Networked Intelligence & Autonomous System Services Integration Toolkit (2026.3)

---

## Table of Contents
1. [Overview](#overview)
2. [Key Features](#key-features)
3. [Architecture & Directory Structure](#architecture--directory-structure)
4. [Prerequisites & Requirements](#prerequisites--requirements)
5. [Installation & Setup](#installation--setup)
6. [Configuration](#configuration)
7. [Running the Application](#running-the-application)
8. [Tool Ecosystem & MCP Integration](#tool-ecosystem--mcp-integration)
9. [Development & Contributing](#development--contributing)
10. [License](#license)

---

## Overview

**OmniAssist** is a lightweight, modular, and extensible AI operational agent framework designed to bridge the gap between large language models and local machine execution. By combining the power of the Google GenAI SDK, native function-calling capabilities, and a flexible Model Context Protocol (MCP) tool registry, OmniAssist operates directly within your terminal environment as a fully autonomous assistant.

Whether you're managing local system scripts, pulling live documentation, or orchestrating multi-step execution graphs, OmniAssist provides a seamless interactive command-line interface wrapped in clean Rich markdown panels.

---

## Key Features

- **Autonomous Tool Execution:** Dynamically interprets user intent, matches prompts against registered tools, and executes native Python or system commands.
- **Persistent CLI Interface:** Powered by Python's `rich` and `readline` libraries to provide a fluid, uninterrupted input loop with arrow-key history and clean block rendering.
- **Robust Error Handling:** Intercepts runtime exceptions, LLM formatting issues, and tool-registry mismatches gracefully to keep the session alive.
- **Modular Sub-system Architecture:** Separates core agent lifecycle management, cognitive reasoning plans, self-modification utilities, and MCP tool registries into distinct, maintainable modules.
- **Secure Environment Management:** Strictly isolates configuration credentials via `.env` files and `.gitignore` safety guards.

---

## Architecture & Directory Structure

```text
omniassist
├── .env.example             # Environment variable template/defaults (committed to git)
├── .gitignore               # Git exclusion rules (env files, venvs, cache, logs)
├── .github/                 # GitHub repository metadata & community guidelines
│   ├── CODE_OF_CONDUCT.md   # Community behavior standards and enforcement guidelines
│   ├── CONTRIBUTING.md      # Guidelines for submitting pull requests, issues, and code
│   ├── SECURITY.md          # Vulnerability reporting process and security policies
│   ├── PULL_REQUEST_TEMPLATE.md # Standard PR checklist, scope, and testing template
│   ├── ISSUE_TEMPLATE/      # GitHub issue creation templates
│   │   ├── bug_report.md    # Template for reporting bugs, errors, and reproducible crashes
│   │   └── feature_request.md # Template for proposing new sub-agents, tools, or enhancements
│   └── workflows/          # GitHub Actions workflows
│       ├── ci.yml           # Continuous integration pipeline
│       └── lint.yml         # Code linting workflow
├── CHANGELOG.md             # Version history and release notes
├── LICENSE.txt              # MIT License terms and copyright notice
├── README.md                # Project documentation, architecture overview, and setup guide
├── ann_summary_report.md    # ANN Summary Report
├── config/
│   └── config.yml           # Unified YAML configuration file for models, paths, and options
├── core/                    # Core agent orchestrator & execution loop
│   ├── __init__.py
│   ├── agent.py             # Main OmniAssist class (lifecycle, primary agent loop)
│   ├── reasoning.py         # Cognitive engine (ReAct, Plan-and-Solve, Self-Reflection)
│   ├── router.py            # Task routing between internal sub-agents and MCP tools
│   ├── selfmodify.py        # Code self-rewriting, agent update, and runtime patch logic
│   └── state.py             # Active conversation state & runtime context tracking
├── interfaces/              # I/O adapters & communication channels
│   ├── adapters/            # External messaging adapters
│   │   └── terminal_adapter.py
│   ├── api/                 # FastAPI server (REST endpoints & WebSocket streams)
│   │   └── server.py
│   └── cli.py               # Interactive terminal interface for OmniAssist
├── memory/                  # Multi-tiered memory architecture
│   ├── conversation.py      # Working memory & short-term message buffer
│   ├── session.py           # Session persistence across agent reboots
│   └── vector_store.py      # Long-term semantic memory (RAG vector index)
├── mcp_tools/               # Model Context Protocol (MCP) server & tool integrations
│   ├── basic_calc.py        # Arithmetic and standard math tool helper
│   ├── code_runner.py       # MCP code execution environment (sandboxed evaluation)
│   ├── ddgs_search.py       # DuckDuckGo web search integration wrapper via `ddgs`
│   ├── file_tools.py        # MCP filesystem interface (I/O, directory traversal, file editing)
│   ├── python_tool.py       # Tool interface for evaluating Python snippets
│   ├── registry.py          # Dynamic MCP server connection manager and tool loader
│   ├── robocalc.py          # Complex calculator (cmath)
│   ├── search_tools.py      # MCP search tools (web scraping, API access, knowledge search)
│   ├── shell_tool.py        # Tool interface for executing system shell commands
│   └── web_fetch.py         # Web content fetching and parsing
├── subagents/               # Specialized sub-agents supervised by OmniAssist
│   ├── base.py              # Abstract base class for specialized sub-agents
│   ├── code_agent.py        # Code generation, execution, and debugging sub-agent
│   ├── planner_agent.py     # Complex task breakdown & multi-step planning sub-agent
│   └── research_agent.py    # Information retrieval & document synthesis sub-agent
├── tests/                   # Automated test suite
│   ├── test_cli.py          # Tests for CLI slash commands
│   ├── test_core.py         # Unit tests for reasoning loops and agent routing
│   ├── test_mcp_tools.py    # Integration tests for MCP tool calls and error recovery
│   └── test_shell_tool.py   # Security tests for shell command blocking
├── requirements.txt         # Dependency declarations (MCP SDK, LLM frameworks, vector stores)
├── requirements-dev.txt     # Dev dependencies (includes -r requirements.txt)
├── requirements-dev-2.txt   # Standalone dev dependencies (pytest only)
└── main.py                  # Entry point script (contains embedded model priority & fallback notes)
```

---

## Prerequisites & Requirements

- **Python:** Version 3.11 or higher.
- **API Key:** A valid Google Gemini API key (`GEMINI_API_KEY` or `GOOGLE_API_KEY`).

---

## Installation & Setup

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/AfifaM9/omniassist.git
   cd omniassist
   ```

2. **Install Dependencies** (choose one method):

   **Method A:** Install `requirements.txt`
   ```bash
   python -m pip install -r requirements.txt
   ```

   **Method B:** Or, Install `requirements-dev.txt` (includes `requirements.txt`)
   ```bash
   python -m pip install -r requirements-dev.txt
   ```

   **Method C:** Concatenate requirements files
   ```bash
   python -m pip install -r requirements.txt -r requirements-dev-2.txt
   ```

---

## Configuration

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Open the `.env` file and insert your Gemini API key:
   ```env
   GEMINI_API_KEY=your_actual_api_key_here
   ```

3. Adjust model settings in `config/config.yml` if needed.

---

## Running the Application

Launch the interactive terminal interface:

```bash
python main.py
```

Once loaded, you can chat with OmniAssist or issue direct commands:
- Type `/help` to see available slash commands.
- Type `exit`, `quit`, or `q` to terminate the session (case insensitive).
- Run system queries or file operations directly through the agent.

---

## Tool Ecosystem & MCP Integration

OmniAssist utilizes a dynamic registry located in `mcp_tools/` to discover and bind callable Python functions. The agent inspects available tool objects, filters out non-callable classes, and maps model function calls directly to execution handlers in `core/router.py`.

---

## Development & Contributing

Contributions are welcome! Please check the `.github/` directory for code of conduct, contribution guidelines, and pull request templates.

1. Fork the repository.
2. Create your feature branch (`git checkout -b feature/amazing-feature`).
3. Commit your changes using casual, descriptive commit messages.
4. Push to the branch (`git push origin feature/amazing-feature`).
5. Open a Pull Request.
   * Add a **Before vs. After** if needed

Once ready to publish changes:
```bash
git add .
git commit -m "update full directory tree in readme and tidy up documentation"
git push origin main
```

---

## License

Distributed under the terms specified in [`LICENSE.txt`](LICENSE.txt).
