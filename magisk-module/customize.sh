SKIPUNZIP=0

ui_print "*****************************************"
ui_print "       ColorOS Native Lyric Fixer        "
ui_print "          for ColorOS 15 / 16            "
ui_print "*****************************************"
ui_print "- Extracting module files..."

set_perm_recursive $MODPATH 0 0 0755 0644
set_perm $MODPATH/service.sh 0 0 0755

ui_print "- Boot service registered successfully."
ui_print "- Done! Please reboot your device."
