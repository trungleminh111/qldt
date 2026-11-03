@echo off
where python >nul 2>nul
if %errorlevel% neq 0 (
    set "PATH=C:\Users\Le Minh Trung\AppData\Local\Programs\Python\Python312;C:\Users\Le Minh Trung\AppData\Local\Programs\Python\Python312\Scripts;%PATH%"
)
pip install pyinstaller openpyxl Flask pg8000
pyinstaller --noconsole --onefile --icon="app_icon.ico" --name "QuanLyDienThoaiDaiDoi" --hidden-import=pg8000 --hidden-import=pg8000.dbapi --add-data "templates;templates" --add-data "static;static" --add-data ".env;." desktop_app.py
if not exist dist mkdir dist
copy /y .env dist\.env
pause