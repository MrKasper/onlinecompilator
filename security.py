# ============================================================
# Защита от спама — ГЛАВНЫЙ ФАКТОР: IP-адрес
# Имя студента используется только для удобства, НЕ для безопасности.
# ============================================================
import time
from collections import defaultdict
from threading import Lock, Semaphore


# ============================================================
# 1. RATE LIMITING (по IP — главный)
# ============================================================
_rate_lock = Lock()
_rate_buckets = defaultdict(list)

# Главный лимит — по IP (жёсткий, нельзя обойти сменой имени)
RATE_IP_MAX = 20           # запросов в минуту с одного IP
RATE_IP_WINDOW = 60

# Вспомогательный — по имени (для метрик, не блокирует жёстко)
RATE_STUDENT_MAX = 15      # запросов в минуту на имя
RATE_STUDENT_WINDOW = 60


def check_rate_limit(key: str, max_requests: int, window: int) -> bool:
    """True — можно. False — превышен лимит."""
    now = time.time()
    with _rate_lock:
        bucket = _rate_buckets[key]
        bucket[:] = [t for t in bucket if now - t < window]
        if len(bucket) >= max_requests:
            return False
        bucket.append(now)
        return True


# ============================================================
# 2. МИНИМАЛЬНОЕ ВРЕМЯ МЕЖДУ ЗАПУСКАМИ (по IP)
# ============================================================
_last_run_lock = Lock()
_last_run_ip = defaultdict(float)
MIN_INTERVAL_SEC = 2.0


def check_min_interval(ip: str) -> tuple[bool, float]:
    """Возвращает (можно, сколько_секунд_ждать). Привязано к IP."""
    now = time.time()
    with _last_run_lock:
        last = _last_run_ip.get(ip, 0)
        delta = now - last
        if delta < MIN_INTERVAL_SEC:
            return False, round(MIN_INTERVAL_SEC - delta, 1)
        _last_run_ip[ip] = now
        return True, 0


# ============================================================
# 3. ДЕТЕКТ СМЕНЫ ИМЕНИ С ОДНОГО IP
# ============================================================
_name_lock = Lock()
_ip_names = defaultdict(list)      # ip -> [(timestamp, name)]
MAX_NAMES_PER_IP = 3               # макс. разных имён с одного IP
NAMES_WINDOW = 300                 # за 5 минут


def check_name_change(ip: str, student: str) -> tuple[bool, str | None]:
    """Проверяет, не меняет ли кто-то имя, чтобы обойти лимит.

    Возвращает (ok, сообщение_об_ошибке).
    """
    now = time.time()
    with _name_lock:
        bucket = _ip_names[ip]
        # Чистим старые
        bucket[:] = [(t, n) for t, n in bucket if now - t < NAMES_WINDOW]

        unique_names = {n for _, n in bucket}

        # Если это новое имя — проверяем, не превышен ли лимит разных имён
        if student not in unique_names and len(unique_names) >= MAX_NAMES_PER_IP:
            return False, (
                f"🔒 С вашего IP уже использовались другие имена "
                f"({', '.join(sorted(unique_names))}). "
                f"Если вы сменили группу — обратитесь к преподавателю."
            )

        bucket.append((now, student))
        return True, None


# ============================================================
# 4. ЛОГ ПОДОЗРИТЕЛЬНЫХ IP
# ============================================================
_suspicious_lock = Lock()
_suspicious_ips = defaultdict(list)   # ip -> [{time, reason, student, code}]


def log_suspicious_ip(ip: str, student: str, reason: str, code: str = ""):
    """Логирует подозрительное действие для панели учителя."""
    with _suspicious_lock:
        _suspicious_ips[ip].append({
            "time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "student": student,
            "reason": reason,
            "code": (code or "")[:300],
        })
        # Ограничиваем размер
        if len(_suspicious_ips[ip]) > 100:
            _suspicious_ips[ip] = _suspicious_ips[ip][-100:]


def get_suspicious() -> dict:
    """Возвращает список подозрительных IP для админки."""
    with _suspicious_lock:
        return {ip: list(events) for ip, events in _suspicious_ips.items()}


def clear_suspicious():
    with _suspicious_lock:
        _suspicious_ips.clear()


# ============================================================
# 5. ОГРАНИЧЕНИЯ РАЗМЕРА
# ============================================================
MAX_CODE_SIZE = 50_000       # 50 КБ кода
MAX_REQUEST_SIZE = 200_000   # 200 КБ тело запроса


def check_code_size(code: str) -> str | None:
    if not isinstance(code, str):
        return "Код должен быть строкой"
    if len(code) > MAX_CODE_SIZE:
        return (f"⚠ Код слишком большой ({len(code):,} символов). "
                f"Максимум {MAX_CODE_SIZE:,}.")
    return None


