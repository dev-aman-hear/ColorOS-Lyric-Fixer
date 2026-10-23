#!/system/bin/sh
# ColorOS Lyric Fixer - Persistent Boot Service
# Automatically checks and ensures rom_update.db has the custom lyric entrance allowlist

MODDIR=${0%/*}
TARGET_DIR="/data/user_de/0/com.oplus.romupdate/databases"
TARGET_DB="$TARGET_DIR/rom_update.db"

# Wait for decrypted user_de storage
while [ ! -d "$TARGET_DIR" ]; do
    sleep 2
done

# If our custom database backup exists in module directory, restore if wiped or modified
if [ -f "$MODDIR/rom_update.db" ]; then
    CURRENT_MD5=$(md5sum "$TARGET_DB" 2>/dev/null | awk '{print $1}')
    BACKUP_MD5=$(md5sum "$MODDIR/rom_update.db" 2>/dev/null | awk '{print $1}')

    if [ "$CURRENT_MD5" != "$BACKUP_MD5" ]; then
        am force-stop com.oplus.romupdate 2>/dev/null
        cp "$MODDIR/rom_update.db" "$TARGET_DB"
        rm -f "$TARGET_DB-journal" "$TARGET_DB-wal" "$TARGET_DB-shm"

        # Dynamically preserve ownership and SELinux context
        ROM_OWNER=$(stat -c '%u:%g' /data/user_de/0/com.oplus.romupdate 2>/dev/null || echo "u0_a259:u0_a259")
        chown "$ROM_OWNER" "$TARGET_DB"
        chmod 660 "$TARGET_DB"
        chcon --reference="$TARGET_DIR" "$TARGET_DB" 2>/dev/null || chcon u:object_r:app_data_file:s0:c3,c257,c512,c768 "$TARGET_DB" 2>/dev/null

        # Reload SystemUI
        pkill -f com.android.systemui
    fi
fi
