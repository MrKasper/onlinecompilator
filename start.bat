@echo off
chcp 65001 >nul
title Онлайн компилятор
cd /d "%~dp0"

echo Проверка зависимостей...
python -c "import flask, waitress" 2>nul
if errorlevel 1 (
    echo Установка зависимостей...
    pip install -r requirements.txt
)

echo.
echo Запуск сервера на http://localhost:8000
echo Админка: http://localhost:8000/admin (пароль: teacher2026)
echo Остановить: Ctrl+C
echo.

start "" cmd /c "timeout /t 3 >nul && start http://localhost:8000"
python app.py
pause