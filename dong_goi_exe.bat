@echo off
where python >nul 2>nul
if %errorlevel% neq 0 (
    set "PATH=C:\Users\Le Minh Trung\AppData\Local\Programs\Python\Python312;C:\Users\Le Minh Trung\AppData\Local\Programs\Python\Python312\Scripts;%PATH%"
)
pip install pyinstaller openpyxl Flask
pyinstaller --noconsole --onefile --icon="app_icon.ico" --name "QuanLyDienThoaiDaiDoi" --add-data "templates;templates" --add-data "static;static" desktop_app.py
pause
