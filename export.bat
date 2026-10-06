@echo off
chcp 65001 >nul
title Экспорт решений
cd /d "%~dp0"
echo Открываю CSV со всеми решениями в браузере...
start http://localhost:8000/api/export.csv