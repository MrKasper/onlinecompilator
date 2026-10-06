# ============================================================
# Flask-приложение: онлайн-компилятор
# Защита: rate-limit по IP, детект смены имени, чёрный список,
# очереди на C#/Python, sandbox, логирование подозрительных IP,
# разблокировка IP и имён для учителя.
# ============================================================
import csv
import io
import os
import secrets
import sys
import traceback
from functools import wraps
from pathlib import Path

from flask import (
    Flask, request, jsonify, send_from_directory,
    session, redirect, render_template_string,
)

from tasks import TASKS
from db import (
    init_db, load_submissions, add_submission, delete_submission,
    load_attempts, add_attempt,
    load_grades, save_grade, delete_grade,
    get_stats, auto_grade, backup_db,
)
from executor import (
    run_code, detect_dotnet, find_python, prepare_csharp_template,
)
from security import (
    # Проверки
    check_rate_limit, check_min_interval,
    check_code_size, check_blacklist, log_suspicious_code,
    check_name_change, check_name_allowed,
    cleanup_old_data,
    # Подозрительные
    log_suspicious_ip, get_suspicious, clear_suspicious,
    unblock_ip, unblock_name,
    # Константы
    MAX_REQUEST_SIZE, MAX_CODE_SIZE,
    RATE_STUDENT_MAX, RATE_STUDENT_WINDOW,
    RATE_IP_MAX, RATE_IP_WINDOW,
    # Очереди
    acquire_cs_slot, release_cs_slot, cs_queue_info,
    acquire_py_slot, release_py_slot, py_queue_info,
)


HERE = Path(__file__).parent
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "teacher2026")

app = Flask(__name__, static_folder=None)
app.secret_key = os.environ.get("SECRET_KEY", secrets.token_hex(16))
app.config["MAX_CONTENT_LENGTH"] = MAX_REQUEST_SIZE


# ============================================================
# Хелпер: реальный IP клиента (учитывает прокси)
# ============================================================
def get_client_ip() -> str:
    forwarded = request.headers.get("X-Forwarded-For", "")
    if forwarded:
        return forwarded.split(",")[0].strip()
    real_ip = request.headers.get("X-Real-IP", "")
    if real_ip:
        return real_ip.strip()
    return request.remote_addr or "unknown"


# ============================================================
# Авторизация
# ============================================================
LOGIN_HTML = """
<!DOCTYPE html><html><head><meta charset="utf-8">
<title>Вход в панель учителя</title>
<style>
body{font-family:system-ui;background:#f5f6f8;display:flex;align-items:center;
justify-content:center;height:100vh;margin:0}
form{background:#fff;padding:32px 36px;border-radius:12px;
box-shadow:0 8px 32px rgba(0,0,0,.08);width:340px}
h2{color:#111827;margin:0 0 20px;font-size:18px}
input{width:100%;padding:10px 14px;border:1px solid #d1d5db;border-radius:6px;
font-size:14px;font-family:inherit;box-sizing:border-box}
input:focus{outline:none;border-color:#2563eb;box-shadow:0 0 0 3px rgba(37,99,235,.12)}
button{margin-top:14px;width:100%;padding:10px;background:#2563eb;color:#fff;
border:none;border-radius:6px;font-size:14px;font-weight:600;cursor:pointer}
button:hover{background:#1d4ed8}
.err{color:#dc2626;font-size:13px;margin-top:8px}
</style></head><body>
<form method="post">
  <h2>🔐 Вход в панель учителя</h2>
  <input type="password" name="password" placeholder="Пароль" autofocus>
  {% if error %}<div class="err">{{ error }}</div>{% endif %}
  <button type="submit">Войти</button>
</form></body></html>
"""


def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get("admin"):
            if request.path.startswith("/api/"):
                return jsonify({"error": "Требуется авторизация"}), 401
            return redirect("/admin/login")
        return f(*args, **kwargs)
    return wrapper