# ============================================================
# 6. ЧЁРНЫЙ СПИСОК КОМАНД
# ============================================================
BLACKLIST = [
    "os.system", "os.popen", "os.exec", "os.spawn", "os.fork",
    "subprocess.", "shutil.rmtree", "shutil.move",
    "eval(", "exec(", "compile(",
    "__import__", "importlib",
    "globals(", "locals(", "vars(",
    "socket.socket", "urllib.request", "requests.get", "requests.post",
    "http.client", "ftplib", "smtplib", "telnetlib",
    "open('/etc", 'open("/etc',
    "open('/root", 'open("/root',
    "open('/home", 'open("/home',
    "open('/var", 'open("/var',
    "rm -rf", "rm -f /", ":(){:|:&};:",
    "System.IO.File.Delete",
    "System.IO.Directory.Delete",
    "Process.Start",
    "System.Diagnostics",
]

SUSPICIOUS = [
    "while true", "while 1", "while(1)", "while(true)",
    "Thread.Sleep(999999", "time.sleep(999",
]


def check_blacklist(code: str) -> str | None:
    if not isinstance(code, str):
        return None
    low = code.lower()
    for pat in BLACKLIST:
        if pat.lower() in low:
            return (f"🚫 Запрещённая конструкция: «{pat}».\n"
                    f"Уберите её из кода.")
    return None


def log_suspicious_code(code: str) -> list[str]:
    if not isinstance(code, str):
        return []
    low = code.lower()
    return [p for p in SUSPICIOUS if p.lower() in low]


# ============================================================
# 7. СТРОГИЙ РЕЖИМ (опционально)
# ============================================================
import os as _os
STRICT_NAMES = _os.environ.get("STRICT_NAMES", "0") == "1"
ALLOWED_NAMES: set[str] = set()
ALLOWED_GROUPS: set[str] = set()

try:
    from students import STUDENTS as _S
    ALLOWED_NAMES = set(_S)
except ImportError:
    pass


def check_name_allowed(student: str, group: str = "") -> str | None:
    """Если STRICT_NAMES=1 — принимает только имена из students.py."""
    if not STRICT_NAMES:
        return None
    if not ALLOWED_NAMES:
        return None
    if student not in ALLOWED_NAMES:
        return ("🔒 Ваше имя не найдено в списке группы. "
                "Обратитесь к преподавателю.")
    return None


# ============================================================
# 8. ОЧЕРЕДЬ НА C#
# ============================================================
_cs_semaphore = Semaphore(2)
_cs_queue_lock = Lock()
_cs_queue_size = 0
CS_QUEUE_TIMEOUT = 60


def acquire_cs_slot():
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
# 9. ОЧЕРЕДЬ НА PYTHON
# ============================================================
_py_semaphore = Semaphore(5)
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


# ============================================================
# 10. АВТООЧИСТКА СТАРЫХ ЗАПИСЕЙ (раз в час)
# ============================================================
_last_cleanup = [time.time()]


def cleanup_old_data():
    """Раз в час чистит устаревшие записи, чтобы память не росла."""
    now = time.time()
    if now - _last_cleanup[0] < 3600:
        return
    _last_cleanup[0] = now

    with _rate_lock:
        for k in list(_rate_buckets.keys()):
            _rate_buckets[k][:] = [t for t in _rate_buckets[k] if now - t < 3600]
            if not _rate_buckets[k]:
                del _rate_buckets[k]

    with _name_lock:
        for ip in list(_ip_names.keys()):
            _ip_names[ip][:] = [(t, n) for t, n in _ip_names[ip]
                                if now - t < NAMES_WINDOW]
            if not _ip_names[ip]:
                del _ip_names[ip]

# ============================================================
# 11. РАЗБЛОКИРОВКА IP (для учителя)
# ============================================================
def unblock_ip(ip: str) -> dict:
    """Снимает все блокировки с IP: rate-limit, имя-лимит, смена имени, suspicious."""
    result = {
        "ip": ip,
        "cleared_rate": 0,
        "cleared_name": 0,
        "cleared_suspicious": 0,
    }
    with _rate_lock:
        # Стираем все ключи, содержащие этот IP
        keys_to_delete = [k for k in _rate_buckets if ip in k]
        for k in keys_to_delete:
            del _rate_buckets[k]
        result["cleared_rate"] = len(keys_to_delete)

    with _name_lock:
        if ip in _ip_names:
            del _ip_names[ip]
            result["cleared_name"] = 1

    with _last_run_lock:
        if ip in _last_run_ip:
            del _last_run_ip[ip]

    with _suspicious_lock:
        if ip in _suspicious_ips:
            result["cleared_suspicious"] = len(_suspicious_ips[ip])
            del _suspicious_ips[ip]

    return result


def unblock_name(student: str) -> dict:
    """Снимает лимит с конкретного имени (без IP)."""
    result = {"student": student, "cleared": 0}
    key = f"student:{student}"
    with _rate_lock:
        if key in _rate_buckets:
            del _rate_buckets[key]
            result["cleared"] = 1
    return result