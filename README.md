# OmniAssist 🚀

Operationalized Multi-Agent Networked Intelligence & Autonomous System Services Integration Toolkit (2026.1)

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
omniassist/
├── config/
│   └── config.yml
├── core/
│   ├── agent.py
│   ├── reasoning.py
│   ├── router.py
│   ├── selfmodify.py
│   └── state.py
├── interfaces/
│   └── cli.py
├── mcp_tools/
│   └── registry.py
├── memory/
├── subagents/
├── tests/
├── .env.example
├── .gitignore
├── LICENSE.txt
├── README.md
├── main.py
└── requirements.txt
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

2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   *(Power users: virtual environments are optional and can be skipped if managing global or system environments directly).*

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
- Type `exit` or `quit` to terminate the session.
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

Once ready to publish changes:
```bash
git add .
git commit -m "update full directory tree in readme and tidy up documentation"
git push origin main
```

---

## License

Distributed under the terms specified in [LICENSE.txt](LICENSE.txt).
