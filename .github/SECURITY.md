# Security Policy & Vulnerability Disclosure Framework 🛡️
OmniAssist operates as an autonomous operational agent framework interacting directly with local system resources, sensitive APIs, and execution environments. Because of its deep system integration and tool-calling capabilities, maintaining a robust, transparent, and rigorous security posture is paramount. 
This document outlines our complete vulnerability reporting guidelines, threat models, architectural security boundaries, and the explicit **whys** behind every defensive measure implemented within the framework.
---
## Table of Contents
1. [Supported Versions](#supported-versions)
2. [Reporting a Vulnerability](#reporting-a-vulnerability)
3. [Core Threat Model & Architecture Security (The Whys)](#core-threat-model--architecture-security-the-whys)
4. [Secure Coding & Operational Best Practices](#secure-coding--operational-best-practices)
5. [Vulnerability Response Lifecycle](#vulnerability-response-lifecycle)
---
## Supported Versions
Only the latest stable release and the current active development branch (`main`) receive security patches. Older minor or major versions are deprecated upon a new stable release due to rapid evolution of our MCP tool registry and core execution loops.

| Version | Supported | Why this policy exists |
| :--- | :--- | :--- |
| 2026.1+ | :white_check_mark: | Active patches, dependency audits, and continuous penetration testing. |
| < 2026.1 | :x: | Legacy versions lack modern sandboxing primitives and secure MCP boundaries. |

---
## Reporting a Vulnerability
**Please do not report security vulnerabilities through public GitHub issues.** Public disclosures expose users to zero-day exploitation before a patch can be developed and deployed.
### Private Disclosure Process
- **Primary Contact:** Send details directly to `security@omniassist.local` (or open a private security advisory on GitHub if available).
- **Required Information:**
  - Clear description of the vulnerability.
  - Steps, scripts, or payloads required to reproduce the issue.
  - Potential impact assessment (e.g., Remote Code Execution, Arbitrary File Read, API Key leakage).
- **Response Timeline:** 
  - **Initial Acknowledgment:** Within 48 hours.
  - **Status Update / Triage:** Within 5 business days.
---
## Core Threat Model & Architecture Security (The Whys)
OmniAssist executes code, interacts with filesystems, and interfaces with external network APIs. Below are the foundational security controls and the explicit architectural reasons (**the whys**) behind them.
### 1. Separation of Environment Variables (`.env` vs `.env.example`)
- **Control:** All secrets (`GEMINI_API_KEY`, custom ports, internal tokens) reside strictly in `.env`, which is ignored by git, while `.env.example` contains only non-sensitive placeholder keys.
- **Why:** Committing production secrets to version control creates permanent historical leaks in git logs, allowing anyone with repository read-access to compromise cloud resources, rack up unauthorized API billing, or pivot into private infrastructure.
### 2. Sandbox Isolation for Code Runners (`mcp_tools/code_runner.py`)
- **Control:** Dynamic python execution and shell tools are wrapped behind strict validation and containment boundaries.
- **Why:** Large language models can occasionally hallucinate malicious code structures, destructive terminal commands (e.g., `rm -rf /`), or recursive loops. Isolating tool execution prevents an unverified LLM output from destroying host operating systems or leaking environment variables via malicious command injections.
### 3. Least Privilege Principle in MCP Registries (`mcp_tools/registry.py`)
- **Control:** Tools are explicitly registered and filtered; arbitrary functions cannot be invoked by the model unless bound within the explicit registry whitelist.
- **Why:** If the model were allowed to dynamically import and invoke arbitrary python system modules (like `subprocess` or `ctypes`) without a strict registry filter, prompt injection attacks could trick the model into executing arbitrary system binaries.
### 4. Git Exclusion Rules (`.gitignore`)
- **Control:** Comprehensive exclusion of `venv/`, cache directories, runtime logs, and local databases.
- **Why:** Prevents accidental pollution of the repository with ephemeral local state, bloated virtual environment binaries, and sensitive SQLite session logs that could leak historical conversation context.
---
## Secure Coding & Operational Best Practices
When extending OmniAssist or writing custom MCP tools (`mcp_tools/`), developers must adhere to these mandatory security guidelines:
1. **Input Sanitization:** Never pass raw, unvalidated string inputs from user prompts or LLM generation directly into shell execution functions or SQL queries.
2. **Credential Handling:** Always retrieve API keys and secrets via environment variable calls (e.g., `os.getenv("GEMINI_API_KEY")`) rather than hardcoding values into script logic.
3. **Error Suppression:** Ensure production error handlers do not leak full stack traces, local file paths, or internal memory contents back to the user interface, as this aids reconnaissance phases during attacks.
---
## Vulnerability Response Lifecycle
1. **Receipt & Triage:** The security team validates the reproduction steps and assesses severity using CVSS v3.1 scoring.
2. **Patch Development:** A secure fix is developed in a private security fork.
3. **Regression Testing:** Automated test suites (`tests/test_core.py`, `tests/test_mcp_tools.py`) verify that the fix does not break core agent workflows.
4. **Coordinated Release:** A patched version is published alongside an advisory detailing the technical impact and upgrade instructions.
