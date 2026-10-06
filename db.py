# ============================================================
# Хранилище на SQLite: submissions / attempts / grades
# ============================================================
import json
import sqlite3
import threading
import time
from pathlib import Path

DB_FILE = Path(__file__).parent / "data.db"
_lock = threading.Lock()


def _conn():
    c = sqlite3.connect(str(DB_FILE), check_same_thread=False)
    c.row_factory = sqlite3.Row
    return c


def init_db():
    with _lock:
        c = _conn()
        c.executescript("""
            CREATE TABLE IF NOT EXISTS submissions (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                student     TEXT NOT NULL,
                group_name  TEXT DEFAULT '',
                task_id     TEXT NOT NULL,
                language    TEXT NOT NULL,
                code        TEXT NOT NULL,
                passed      INTEGER NOT NULL,
                total       INTEGER NOT NULL,
                timestamp   TEXT NOT NULL,
                tests_json  TEXT,
                UNIQUE(student, task_id, language)
            );
            CREATE TABLE IF NOT EXISTS attempts (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                student     TEXT NOT NULL,
                group_name  TEXT DEFAULT '',
                task_id     TEXT NOT NULL,
                language    TEXT NOT NULL,
                code        TEXT NOT NULL,
                passed      INTEGER NOT NULL,
                total       INTEGER NOT NULL,
                error       TEXT,
                timestamp   TEXT NOT NULL,
                tests_json  TEXT
            );
            CREATE TABLE IF NOT EXISTS grades (
                student     TEXT NOT NULL,
                task_id     TEXT NOT NULL,
                grade       INTEGER,
                auto_grade  INTEGER,
                comment     TEXT DEFAULT '',
                teacher     TEXT DEFAULT '',
                timestamp   TEXT NOT NULL,
                PRIMARY KEY (student, task_id)
            );
            CREATE INDEX IF NOT EXISTS idx_attempts_student
                ON attempts(student);
            CREATE INDEX IF NOT EXISTS idx_attempts_task
                ON attempts(task_id);
            CREATE INDEX IF NOT EXISTS idx_submissions_student
                ON submissions(student);
        """)
        c.commit()
        c.close()


def _row_to_dict(row):
    return {k: row[k] for k in row.keys()} if row else None


# ---------------- Лучшие решения ----------------
def load_submissions():
    with _lock:
        c = _conn()
        rows = c.execute(
            "SELECT * FROM submissions ORDER BY timestamp DESC"
        ).fetchall()
        c.close()
    items = []
    for r in rows:
        d = _row_to_dict(r)
        try:
            d["tests"] = json.loads(d.pop("tests_json") or "[]")
        except Exception:
            d["tests"] = []
        items.append(d)
    return items


def add_submission(student, group_name, task_id, language, code, passed, total, tests):
    with _lock:
        c = _conn()
        now = time.strftime("%Y-%m-%d %H:%M:%S")
        tj = json.dumps([{"name": t["name"], "passed": t["passed"]} for t in tests],
                        ensure_ascii=False)
        # Проверяем, есть ли уже запись
        old = c.execute(
            "SELECT passed FROM submissions WHERE student=? AND task_id=? AND language=?",
            (student, task_id, language)
        ).fetchone()
        if old and old["passed"] > passed:
            # Не перезаписываем лучший результат
            c.close()
            return
        c.execute("""
            INSERT INTO submissions (student, group_name, task_id, language,
                code, passed, total, timestamp, tests_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(student, task_id, language) DO UPDATE SET
                code=excluded.code,
                passed=excluded.passed,
                total=excluded.total,
                timestamp=excluded.timestamp,
                tests_json=excluded.tests_json,
                group_name=excluded.group_name
        """, (student, group_name, task_id, language, code, passed, total, now, tj))
        c.commit()
        c.close()


def delete_submission(student, task_id, language):
    with _lock:
        c = _conn()
        c.execute("DELETE FROM submissions WHERE student=? AND task_id=? AND language=?",
                  (student, task_id, language))
        c.commit()
        c.close()


# ---------------- История попыток ----------------
def load_attempts(student=None, task_id=None, limit=200):
    sql = "SELECT * FROM attempts WHERE 1=1"
    params = []
    if student:
        sql += " AND student=?"
        params.append(student)
    if task_id:
        sql += " AND task_id=?"
        params.append(task_id)
    sql += " ORDER BY timestamp DESC LIMIT ?"
    params.append(limit)

    with _lock:
        c = _conn()
        rows = c.execute(sql, params).fetchall()
        c.close()
    items = []
    for r in rows:
        d = _row_to_dict(r)
        try:
            d["tests"] = json.loads(d.pop("tests_json") or "[]")
        except Exception:
            d["tests"] = []
        items.append(d)
    return items


