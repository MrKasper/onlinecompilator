# ============================================================
# Flask-приложение: онлайн-компилятор
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
    session, redirect, render_template_string, abort,
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


HERE = Path(__file__).parent
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "Kexibqltym15w")

app = Flask(__name__, static_folder=None)
app.secret_key = os.environ.get("SECRET_KEY", secrets.token_hex(16))


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
    # не отдаём студенту solution
    public = {k: v for k, v in task.items() if k != "solution"}
    return jsonify(public)


@app.route("/api/tasks/<task_id>/solution")
def api_task_solution(task_id):
    """Разбор решения — только для авторизованных или по параметру force для студента после успеха."""
    task = next((t for t in TASKS if t["id"] == task_id), None)
    if not task:
        return jsonify({"error": "Задача не найдена"}), 404
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
# API — запуск
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

    task = next((t for t in TASKS if t["id"] == task_id), None)
    if not task:
        return jsonify({"error": f"Задача '{task_id}' не найдена", "tests": []})

    print(f"[RUN]  {student!r} ({group_name or '—'}) · {task_id!r} · {language!r}")
    result = run_code(code, task, language, custom_tests=custom_tests)

    # Всегда пишем в историю
    add_attempt(
        student=student, group_name=group_name,
        task_id=task_id, language=language, code=code,
        passed=result.get("passed", 0), total=result.get("total", 0),
        tests=result.get("tests", []), error=result.get("error"),
    )

    # Полное решение → сохраняем лучший + автооценка
    if (not result.get("error") and result.get("total", 0) > 0
            and result.get("passed") == result.get("total")):
        add_submission(
            student=student, group_name=group_name,
            task_id=task_id, language=language, code=code,
            passed=result["passed"], total=result["total"],
            tests=result["tests"],
        )
        # Автооценка (если учитель ещё не поставил вручную)
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
    """Для студента — его собственные попытки без пароля."""
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
    })


# ============================================================
# Ошибки
# ============================================================
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
    print(f"\n🐍 Python: {sys.executable}")
    dn = detect_dotnet()
    if dn:
        print(f"🔷 .NET:   {dn['exe']} ({dn['framework']})")
    print(f"\n🚀 Сервер:  http://localhost:8000")
    print(f"👨‍🏫 Админка: http://localhost:8000/admin")
    print(f"🔐 Пароль:  {ADMIN_PASSWORD}")
    print(f"📚 Задач:   {len(TASKS)}\n")
    app.run(host="0.0.0.0", port=8000, debug=False)