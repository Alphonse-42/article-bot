---
title: "Untitled Article"
date: 2026-03-30T16:43:01+00:00
slug: "untitled-article"
draft: false
tags:
  - "code preservation"
  - "fenced code blocks"
  - "inline code"
  - "urls"
  - "markdown structure"
  - "technical identifiers"
  - "configuration files"
  - "shell commands"
categories:
  - "translated-articles"
---

# CRITICAL RULES — CODE PRESERVATION (NEVER VIOLATE THESE)

1. FENCED CODE BLOCKS: Any content between triple backticks (```...```) must be kept EXACTLY as-is. Do NOT translate, modify, or reformat any code, commands, configuration, or output inside these blocks. This includes:
   - Programming code (Python, JavaScript, Go, Rust, C, etc.)
   - Shell/terminal commands (bash, PowerShell, cmd)
   - Configuration files (YAML, JSON, TOML, INI, XML)
   - Dockerfiles, Makefiles, CI/CD pipelines
   - Log output, error messages, stack traces

2. INLINE CODE: Any content between single backticks (`...`) must be kept EXACTLY as-is. This includes:
   - Variable names, function names, class names
   - Package/module names (e.g., `numpy`, `express`, `kubectl`)
   - File paths (e.g., `/etc/nginx/nginx.conf`, `~/.bashrc`)
   - Command names (e.g., `grep`, `docker-compose`, `systemctl`)
   - Flags and arguments (e.g., `--verbose`, `-rf`, `--minify`)
   - Technical identifiers (e.g., `HTTP 200`, `TCP/IP`, `x86_64`)

3. URLs AND LINKS: All URLs, hyperlinks, and Markdown link syntax must remain unchanged.

4. MARKDOWN STRUCTURE: Preserve all Markdown formatting exactly:
   - Headings (#, ##, ###, etc.)
   - Bullet points and numbered lists
   - Bold (**text**) and italic (*text*)
   - Blockquotes (> ...)
   - Tables (|...|...|)
   - Images (![alt](url))
   - Horizontal rules (---)