def add_attempt(student, group_name, task_id, language, code, passed, total, tests, error=None):
    with _lock:
        c = _conn()
        now = time.strftime("%Y-%m-%d %H:%M:%S")
        tj = json.dumps([{"name": t["name"], "passed": t["passed"]} for t in tests],
                        ensure_ascii=False)
        c.execute("""
            INSERT INTO attempts (student, group_name, task_id, language,
                code, passed, total, error, timestamp, tests_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (student, group_name, task_id, language, code,
              passed, total, error, now, tj))
        c.commit()
        # Обрезаем до 10000 последних
        c.execute("""
            DELETE FROM attempts WHERE id NOT IN (
                SELECT id FROM attempts ORDER BY id DESC LIMIT 10000
            )
        """)
        c.commit()
        c.close()


# ---------------- Оценки ----------------
def load_grades():
    with _lock:
        c = _conn()
        rows = c.execute("SELECT * FROM grades").fetchall()
        c.close()
    return [_row_to_dict(r) for r in rows]


def save_grade(student, task_id, grade, comment="", teacher="", auto_grade=None):
    with _lock:
        c = _conn()
        now = time.strftime("%Y-%m-%d %H:%M:%S")
        c.execute("""
            INSERT INTO grades (student, task_id, grade, auto_grade, comment, teacher, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(student, task_id) DO UPDATE SET
                grade=excluded.grade,
                auto_grade=COALESCE(excluded.auto_grade, grades.auto_grade),
                comment=excluded.comment,
                teacher=excluded.teacher,
                timestamp=excluded.timestamp
        """, (student, task_id, grade, auto_grade, comment, teacher, now))
        c.commit()
        c.close()


def delete_grade(student, task_id):
    with _lock:
        c = _conn()
        c.execute("DELETE FROM grades WHERE student=? AND task_id=?", (student, task_id))
        c.commit()
        c.close()


# ---------------- Автооценка ----------------
def auto_grade(passed: int, total: int):
    """Формула автоматической оценки по проценту пройденных тестов."""
    if total <= 0:
        return None
    pct = passed / total * 100
    if pct >= 100: return 5
    if pct >= 80:  return 4
    if pct >= 60:  return 3
    if pct > 0:    return 2
    return None


# ---------------- Статистика ----------------
def get_stats():
    with _lock:
        c = _conn()
        subs = c.execute("SELECT * FROM submissions").fetchall()
        atts = c.execute("SELECT student, COUNT(*) AS cnt FROM attempts GROUP BY student").fetchall()
        grds = c.execute("SELECT * FROM grades").fetchall()
        c.close()

    stats = {}

    def ensure(name):
        if name not in stats:
            stats[name] = {
                "student": name,
                "solved": 0,
                "attempts": 0,
                "by_lang": {"python": 0, "csharp": 0},
                "grades": [],
            }
        return stats[name]

    for s in subs:
        st = ensure(s["student"])
        if s["passed"] == s["total"]:
            st["solved"] += 1
            st["by_lang"][s["language"]] = st["by_lang"].get(s["language"], 0) + 1

    for a in atts:
        ensure(a["student"])["attempts"] = a["cnt"]

    for g in grds:
        st = ensure(g["student"])
        val = g["grade"] if g["grade"] is not None else g["auto_grade"]
        if isinstance(val, (int, float)):
            st["grades"].append(val)

    for name, st in stats.items():
        st["avg_grade"] = round(sum(st["grades"]) / len(st["grades"]), 2) if st["grades"] else None
        st.pop("grades", None)

    return stats


# ---------------- Резервная копия ----------------
def backup_db():
    import shutil
    if not DB_FILE.exists():
        return None
    bdir = Path(__file__).parent / "backups"
    bdir.mkdir(exist_ok=True)
    stamp = time.strftime("%Y-%m-%d_%H-%M-%S")
    dst = bdir / f"data_{stamp}.db"
    shutil.copy2(DB_FILE, dst)
    # Оставляем только 30 последних
    files = sorted(bdir.glob("data_*.db"))
    for old in files[:-30]:
        old.unlink()
    return str(dst)