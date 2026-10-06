#!/bin/bash
# ============================================================
# Запуск онлайн-компилятора на Linux / macOS
# IP: 192.168.3.18   Порт: 5050
# ============================================================

set -e
cd "$(dirname "$0")"

# ---------- Цветной вывод ----------
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m'

echo -e "${BOLD}${BLUE}"
echo "=========================================="
echo "   ОНЛАЙН КОМПИЛЯТОР — ЗАПУСК"
echo "=========================================="
echo -e "${NC}"

# ---------- Настройки сервера ----------
HOST="${HOST:-0.0.0.0}"              # слушать все интерфейсы
PORT="${PORT:-5050}"                 # порт
PUBLIC_HOST="${PUBLIC_HOST:-192.168.3.18}"   # IP для отображения в браузере
ADMIN_PASSWORD="${ADMIN_PASSWORD:-Kexibqltym15w}"
WORKERS="${WORKERS:-4}"
THREADS="${THREADS:-8}"
TIMEOUT="${TIMEOUT:-300}"

# ---------- Проверка Python ----------
echo -e "${BOLD}[1/5]${NC} Проверка Python..."
if command -v python3 &>/dev/null; then
    PYTHON=python3
elif command -v python &>/dev/null; then
    PYTHON=python
else
    echo -e "${RED}  ✗ Python не найден в PATH!${NC}"
    echo "  Установите: sudo apt install python3 python3-pip python3-venv"
    exit 1
fi
PY_VER=$($PYTHON --version 2>&1 | awk '{print $2}')
echo -e "  ${GREEN}✓${NC} Python найден: ${BOLD}$PY_VER${NC} ($PYTHON)"

# ---------- Виртуальное окружение ----------
echo -e "${BOLD}[2/5]${NC} Виртуальное окружение..."
if [ ! -d "venv" ]; then
    echo "  Создаю venv..."
    $PYTHON -m venv venv || {
        echo -e "${RED}  ✗ Не удалось создать venv${NC}"
        echo "  Установите: sudo apt install python3-venv"
        exit 1
    }
    echo -e "  ${GREEN}✓${NC} venv создан"
else
    echo -e "  ${GREEN}✓${NC} venv уже существует"
fi

# shellcheck disable=SC1091
source venv/bin/activate

# ---------- Установка зависимостей ----------
echo -e "${BOLD}[3/5]${NC} Зависимости..."
if [ ! -f "requirements.txt" ]; then
    echo -e "${RED}  ✗ Не найден requirements.txt${NC}"
    exit 1
fi
if [ ! -f "venv/.installed" ] || [ "requirements.txt" -nt "venv/.installed" ]; then
    echo "  Устанавливаю пакеты (может занять минуту)..."
    pip install --upgrade pip --quiet
    pip install -r requirements.txt --quiet
    touch venv/.installed
    echo -e "  ${GREEN}✓${NC} Зависимости установлены"
else
    echo -e "  ${GREEN}✓${NC} Зависимости уже установлены"
fi

# ---------- Проверка файлов ----------
echo -e "${BOLD}[4/5]${NC} Проверка файлов проекта..."
REQUIRED_FILES=("app.py" "wsgi.py" "db.py" "executor.py" "tasks.py" "index.html" "admin.html")
MISSING=0
for f in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$f" ]; then
        echo -e "  ${RED}✗ Не найден: $f${NC}"
        MISSING=1
    fi
done
if [ $MISSING -eq 1 ]; then
    echo -e "${RED}  Не хватает файлов проекта.${NC}"
    exit 1
fi
echo -e "  ${GREEN}✓${NC} Все файлы на месте"

# ---------- Проверка .NET ----------
if command -v dotnet &>/dev/null; then
    DOTNET_VER=$(dotnet --version 2>/dev/null | head -n1)
    echo -e "  ${GREEN}✓${NC} .NET SDK: ${BOLD}$DOTNET_VER${NC}"
else
    echo -e "  ${YELLOW}⚠ .NET SDK не найден — задачи на C# работать НЕ будут.${NC}"
    echo "    Установка: sudo apt install dotnet-sdk-8.0"
    echo "    Или: https://dotnet.microsoft.com/download"
fi

# ---------- Проверка доступности порта ----------
echo -e "${BOLD}[5/5]${NC} Проверка порта $PORT..."
if command -v lsof &>/dev/null && lsof -i :"$PORT" &>/dev/null; then
    echo -e "  ${YELLOW}⚠ Порт $PORT уже занят!${NC}"
    echo "  Используйте другой: PORT=5051 ./start.sh"
    echo "  Или найдите процесс: sudo lsof -i :$PORT"
    read -p "  Продолжить всё равно? [y/N] " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo -e "  ${GREEN}✓${NC} Порт $PORT свободен"
fi

# ---------- Определение реального IP ----------
REAL_IP=$(hostname -I 2>/dev/null | awk '{print $1}')
if [ -z "$REAL_IP" ]; then
    REAL_IP="$PUBLIC_HOST"
fi

# ---------- Запуск ----------
echo ""
echo -e "${BOLD}${GREEN}=========================================="
echo "   СЕРВЕР ЗАПУЩЕН"
echo -e "==========================================${NC}"
echo ""
echo -e "  ${BOLD}Студенты:${NC}  http://$REAL_IP:$PORT"
echo -e "  ${BOLD}Учитель:${NC}   http://$REAL_IP:$PORT/admin"
echo -e "  ${BOLD}Пароль:${NC}    $ADMIN_PASSWORD"
echo -e "  ${BOLD}Задач:${NC}     $(grep -c '"id":' tasks.py 2>/dev/null || echo '?')"
echo ""
echo -e "  ${BOLD}Локально:${NC}  http://localhost:$PORT"
echo -e "  ${YELLOW}Остановить: Ctrl+C${NC}"
echo -e "${BOLD}${GREEN}==========================================${NC}"
echo ""

export ADMIN_PASSWORD
export HOST
export PORT

# ---------- Открыть браузер (локально) ----------
if command -v xdg-open &>/dev/null; then
    (sleep 3 && xdg-open "http://localhost:$PORT" >/dev/null 2>&1 &)
elif command -v open &>/dev/null; then
    (sleep 3 && open "http://localhost:$PORT" >/dev/null 2>&1 &)
fi

# ---------- Запуск gunicorn ----------
if command -v gunicorn &>/dev/null; then
    exec gunicorn \
        -w "$WORKERS" \
        -k gthread \
        --threads "$THREADS" \
        -b "$HOST:$PORT" \
        --timeout "$TIMEOUT" \
        --access-logfile - \
        --error-logfile - \
        wsgi:app
else
    echo -e "${YELLOW}⚠ gunicorn не найден — использую встроенный сервер Flask${NC}"
    echo -e "${YELLOW}  Для продакшена: pip install gunicorn${NC}"
    echo ""
    exec python app.py
fi