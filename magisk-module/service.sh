#!/system/bin/sh
# ColorOS Lyric Fixer - Persistent Boot Service
# Automatically checks and ensures rom_update.db has the custom lyric entrance allowlist

MODDIR=${0%/*}
TARGET_DB="/data/user_de/0/com.oplus.romupdate/databases/rom_update.db"

# Wait for decrypted user_de storage
while [ ! -d /data/user_de/0/com.oplus.romupdate/databases ]; do
    sleep 2
done

# If our custom database backup exists in module directory, restore if wiped
if [ -f "$MODDIR/rom_update.db" ]; then
    CURRENT_MD5=$(md5sum "$TARGET_DB" 2>/dev/null | awk '{print $1}')
    BACKUP_MD5=$(md5sum "$MODDIR/rom_update.db" 2>/dev/null | awk '{print $1}')

    if [ "$CURRENT_MD5" != "$BACKUP_MD5" ]; then
        am force-stop com.oplus.romupdate
        cp "$MODDIR/rom_update.db" "$TARGET_DB"
        rm -f "$TARGET_DB-journal"
        chown u0_a259:u0_a259 "$TARGET_DB"
        chmod 660 "$TARGET_DB"
        chcon u:object_r:app_data_file:s0:c3,c257,c512,c768 "$TARGET_DB"
        pkill -f com.android.systemui
    fi
fi
