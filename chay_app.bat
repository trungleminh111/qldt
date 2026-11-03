@echo off
where python >nul 2>nul
if %errorlevel% neq 0 (
    set "PATH=C:\Users\Le Minh Trung\AppData\Local\Programs\Python\Python312;C:\Users\Le Minh Trung\AppData\Local\Programs\Python\Python312\Scripts;%PATH%"
)
python desktop_app.py
pause
