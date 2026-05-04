@echo off
echo Starting Nuitka build with Python 3.12 + MinGW64...
"C:\Users\andhika.gulpa\AppData\Roaming\uv\tools\nuitka\Scripts\python.exe" -m nuitka --standalone --onefile --windows-console-mode=disable --enable-plugin=tk-inter --include-module=keyboard --include-package=mido --mingw64 --lto=yes --assume-yes-for-downloads --output-filename=playSong_clean.exe --output-dir=dist_nuitka playSong_clean.py
echo.
echo Build exit code: %ERRORLEVEL%
