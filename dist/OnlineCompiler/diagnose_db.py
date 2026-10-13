# ============================================================
# Диагностика data.db: показывает все таблицы, колонки и данные
# ============================================================
import sqlite3
import sys
from pathlib import Path

if getattr(sys, "frozen", False):
    APP_DIR = Path(sys.executable).parent
else:
    APP_DIR = Path(__file__).parent

DB = APP_DIR / "data.db"

print(f"БД: {DB}")
print(f"Существует: {DB.exists()}")
print()

if not DB.exists():
    print("Файл не найден — запустите OnlineCompiler.exe для создания.")
    input("Enter...")
    sys.exit()

c = sqlite3.connect(str(DB))
c.row_factory = sqlite3.Row

# Все таблицы
tables = [r[0] for r in c.execute(
    "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
)]
print("=== Таблицы ===")
for t in tables:
    n = c.execute(f"SELECT COUNT(*) FROM [{t}]").fetchone()[0]
    print(f"  {t}: {n} строк")
print()

# Схема каждой таблицы с именем submissions/submission/attempts
for t in tables:
    if "submission" in t.lower() or "attempt" in t.lower() or "grade" in t.lower():
        print(f"=== Схема таблицы {t} ===")
        for row in c.execute(f"PRAGMA table_info([{t}])"):
            # row: cid, name, type, notnull, dflt_value, pk
            print(f"  {row[1]:25s} {row[2]:10s} notnull={row[3]} default={row[4]}")
        print()

        # Первые 5 строк
        print(f"=== Первые 5 строк из {t} ===")
        for row in c.execute(f"SELECT * FROM [{t}] LIMIT 5"):
            d = dict(row)
            # Обрезаем длинные значения
            for k, v in d.items():
                if isinstance(v, str) and len(v) > 60:
                    d[k] = v[:60] + "..."
            print(f"  {d}")
        print()

        # Последние 3 строки по rowid
        print(f"=== Последние 3 строки из {t} (по rowid) ===")
        for row in c.execute(f"SELECT * FROM [{t}] ORDER BY rowid DESC LIMIT 3"):
            d = dict(row)
            for k, v in d.items():
                if isinstance(v, str) and len(v) > 60:
                    d[k] = v[:60] + "..."
            print(f"  {d}")
        print()

c.close()
input("Enter...")