# ============================================================
# Страницы
# ============================================================
@app.route("/")
def index():
    return send_from_directory(str(HERE), "index.html")


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    error = None
    if request.method == "POST":
        if request.form.get("password") == ADMIN_PASSWORD:
            session["admin"] = True
            return redirect("/admin")
        error = "Неверный пароль"
    return render_template_string(LOGIN_HTML, error=error)


@app.route("/admin/logout")
def admin_logout():
    session.pop("admin", None)
    return redirect("/admin/login")


@app.route("/admin")
@admin_required
def admin():
    return send_from_directory(str(HERE), "admin.html")


# ============================================================
# API — общее
# ============================================================
@app.route("/api/tasks")
def api_tasks():
    return jsonify([
        {"id": t["id"], "title": t["title"],
         "difficulty": t.get("difficulty", "easy"),
         "tags": t.get("tags", [])}
        for t in TASKS
    ])


@app.route("/api/tasks/<task_id>")
def api_task(task_id):
    task = next((t for t in TASKS if t["id"] == task_id), None)
    if not task:
        return jsonify({"error": "Задача не найдена"}), 404
    public = {k: v for k, v in task.items() if k != "solution"}
    return jsonify(public)


@app.route("/api/tasks/<task_id>/solution")
def api_task_solution(task_id):
    """Разбор решения — только после успешного решения студентом."""
    task = next((t for t in TASKS if t["id"] == task_id), None)
    if not task:
        return jsonify({"error": "Задача не найдена"}), 404

    student = request.args.get("student", "").strip()
    if not student:
        return jsonify({"error": "Укажите имя (параметр student)"}), 400

    subs = load_submissions()
    solved = any(
        s["student"] == student and s["task_id"] == task_id
        and s["passed"] == s["total"]
        for s in subs
    )
    if not solved:
        return jsonify({
            "error": "🔒 Разбор доступен только после успешного решения задачи."
        }), 403

    sol = task.get("solution")
    if not sol:
        return jsonify({"error": "Разбор для этой задачи пока не добавлен"}), 404
    return jsonify(sol)


@app.route("/api/students")
def api_students():
    names = set()
    for s in load_submissions():
        if s.get("student"):
            names.add(s["student"])
    return jsonify(sorted(names))


