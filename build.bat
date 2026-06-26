@echo off
echo Building WinAppManager EXE...
pip install -r requirements.txt
pyinstaller --noconfirm --onedir --windowed --icon "resources/icon.ico" --name "WinAppManager" --add-data "resources;resources/" "main.py"
echo Build Complete! Check the 'dist' folder.
pause
