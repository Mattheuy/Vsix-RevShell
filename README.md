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
python3 vsixgen.py <LHOST> <LPORT> <output.vsix>
