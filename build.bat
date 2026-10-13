@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul
title Сборка OnlineCompiler.exe
color 0A
cd /d "%~dp0"

echo.
echo ==========================================
echo    СБОРКА ONLINE COMPILER
echo ==========================================
echo.

REM ============================================================
REM [1/6] Проверка Python
REM ============================================================
echo [1/6] Проверка Python...
where python >nul 2>nul
if errorlevel 1 (
    echo   [ОШИБКА] Python не найден в PATH
    echo   Установите Python 3.9+ и добавьте в PATH
    pause
    exit /b 1
)
for /f "tokens=2" %%v in ('python --version 2^>^&1') do set "PY_VER=%%v"
echo   Python: !PY_VER!

REM ============================================================
REM [2/6] Виртуальное окружение
REM ============================================================
echo [2/6] Проверка venv...
if not exist "venv\Scripts\python.exe" (
    echo   Создаю venv...
    python -m venv venv
    if errorlevel 1 (
        echo   [ОШИБКА] Не удалось создать venv
        pause
        exit /b 1
    )
)

call venv\Scripts\activate.bat
if errorlevel 1 (
    echo   [ОШИБКА] Не удалось активировать venv
    pause
    exit /b 1
)
echo   venv активирован

REM ============================================================
REM [3/6] Установка зависимостей
REM ============================================================
echo [3/6] Проверка зависимостей...
python -c "import flask" >nul 2>nul
if errorlevel 1 (
    echo   Устанавливаю Flask и Waitress...
    pip install -r requirements.txt
)
python -c "import PyInstaller" >nul 2>nul
if errorlevel 1 (
    echo   Устанавливаю PyInstaller...
    pip install pyinstaller
)
echo   Зависимости готовы

REM ============================================================
REM [4/6] Очистка старых сборок
REM ============================================================
echo [4/6] Очистка старых сборок...
if exist "build" rmdir /S /Q "build" >nul 2>nul
if exist "dist" rmdir /S /Q "dist" >nul 2>nul
echo   Очищено

REM ============================================================
REM [5/6] Сборка через PyInstaller
REM ============================================================
echo [5/6] Сборка OnlineCompiler.exe (может занять 1-2 минуты)...
pyinstaller --clean compiler.spec
if errorlevel 1 (
    echo   [ОШИБКА] Сборка не удалась
    pause
    exit /b 1
)

REM ============================================================
REM [6/6] Копирование БД и вспомогательных файлов
REM ============================================================
echo [6/6] Копирование данных...

REM Если есть существующая data.db — копируем в dist
if exist "data.db" (
    copy /Y "data.db" "dist\OnlineCompiler\data.db" >nul
    echo   Скопирована data.db
) else (
    echo   data.db ещё нет — создастся при первом запуске
)

REM Создаём папку backups рядом с exe
if not exist "dist\OnlineCompiler\backups" mkdir "dist\OnlineCompiler\backups"
echo   Папка backups готова

REM ============================================================
REM Создаём start.bat внутри dist\OnlineCompiler\
REM ============================================================
(
    echo @echo off
    echo chcp 65001 ^>nul
    echo title OnlineCompiler
    echo cd /d "%%~dp0"
    echo echo.
    echo echo ==========================================
    echo echo    ONLINE COMPILER ЗАПУЩЕН
    echo echo ==========================================
    echo echo.
    echo echo   Студенты:  http://localhost:5050
    echo echo   Учитель:   http://localhost:5050/admin
    echo echo.
    echo echo   Остановить: Ctrl+C
    echo echo ==========================================
    echo echo.
    echo start "" cmd /c "timeout /t 2 ^>nul ^&^& start http://localhost:5050"
    echo OnlineCompiler.exe
    echo pause
) > "dist\OnlineCompiler\start.bat"

REM Создаём ярлык на админку
(
    echo @echo off
    echo start http://localhost:5050/admin
) > "dist\OnlineCompiler\admin.bat"

REM ============================================================
REM ГОТОВО
REM ============================================================
echo.
echo ==========================================
echo    СБОРКА ЗАВЕРШЕНА
echo ==========================================
echo.
echo   Папка сборки:  dist\OnlineCompiler\
echo.
echo   Содержимое:
echo     - OnlineCompiler.exe    ^(основной файл^)
echo     - start.bat             ^(запуск + открыть браузер^)
echo     - admin.bat             ^(открыть панель учителя^)
echo     - data.db               ^(база, если была^)
echo     - backups\              ^(резервные копии^)
echo     - index.html, admin.html
echo     - _internal\            ^(библиотеки Python^)
echo.
echo   Для работы: перенесите всю папку OnlineCompiler
echo   на нужный ПК и запустите start.bat
echo.
pause
endlocal