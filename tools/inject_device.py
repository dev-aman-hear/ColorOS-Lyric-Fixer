#!/usr/bin/env python3
"""
ColorOS Lyric Fixer - Root Device Injector Tool
Author: Aman (dev-aman-hear)

Injects modified XML configuration into ColorOS RomUpdate database
(/data/user_de/0/com.oplus.romupdate/databases/rom_update.db) via ADB and KernelSU/Magisk root.
"""

import argparse
import hashlib
import os
import sqlite3
import subprocess
import sys
import tempfile

FILTER_NAME = "app_systemui_oplus_media_controller_config"
DB_REMOTE_PATH = "/data/user_de/0/com.oplus.romupdate/databases/rom_update.db"

def run_adb(args):
    cmd = ["adb"] + args
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if res.returncode != 0:
        print(f"[-] ADB error: {res.stderr.strip()}")
        sys.exit(1)
    return res.stdout.strip()

def run_root_shell(sh_command):
    # Piping through KernelSU / su
    ps_cmd = f'echo "{sh_command}" | adb shell "/data/adb/ksud debug su || su -c sh || su"'
    res = subprocess.run(ps_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return res.stdout.strip()

def inject(xml_file: str, version: str):
    if not os.path.exists(xml_file):
        print(f"[-] XML file not found: {xml_file}")
        sys.exit(1)

    with open(xml_file, "r", encoding="utf-8") as f:
        xml_content = f.read()

    md5_hash = hashlib.md5(xml_content.encode("utf-8")).hexdigest()

    temp_dir = tempfile.gettempdir()
    local_db = os.path.join(temp_dir, "rom_update_temp.db")

    print("[*] Pulling current rom_update.db from device...")
    # Pull to tmp first with root copy
    run_root_shell(f"cp {DB_REMOTE_PATH} /data/local/tmp/rom_update.db && chmod 666 /data/local/tmp/rom_update.db")
    run_adb(["pull", "/data/local/tmp/rom_update.db", local_db])

    print("[*] Modifying SQLite database locally...")
    conn = sqlite3.connect(local_db)
    cursor = conn.cursor()

    cursor.execute("SELECT _id FROM update_list WHERE filterName=?", (FILTER_NAME,))
    row = cursor.fetchone()
    if row:
        print(f"[+] Updating existing entry (ID: {row[0]})...")
        cursor.execute("UPDATE update_list SET version=?, isOpen=1, md5=?, xml=? WHERE filterName=?",
                       (version, md5_hash, xml_content, FILTER_NAME))
    else:
        print("[+] Inserting new record into update_list...")
        cursor.execute("INSERT INTO update_list (filterName, version, isOpen, md5, url, xml, binary) VALUES (?, ?, 1, ?, NULL, ?, NULL)",
                       (FILTER_NAME, version, md5_hash, xml_content))

    conn.commit()
    conn.close()

    print("[*] Pushing updated database to device...")
    run_adb(["push", local_db, "/data/local/tmp/rom_update.db"])

    print("[*] Deploying database with proper ownership & SELinux contexts...")
    deploy_cmd = (
        f"am force-stop com.oplus.romupdate && "
        f"cp /data/local/tmp/rom_update.db {DB_REMOTE_PATH} && "
        f"rm -f {DB_REMOTE_PATH}-journal && "
        f"chown u0_a259:u0_a259 {DB_REMOTE_PATH} && "
        f"chmod 660 {DB_REMOTE_PATH} && "
        f"chcon u:object_r:app_data_file:s0:c3,c257,c512,c768 {DB_REMOTE_PATH} && "
        f"pkill -f com.android.systemui"
    )
    run_root_shell(deploy_cmd)
    print("[✔] Successfully injected! SystemUI restarted.")
    print("[*] Testing live preferences...")
    check = run_root_shell("cat /data/user_de/0/com.android.systemui/shared_prefs/oplus_media_controller_config_sp.xml | grep rus_lyric_entrance_key")
    print(f"Live policy: {check}")

def main():
    parser = argparse.ArgumentParser(description="Inject patched XML into device ROM Update database.")
    parser.add_argument("-x", "--xml", required=True, help="Path to patched XML file")
    parser.add_argument("-v", "--version", default="2026102401", help="Version to use (must be > 1610260810)")
    args = parser.parse_args()

    inject(args.xml, args.version)

if __name__ == "__main__":
    main()
