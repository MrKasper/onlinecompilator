@echo off
chcp 65001 >nul
title Панель учителя
cd /d "%~dp0"
start http://localhost:8000/admin