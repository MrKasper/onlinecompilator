# ============================================================
# Запуск и проверка решений (Python + C#) с кэшем сборки
# ============================================================
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


_dotnet_cache = None
_HERE = Path(__file__).parent
_CS_CACHE = _HERE / "cs_cache"
_CS_TEMPLATE = _CS_CACHE / "template"


# ============================================================
# Перевод ошибок
# ============================================================
ERROR_HINTS = [
    # ---------- Python ----------
    ("SyntaxError",         "💡 Синтаксическая ошибка. Проверьте скобки, кавычки и двоеточия."),
    ("IndentationError",    "💡 Ошибка отступов. В Python отступы важны."),
    ("TabError",            "💡 Смешаны табы и пробелы. Используйте 4 пробела."),
    ("NameError",           "💡 Переменная не определена. Проверьте написание имён."),
    ("TypeError",           "💡 Несовместимые типы. Нельзя сложить строку и число."),
    ("ValueError",          "💡 Неверное значение. Возможно, input() вернул не число."),
    ("IndexError",          "💡 Выход за границы списка или строки."),
    ("KeyError",            "💡 Ключ не найден в словаре."),
    ("ZeroDivisionError",   "💡 Деление на ноль."),
    ("EOFError",            "💡 Не хватило данных на входе — забыли input()?"),
    ("RecursionError",      "💡 Слишком глубокая рекурсия — нет базового случая?"),
    ("ModuleNotFoundError", "💡 Модуль не найден. Проверьте import."),
    ("AttributeError",      "💡 У объекта нет такого атрибута."),
    # ---------- C# ----------
    ("CS1002",  "💡 C#: пропущена точка с запятой ;"),
    ("CS1513",  "💡 C#: пропущена закрывающая скобка }"),
    ("CS1001",  "💡 C#: ожидался идентификатор."),
    ("CS0103",  "💡 C#: имя не существует — опечатка?"),
    ("CS0029",  "💡 C#: несовместимые типы."),
    ("CS0266",  "💡 C#: нужно явное приведение (int) или (double)."),
    ("CS0165",  "💡 C#: используется неинициализированная переменная."),
    ("NETSDK1045", "💡 C#: установленная версия .NET SDK не поддерживает target framework. "
                   "Проверьте `dotnet --list-sdks`."),
    ("System.FormatException", "💡 C#: не удалось разобрать число."),
    ("System.NullReferenceException", "💡 C#: обращение к null."),
    ("System.IndexOutOfRangeException", "💡 C#: выход за границы массива."),
    ("System.DivideByZeroException", "💡 C#: деление на ноль."),
]


def humanize_error(stderr: str, language: str = "python") -> str:
    if not stderr:
        return stderr
    hints = []
    for key, hint in ERROR_HINTS:
        if key in stderr and hint not in hints:
            hints.append(hint)
    return stderr + ("\n\n" + "\n".join(hints) if hints else "")


# ============================================================
# Python / .NET detection
# ============================================================
def find_python() -> str:
    if sys.executable and Path(sys.executable).exists():
        return sys.executable
    for name in ("python3", "python", "py"):
        p = shutil.which(name)
        if p:
            return p
    raise RuntimeError("Python не найден в PATH")


def detect_dotnet():
    """Определяет путь к dotnet и наиболее совместимый target framework.

    Берём МИНИМАЛЬНУЮ мажорную версию SDK — это гарантирует,
    что проект соберётся и запустится на любой установленной версии рантайма.
    """
    global _dotnet_cache
    if _dotnet_cache is not None:
        return _dotnet_cache

    exe = shutil.which("dotnet") or shutil.which("dotnet.exe")
    if not exe:
        _dotnet_cache = False
        return None

    framework = "net8.0"
    versions = []
    try:
        r = subprocess.run(
            [exe, "--list-sdks"],
            capture_output=True, text=True, timeout=15,
            encoding="utf-8", errors="replace",
        )
        for line in (r.stdout or "").splitlines():
            parts = line.split()
            if parts and parts[0]:
                try:
                    major = int(parts[0].split(".")[0])
                    versions.append(major)
                except (ValueError, IndexError):
                    pass

        if versions:
            versions = sorted(set(versions))
            major = min(versions)  # ← минимальная, а не максимальная
            if major >= 9:
                framework = f"net{major}.0"
            elif major == 8:
                framework = "net8.0"
            elif major == 7:
                framework = "net7.0"
            elif major == 6:
                framework = "net6.0"
            else:
                framework = "net8.0"
            print(f"[✓] .NET SDK versions: {versions}, target = {framework}")
        else:
            print("[!] .NET найден, но SDK не установлен (только runtime)")
    except Exception as e:
        print(f"[!] Ошибка определения .NET: {e}")

    _dotnet_cache = {"exe": exe, "framework": framework}
    return _dotnet_cache


