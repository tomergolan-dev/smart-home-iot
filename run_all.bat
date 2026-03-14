@echo off
title Smart Home IoT System Launcher

echo ===============================
echo Starting Smart Home IoT System
echo ===============================

echo.

echo Starting Manager...
start cmd /k python manager\manager.py

timeout /t 2 >nul

echo Starting AC Relay Emulator...
start cmd /k python emulators\ac_relay.py

timeout /t 2 >nul

echo Starting Temperature Sensor Emulator...
start cmd /k python emulators\temperature_sensor.py

timeout /t 2 >nul

echo Starting Button Emulator...
start cmd /k python emulators\button_emulator.py

timeout /t 2 >nul

echo Starting GUI...
start cmd /k python gui\gui.py

echo.
echo System started successfully!
pause