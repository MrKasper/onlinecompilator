# ============================================================
# Эвристический детектор ИИ в коде студента.
# Не даёт 100% гарантии, но подсвечивает типичные паттерны.
# ============================================================
import re
import json


# Обороты, характерные для сгенерированного кода
AI_MARKERS_RU = [
    "шаг 1", "шаг 2", "шаг 3",
    "итак,", "для начала", "затем",
    "объяснение", "результат:",
    "пример использования", "пример:",
    "обратите внимание",
    "данный код", "эта функция", "данная функция",
    "проверяем", "вычисляем", "получаем",
]

AI_MARKERS_EN = [
    "step 1", "step 2", "step 3",
    "args:", "returns:", "return:",
    "example:", "note:",
    "this function", "this program",
    "here we", "we can see",
]


def _is_comment(line: str, language: str) -> bool:
    s = line.strip()
    if not s:
        return False
    if language == "python":
        return s.startswith("#")
    if language == "csharp":
        return s.startswith("//") or s.startswith("///")
    return False


def _strip_comment_marker(line: str) -> str:
    s = line.strip()
    # убираем // /// #
    while s and s[0] in "#/":
        s = s[1:]
    return s.strip()


def analyze_code(code: str, language: str, task: dict = None) -> tuple[int, list[str]]:
    """Анализирует код и возвращает (score, [причины])."""
    if not isinstance(code, str) or not code.strip():
        return 0, []

    score = 0
    reasons = []

    lines = code.split("\n")
    non_empty = [l for l in lines if l.strip()]
    comments = [l for l in lines if _is_comment(l, language)]
    code_lines = [l for l in non_empty if not _is_comment(l, language)]

    # ---------- 1. Много комментариев ----------
    if non_empty:
        comment_ratio = len(comments) / len(non_empty)
        if comment_ratio >= 0.35 and len(comments) >= 3:
            score += 2
            reasons.append(
                f"Много комментариев: {len(comments)} из {len(non_empty)} строк "
                f"({comment_ratio:.0%})"
            )

    # ---------- 2. Комментарии как полные предложения ----------
    full_sentence = 0
    for cl in comments:
        text = _strip_comment_marker(cl)
        # Длинный текст + заканчивается на .!? — стиль ИИ
        if len(text) >= 20 and text.rstrip().endswith((".", "!", "?")):
            full_sentence += 1
    if full_sentence >= 2:
        score += 2
        reasons.append(
            f"Комментарии оформлены как полные предложения ({full_sentence} шт)"
        )

    # ---------- 3. Маркеры «ИИ-оборотов» ----------
    low = code.lower()
    found = []
    for m in AI_MARKERS_RU + AI_MARKERS_EN:
        if m in low:
            found.append(m)
    if found:
        bonus = min(3, len(found))
        score += bonus
        reasons.append(
            "Найдены характерные обороты: " + ", ".join(found[:3])
        )

    # ---------- 4. Эмодзи в коде ----------
    emoji_count = sum(1 for ch in code if ord(ch) > 0x1F000)
    if emoji_count > 0:
        score += 3
        reasons.append(f"Эмодзи в коде ({emoji_count} шт)")

    # ---------- 5. Python: type hints и docstrings ----------
    if language == "python":
        if re.search(r"def\s+\w+\s*\([^)]*:\s*\w+", code) and re.search(r"->\s*\w+", code):
            score += 2
            reasons.append("Type hints в Python (для простой задачи избыточно)")
        if '"""' in code or "'''" in code:
            score += 2
            reasons.append("Docstring присутствует")

    # ---------- 6. C#: XML-doc ----------
    if language == "csharp":
        if "///" in code and "<summary>" in code.lower():
            score += 3
            reasons.append("XML-doc комментарии C# (/// <summary>)")

    # ---------- 7. Длинные описательные имена ----------
    # Ищем идентификаторы длиной >= 10 символов
    names = re.findall(r"\b[a-z][a-zA-Z0-9_]{9,}\b", code)
    builtin = {
        "console", "writeline", "readline", "parse", "program",
        "using", "namespace", "class",
    }
    names = [n for n in names if n.lower() not in builtin]
    unique_names = set(names)
    if len(unique_names) >= 3:
        score += 1
        reasons.append(
            f"Длинные описательные имена: {', '.join(list(unique_names)[:3])}"
        )

    # ---------- 8. Пустые строки между блоками ----------
    empty = len([l for l in lines if not l.strip()])
    if code_lines and empty > len(code_lines) * 0.6:
        score += 1
        reasons.append("Код разбит пустыми строками (нетипично для студентов)")

    # ---------- 9. Слишком сложная структура для простой задачи ----------
    if task and task.get("difficulty") == "easy":
        # Проверяем наличие try/except или функций — для easy это избыточно
        if language == "python":
            if "try:" in code and "except" in code:
                score += 1
                reasons.append("try/except в простой задаче")
            if "def " in code and len(code_lines) < 15:
                score += 1
                reasons.append("Функция определена, но используется один раз")
        if language == "csharp":
            if "try" in code and "catch" in code:
                score += 1
                reasons.append("try/catch в простой задаче")

    return score, reasons


def classify(score: int) -> str:
    """Возвращает уровень: 'clean', 'suspicious', 'ai'."""
    if score >= 6:
        return "ai"
    if score >= 3:
        return "suspicious"
    return "clean"


def analyze_to_json(code: str, language: str, task: dict = None) -> tuple[int, str]:
    """Готово для сохранения в БД: (score, reasons_json)."""
    score, reasons = analyze_code(code, language, task)
    return score, json.dumps(reasons, ensure_ascii=False)