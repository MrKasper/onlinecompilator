# ============================================================
# WSGI-точка входа для gunicorn (Linux) и waitress (Windows)
# Отключает все лишние логи — stdout/stderr уходят в /dev/null
# ============================================================
import os
import sys
import logging

# ---------- Отключаем логи Flask / Werkzeug ----------
logging.getLogger("werkzeug").disabled = True
logging.getLogger("flask.app").disabled = True
logging.getLogger("flask").disabled = True
logging.getLogger("gunicorn").disabled = True
logging.getLogger("gunicorn.access").disabled = True
logging.getLogger("gunicorn.error").disabled = True

# ---------- Отключаем print() из кода ----------
QUIET = os.environ.get("QUIET", "1")
if QUIET == "1":
    try:
        _devnull = open(os.devnull, "w")
        sys.stdout = _devnull
        sys.stderr = _devnull
    except Exception:
        pass

# ---------- Импортируем приложение ----------
from app import app

if __name__ == "__main__":
    app.run()