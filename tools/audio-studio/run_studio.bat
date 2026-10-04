@echo off
cd /d "%~dp0"
python studio.py
if errorlevel 1 pause
