#!/usr/bin/env python3
"""
ColorOS Lyric Fixer - Configuration Patch Tool
Author: Aman (dev-aman-hear)

Injects custom music player package names into ColorOS / OxygenOS / Realme UI
SystemUI media controller configuration XML with lyricEntrance="52".
"""

import argparse
import sys
from datetime import datetime

def patch_xml(input_path: str, output_path: str, packages: list, custom_version: str = None):
    with open(input_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Determine version to use
    if custom_version:
        new_version = custom_version
    else:
        new_version = datetime.now().strftime("%Y%m%d01")

    # Update version tag
    if "<version>" in content and "</version>" in content:
        start_v = content.find("<version>") + len("<version>")
        end_v = content.find("</version>")
        old_version = content[start_v:end_v]
        content = content[:start_v] + new_version + content[end_v:]
        print(f"[+] Version updated: {old_version} -> {new_version}")

    # Process each package
    for pkg in packages:
        pkg = pkg.strip()
        if not pkg:
            continue

        # 1. Whitelist insertion
        wl_tag = f'<packageName name="{pkg}"/>'
        if wl_tag in content or f'<packageName name="{pkg}"' in content:
            print(f"[*] Package '{pkg}' already in whitelist.")
        else:
            ref_wl = '<packageName name="com.heytap.music"/>'
            if ref_wl in content:
                content = content.replace(ref_wl, f"{ref_wl}\n        {wl_tag}", 1)
                print(f"[+] Added '{pkg}' to <whitelist>.")
            else:
                if "</whitelist>" in content:
                    content = content.replace("</whitelist>", f"    {wl_tag}\n    </whitelist>", 1)
                    print(f"[+] Added '{pkg}' before </whitelist>.")
                else:
                    print(f"[-] Warning: <whitelist> tag not found!")

        # 2. Policy insertion
        policy_tag = f'<packageName name="{pkg}" actionPriority="1" actionPriorityQs="2" lyricEntrance="52"/>'
        if f'name="{pkg}"' in content and 'lyricEntrance="52"' in content:
            print(f"[*] Policy for '{pkg}' already configured.")
        else:
            ref_policy = '<packageName name="com.heytap.music" actionPriority="1" actionPriorityQs="2" lyricEntrance="52"/>'
            if ref_policy in content:
                content = content.replace(ref_policy, f"{ref_policy}\n        {policy_tag}", 1)
                print(f"[+] Added '{pkg}' policy (lyricEntrance=52).")
            else:
                if "</policy>" in content:
                    content = content.replace("</policy>", f"    {policy_tag}\n    </policy>", 1)
                    print(f"[+] Added '{pkg}' policy before </policy>.")
                else:
                    print(f"[-] Warning: <policy> tag not found!")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"[✔] Successfully generated patched XML at: {output_path}")

def main():
    parser = argparse.ArgumentParser(description="Patch ColorOS media controller XML config with lyric allowlist.")
    parser.add_argument("-i", "--input", required=True, help="Path to original app_systemui_oplus_media_controller_config.xml")
    parser.add_argument("-o", "--output", required=True, help="Path to save patched XML")
    parser.add_argument("-p", "--packages", nargs="+", required=True, help="Package name(s) to add (e.g. com.aman.auramusic)")
    parser.add_argument("-v", "--version", help="Custom version number (e.g. 2026102401)")
    args = parser.parse_args()

    patch_xml(args.input, args.output, args.packages, args.version)

if __name__ == "__main__":
    main()