# ============================================================
# API — запуск (с полной защитой)
# ============================================================
@app.route("/api/run", methods=["POST"])
def api_run():
    data = request.get_json(force=True) or {}
    task_id = data.get("task_id", "")
    code = data.get("code", "")
    language = data.get("language", "python")
    student = (data.get("student") or "Аноним").strip()
    group_name = (data.get("group") or "").strip()
    custom_tests = data.get("custom_tests") or []

    ip = get_client_ip()

    # ---------- 0. Раз в час чистим устаревшие записи ----------
    cleanup_old_data()

    # ---------- 1. Минимальный интервал (2 сек) — по IP ----------
    ok, wait = check_min_interval(ip)
    if not ok:
        return jsonify({
            "error": f"⏱ Подождите {wait} сек. перед следующим запуском.",
            "tests": []
        }), 429

    # ---------- 2. Rate limit по IP (ГЛАВНЫЙ) ----------
    if not check_rate_limit(f"ip:{ip}", RATE_IP_MAX, RATE_IP_WINDOW):
        log_suspicious_ip(ip, student,
                          f"rate_limit_ip ({RATE_IP_MAX}/{RATE_IP_WINDOW}s)", code)
        print(f"[RATE-IP] {ip} · {student} — превышен лимит IP")
        return jsonify({
            "error": f"⏱ Слишком много запросов с вашего IP. "
                     f"Не более {RATE_IP_MAX} в минуту. Подождите.",
            "tests": []
        }), 429

    # ---------- 3. Rate limit по имени (вспомогательный) ----------
    if not check_rate_limit(f"student:{student}",
                            RATE_STUDENT_MAX, RATE_STUDENT_WINDOW):
        log_suspicious_ip(ip, student,
                          f"rate_limit_name ({RATE_STUDENT_MAX}/{RATE_STUDENT_WINDOW}s)",
                          code)
        print(f"[RATE-NAME] {ip} · {student} — превышен лимит имени")
        return jsonify({
            "error": f"⏱ Слишком много запусков от имени «{student}». "
                     f"Не более {RATE_STUDENT_MAX} в минуту.",
            "tests": []
        }), 429

    # ---------- 4. Детект смены имени с одного IP ----------
    ok, err = check_name_change(ip, student)
    if not ok:
        log_suspicious_ip(ip, student, "name_change_block", code)
        print(f"[NAME-CHANGE] {ip} · {student} — блок")
        return jsonify({"error": err, "tests": []}), 429

    # ---------- 5. Строгий режим (если STRICT_NAMES=1) ----------
    name_err = check_name_allowed(student, group_name)
    if name_err:
        log_suspicious_ip(ip, student, "name_not_allowed", code)
        return jsonify({"error": name_err, "tests": []}), 403

    # ---------- 6. Размер кода ----------
    size_err = check_code_size(code)
    if size_err:
        return jsonify({"error": size_err, "tests": []}), 413

    # ---------- 7. Чёрный список команд ----------
    danger = check_blacklist(code)
    if danger:
        log_suspicious_ip(ip, student, f"blacklist: {danger[:60]}", code)
        print(f"[BLACKLIST] {ip} · {student} · {danger[:60]}")
        return jsonify({"error": danger, "tests": []}), 400

    # Логируем подозрительное, но не блокируем
    sus = log_suspicious_code(code)
    if sus:
        log_suspicious_ip(ip, student, f"suspicious_code: {sus}", code)
        print(f"[SUSPICIOUS] {ip} · {student} · {sus}")

    # ---------- 8. Проверка задачи ----------
    task = next((t for t in TASKS if t["id"] == task_id), None)
    if not task:
        return jsonify({"error": f"Задача '{task_id}' не найдена", "tests": []}), 404

    # ---------- 9. Очередь на C# / Python ----------
    if language == "csharp":
        acquired, position = acquire_cs_slot()
        if not acquired:
            log_suspicious_ip(ip, student, "cs_queue_overflow", code)
            return jsonify({
                "error": "⏱ Очередь на C# переполнена. Попробуйте через минуту.",
                "tests": []
            }), 503
        print(f"[RUN-CS] {ip} · {student!r} · {task_id!r} (очередь #{position})")
        try:
            result = run_code(code, task, language, custom_tests=custom_tests)
        finally:
            release_cs_slot()

    elif language == "python":
        acquired, position = acquire_py_slot()
        if not acquired:
            log_suspicious_ip(ip, student, "py_queue_overflow", code)
            return jsonify({
                "error": "⏱ Очередь на Python переполнена. Попробуйте через минуту.",
                "tests": []
            }), 503
        print(f"[RUN-PY] {ip} · {student!r} · {task_id!r} (очередь #{position})")
        try:
            result = run_code(code, task, language, custom_tests=custom_tests)
        finally:
            release_py_slot()

    else:
        return jsonify({"error": f"Язык '{language}' не поддерживается", "tests": []}), 400

    # ---------- 10. Сохранение результата ----------
    add_attempt(
        student=student, group_name=group_name,
        task_id=task_id, language=language, code=code,
        passed=result.get("passed", 0), total=result.get("total", 0),
        tests=result.get("tests", []), error=result.get("error"),
    )

    if (not result.get("error") and result.get("total", 0) > 0
            and result.get("passed") == result.get("total")):
        add_submission(
            student=student, group_name=group_name,
            task_id=task_id, language=language, code=code,
            passed=result["passed"], total=result["total"],
            tests=result["tests"],
        )
        ag = auto_grade(result["passed"], result["total"])
        existing = next(
            (g for g in load_grades()
             if g["student"] == student and g["task_id"] == task_id), None
        )
        if existing is None or existing.get("grade") is None:
            save_grade(student, task_id, grade=None, auto_grade=ag)

    return jsonify(result)


# ============================================================
# API — админские (защищены)
# ============================================================
@app.route("/api/submissions")
@admin_required
def api_submissions():
    return jsonify(load_submissions())


