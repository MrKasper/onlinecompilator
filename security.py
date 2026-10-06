# ============================================================
# Защита от спама и злоупотреблений
# ============================================================
import time
from collections import defaultdict
from threading import Lock, Semaphore


# ============================================================
# 1. RATE LIMITING
# ============================================================
_rate_lock = Lock()
_rate_buckets = defaultdict(list)

# Настройки (можно переопределить через env)
RATE_STUDENT_MAX = 10      # запросов в минуту на студента
RATE_STUDENT_WINDOW = 60   # окно в секундах
RATE_IP_MAX = 30           # запросов в минуту на IP
RATE_IP_WINDOW = 60


def check_rate_limit(key: str, max_requests: int, window: int) -> bool:
    """True — можно продолжать. False — превышен лимит."""
    now = time.time()
    with _rate_lock:
        bucket = _rate_buckets[key]
        bucket[:] = [t for t in bucket if now - t < window]
        if len(bucket) >= max_requests:
            return False
        bucket.append(now)
        return True


# ============================================================
# 2. МИНИМАЛЬНОЕ ВРЕМЯ МЕЖДУ ЗАПУСКАМИ
# ============================================================
_last_run_lock = Lock()
_last_run = defaultdict(float)
MIN_INTERVAL_SEC = 2.0   # минимум 2 секунды между запусками


def check_min_interval(student: str) -> tuple[bool, float]:
    """Возвращает (можно, сколько_секунд_ждать)."""
    now = time.time()
    with _last_run_lock:
        last = _last_run.get(student, 0)
        delta = now - last
        if delta < MIN_INTERVAL_SEC:
            return False, round(MIN_INTERVAL_SEC - delta, 1)
        _last_run[student] = now
        return True, 0


# ============================================================
# 3. ОГРАНИЧЕНИЯ РАЗМЕРА
# ============================================================
MAX_CODE_SIZE = 50_000       # 50 КБ кода
MAX_REQUEST_SIZE = 200_000   # 200 КБ тело запроса


def check_code_size(code: str) -> str | None:
    """Возвращает текст ошибки или None."""
    if not isinstance(code, str):
        return "Код должен быть строкой"
    if len(code) > MAX_CODE_SIZE:
        return (f"⚠ Код слишком большой ({len(code):,} символов). "
                f"Максимум {MAX_CODE_SIZE:,}.")
    return None


# ============================================================
# 4. ЧЁРНЫЙ СПИСОК КОМАНД
# ============================================================
BLACKLIST = [
    # Работа с системой
    "os.system", "os.popen", "os.exec", "os.spawn", "os.fork",
    "subprocess.", "shutil.rmtree", "shutil.move",
    # Опасные функции
    "eval(", "exec(", "compile(",
    "__import__", "importlib",
    "globals(", "locals(", "vars(",
    # Сеть
    "socket.socket", "urllib.request", "requests.get", "requests.post",
    "http.client", "ftplib", "smtplib", "telnetlib",
    # Файлы вне песочницы
    "open('/etc", 'open("/etc',
    "open('/root", 'open("/root',
    "open('/home", 'open("/home',
    "open('/var", 'open("/var',
    # Уничтожение
    "rm -rf", "rm -f /", ":(){:|:&};:",   # fork bomb
    # Деструктивные вызовы C#
    "System.IO.File.Delete",
    "System.IO.Directory.Delete",
    "Process.Start",
    "System.Diagnostics",
]

# Мягкая проверка (не блокируем, но логируем)
SUSPICIOUS = [
    "while true", "while 1", "while(1)", "while(true)",
    "Thread.Sleep(999999", "time.sleep(999",
]


def check_blacklist(code: str) -> str | None:
    """Проверка на запрещённые конструкции. Возвращает текст ошибки или None."""
    if not isinstance(code, str):
        return None
    low = code.lower()
    for pat in BLACKLIST:
        if pat.lower() in low:
            return (f"🚫 Запрещённая конструкция: «{pat}».\n"
                    f"Уберите её из кода. Если считаете блокировку ошибочной — "
                    f"обратитесь к преподавателю.")
    return None


def log_suspicious(code: str) -> list[str]:
    """Возвращает список подозрительных конструкций (для логирования)."""
    if not isinstance(code, str):
        return []
    low = code.lower()
    return [p for p in SUSPICIOUS if p.lower() in low]


# ============================================================
# 5. ОЧЕРЕДЬ НА C#
# ============================================================
_cs_semaphore = Semaphore(2)   # одновременно не более 2 сборок C#
_cs_queue_lock = Lock()
_cs_queue_size = 0
CS_QUEUE_TIMEOUT = 60          # максимум 60 сек ожидания


def acquire_cs_slot():
    """Занимает слот сборки C#. Возвращает (успех, позиция_в_очереди)."""
    global _cs_queue_size
    with _cs_queue_lock:
        _cs_queue_size += 1
        position = _cs_queue_size

    acquired = _cs_semaphore.acquire(timeout=CS_QUEUE_TIMEOUT)

    if not acquired:
        with _cs_queue_lock:
            _cs_queue_size -= 1
        return False, position
    return True, position


def release_cs_slot():
    global _cs_queue_size
    _cs_semaphore.release()
    with _cs_queue_lock:
        _cs_queue_size -= 1


def cs_queue_info() -> dict:
    with _cs_queue_lock:
        return {"in_queue": _cs_queue_size}


# ============================================================
# 6. ОЧЕРЕДЬ НА PYTHON
# ============================================================
_py_semaphore = Semaphore(5)   # одновременно не более 5 Python-запусков
_py_queue_lock = Lock()
_py_queue_size = 0
PY_QUEUE_TIMEOUT = 30


def acquire_py_slot():
    global _py_queue_size
    with _py_queue_lock:
        _py_queue_size += 1
        position = _py_queue_size
    acquired = _py_semaphore.acquire(timeout=PY_QUEUE_TIMEOUT)
    if not acquired:
        with _py_queue_lock:
            _py_queue_size -= 1
        return False, position
    return True, position


def release_py_slot():
    global _py_queue_size
    _py_semaphore.release()
    with _py_queue_lock:
        _py_queue_size -= 1


def py_queue_info() -> dict:
    with _py_queue_lock:
        return {"in_queue": _py_queue_size}