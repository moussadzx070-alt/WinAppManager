@echo off
echo Building DZ Manager z EXE...
pip install -r requirements.txt
pyinstaller --noconfirm --onedir --windowed --icon "resources/icon.ico" --name "DZ_Manager_z" --add-data "resources;resources/" "main.py"
echo Build Complete! Check the 'dist' folder.
pause