@app.route("/api/submissions", methods=["DELETE"])
@admin_required
def api_delete_submission():
    data = request.get_json(force=True) or {}
    student = data.get("student", "")
    task_id = data.get("task_id", "")
    language = data.get("language", "")
    if not (student and task_id and language):
        return jsonify({"error": "Не указаны параметры"}), 400
    delete_submission(student, task_id, language)
    print(f"[DEL]  {student} · {task_id} · {language}")
    return jsonify({"ok": True})


@app.route("/api/attempts")
@admin_required
def api_attempts():
    student = request.args.get("student")
    task_id = request.args.get("task_id")
    return jsonify(load_attempts(student=student, task_id=task_id, limit=500))


@app.route("/api/attempts/me")
def api_attempts_me():
    """История попыток студента (без авторизации)."""
    student = request.args.get("student", "").strip()
    if not student:
        return jsonify([])
    return jsonify(load_attempts(student=student, limit=200))


@app.route("/api/grades")
def api_grades():
    return jsonify(load_grades())


@app.route("/api/grade", methods=["POST"])
@admin_required
def api_save_grade():
    data = request.get_json(force=True) or {}
    student = (data.get("student") or "").strip()
    task_id = data.get("task_id", "")
    grade = data.get("grade")
    comment = data.get("comment", "")
    teacher = data.get("teacher", "")
    try:
        grade = int(grade) if grade not in (None, "") else None
    except (ValueError, TypeError):
        grade = None
    save_grade(student, task_id, grade=grade, comment=comment, teacher=teacher)
    print(f"[GRADE] {student} · {task_id} · {grade}")
    return jsonify({"ok": True})


@app.route("/api/grade", methods=["DELETE"])
@admin_required
def api_delete_grade():
    data = request.get_json(force=True) or {}
    delete_grade(data.get("student", ""), data.get("task_id", ""))
    return jsonify({"ok": True})


@app.route("/api/stats")
@admin_required
def api_stats():
    return jsonify(get_stats())


@app.route("/api/backup", methods=["POST"])
@admin_required
def api_backup():
    path = backup_db()
    return jsonify({"ok": True, "path": path})


# ============================================================
# API — подозрительные IP и разблокировка
# ============================================================
@app.route("/api/suspicious")
@admin_required
def api_suspicious():
    """Список подозрительных IP с событиями."""
    return jsonify(get_suspicious())


@app.route("/api/suspicious", methods=["DELETE"])
@admin_required
def api_clear_suspicious():
    """Полная очистка списка (но БЕЗ снятия блокировок)."""
    clear_suspicious()
    print("[SUSPICIOUS] очищен список")
    return jsonify({"ok": True})


@app.route("/api/suspicious/unblock", methods=["POST"])
@admin_required
def api_unblock_ip():
    """Разблокировать IP: снять rate-limit, имя-лимит, смену имени, suspicious."""
    data = request.get_json(force=True) or {}
    ip = (data.get("ip") or "").strip()
    if not ip:
        return jsonify({"error": "Не указан IP"}), 400
    result = unblock_ip(ip)
    print(f"[UNBLOCK] {ip} — снято: rate={result['cleared_rate']}, "
          f"names={result['cleared_name']}, susp={result['cleared_suspicious']}")
    return jsonify({"ok": True, "result": result})


@app.route("/api/suspicious/unblock-name", methods=["POST"])
@admin_required
def api_unblock_name():
    """Снять лимит с конкретного имени."""
    data = request.get_json(force=True) or {}
    student = (data.get("student") or "").strip()
    if not student:
        return jsonify({"error": "Не указано имя"}), 400
    result = unblock_name(student)
    print(f"[UNBLOCK-NAME] {student} — снято: {result['cleared']}")
    return jsonify({"ok": True, "result": result})