def prepare_csharp_template():
    """Один раз собирает шаблон — при следующих запусках переиспользует obj/."""
    info = detect_dotnet()
    if not info:
        return False

    # Если шаблон есть, но target framework не совпадает — пересобираем
    csproj = _CS_TEMPLATE / "App.csproj"
    if csproj.exists():
        try:
            content = csproj.read_text(encoding="utf-8")
            if f"<TargetFramework>{info['framework']}</TargetFramework>" not in content:
                print(f"[!] Шаблон C# устарел — пересобираю под {info['framework']}")
                shutil.rmtree(_CS_TEMPLATE, ignore_errors=True)
        except Exception:
            pass

    _CS_CACHE.mkdir(exist_ok=True)
    _CS_TEMPLATE.mkdir(exist_ok=True)

    if not csproj.exists():
        csproj.write_text(
            '<Project Sdk="Microsoft.NET.Sdk">\n'
            '  <PropertyGroup>\n'
            '    <OutputType>Exe</OutputType>\n'
            f'    <TargetFramework>{info["framework"]}</TargetFramework>\n'
            '    <Nullable>disable</Nullable>\n'
            '    <ImplicitUsings>enable</ImplicitUsings>\n'
            '    <AssemblyName>App</AssemblyName>\n'
            '    <InvariantGlobalization>true</InvariantGlobalization>\n'
            '  </PropertyGroup>\n'
            '</Project>\n',
            encoding="utf-8",
        )
    (_CS_TEMPLATE / "Program.cs").write_text(
        "class Program { static void Main() { } }", encoding="utf-8"
    )

    env = os.environ.copy()
    env["NUGET_PACKAGES"] = str(_CS_CACHE / "nuget")
    env["DOTNET_CLI_TELEMETRY_OPTOUT"] = "1"
    env["DOTNET_NOLOGO"] = "1"
    env["DOTNET_SKIP_FIRST_TIME_EXPERIENCE"] = "1"

    try:
        result = subprocess.run(
            [info["exe"], "build", "-c", "Release", "--nologo"],
            cwd=str(_CS_TEMPLATE), capture_output=True, text=True,
            timeout=180, encoding="utf-8", errors="replace", env=env,
        )
        if result.returncode != 0:
            print(f"[!] Не удалось подготовить шаблон C#:")
            print((result.stdout or "") + (result.stderr or ""))
            return False
        print(f"[✓] Шаблон C# подготовлен ({info['framework']})")
        return True
    except Exception as e:
        print(f"[!] Ошибка подготовки шаблона C#: {e}")
        return False


# ============================================================
# Нормализация вывода
# ============================================================
def _normalize(s):
    if s is None:
        return ""
    s = str(s).replace("\ufeff", "").replace("\ufffd", "")
    lines = [l.rstrip() for l in s.split("\n")]
    while lines and not lines[-1]: lines.pop()
    while lines and not lines[0]:  lines.pop(0)
    return "\n".join(lines)


# ============================================================
# Диспетчер
# ============================================================
def run_code(code, task, language, custom_tests=None):
    if not isinstance(code, str):
        code = "" if code is None else str(code)

    test_cases = list(task.get("test_cases") or [])
    if custom_tests:
        for i, ct in enumerate(custom_tests, 1):
            if ct.get("input") is None and ct.get("expected") is None:
                continue
            test_cases.append({
                "input": ct.get("input", ""),
                "expected": ct.get("expected", ""),
                "_custom": True,
                "_label": f"Свой тест {i}",
            })

    if not test_cases:
        return {"error": "Нет тестов", "tests": []}
    if language not in ("python", "csharp"):
        return {"error": f"Язык '{language}' не поддерживается", "tests": []}

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        if language == "python":
            results, fatal = _run_python(code, tmp_path, test_cases)
        else:
            results, fatal = _run_csharp(code, tmp_path, test_cases)

    if fatal:
        return fatal

    return {
        "tests": results,
        "passed": sum(1 for r in results if r["passed"]),
        "total": len(results),
    }


