# ============================================================
# Хранилище: лучшие решения, история попыток, оценки
# ============================================================
import json
import threading
import time
from pathlib import Path

BASE = Path(__file__).parent
SUBMISSIONS_FILE = BASE / "submissions.json"   # лучшие решения
ATTEMPTS_FILE    = BASE / "attempts.json"      # все попытки (история)
GRADES_FILE      = BASE / "grades.json"        # оценки от учителя

_lock = threading.Lock()


def _load(path):
    if not path.exists():
        return []
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return []


def _save(path, items):
    path.write_text(
        json.dumps(items, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


# ---------------- Лучшие решения ----------------
def load_submissions():
    return _load(SUBMISSIONS_FILE)


def add_submission(student, task_id, language, code, passed, total, tests):
    with _lock:
        items = _load(SUBMISSIONS_FILE)
        entry = {
            "student": (student or "").strip()[:80],
            "task_id": task_id,
            "language": language,
            "code": code,
            "passed": passed,
            "total": total,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "tests": [{"name": t["name"], "passed": t["passed"]} for t in tests],
        }
        key = (entry["student"], entry["task_id"], entry["language"])
        replaced = False
        for i, it in enumerate(items):
            ik = (it.get("student"), it.get("task_id"), it.get("language"))
            if ik == key:
                if entry["passed"] >= it.get("passed", 0):
                    items[i] = entry
                replaced = True
                break
        if not replaced:
            items.append(entry)
        _save(SUBMISSIONS_FILE, items)
        return entry


# ---------------- История попыток ----------------
def load_attempts(student=None, task_id=None, limit=None):
    items = _load(ATTEMPTS_FILE)
    if student:
        items = [it for it in items if it.get("student") == student]
    if task_id:
        items = [it for it in items if it.get("task_id") == task_id]
    items.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    if limit:
        items = items[:limit]
    return items


def add_attempt(student, task_id, language, code, passed, total, tests, error=None):
    """Сохраняет КАЖДУЮ попытку — и удачную, и нет."""
    with _lock:
        items = _load(ATTEMPTS_FILE)
        items.append({
            "student": (student or "Аноним").strip()[:80],
            "task_id": task_id,
            "language": language,
            "code": code,
            "passed": passed,
            "total": total,
            "error": error,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "tests": [{"name": t["name"], "passed": t["passed"]} for t in tests],
        })
        if len(items) > 5000:
            items = items[-5000:]
        _save(ATTEMPTS_FILE, items)


# ---------------- Оценки ----------------
def load_grades():
    return _load(GRADES_FILE)


def get_grade(student, task_id):
    for g in load_grades():
        if g.get("student") == student and g.get("task_id") == task_id:
            return g
    return None


def save_grade(student, task_id, grade, comment="", teacher=""):
    with _lock:
        items = _load(GRADES_FILE)
        entry = {
            "student": student,
            "task_id": task_id,
            "grade": grade,
            "comment": comment,
            "teacher": teacher,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        }
        key = (student, task_id)
        for i, it in enumerate(items):
            if (it.get("student"), it.get("task_id")) == key:
                items[i] = entry
                _save(GRADES_FILE, items)
                return entry
        items.append(entry)
        _save(GRADES_FILE, items)
        return entry


# ---------------- Статистика ----------------
def get_stats():
    """Агрегированная статистика по студентам."""
    subs = load_submissions()
    attempts = load_attempts()
    grades = load_grades()

    stats = {}

    def ensure(name):
        if name not in stats:
            stats[name] = {
                "student": name,
                "solved": 0,
                "attempts": 0,
                "total_passed": 0,
                "by_lang": {"python": 0, "csharp": 0},
                "avg_grade": None,
                "grades": [],
            }
        return stats[name]

    for s in subs:
        st = ensure(s.get("student", ""))
        if s.get("passed") == s.get("total"):
            st["solved"] += 1
            lang = s.get("language", "python")
            st["by_lang"][lang] = st["by_lang"].get(lang, 0) + 1
        st["total_passed"] += s.get("passed", 0)

    for a in attempts:
        st = ensure(a.get("student", ""))
        st["attempts"] += 1

    for g in grades:
        st = ensure(g.get("student", ""))
        if isinstance(g.get("grade"), (int, float)):
            st["grades"].append(g["grade"])

    for name, st in stats.items():
        if st["grades"]:
            st["avg_grade"] = round(sum(st["grades"]) / len(st["grades"]), 2)
        del st["grades"]

    return stats