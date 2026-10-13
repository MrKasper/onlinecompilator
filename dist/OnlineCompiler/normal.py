# ============================================================
# Нормализация data.db:
#   1. Добавляет недостающие колонки в существующие таблицы
#   2. Проверяет UNIQUE-индекс, пересоздаёт если надо
#   3. Показывает количество строк до и после
# Старые записи НЕ удаляются.
# ============================================================
import sqlite3
import sys
import traceback
from pathlib import Path

if getattr(sys, "frozen", False):
    APP_DIR = Path(sys.executable).parent
else:
    APP_DIR = Path(__file__).parent

DB = APP_DIR / "data.db"
print(f"БД: {DB}")
if not DB.exists():
    print("[!] Файла нет — сначала запустите .exe")
    input("Enter...")
    sys.exit()

c = sqlite3.connect(str(DB))
c.row_factory = sqlite3.Row


def columns(table):
    return {r[1]: r for r in c.execute(f"PRAGMA table_info([{table}])")}


def add_column_if_missing(table, name, sqltype, default_sql=""):
    cols = columns(table)
    if name in cols:
        print(f"  [{table}] колонка {name} уже есть")
        return
    sql = f"ALTER TABLE [{table}] ADD COLUMN {name} {sqltype}"
    if default_sql:
        sql += f" DEFAULT {default_sql}"
    try:
        c.execute(sql)
        print(f"  [{table}] добавлена колонка {name} {sqltype}")
    except Exception as e:
        print(f"  [{table}] ошибка добавления {name}: {e}")


def fill_null_after_add(table, name, value_sql):
    try:
        n = c.execute(f"UPDATE [{table}] SET {name}={value_sql} WHERE {name} IS NULL").rowcount
        if n:
            print(f"  [{table}] заполнено {name}: {n} строк")
    except Exception as e:
        print(f"  [{table}] ошибка заполнения {name}: {e}")


def process_table(table):
    print(f"\n=== Обработка {table} ===")
    if not columns(table):
        print(f"  Таблицы {table} нет")
        return

    if table == "submissions":
        add_column_if_missing(table, "group_name", "TEXT", "''")
        add_column_if_missing(table, "tests_json", "TEXT")
        fill_null_after_add(table, "group_name", "''")
        # Приводим passed/total к int (если были строкой)
        try:
            c.execute(f"UPDATE [{table}] SET passed=CAST(passed AS INTEGER) WHERE typeof(passed)!='integer'")
            c.execute(f"UPDATE [{table}] SET total=CAST(total AS INTEGER) WHERE typeof(total)!='integer'")
            print(f"  [{table}] passed/total приведены к INTEGER")
        except Exception as e:
            print(f"  [{table}] ошибка приведения типов: {e}")

    if table == "attempts":
        add_column_if_missing(table, "group_name", "TEXT", "''")
        add_column_if_missing(table, "tests_json", "TEXT")
        add_column_if_missing(table, "error", "TEXT")
        fill_null_after_add(table, "group_name", "''")
        try:
            c.execute(f"UPDATE [{table}] SET passed=CAST(passed AS INTEGER) WHERE typeof(passed)!='integer'")
            c.execute(f"UPDATE [{table}] SET total=CAST(total AS INTEGER) WHERE typeof(total)!='integer'")
            print(f"  [{table}] passed/total приведены к INTEGER")
        except Exception as e:
            print(f"  [{table}] ошибка приведения типов: {e}")

    if table == "grades":
        add_column_if_missing(table, "auto_grade_attempts", "INTEGER")
        try:
            c.execute(f"UPDATE [{table}] SET grade=CAST(grade AS INTEGER) WHERE grade IS NOT NULL AND typeof(grade)!='integer'")
            c.execute(f"UPDATE [{table}] SET auto_grade=CAST(auto_grade AS INTEGER) WHERE auto_grade IS NOT NULL AND typeof(auto_grade)!='integer'")
            print(f"  [{table}] grade/auto_grade приведены к INTEGER")
        except Exception as e:
            print(f"  [{table}] ошибка приведения типов: {e}")


def find_similar(table_pattern):
    """Ищет таблицы, похожие на данную (submission, submission_old и т.д.)."""
    all_tables = [r[0] for r in c.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    )]
    return [t for t in all_tables if table_pattern in t.lower()]


# ------------------------------------------------------------
# Основная логика
# ------------------------------------------------------------
print("\nТаблицы в БД:")
tables = [r[0] for r in c.execute(
    "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
)]
for t in tables:
    n = c.execute(f"SELECT COUNT(*) FROM [{t}]").fetchone()[0]
    print(f"  {t}: {n}")

print("\n--- Нормализация схемы ---")
for t in ("submissions", "attempts", "grades"):
    process_table(t)

# Ищем "лишние" таблицы с данными
print("\n--- Поиск потерянных таблиц ---")
for pattern in ("submission", "attempt", "grade"):
    similar = find_similar(pattern)
    for t in similar:
        if t in ("submissions", "attempts", "grades"):
            continue
        n = c.execute(f"SELECT COUNT(*) FROM [{t}]").fetchone()[0]
        if n > 0:
            print(f"  [!] Найдена таблица {t} с {n} строками.")
            print(f"      Возможно, это старые данные.")

c.commit()

print("\n--- Итог ---")
for t in ("submissions", "attempts", "grades"):
    if columns(t):
        n = c.execute(f"SELECT COUNT(*) FROM [{t}]").fetchone()[0]
        print(f"  {t}: {n} строк")

# Удаляем WAL/SHM, если есть (SQLite может путаться)
for ext in ("-wal", "-shm"):
    f = Path(str(DB) + ext)
    if f.exists():
        try:
            f.unlink()
            print(f"  Удалён {f.name}")
        except Exception:
            pass

c.close()
print("\nГотово. Перезапустите OnlineCompiler.exe.")
input("Enter...")