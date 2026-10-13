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
REM [0/7] Поиск рабочего Python
REM ============================================================
echo [0/7] Поиск Python...

set "PY_CMD="

REM Пробуем py -3 (Python Launcher) — самый надёжный
py -3 --version >nul 2>nul
if not errorlevel 1 (
    set "PY_CMD=py -3"
    echo   Найден: py -3
    goto :python_found
)

REM Пробуем python — но проверяем, что это НЕ заглушка Microsoft Store
python --version >nul 2>nul
if not errorlevel 1 (
    REM Заглушка MS Store не выводит версию на stdout
    for /f "tokens=*" %%v in ('python --version 2^>^&1') do set "PY_TEST=%%v"
    echo !PY_TEST! | findstr /C:"Python 3" >nul
    if not errorlevel 1 (
        set "PY_CMD=python"
        echo   Найден: python
        goto :python_found
    )
)

REM Пробуем python3
python3 --version >nul 2>nul
if not errorlevel 1 (
    set "PY_CMD=python3"
    echo   Найден: python3
    goto :python_found
)

REM Ничего не нашли
echo.
echo   [ОШИБКА] Рабочий Python не найден!
echo.
echo   Возможные причины:
echo     1. Python не установлен
echo     2. В PATH находится заглушка Microsoft Store
echo     3. Python не добавлен в PATH при установке
echo.
echo   Как исправить:
echo     1. Скачайте Python 3.11 с https://www.python.org/downloads/
echo     2. При установке поставьте галочку "Add Python to PATH"
echo     3. Отключите заглушки Microsoft Store:
echo        Параметры - Приложения - Дополнительные параметры -
echo        Псевдонимы выполнения приложения - отключите python.exe и python3.exe
echo.
pause
exit /b 1

:python_found
REM Проверяем версию
for /f "tokens=*" %%v in ('%PY_CMD% --version 2^>^&1') do set "PY_VER=%%v"
echo   Версия: !PY_VER!

REM ============================================================
REM [1/7] Виртуальное окружение
REM ============================================================
echo [1/7] Проверка venv...
if not exist "venv\Scripts\python.exe" (
    echo   Создаю venv...
    %PY_CMD% -m venv venv
    if errorlevel 1 (
        echo   [ОШИБКА] Не удалось создать venv
        echo.
        echo   Попробуйте вручную:
        echo     %PY_CMD% -m venv venv
        pause
        exit /b 1
    )
) else (
    REM Проверяем, что venv рабочий
    venv\Scripts\python.exe --version >nul 2>nul
    if errorlevel 1 (
        echo   venv сломан — пересоздаю...
        rmdir /S /Q "venv" >nul 2>nul
        %PY_CMD% -m venv venv
        if errorlevel 1 (
            echo   [ОШИБКА] Не удалось пересоздать venv
            pause
            exit /b 1
        )
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
REM [2/7] Установка зависимостей
REM ============================================================
echo [2/7] Проверка зависимостей...
python -c "import flask" >nul 2>nul
if errorlevel 1 (
    echo   Устанавливаю Flask и Waitress...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo   [ОШИБКА] Не удалось установить Flask/Waitress
        pause
        exit /b 1
    )
)
python -c "import PyInstaller" >nul 2>nul
if errorlevel 1 (
    echo   Устанавливаю PyInstaller...
    pip install pyinstaller
    if errorlevel 1 (
        echo   [ОШИБКА] Не удалось установить PyInstaller
        pause
        exit /b 1
    )
)
echo   Зависимости готовы

REM ============================================================
REM [3/7] Проверка файлов проекта
REM ============================================================
echo [3/7] Проверка файлов проекта...
set "MISSING=0"
for %%f in (app.py db.py executor.py security.py tasks.py index.html admin.html compiler.spec) do (
    if not exist "%%f" (
        echo   [ОШИБКА] Не найден %%f
        set "MISSING=1"
    )
)
if !MISSING!==1 (
    echo.
    echo   Не хватает файлов проекта.
    pause
    exit /b 1
)
echo   Все файлы на месте

REM ============================================================
REM [4/7] Очистка старых сборок
REM ============================================================
echo [4/7] Очистка старых сборок...
if exist "build" rmdir /S /Q "build" >nul 2>nul
if exist "dist" rmdir /S /Q "dist" >nul 2>nul
echo   Очищено

REM ============================================================
REM [5/7] Сборка через PyInstaller
REM ============================================================
echo [5/7] Сборка OnlineCompiler.exe (может занять 1-2 минуты)...
echo   Команда: pyinstaller --clean compiler.spec
echo.
pyinstaller --clean compiler.spec
if errorlevel 1 (
    echo.
    echo   [ОШИБКА] Сборка не удалась
    echo.
    echo   Проверьте сообщения выше. Возможные причины:
    echo     - ошибки в Python-коде
    echo     - не все зависимости установлены
    echo     - PyInstaller не может найти compiler.spec
    pause
    exit /b 1
)
echo   Сборка завершена успешно

REM ============================================================
REM [6/7] Копирование БД и вспомогательных файлов
REM ============================================================
echo [6/7] Копирование данных...

if not exist "dist\OnlineCompiler" (
    echo   [ОШИБКА] Папка dist\OnlineCompiler не создана
    pause
    exit /b 1
)

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

REM Копируем .secret_key если есть (чтобы сессия сохранилась)
if exist ".secret_key" (
    copy /Y ".secret_key" "dist\OnlineCompiler\.secret_key" >nul
    echo   Скопирован .secret_key
)

REM ============================================================
REM [7/7] Создание start.bat и admin.bat
REM ============================================================
echo [7/7] Создание start.bat и admin.bat...

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

(
    echo @echo off
    echo start http://localhost:5050/admin
) > "dist\OnlineCompiler\admin.bat"

REM ============================================================
REM ГОТОВО
REM ============================================================
echo.
echo ==========================================
echo    СБОРКА ЗАВЕРШЕНА УСПЕШНО
echo ==========================================
echo.
echo   Папка сборки:  dist\OnlineCompiler\
echo.
echo   Содержимое:
echo     - OnlineCompiler.exe    (основной файл)
echo     - start.bat             (запуск + открыть браузер)
echo     - admin.bat             (открыть панель учителя)
echo     - data.db               (база, если была)
echo     - backups\              (резервные копии)
echo     - index.html, admin.html
echo     - _internal\            (библиотеки Python)
echo.
echo   Для работы: перенесите всю папку OnlineCompiler
echo   на нужный ПК и запустите start.bat
echo.
pause
endlocal