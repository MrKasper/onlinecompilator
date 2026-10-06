# ============================================================
# Хранилище на SQLite: submissions / attempts / grades
# Автооценка учитывает и процент тестов, и количество попыток
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

        # ---- Миграция: auto_grade_attempts в существующие БД ----
        try:
            cols = [r[1] for r in c.execute("PRAGMA table_info(grades)").fetchall()]
            if "auto_grade_attempts" not in cols:
                c.execute("ALTER TABLE grades ADD COLUMN auto_grade_attempts INTEGER")
                print("[db] Добавлено поле auto_grade_attempts", flush=True)
        except Exception as e:
            print(f"[db] Миграция auto_grade_attempts: {e}", flush=True)

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
        old = c.execute(
            "SELECT passed FROM submissions WHERE student=? AND task_id=? AND language=?",
            (student, task_id, language)
        ).fetchone()
        if old and old["passed"] > passed:
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


def count_attempts(student, task_id):
    """Сколько попыток было у студента по этой задаче (по всем языкам)."""
    with _lock:
        c = _conn()
        row = c.execute(
            "SELECT COUNT(*) AS cnt FROM attempts WHERE student=? AND task_id=?",
            (student, task_id)
        ).fetchone()
        c.close()
    return row["cnt"] if row else 0


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


def save_grade(student, task_id, grade, comment="", teacher="",
               auto_grade=None, auto_grade_attempts=None):
    with _lock:
        c = _conn()
        now = time.strftime("%Y-%m-%d %H:%M:%S")
        c.execute("""
            INSERT INTO grades (student, task_id, grade, auto_grade,
                                auto_grade_attempts, comment, teacher, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(student, task_id) DO UPDATE SET
                grade=excluded.grade,
                auto_grade=COALESCE(excluded.auto_grade, grades.auto_grade),
                auto_grade_attempts=COALESCE(excluded.auto_grade_attempts,
                                             grades.auto_grade_attempts),
                comment=excluded.comment,
                teacher=excluded.teacher,
                timestamp=excluded.timestamp
        """, (student, task_id, grade, auto_grade, auto_grade_attempts,
              comment, teacher, now))
        c.commit()
        c.close()


def delete_grade(student, task_id):
    with _lock:
        c = _conn()
        c.execute("DELETE FROM grades WHERE student=? AND task_id=?", (student, task_id))
        c.commit()
        c.close()


# ---------------- Автооценка ----------------
def auto_grade(passed: int, total: int, attempts: int = 1):
    """Формула автоматической оценки.

    Учитывает:
      1) Процент пройденных тестов
      2) Количество попыток (чем больше — тем ниже)

    Итог = минимум из двух.

    Пороги:
      По тестам:   100% → 5, ≥80% → 4, ≥60% → 3, >0% → 2
      По попыткам: 1-2 → 5, 3-5 → 4, 6-10 → 3, 11+ → 2
    """
    if total <= 0:
        return None

    pct = passed / total * 100
    if pct >= 100:
        g_pct = 5
    elif pct >= 80:
        g_pct = 4
    elif pct >= 60:
        g_pct = 3
    elif pct > 0:
        g_pct = 2
    else:
        return None

    if attempts <= 2:
        g_att = 5
    elif attempts <= 5:
        g_att = 4
    elif attempts <= 10:
        g_att = 3
    else:
        g_att = 2

    return min(g_pct, g_att)


# ---------------- Статистика ----------------
def get_stats():
    with _lock:
        c = _conn()
        subs = c.execute("SELECT * FROM submissions").fetchall()
        atts = c.execute(
            "SELECT student, COUNT(*) AS cnt FROM attempts GROUP BY student"
        ).fetchall()
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
    files = sorted(bdir.glob("data_*.db"))
    for old in files[:-30]:
        old.unlink()
    return str(dst)