# ============================================================
# API — экспорт CSV
# ============================================================
@app.route("/api/export.csv")
@admin_required
def api_export_csv():
    items = load_submissions()
    titles = {t["id"]: t["title"] for t in TASKS}
    grades_map = {(g["student"], g["task_id"]): g for g in load_grades()}

    buf = io.StringIO()
    writer = csv.writer(buf, delimiter=";")
    writer.writerow(["Студент", "Группа", "Задача", "Язык",
                     "Пройдено", "Всего", "Время", "Оценка", "Автооценка",
                     "Комментарий", "Код"])
    for it in items:
        g = grades_map.get((it["student"], it["task_id"])) or {}
        writer.writerow([
            it.get("student", ""), it.get("group_name", ""),
            titles.get(it.get("task_id"), it.get("task_id", "")),
            it.get("language", ""), it.get("passed", 0), it.get("total", 0),
            it.get("timestamp", ""),
            g.get("grade", ""), g.get("auto_grade", ""),
            g.get("comment", ""),
            (it.get("code") or "").replace("\r", ""),
        ])
    data = ("\ufeff" + buf.getvalue()).encode("utf-8")
    return app.response_class(
        data, mimetype="text/csv; charset=utf-8",
        headers={"Content-Disposition": 'attachment; filename="submissions.csv"'},
    )


# ============================================================
# API — диагностика
# ============================================================
@app.route("/api/debug")
def api_debug():
    dn = detect_dotnet()
    return jsonify({
        "python": sys.executable,
        "dotnet": dn["exe"] if dn else None,
        "framework": dn["framework"] if dn else None,
        "tasks": len(TASKS),
        "submissions": len(load_submissions()),
        "attempts": len(load_attempts(limit=10**9)),
        "grades": len(load_grades()),
        "suspicious_ips": len(get_suspicious()),
        "queue_cs": cs_queue_info(),
        "queue_py": py_queue_info(),
        "limits": {
            "rate_ip": f"{RATE_IP_MAX}/{RATE_IP_WINDOW}s",
            "rate_student": f"{RATE_STUDENT_MAX}/{RATE_STUDENT_WINDOW}s",
            "max_code_size": MAX_CODE_SIZE,
            "max_request_size": MAX_REQUEST_SIZE,
        }
    })


# ============================================================
# Обработка ошибок
# ============================================================
@app.errorhandler(413)
def too_large(e):
    return jsonify({
        "error": f"⚠ Слишком большой запрос. Максимум {MAX_REQUEST_SIZE:,} байт.",
        "tests": []
    }), 413


@app.errorhandler(500)
def err500(e):
    traceback.print_exc()
    return jsonify({"error": str(e)}), 500


# ============================================================
# Инициализация
# ============================================================
def startup():
    init_db()
    prepare_csharp_template()


startup()


if __name__ == "__main__":
    import socket

    PORT = int(os.environ.get("PORT", 5050))
    HOST = os.environ.get("HOST", "0.0.0.0")

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
    except Exception:
        local_ip = "127.0.0.1"

    print(f"\n🐍 Python: {sys.executable}")
    dn = detect_dotnet()
    if dn:
        print(f"🔷 .NET:   {dn['exe']} ({dn['framework']})")
    print(f"\n🚀 Студенты: http://{local_ip}:{PORT}")
    print(f"👨‍🏫 Учитель:  http://{local_ip}:{PORT}/admin")
    print(f"🔐 Пароль:   {ADMIN_PASSWORD}")
    print(f"📚 Задач:    {len(TASKS)}")
    print(f"🛡  Защита:")
    print(f"     - IP-лимит:      {RATE_IP_MAX}/{RATE_IP_WINDOW}с (главный)")
    print(f"     - Имя-лимит:     {RATE_STUDENT_MAX}/{RATE_STUDENT_WINDOW}с (вспом.)")
    print(f"     - Мин. интервал: 2 сек")
    print(f"     - Макс. код:     {MAX_CODE_SIZE:,} байт")
    print(f"     - Макс. запрос:  {MAX_REQUEST_SIZE:,} байт")
    print(f"     - Очередь C#:    2 одновременно")
    print(f"     - Очередь Py:    5 одновременно\n")

    app.run(host=HOST, port=PORT, debug=False, threaded=True)