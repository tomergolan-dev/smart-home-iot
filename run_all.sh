#!/bin/bash

PROJECT_DIR="/Users/tomergolan/Documents/GitHub/smart-home-iot"

echo "==============================="
echo "Starting Smart Home IoT System"
echo "==============================="
echo ""

osascript <<EOF
tell application "Terminal"
    activate

    do script "cd \"$PROJECT_DIR\" && python3 manager/manager.py"
    delay 2

    do script "cd \"$PROJECT_DIR\" && python3 emulators/ac_relay.py"
    delay 2

    do script "cd \"$PROJECT_DIR\" && python3 emulators/temperature_sensor.py"
    delay 2

    do script "cd \"$PROJECT_DIR\" && python3 emulators/button_emulator.py"
    delay 2

    do script "cd \"$PROJECT_DIR\" && python3 gui/gui.py"
end tell
EOF

echo "System started successfully!"