# ============================================================
# Python
# ============================================================
def _run_python(code, tmp_path, test_cases):
    try:
        python_exe = find_python()
    except Exception as e:
        return None, {"error": str(e)}

    (tmp_path / "main.py").write_text(code, encoding="utf-8")

    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONUTF8"] = "1"

    results = []
    for i, tc in enumerate(test_cases, 1):
        name = tc.get("_label") or f"Тест {i}"
        stdin = tc.get("input", "")
        expected = tc.get("expected", "")
        try:
            r = subprocess.run(
                [python_exe, "-X", "utf8", "main.py"],
                cwd=str(tmp_path), input=stdin, capture_output=True,
                text=True, timeout=10, encoding="utf-8",
                errors="replace", env=env,
            )
            if r.returncode != 0:
                results.append({
                    "name": name, "passed": False,
                    "message": "Ошибка:\n" + humanize_error(r.stderr or "", "python")[:600],
                })
                continue
            passed = _normalize(r.stdout) == _normalize(expected)
            msg = "OK" if passed else (
                f"Вход: {stdin!r}\nОжидалось: {expected!r}\nПолучено:  {(r.stdout or '').strip()!r}"
            )
            results.append({"name": name, "passed": passed, "message": msg})
        except subprocess.TimeoutExpired:
            results.append({"name": name, "passed": False,
                            "message": "⏱ Превышено время (10 сек)."})
        except Exception as e:
            results.append({"name": name, "passed": False, "message": f"Ошибка: {e}"})
    return results, None


# ============================================================
# C# с кэшем
# ============================================================
def _run_csharp(code, tmp_path, test_cases):
    info = detect_dotnet()
    if not info:
        return None, {"error": "Не найден .NET SDK. Установите .NET 8: "
                               "sudo apt install dotnet-sdk-8.0"}

    # Копируем шаблон (если есть) — тогда obj/ уже готов
    if _CS_TEMPLATE.exists():
        try:
            shutil.copytree(_CS_TEMPLATE, tmp_path, dirs_exist_ok=True)
        except Exception:
            pass

    # Если шаблона нет — создаём csproj вручную
    csproj_path = tmp_path / "App.csproj"
    if not csproj_path.exists():
        csproj_path.write_text(
            '<Project Sdk="Microsoft.NET.Sdk">\n'
            '  <PropertyGroup>\n'
            '    <OutputType>Exe</OutputType>\n'
            f'    <TargetFramework>{info["framework"]}</TargetFramework>\n'
            '    <Nullable>disable</Nullable>\n'
            '    <ImplicitUsings>enable</ImplicitUsings>\n'
            '  </PropertyGroup>\n'
            '</Project>\n',
            encoding="utf-8",
        )

    (tmp_path / "Program.cs").write_text(code, encoding="utf-8")

    env = os.environ.copy()
    env["NUGET_PACKAGES"] = str(_CS_CACHE / "nuget")
    env["DOTNET_CLI_TELEMETRY_OPTOUT"] = "1"
    env["DOTNET_NOLOGO"] = "1"
    env["DOTNET_SKIP_FIRST_TIME_EXPERIENCE"] = "1"

    out_dir = tmp_path / "out"
    no_restore = (tmp_path / "obj" / "project.assets.json").exists()

    build_args = [info["exe"], "build", "-c", "Release", "-o", str(out_dir), "--nologo"]
    if no_restore:
        build_args.append("--no-restore")

    try:
        build = subprocess.run(
            build_args, cwd=str(tmp_path), capture_output=True,
            text=True, timeout=120, encoding="utf-8",
            errors="replace", env=env,
        )
    except subprocess.TimeoutExpired:
        return None, {"error": "⏱ Превышено время сборки (120 сек)."}

    if build.returncode != 0:
        err = ((build.stdout or "") + "\n" + (build.stderr or "")).strip()[-2500:]
        return None, {"error": "Ошибка компиляции:\n" + humanize_error(err, "csharp")}

    exe_name = "App.exe" if sys.platform == "win32" else "App"
    exe_path = out_dir / exe_name
    if not exe_path.exists():
        return None, {"error": f"Не найден {exe_path}"}

    results = []
    for i, tc in enumerate(test_cases, 1):
        name = tc.get("_label") or f"Тест {i}"
        stdin = tc.get("input", "")
        expected = tc.get("expected", "")
        try:
            r = subprocess.run(
                [str(exe_path)], cwd=str(tmp_path), input=stdin,
                capture_output=True, text=True, timeout=10,
                encoding="utf-8", errors="replace", env=env,
            )
            if r.returncode != 0:
                results.append({
                    "name": name, "passed": False,
                    "message": "Ошибка:\n" + humanize_error(r.stderr or "", "csharp")[:600],
                })
                continue
            passed = _normalize(r.stdout) == _normalize(expected)
            msg = "OK" if passed else (
                f"Вход: {stdin!r}\nОжидалось: {expected!r}\nПолучено:  {(r.stdout or '').strip()!r}"
            )
            results.append({"name": name, "passed": passed, "message": msg})
        except subprocess.TimeoutExpired:
            results.append({"name": name, "passed": False,
                            "message": "⏱ Превышено время (10 сек)."})
        except Exception as e:
            results.append({"name": name, "passed": False, "message": f"Ошибка: {e}"})
    return results, None