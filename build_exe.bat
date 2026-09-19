@echo off
setlocal
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m PyInstaller --noconfirm --clean --onefile --name YtDown --add-data "templates;templates" --add-data "static;static" --collect-all imageio_ffmpeg --collect-all pytubefix app.py
echo.
echo Pronto: dist\YtDown.exe
pause
