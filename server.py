# ============================================================
# HTTP-сервер онлайн-компилятора
# ============================================================
import csv
import http.server
import io
import json
import sys
import traceback
from pathlib import Path
from urllib.parse import urlparse, parse_qs, unquote

from tasks import TASKS
from storage import (
    load_submissions, add_submission, add_attempt,
    load_attempts, load_grades, save_grade, get_stats,
)
from executor import run_code, detect_dotnet, find_python


PORT = 8000
HERE = Path(__file__).parent


class Handler(http.server.BaseHTTPRequestHandler):

    # ---------- GET ----------
    def do_GET(self):
        try:
            parsed = urlparse(self.path)
            path = parsed.path
            query = parse_qs(parsed.query)

            if path in ("/", "/index.html"):
                self._file(HERE / "index.html", "text/html; charset=utf-8")
                return

            if path == "/admin":
                self._file(HERE / "admin.html", "text/html; charset=utf-8")
                return

            if path == "/api/tasks":
                self._json([
                    {
                        "id": t["id"],
                        "title": t["title"],
                        "difficulty": t.get("difficulty", "easy"),
                        "tags": t.get("tags", []),
                    }
                    for t in TASKS
                ])
                return

            if path.startswith("/api/tasks/"):
                task_id = path.rsplit("/", 1)[-1]
                task = next((t for t in TASKS if t["id"] == task_id), None)
                if task:
                    self._json(task)
                else:
                    self._err(404, "Задача не найдена")
                return

            if path == "/api/students":
                # Собираем имена из сохранённых решений + все из попыток
                names = set()
                for s in load_submissions():
                    if s.get("student"):
                        names.add(s["student"])
                for a in load_attempts():
                    if a.get("student"):
                        names.add(a["student"])
                self._json(sorted(names))
                return

            if path == "/api/submissions":
                self._json(load_submissions())
                return

            if path == "/api/attempts":
                # Правильное декодирование ?student=Иванов+Иван
                student = query.get("student", [None])[0]
                if student:
                    student = unquote(student)
                task_id = query.get("task_id", [None])[0]
                if task_id:
                    task_id = unquote(task_id)
                self._json(load_attempts(student=student, task_id=task_id, limit=200))
                return

            if path == "/api/grades":
                self._json(load_grades())
                return

            if path == "/api/stats":
                self._json(get_stats())
                return

            if path == "/api/export.csv":
                self._csv(load_submissions())
                return

            if path == "/api/debug":
                dn = detect_dotnet()
                self._json({
                    "python": sys.executable,
                    "dotnet": dn["exe"] if dn else None,
                    "framework": dn["framework"] if dn else None,
                    "tasks": len(TASKS),
                    "submissions": len(load_submissions()),
                    "attempts": len(load_attempts()),
                    "grades": len(load_grades()),
                })
                return

            self._err(404, "Not found")

        except Exception as e:
            print("[GET]", e)
            traceback.print_exc()
            self._err(500, str(e))

    # ---------- POST ----------
    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length", 0) or 0)
            raw = self.rfile.read(length).decode("utf-8") if length else "{}"
            data = json.loads(raw)

            # --- Запуск кода ---
            if self.path == "/api/run":
                task_id = data.get("task_id", "")
                code = data.get("code", "")
                language = data.get("language", "python")
                student = (data.get("student") or "Аноним").strip()

                task = next((t for t in TASKS if t["id"] == task_id), None)
                if not task:
                    self._json({"error": f"Задача '{task_id}' не найдена", "tests": []})
                    return

                print(f"[RUN]  {student!r} · task={task_id!r} lang={language!r}")
                result = run_code(code, task, language)

                # Всегда пишем в историю (и неудачные тоже)
                add_attempt(
                    student=student,
                    task_id=task_id,
                    language=language,
                    code=code,
                    passed=result.get("passed", 0),
                    total=result.get("total", 0),
                    tests=result.get("tests", []),
                    error=result.get("error"),
                )

                # Если полностью решено — обновим «лучшее решение»
                if (not result.get("error") and result.get("total", 0) > 0
                        and result.get("passed") == result.get("total")):
                    add_submission(
                        student=student,
                        task_id=task_id,
                        language=language,
                        code=code,
                        passed=result["passed"],
                        total=result["total"],
                        tests=result["tests"],
                    )

                self._json(result)
                return

            # --- Оценка от учителя ---
            if self.path == "/api/grade":
                student = (data.get("student") or "").strip()
                task_id = data.get("task_id", "")
                grade = data.get("grade")
                comment = data.get("comment", "")
                teacher = data.get("teacher", "")
                if not student or not task_id:
                    self._json({"error": "Не указан студент или задача"})
                    return
                try:
                    grade = int(grade) if grade not in (None, "") else None
                except (ValueError, TypeError):
                    grade = None
                entry = save_grade(student, task_id, grade, comment, teacher)
                print(f"[GRADE] {student!r} · {task_id!r} · {grade}")
                self._json({"ok": True, "entry": entry})
                return

            self._err(404, "Not found")

        except Exception as e:
            print("[POST]", e)
            traceback.print_exc()
            self._json({"error": f"Внутренняя ошибка: {e}", "tests": []})

    # ---------- Отправка ответов ----------
    def _json(self, obj):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _file(self, path, content_type):
        if not path.exists():
            self._err(404, "Файл не найден")
            return
        data = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _err(self, code, msg):
        body = json.dumps({"error": msg}, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _csv(self, items):
        buf = io.StringIO()
        writer = csv.writer(buf, delimiter=";")
        writer.writerow(["Студент", "Задача", "Язык", "Пройдено", "Всего",
                         "Время", "Оценка", "Комментарий", "Код"])
        titles = {t["id"]: t["title"] for t in TASKS}
        grades_map = {(g["student"], g["task_id"]): g for g in load_grades()}

        for it in items:
            g = grades_map.get((it.get("student"), it.get("task_id"))) or {}
            writer.writerow([
                it.get("student", ""),
                titles.get(it.get("task_id"), it.get("task_id", "")),
                it.get("language", ""),
                it.get("passed", 0),
                it.get("total", 0),
                it.get("timestamp", ""),
                g.get("grade", ""),
                g.get("comment", ""),
                (it.get("code") or "").replace("\r", ""),
            ])

        data = ("\ufeff" + buf.getvalue()).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/csv; charset=utf-8")
        self.send_header("Content-Disposition",
                         'attachment; filename="submissions.csv"')
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, *args):
        pass


if __name__ == "__main__":
    print(f"\n🐍 Python: {sys.executable}")
    dn = detect_dotnet()
    if dn:
        print(f"🔷 .NET:   {dn['exe']} ({dn['framework']})")
    else:
        print("🔷 .NET:   НЕ НАЙДЕН — C#-задачи не будут работать")
    print(f"\n🚀 Онлайн компилятор: http://localhost:{PORT}")
    print(f"👨‍🏫 Панель учителя:    http://localhost:{PORT}/admin")
    print(f"📚 Задач:  {len(TASKS)}")
    print(f"💾 Попыток сохранено: {len(load_attempts())}")
    print(f"   Остановить: Ctrl+C\n")

    with http.server.ThreadingHTTPServer(("", PORT), Handler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nОстановлено")