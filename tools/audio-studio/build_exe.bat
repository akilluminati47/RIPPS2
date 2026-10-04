@echo off
rem Builds "RIPPS2 Audio Studio.exe" in dist\ (pip install pyinstaller first)
cd /d "%~dp0"
python -m PyInstaller --noconfirm --onefile --windowed --name "RIPPS2 Audio Studio" --add-data "fonts;fonts" --exclude-module scipy --exclude-module tkinter --exclude-module matplotlib studio.py
