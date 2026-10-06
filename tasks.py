# ============================================================
# ЗАДАЧИ для онлайн-компилятора
# Каждая задача — словарь:
#   id           — уникальный идентификатор
#   title        — название
#   difficulty   — easy / medium / hard
#   description  — условие
#   starter      — стартовый код: {"python": "...", "csharp": "..."}
#   test_cases   — список {"input": "...", "expected": "..."}
# ============================================================

TASKS = [
    # --------- 1 ---------
    {
        "id": "max-digit-2",
        "title": "Максимальная цифра двузначного числа",
        "difficulty": "easy",
        "description": (
            "Определите максимальную цифру двузначного числа.\n"
            "Вход: целое положительное двузначное число N (10 ≤ N ≤ 99).\n"
            "Выход: максимальная цифра числа."
        ),
        "starter": {
            "python": "n = int(input())\n\n# ваш код здесь\n",
            "csharp": (
                "using System;\n\n"
                "class Program\n{\n"
                "    static void Main()\n    {\n"
                "        int n = int.Parse(Console.ReadLine());\n"
                "        // ваш код здесь\n    }\n}\n"
            ),
        },
        "test_cases": [
            {"input": "25", "expected": "5"},
            {"input": "70", "expected": "7"},
            {"input": "10", "expected": "1"},
            {"input": "99", "expected": "9"},
            {"input": "43", "expected": "4"},
        ],
    },
    # --------- 2 ---------
    {
        "id": "age",
        "title": "Возраст",
        "difficulty": "easy",
        "description": (
            "Вводятся два целых числа — возраст папы и мамы.\n"
            "Выведите одну из строк:\n"
            "Mother is older than father\n"
            "Mother is younger than father\n"
            "Mother and father are of the same age"
        ),
        "starter": {
            "python": "father, mother = map(int, input().split())\n\n# ваш код здесь\n",
            "csharp": (
                "using System;\n\n"
                "class Program\n{\n"
                "    static void Main()\n    {\n"
                "        var parts = Console.ReadLine().Split();\n"
                "        int father = int.Parse(parts[0]);\n"
                "        int mother = int.Parse(parts[1]);\n"
                "        // ваш код здесь\n    }\n}\n"
            ),
        },
        "test_cases": [
            {"input": "7043 2268", "expected": "Mother is younger than father"},
            {"input": "9171 9171", "expected": "Mother and father are of the same age"},
            {"input": "30 50", "expected": "Mother is older than father"},
            {"input": "100 100", "expected": "Mother and father are of the same age"},
        ],
    },
    # --------- 3 ---------
    {
        "id": "hello-n",
        "title": "N раз Hello world",
        "difficulty": "easy",
        "description": (
            "Выведите «Hello world» N раз, каждое — с новой строки.\n"
            "Вход: одно натуральное число N (1 ≤ N ≤ 300)."
        ),
        "starter": {
            "python": "n = int(input())\n\n# ваш код здесь\n",
            "csharp": (
                "using System;\n\n"
                "class Program\n{\n"
                "    static void Main()\n    {\n"
                "        int n = int.Parse(Console.ReadLine());\n"
                "        // ваш код здесь\n    }\n}\n"
            ),
        },
        "test_cases": [
            {"input": "2", "expected": "Hello world\nHello world"},
            {"input": "1", "expected": "Hello world"},
            {"input": "3", "expected": "Hello world\nHello world\nHello world"},
        ],
    },
    # --------- 4 ---------
    {
        "id": "from-1-to-n",
        "title": "От 1 до N и обратно",
        "difficulty": "easy",
        "description": (
            "Выведите две строки:\n"
            "1) числа от 1 до N через пробел\n"
            "2) числа от N до 1 через пробел\n"
            "В конце строк пробел не ставить."
        ),
        "starter": {
            "python": "n = int(input())\n\n# ваш код здесь\n",
            "csharp": (
                "using System;\n\n"
                "class Program\n{\n"
                "    static void Main()\n    {\n"
                "        int n = int.Parse(Console.ReadLine());\n"
                "        // ваш код здесь\n    }\n}\n"
            ),
        },
        "test_cases": [
            {"input": "4", "expected": "1 2 3 4\n4 3 2 1"},
            {"input": "2", "expected": "1 2\n2 1"},
            {"input": "1", "expected": "1\n1"},
        ],
    },
    # --------- 5 ---------
    {
        "id": "digits-count",
        "title": "Количество цифр",
        "difficulty": "easy",
        "description": (
            "Найдите количество цифр натурального числа N.\n"
            "Вход: N ≤ 200000000.\n"
            "Выход: одно целое число — количество цифр."
        ),
        "starter": {
            "python": "n = int(input())\n\n# ваш код здесь\n",
            "csharp": (
                "using System;\n\n"
                "class Program\n{\n"
                "    static void Main()\n    {\n"
                "        int n = int.Parse(Console.ReadLine());\n"
                "        // ваш код здесь\n    }\n}\n"
            ),
        },
        "test_cases": [
            {"input": "123456789", "expected": "9"},
            {"input": "2918585", "expected": "7"},
            {"input": "5", "expected": "1"},
            {"input": "100000000", "expected": "9"},
        ],
    },
    # --------- 6 ---------
    {
        "id": "digits-sum",
        "title": "Сумма цифр",
        "difficulty": "medium",
        "description": (
            "Найдите сумму цифр натурального числа N.\n"
            "Вход: N ≤ 200000000.\n"
            "Выход: одно целое число — сумма цифр."
        ),
        "starter": {
            "python": "n = int(input())\n\n# ваш код здесь\n",
            "csharp": (
                "using System;\n\n"
                "class Program\n{\n"
                "    static void Main()\n    {\n"
                "        int n = int.Parse(Console.ReadLine());\n"
                "        // ваш код здесь\n    }\n}\n"
            ),
        },
        "test_cases": [
            {"input": "123456789", "expected": "45"},
            {"input": "11706526", "expected": "28"},
            {"input": "100", "expected": "1"},
        ],
    },
    # --------- 7 ---------
    {
        "id": "digits-max",
        "title": "Максимальная цифра числа",
        "difficulty": "medium",
        "description": (
            "Найдите максимальную цифру натурального числа N.\n"
            "Вход: N ≤ 2000000000.\n"
            "Выход: одна цифра — наибольшая в числе."
        ),
        "starter": {
            "python": "n = int(input())\n\n# ваш код здесь\n",
            "csharp": (
                "using System;\n\n"
                "class Program\n{\n"
                "    static void Main()\n    {\n"
                "        long n = long.Parse(Console.ReadLine());\n"
                "        // ваш код здесь\n    }\n}\n"
            ),
        },
        "test_cases": [
            {"input": "37585991", "expected": "9"},
            {"input": "1234567890", "expected": "9"},
            {"input": "111", "expected": "1"},
            {"input": "909", "expected": "9"},
        ],
    },
    # --------- 8 ---------
    {
        "id": "palindrome",
        "title": "Палиндром",
        "difficulty": "medium",
        "description": (
            "Определите, является ли натуральное число N палиндромом.\n"
            "Вход: N ≤ 200000000.\n"
            "Выход: Yes или No."
        ),
        "starter": {
            "python": "n = int(input())\n\n# ваш код здесь\n",
            "csharp": (
                "using System;\n\n"
                "class Program\n{\n"
                "    static void Main()\n    {\n"
                "        int n = int.Parse(Console.ReadLine());\n"
                "        // ваш код здесь\n    }\n}\n"
            ),
        },
        "test_cases": [
            {"input": "50505", "expected": "Yes"},
            {"input": "785604", "expected": "No"},
            {"input": "121", "expected": "Yes"},
            {"input": "10", "expected": "No"},
        ],
    },
    # --------- 9 ---------
    {
        "id": "divisors",
        "title": "Делители числа",
        "difficulty": "medium",
        "description": (
            "Найдите все делители натурального числа N (1 ≤ N ≤ 10000).\n"
            "Выведите две строки: сначала в порядке возрастания, затем — убывания.\n"
            "Числа в строках через пробел, в конце пробел не ставить."
        ),
        "starter": {
            "python": "n = int(input())\n\n# ваш код здесь\n",
            "csharp": (
                "using System;\nusing System.Collections.Generic;\n\n"
                "class Program\n{\n"
                "    static void Main()\n    {\n"
                "        int n = int.Parse(Console.ReadLine());\n"
                "        // ваш код здесь\n    }\n}\n"
            ),
        },
        "test_cases": [
            {"input": "11", "expected": "1 11\n11 1"},
            {"input": "60", "expected":
                "1 2 3 4 5 6 10 12 15 20 30 60\n"
                "60 30 20 15 12 10 6 5 4 3 2 1"},
            {"input": "1", "expected": "1\n1"},
        ],
    },
    # --------- 10 ---------
    {
        "id": "gcd",
        "title": "НОД",
        "difficulty": "medium",
        "description": (
            "Найдите наибольший общий делитель двух целых неотрицательных чисел,\n"
            "не превосходящих 10000. Хотя бы одно из них > 0.\n"
            "Выход: одно целое число — НОД."
        ),
        "starter": {
            "python": "a, b = map(int, input().split())\n\n# ваш код здесь\n",
            "csharp": (
                "using System;\n\n"
                "class Program\n{\n"
                "    static void Main()\n    {\n"
                "        var parts = Console.ReadLine().Split();\n"
                "        int a = int.Parse(parts[0]);\n"
                "        int b = int.Parse(parts[1]);\n"
                "        // ваш код здесь\n    }\n}\n"
            ),
        },
        "test_cases": [
            {"input": "60 22", "expected": "2"},
            {"input": "12 18", "expected": "6"},
            {"input": "7 13", "expected": "1"},
            {"input": "100 100", "expected": "100"},
        ],
    },
    # --------- 11 ---------
    {
        "id": "first-n-odd",
        "title": "Первые N нечётных чисел",
        "difficulty": "easy",
        "description": (
            "Выведите N наименьших натуральных нечётных чисел через пробел.\n"
            "Вход: N (1 ≤ N ≤ 300). В конце строки пробел не ставить."
        ),
        "starter": {
            "python": "n = int(input())\n\n# ваш код здесь\n",
            "csharp": (
                "using System;\n\n"
                "class Program\n{\n"
                "    static void Main()\n    {\n"
                "        int n = int.Parse(Console.ReadLine());\n"
                "        // ваш код здесь\n    }\n}\n"
            ),
        },
        "test_cases": [
            {"input": "6", "expected": "1 3 5 7 9 11"},
            {"input": "9", "expected": "1 3 5 7 9 11 13 15 17"},
            {"input": "1", "expected": "1"},
        ],
    },
    # --------- 12 ---------
    {
        "id": "odd-range",
        "title": "Нечётные числа в диапазоне",
        "difficulty": "easy",
        "description": (
            "Вводятся A и B (1 ≤ A < B < 300).\n"
            "Выведите все нечётные числа из [A, B] через пробел.\n"
            "В конце строки пробел не ставить."
        ),
        "starter": {
            "python": "a, b = map(int, input().split())\n\n# ваш код здесь\n",
            "csharp": (
                "using System;\n\n"
                "class Program\n{\n"
                "    static void Main()\n    {\n"
                "        var parts = Console.ReadLine().Split();\n"
                "        int a = int.Parse(parts[0]);\n"
                "        int b = int.Parse(parts[1]);\n"
                "        // ваш код здесь\n    }\n}\n"
            ),
        },
        "test_cases": [
            {"input": "6 13", "expected": "7 9 11 13"},
            {"input": "153 154", "expected": "153"},
            {"input": "1 10", "expected": "1 3 5 7 9"},
        ],
    },
    # --------- 13 ---------
    {
        "id": "sums-1-n",
        "title": "Суммы от 1 до N",
        "difficulty": "easy",
        "description": (
            "Выведите N строк вида [K] + [N+1-K] = [N+1], K = 1..N.\n"
            "Между числами и знаками — по одному пробелу.\n"
            "Пример для N=3:\n"
            "1 + 3 = 4\n2 + 2 = 4\n3 + 1 = 4"
        ),
        "starter": {
            "python": "n = int(input())\n\n# ваш код здесь\n",
            "csharp": (
                "using System;\n\n"
                "class Program\n{\n"
                "    static void Main()\n    {\n"
                "        int n = int.Parse(Console.ReadLine());\n"
                "        // ваш код здесь\n    }\n}\n"
            ),
        },
        "test_cases": [
            {"input": "3", "expected": "1 + 3 = 4\n2 + 2 = 4\n3 + 1 = 4"},
            {"input": "1", "expected": "1 + 1 = 2"},
            {"input": "5", "expected":
                "1 + 5 = 6\n2 + 4 = 6\n3 + 3 = 6\n4 + 2 = 6\n5 + 1 = 6"},
        ],
    },
    # --------- 14 ---------
    {
        "id": "squares",
        "title": "Таблица квадратов",
        "difficulty": "easy",
        "description": (
            "Выведите N строк вида K^2 = M, K = 1..N, M = K*K.\n"
            "Пример для N=3:\n"
            "1^2 = 1\n2^2 = 4\n3^2 = 9"
        ),
        "starter": {
            "python": "n = int(input())\n\n# ваш код здесь\n",
            "csharp": (
                "using System;\n\n"
                "class Program\n{\n"
                "    static void Main()\n    {\n"
                "        int n = int.Parse(Console.ReadLine());\n"
                "        // ваш код здесь\n    }\n}\n"
            ),
        },
        "test_cases": [
            {"input": "5", "expected":
                "1^2 = 1\n2^2 = 4\n3^2 = 9\n4^2 = 16\n5^2 = 25"},
            {"input": "1", "expected": "1^2 = 1"},
            {"input": "3", "expected": "1^2 = 1\n2^2 = 4\n3^2 = 9"},
        ],
    },
    # --------- 15 ---------
    {
        "id": "seq-length",
        "title": "Длина последовательности",
        "difficulty": "medium",
        "description": (
            "Считывайте числа по одному до первого 0.\n"
            "Выведите количество чисел до завершающего 0 (не считая его).\n"
            "Вход: не более 100000 чисел."
        ),
        "starter": {
            "python": "count = 0\nwhile True:\n    n = int(input())\n    if n == 0:\n        break\n    # ваш код здесь\nprint(count)\n",
            "csharp": (
                "using System;\n\n"
                "class Program\n{\n"
                "    static void Main()\n    {\n"
                "        int count = 0;\n"
                "        while (true)\n        {\n"
                "            int n = int.Parse(Console.ReadLine());\n"
                "            if (n == 0) break;\n"
                "            // ваш код здесь\n        }\n"
                "        Console.WriteLine(count);\n    }\n}\n"
            ),
        },
        "test_cases": [
            {"input": "1\n3\n7\n9\n0", "expected": "4"},
            {"input": "5\n0", "expected": "1"},
            {"input": "0", "expected": "0"},
            {"input": "10\n20\n30\n40\n50\n0", "expected": "5"},
        ],
    },
    # --------- 16 ---------
    {
        "id": "even-positive",
        "title": "Количество чётных положительных",
        "difficulty": "medium",
        "description": (
            "Считывайте числа до первого 0. Посчитайте количество чётных\n"
            "положительных чисел (не считая завершающего 0)."
        ),
        "starter": {
            "python": "count = 0\nwhile True:\n    n = int(input())\n    if n == 0:\n        break\n    # ваш код здесь\nprint(count)\n",
            "csharp": (
                "using System;\n\n"
                "class Program\n{\n"
                "    static void Main()\n    {\n"
                "        int count = 0;\n"
                "        while (true)\n        {\n"
                "            int n = int.Parse(Console.ReadLine());\n"
                "            if (n == 0) break;\n"
                "            // ваш код здесь\n        }\n"
                "        Console.WriteLine(count);\n    }\n}\n"
            ),
        },
        "test_cases": [
            {"input": "1\n2\n-4\n0", "expected": "1"},
            {"input": "5\n10\n2\n4\n0", "expected": "3"},
            {"input": "-2\n-4\n0", "expected": "0"},
            {"input": "0", "expected": "0"},
        ],
    },
    # --------- 17 ---------
    {
        "id": "addition-game",
        "title": "Арифметическая игра «Сложение»",
        "difficulty": "medium",
        "description": (
            "Сумма двух двузначных чисел ab и cd равна двузначному числу ef.\n"
            "Известны a, d, e, f. Найдите b, c.\n"
            "Вход: 4 цифры a, d, e, f (0..9) через пробел.\n"
            "Выход: две цифры b и c через пробел (в этом порядке).\n"
            "Гарантируется, что решение существует и единственно."
        ),
        "starter": {
            "python": "a, d, e, f = map(int, input().split())\n\n# ваш код здесь\n",
            "csharp": (
                "using System;\n\n"
                "class Program\n{\n"
                "    static void Main()\n    {\n"
                "        var parts = Console.ReadLine().Split();\n"
                "        int a = int.Parse(parts[0]);\n"
                "        int d = int.Parse(parts[1]);\n"
                "        int e = int.Parse(parts[2]);\n"
                "        int f = int.Parse(parts[3]);\n"
                "        // ваш код здесь\n    }\n}\n"
            ),
        },
        "test_cases": [
            {"input": "1 4 4 1", "expected": "7 2"},
            {"input": "2 5 5 0", "expected": "5 2"},
            {"input": "3 1 5 2", "expected": "1 2"},
        ],
    },
    # --------- 18 ---------
    {
        "id": "subtraction-game",
        "title": "Арифметическая игра «Вычитание»",
        "difficulty": "medium",
        "description": (
            "Из двузначного числа ab вычитается двузначное cd, результат — ef.\n"
            "Известны a, d, e, f. Найдите b, c.\n"
            "Вход: 4 цифры a, d, e, f (0..9) через пробел.\n"
            "Выход: две цифры b и c через пробел (в этом порядке).\n"
            "Гарантируется, что решение существует и единственно."
        ),
        "starter": {
            "python": "a, d, e, f = map(int, input().split())\n\n# ваш код здесь\n",
            "csharp": (
                "using System;\n\n"
                "class Program\n{\n"
                "    static void Main()\n    {\n"
                "        var parts = Console.ReadLine().Split();\n"
                "        int a = int.Parse(parts[0]);\n"
                "        int d = int.Parse(parts[1]);\n"
                "        int e = int.Parse(parts[2]);\n"
                "        int f = int.Parse(parts[3]);\n"
                "        // ваш код здесь\n    }\n}\n"
            ),
        },
        "test_cases": [
            {"input": "5 6 2 5", "expected": "1 2"},
            {"input": "7 4 1 8", "expected": "2 5"},
            {"input": "9 0 5 0", "expected": "0 4"},
        ],
    },
    # --------- 19 ---------
    {
        "id": "segment-halfplane",
        "title": "Отрезок в полуплоскости",
        "difficulty": "easy",
        "description": (
            "Даны координаты концов отрезка X1 Y1 X2 Y2.\n"
            "Выведите одну из строк:\n"
            "Otrezok lezhit v levoi poluploskosti — если обе точки слева (x < 0)\n"
            "Otrezok lezhit v pravoi poluploskosti — если обе точки справа (x > 0)\n"
            "Otrezok peresekaet os' OY — в остальных случаях"
        ),
        "starter": {
            "python": "x1, y1, x2, y2 = map(int, input().split())\n\n# ваш код здесь\n",
            "csharp": (
                "using System;\n\n"
                "class Program\n{\n"
                "    static void Main()\n    {\n"
                "        var p = Console.ReadLine().Split();\n"
                "        int x1 = int.Parse(p[0]);\n"
                "        int y1 = int.Parse(p[1]);\n"
                "        int x2 = int.Parse(p[2]);\n"
                "        int y2 = int.Parse(p[3]);\n"
                "        // ваш код здесь\n    }\n}\n"
            ),
        },
        "test_cases": [
            {"input": "-8765 -997 1196 -2463", "expected": "Otrezok peresekaet os' OY"},
            {"input": "809 7988 3353 380", "expected": "Otrezok lezhit v pravoi poluploskosti"},
            {"input": "-5 -5 -3 -1", "expected": "Otrezok lezhit v levoi poluploskosti"},
            {"input": "-2 0 3 0", "expected": "Otrezok peresekaet os' OY"},
        ],
    },
    # --------- 20 ---------
    {
        "id": "circle-strip",
        "title": "Круг в полосе",
        "difficulty": "medium",
        "description": (
            "Вводятся x, y, R, a — координаты центра круга, радиус и ширина полосы.\n"
            "Полоса — часть плоскости между прямыми y=0 и y=a.\n"
            "Выведите одну из строк:\n"
            "Krug lezhit v polose — круг целиком в полосе\n"
            "Krug nad polosoi — круг целиком выше полосы\n"
            "Krug pod polosoi — круг целиком ниже полосы\n"
            "Krug chastichno zakryt polosoi — иначе"
        ),
        "starter": {
            "python": "x, y, r, a = map(int, input().split())\n\n# ваш код здесь\n",
            "csharp": (
                "using System;\n\n"
                "class Program\n{\n"
                "    static void Main()\n    {\n"
                "        var p = Console.ReadLine().Split();\n"
                "        int x = int.Parse(p[0]);\n"
                "        int y = int.Parse(p[1]);\n"
                "        int r = int.Parse(p[2]);\n"
                "        int a = int.Parse(p[3]);\n"
                "        // ваш код здесь\n    }\n}\n"
            ),
        },
        "test_cases": [
            {"input": "4 4 2 2", "expected": "Krug nad polosoi"},
            {"input": "1 1 1 5", "expected": "Krug lezhit v polose"},
            {"input": "0 -5 2 3", "expected": "Krug pod polosoi"},
            {"input": "0 5 1 10", "expected": "Krug lezhit v polose"},
            {"input": "0 0 3 5", "expected": "Krug chastichno zakryt polosoi"},
        ],
    },
    # --------- 21 ---------
    {
        "id": "boxes",
        "title": "Ящики",
        "difficulty": "medium",
        "description": (
            "Нужно погрузить K единиц товара. Погрузчик может за один раз взять\n"
            "один или два ящика (при этом ящики разные — 1-го и 2-го типа).\n"
            "Ящик 1 вмещает A1 единиц и весит B1.\n"
            "Ящик 2 вмещает A2 единиц и весит B2.\n"
            "Суммарный вес за раз не должен превышать W.\n\n"
            "Выведите Yes, если можно погрузить всё за один раз, иначе No."
        ),
        "starter": {
            "python": (
                "k, w = map(int, input().split())\n"
                "a1, b1 = map(int, input().split())\n"
                "a2, b2 = map(int, input().split())\n\n"
                "# ваш код здесь\n"
            ),
            "csharp": (
                "using System;\n\n"
                "class Program\n{\n"
                "    static void Main()\n    {\n"
                "        var p1 = Console.ReadLine().Split();\n"
                "        int k = int.Parse(p1[0]);\n"
                "        int w = int.Parse(p1[1]);\n"
                "        var p2 = Console.ReadLine().Split();\n"
                "        int a1 = int.Parse(p2[0]);\n"
                "        int b1 = int.Parse(p2[1]);\n"
                "        var p3 = Console.ReadLine().Split();\n"
                "        int a2 = int.Parse(p3[0]);\n"
                "        int b2 = int.Parse(p3[1]);\n"
                "        // ваш код здесь\n    }\n}\n"
            ),
        },
        "test_cases": [
            {"input": "10 15\n5 7\n8 4", "expected": "Yes"},
            {"input": "15 10\n10 5\n12 7", "expected": "No"},
            {"input": "5 5\n3 2\n4 3", "expected": "No"},
            {"input": "3 4\n3 2\n4 3", "expected": "Yes"},
        ],
    },
    # --------- 22 ---------
    {
        "id": "cards",
        "title": "Cards",
        "difficulty": "easy",
        "description": (
            "Для числа N (1 ≤ N ≤ 100) подберите правильное окончание:\n"
            "1 karta (1, 21, 31, ...)\n"
            "2 karty (2-4, 22-24, 32-34, ...)\n"
            "5 kart  (5-20, 25-30, 11-14, ...)\n"
            "Выведите: N слово (через один пробел)."
        ),
        "starter": {
            "python": "n = int(input())\n\n# ваш код здесь\n",
            "csharp": (
                "using System;\n\n"
                "class Program\n{\n"
                "    static void Main()\n    {\n"
                "        int n = int.Parse(Console.ReadLine());\n"
                "        // ваш код здесь\n    }\n}\n"
            ),
        },
        "test_cases": [
            {"input": "1", "expected": "1 karta"},
            {"input": "2", "expected": "2 karty"},
            {"input": "5", "expected": "5 kart"},
            {"input": "11", "expected": "11 kart"},
            {"input": "22", "expected": "22 karty"},
            {"input": "55", "expected": "55 kart"},
            {"input": "21", "expected": "21 karta"},
            {"input": "100", "expected": "100 kart"},
            {"input": "14", "expected": "14 kart"},
            {"input": "24", "expected": "24 karty"},
        ],
    },
    # --------- 23 ---------
    {
        "id": "cheviana",
        "title": "Чевиана треугольника",
        "difficulty": "hard",
        "description": (
            "Даны координаты A, B, C, D (точка D лежит на отрезке AC).\n"
            "Выясните, чем является BD:\n"
            "Mediana — D середина AC\n"
            "Bissektrisa — AD/DC = AB/BC\n"
            "Vysota — BD ⟂ AC\n"
            "Mediana, bissektrisa i vysota — если всё сразу\n"
            "Cheviana — если ничего из перечисленного\n"
            "Ввод: Xa Ya Xb Yb Xc Yc Xd Yd — 8 целых чисел."
        ),
        "starter": {
            "python": (
                "xa, ya, xb, yb, xc, yc, xd, yd = map(int, input().split())\n\n"
                "# ваш код здесь\n"
            ),
            "csharp": (
                "using System;\n\n"
                "class Program\n{\n"
                "    static void Main()\n    {\n"
                "        var p = Console.ReadLine().Split();\n"
                "        int xa=int.Parse(p[0]), ya=int.Parse(p[1]);\n"
                "        int xb=int.Parse(p[2]), yb=int.Parse(p[3]);\n"
                "        int xc=int.Parse(p[4]), yc=int.Parse(p[5]);\n"
                "        int xd=int.Parse(p[6]), yd=int.Parse(p[7]);\n"
                "        // ваш код здесь\n    }\n}\n"
            ),
        },
        "test_cases": [
            {"input": "0 0 0 4 2 0 1 0", "expected": "Mediana"},
            {"input": "-1 3 3 6 3 1 1 2", "expected": "Mediana, bissektrisa i vysota"},
            {"input": "0 0 1 1 2 0 1 0", "expected": "Mediana, bissektrisa i vysota"},
        ],
    },
    # --------- 24 ---------
    {
        "id": "odd-progression",
        "title": "Нечётная прогрессия",
        "difficulty": "medium",
        "description": (
            "Даны количество N и сумма S нескольких подряд идущих нечётных чисел.\n"
            "Найдите эти числа.\n"
            "Вход: N S (N, S ≤ 2000).\n"
            "Выход: N искомых целых нечётных чисел через пробел (без пробела в конце)."
        ),
        "starter": {
            "python": "n, s = map(int, input().split())\n\n# ваш код здесь\n",
            "csharp": (
                "using System;\n\n"
                "class Program\n{\n"
                "    static void Main()\n    {\n"
                "        var p = Console.ReadLine().Split();\n"
                "        int n = int.Parse(p[0]);\n"
                "        int s = int.Parse(p[1]);\n"
                "        // ваш код здесь\n    }\n}\n"
            ),
        },
        "test_cases": [
            {"input": "5 35", "expected": "3 5 7 9 11"},
            {"input": "1 49", "expected": "49"},
            {"input": "3 21", "expected": "5 7 9"},
            {"input": "4 40", "expected": "7 9 11 13"},
        ],
    },
    # --------- 25 ---------
    {
        "id": "digits-reverse",
        "title": "Цифры числа в обратном порядке",
        "difficulty": "medium",
        "description": (
            "Выведите цифры натурального числа N (N ≤ 200000000) через пробел,\n"
            "начиная с младшей. В конце строки пробел не ставить.\n"
            "Пример: 123456789 → 9 8 7 6 5 4 3 2 1"
        ),
        "starter": {
            "python": "n = int(input())\n\n# ваш код здесь\n",
            "csharp": (
                "using System;\n\n"
                "class Program\n{\n"
                "    static void Main()\n    {\n"
                "        int n = int.Parse(Console.ReadLine());\n"
                "        // ваш код здесь\n    }\n}\n"
            ),
        },
        "test_cases": [
            {"input": "123456789", "expected": "9 8 7 6 5 4 3 2 1"},
            {"input": "203933044", "expected": "4 4 0 3 3 9 3 0 2"},
            {"input": "5", "expected": "5"},
            {"input": "100", "expected": "0 0 1"},
        ],
    },
    # --------- 26 ---------
    {
        "id": "sum-multiply",
        "title": "Сумма и произведение",
        "difficulty": "easy",
        "description": (
            "Найдите сумму и произведение двух чисел n и m\n"
            "(-10^4 ≤ n, m ≤ 10^4).\n"
            "Выход: сумма и произведение через пробел."
        ),
        "starter": {
            "python": "n, m = map(int, input().split())\n\n# ваш код здесь\n",
            "csharp": (
                "using System;\n\n"
                "class Program\n{\n"
                "    static void Main()\n    {\n"
                "        var p = Console.ReadLine().Split();\n"
                "        int n = int.Parse(p[0]);\n"
                "        int m = int.Parse(p[1]);\n"
                "        // ваш код здесь\n    }\n}\n"
            ),
        },
        "test_cases": [
            {"input": "10 20", "expected": "30 200"},
            {"input": "-1 1", "expected": "0 -1"},
            {"input": "0 0", "expected": "0 0"},
            {"input": "5 -3", "expected": "2 -15"},
            {"input": "-7 -8", "expected": "-15 56"},
        ],
    },
    # --------- 27 ---------
    {
        "id": "next-even",
        "title": "Следующее чётное",
        "difficulty": "easy",
        "description": (
            "Дано целое число N (1 ≤ N ≤ 50).\n"
            "Выведите следующее за ним чётное число.\n"
            "При решении нельзя использовать if и циклы."
        ),
        "starter": {
            "python": "n = int(input())\n\n# ваш код здесь (без if и циклов)\n",
            "csharp": (
                "using System;\n\n"
                "class Program\n{\n"
                "    static void Main()\n    {\n"
                "        int n = int.Parse(Console.ReadLine());\n"
                "        // ваш код здесь (без if и циклов)\n    }\n}\n"
            ),
        },
        "test_cases": [
            {"input": "7", "expected": "8"},
            {"input": "8", "expected": "10"},
            {"input": "1", "expected": "2"},
            {"input": "2", "expected": "4"},
            {"input": "49", "expected": "50"},
            {"input": "50", "expected": "52"},
        ],
    },
    # --------- 28 ---------
    {
        "id": "century-year",
        "title": "Век и год",
        "difficulty": "easy",
        "description": (
            "Дан год (положительное, ≤ 10000, не кратное 100).\n"
            "Определите, какой сейчас век, и сколько лет прошло с его начала.\n"
            "Выход: два числа через пробел — век и годы.\n"
            "Пример: 1234 → 13 34"
        ),
        "starter": {
            "python": "year = int(input())\n\n# ваш код здесь\n",
            "csharp": (
                "using System;\n\n"
                "class Program\n{\n"
                "    static void Main()\n    {\n"
                "        int year = int.Parse(Console.ReadLine());\n"
                "        // ваш код здесь\n    }\n}\n"
            ),
        },
        "test_cases": [
            {"input": "1234", "expected": "13 34"},
            {"input": "3082", "expected": "31 82"},
            {"input": "101", "expected": "2 1"},
            {"input": "1901", "expected": "20 1"},
            {"input": "9999", "expected": "100 99"},
        ],
    },
    # --------- 29 ---------
    {
        "id": "sum-reverse",
        "title": "Сумма с инверсией",
        "difficulty": "easy",
        "description": (
            "Дано двузначное число N (10 ≤ N ≤ 99).\n"
            "Разверните его и сложите с исходным.\n"
            "Формат вывода: (исходное) + (развёрнутое) = (сумма)\n"
            "Знаки + и = отделены пробелами.\n"
            "Пример: 82 → 82 + 28 = 110"
        ),
        "starter": {
            "python": "n = int(input())\n\n# ваш код здесь\n",
            "csharp": (
                "using System;\n\n"
                "class Program\n{\n"
                "    static void Main()\n    {\n"
                "        int n = int.Parse(Console.ReadLine());\n"
                "        // ваш код здесь\n    }\n}\n"
            ),
        },
        "test_cases": [
            {"input": "82", "expected": "82 + 28 = 110"},
            {"input": "30", "expected": "30 + 3 = 33"},
            {"input": "10", "expected": "10 + 1 = 11"},
            {"input": "99", "expected": "99 + 99 = 198"},
            {"input": "45", "expected": "45 + 54 = 99"},
        ],
    },
    # --------- 30 ---------
    {
        "id": "apple-division",
        "title": "Делёж яблок",
        "difficulty": "easy",
        "description": (
            "N школьников делят K яблок «поровну» — так, чтобы у любых двух\n"
            "школьников яблок отличалось не более чем на 1.\n"
            "Выведите количество школьников, которым достанется меньше, чем другим.\n"
            "При решении нельзя использовать if и циклы."
        ),
        "starter": {
            "python": "n, k = map(int, input().split())\n\n# ваш код здесь (без if и циклов)\n",
            "csharp": (
                "using System;\n\n"
                "class Program\n{\n"
                "    static void Main()\n    {\n"
                "        var p = Console.ReadLine().Split();\n"
                "        int n = int.Parse(p[0]);\n"
                "        int k = int.Parse(p[1]);\n"
                "        // ваш код здесь (без if и циклов)\n    }\n}\n"
            ),
        },
        "test_cases": [
            {"input": "7 30", "expected": "5"},
            {"input": "7 28", "expected": "0"},
            {"input": "3 10", "expected": "2"},
            {"input": "1 5", "expected": "0"},
            {"input": "10 3", "expected": "7"},
        ],
    },
    # --------- 31 ---------
    {
        "id": "oranges",
        "title": "Апельсины",
        "difficulty": "easy",
        "description": (
            "Вчера купили N апельсинов. Настя съела на F меньше, чем папа,\n"
            "и на M больше, чем мама.\n"
            "Вход: N, F, M (10 ≤ N ≤ 100, 1 ≤ F ≤ 40, 1 ≤ M ≤ 40).\n"
            "Гарантируется, что ответ — целые положительные числа.\n"
            "Выход: сколько съели папа, Настя и мама (через пробел)."
        ),
        "starter": {
            "python": "n, f, m = map(int, input().split())\n\n# ваш код здесь\n",
            "csharp": (
                "using System;\n\n"
                "class Program\n{\n"
                "    static void Main()\n    {\n"
                "        var p = Console.ReadLine().Split();\n"
                "        int n = int.Parse(p[0]);\n"
                "        int f = int.Parse(p[1]);\n"
                "        int m = int.Parse(p[2]);\n"
                "        // ваш код здесь\n    }\n}\n"
            ),
        },
        "test_cases": [
            {"input": "65 10 5", "expected": "30 20 15"},
            {"input": "79 26 16", "expected": "49 23 7"},
            {"input": "30 5 3", "expected": "12 7 4"},
        ],
    },
    # --------- 32 ---------
    {
        "id": "sign",
        "title": "Знак числа",
        "difficulty": "easy",
        "description": (
            "sign(x) = 1, если x > 0; -1, если x < 0; 0, если x = 0.\n"
            "Вход: x (|x| ≤ 10^9).\n"
            "Выход: значение sign(x)."
        ),
        "starter": {
            "python": "x = int(input())\n\n# ваш код здесь\n",
            "csharp": (
                "using System;\n\n"
                "class Program\n{\n"
                "    static void Main()\n    {\n"
                "        long x = long.Parse(Console.ReadLine());\n"
                "        // ваш код здесь\n    }\n}\n"
            ),
        },
        "test_cases": [
            {"input": "179", "expected": "1"},
            {"input": "-1", "expected": "-1"},
            {"input": "0", "expected": "0"},
            {"input": "1000000000", "expected": "1"},
            {"input": "-1000000000", "expected": "-1"},
        ],
    },
    # --------- 33 ---------
    {
        "id": "max3",
        "title": "Максимум из трёх",
        "difficulty": "easy",
        "description": (
            "Вводятся три целых числа (|x| ≤ 10000).\n"
            "Выведите одну из строк:\n"
            "First number is maximal\n"
            "Second number is maximal\n"
            "Third number is maximal"
        ),
        "starter": {
            "python": "a, b, c = map(int, input().split())\n\n# ваш код здесь\n",
            "csharp": (
                "using System;\n\n"
                "class Program\n{\n"
                "    static void Main()\n    {\n"
                "        var p = Console.ReadLine().Split();\n"
                "        int a = int.Parse(p[0]);\n"
                "        int b = int.Parse(p[1]);\n"
                "        int c = int.Parse(p[2]);\n"
                "        // ваш код здесь\n    }\n}\n"
            ),
        },
        "test_cases": [
            {"input": "3363 -7244 -2969", "expected": "First number is maximal"},
            {"input": "-6420 -4624 -7098", "expected": "Second number is maximal"},
            {"input": "1 2 3", "expected": "Third number is maximal"},
            {"input": "5 5 3", "expected": "First number is maximal"},
            {"input": "-1 -2 -3", "expected": "First number is maximal"},
        ],
    },
    # --------- 34 ---------
    {
        "id": "cutlets",
        "title": "Котлеты",
        "difficulty": "medium",
        "description": (
            "На сковородку одновременно можно положить k котлет.\n"
            "Каждую котлету нужно обжаривать с каждой стороны по 1 минуте.\n"
            "За какое наименьшее время удастся поджарить n котлет?\n"
            "Вход: n, k (не превосходят 32000)."
        ),
        "starter": {
            "python": "n, k = map(int, input().split())\n\n# ваш код здесь\n",
            "csharp": (
                "using System;\n\n"
                "class Program\n{\n"
                "    static void Main()\n    {\n"
                "        var p = Console.ReadLine().Split();\n"
                "        int n = int.Parse(p[0]);\n"
                "        int k = int.Parse(p[1]);\n"
                "        // ваш код здесь\n    }\n}\n"
            ),
        },
        "test_cases": [
            {"input": "3 2", "expected": "3"},
            {"input": "5 4", "expected": "3"},
            {"input": "1 1", "expected": "2"},
            {"input": "2 10", "expected": "2"},
            {"input": "10 3", "expected": "7"},
        ],
    },
    # --------- 35 ---------
    {
        "id": "triangle-sides",
        "title": "Треугольник со сторонами",
        "difficulty": "medium",
        "description": (
            "Вводятся 3 положительных числа — длины отрезков.\n"
            "Выведите одно из сообщений:\n"
            "Triangle is equilateral — равносторонний\n"
            "Triangle is isosceles — равнобедренный\n"
            "Triangle is scalene — разносторонний\n"
            "Triangle is invalid — треугольника не существует"
        ),
        "starter": {
            "python": "a, b, c = map(int, input().split())\n\n# ваш код здесь\n",
            "csharp": (
                "using System;\n\n"
                "class Program\n{\n"
                "    static void Main()\n    {\n"
                "        var p = Console.ReadLine().Split();\n"
                "        int a = int.Parse(p[0]);\n"
                "        int b = int.Parse(p[1]);\n"
                "        int c = int.Parse(p[2]);\n"
                "        // ваш код здесь\n    }\n}\n"
            ),
        },
        "test_cases": [
            {"input": "100 60 80", "expected": "Triangle is scalene"},
            {"input": "4653 4653 4653", "expected": "Triangle is equilateral"},
            {"input": "5 5 8", "expected": "Triangle is isosceles"},
            {"input": "1 2 10", "expected": "Triangle is invalid"},
            {"input": "3 4 5", "expected": "Triangle is scalene"},
        ],
    },
    # --------- 36 ---------
    {
        "id": "triangle-angles",
        "title": "Треугольник с углами",
        "difficulty": "medium",
        "description": (
            "Вводятся 3 целых числа — длины отрезков.\n"
            "Выведите одно из сообщений:\n"
            "Triangle is rectangular — прямоугольный\n"
            "Triangle is content obtuse angle — тупоугольный\n"
            "Triangle is consist of sharp angles — остроугольный\n"
            "Triangle is invalid — треугольника не существует"
        ),
        "starter": {
            "python": "a, b, c = map(int, input().split())\n\n# ваш код здесь\n",
            "csharp": (
                "using System;\n\n"
                "class Program\n{\n"
                "    static void Main()\n    {\n"
                "        var p = Console.ReadLine().Split();\n"
                "        int a = int.Parse(p[0]);\n"
                "        int b = int.Parse(p[1]);\n"
                "        int c = int.Parse(p[2]);\n"
                "        // ваш код здесь\n    }\n}\n"
            ),
        },
        "test_cases": [
            {"input": "3 4 5", "expected": "Triangle is rectangular"},
            {"input": "878 3766 2000", "expected": "Triangle is invalid"},
            {"input": "5 5 6", "expected": "Triangle is consist of sharp angles"},
            {"input": "3 3 5", "expected": "Triangle is content obtuse angle"},
            {"input": "6 8 10", "expected": "Triangle is rectangular"},
        ],
    },
]