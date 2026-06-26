# Алгоритмические задачи — подходы и код

Ответы на задачи **Q1–Q13** из раздела 6.1 книги MLIB.  
Каждый раздел содержит: идею решения, сложность и Python-реализацию.

> Нумерация соответствует [веб-версии книги](https://huyenchip.com/ml-interviews-book/contents/6.1-algorithms.html) (Q1 — первый вопрос в книге).

---

## Q1. Фильтрация 1M статей по схожести

**Подход:**
1. **Точные дубликаты** — хеш содержимого (MD5/SHA256).
2. **Почти-дубликаты** — MinHash + оценка Jaccard по шинглам (k-граммы слов). Для масштаба 1M документов применяют LSH (Locality-Sensitive Hashing) — разбить сигнатуры на bands и bucket; O(1) вместо O(n²) для поиска кандидатов.
3. **Порог** — оставить по одной статье из каждого кластера похожих документов.

**Сложность:** O(n · d) для вычисления сигнатур (d — число хешей); O(n) для LSH-фильтрации.

```python
import hashlib
from collections import defaultdict

def shingling(text: str, k: int = 5) -> set[str]:
    """k-граммы слов."""
    words = text.lower().split()
    return {" ".join(words[i:i+k]) for i in range(len(words) - k + 1)}

def minhash_signature(shingles: set[str], num_hashes: int = 128) -> list[int]:
    sig = []
    for seed in range(num_hashes):
        min_val = min(
            int(hashlib.md5(f"{seed}{s}".encode()).hexdigest(), 16)
            for s in shingles
        ) if shingles else 0
        sig.append(min_val)
    return sig

def jaccard_estimate(sig1: list[int], sig2: list[int]) -> float:
    return sum(a == b for a, b in zip(sig1, sig2)) / len(sig1)

def filter_similar_articles(articles: list[str], threshold: float = 0.8) -> list[str]:
    signatures = [minhash_signature(shingling(text)) for text in articles]
    dropped = set()
    for i in range(len(articles)):
        if i in dropped:
            continue
        for j in range(i + 1, len(articles)):
            if j not in dropped and jaccard_estimate(signatures[i], signatures[j]) >= threshold:
                dropped.add(j)
    return [articles[i] for i in range(len(articles)) if i not in dropped]
```

---

## Q2. Justify alignment

**Подход:** Собирать слова в строки до достижения `max_width`. Для каждой строки (кроме последней) равномерно распределить пробелы между словами; если нацело не делится — первые щели получают +1 пробел.

**Сложность:** O(n) по суммарному числу символов.

```python
def full_justify(words: list[str], max_width: int) -> list[str]:
    lines: list[list[str]] = []
    current: list[str] = []
    cur_len = 0

    for word in words:
        # +len(current) — минимально необходимые пробелы между словами
        if cur_len + len(word) + len(current) > max_width:
            lines.append(current)
            current, cur_len = [], 0
        current.append(word)
        cur_len += len(word)
    lines.append(current)

    result = []
    for i, line in enumerate(lines):
        if i == len(lines) - 1 or len(line) == 1:
            # Последняя строка или единственное слово — выравнивание влево
            result.append(" ".join(line).ljust(max_width))
            continue
        total_spaces = max_width - sum(len(w) for w in line)
        gaps = len(line) - 1
        space, extra = divmod(total_spaces, gaps)
        row = ""
        for j, word in enumerate(line[:-1]):
            row += word + " " * (space + (1 if j < extra else 0))
        result.append(row + line[-1])
    return result

# Пример
# full_justify(["This", "is", "an", "example", "of", "text", "justification."], 16)
# → ["This    is    an", "example  of text", "justification.  "]
```

---

## Q3. Файлы с дублированным контентом (в директории)

**Подход:** Обойти дерево директорий (`os.walk`), для каждого файла вычислить MD5-хеш содержимого, сгруппировать по хешу. Группы с ≥2 файлами — дубликаты.

**Сложность:** O(суммарный размер всех файлов).

```python
import os
import hashlib
from collections import defaultdict

def file_hash(path: str, chunk_size: int = 65_536) -> str:
    md5 = hashlib.md5()
    with open(path, "rb") as f:
        while data := f.read(chunk_size):
            md5.update(data)
    return md5.hexdigest()

def find_duplicates(directory: str) -> dict[str, list[str]]:
    hash_map: dict[str, list[str]] = defaultdict(list)
    for root, _, files in os.walk(directory):
        for fname in files:
            path = os.path.join(root, fname)
            hash_map[file_hash(path)].append(path)
    return {h: paths for h, paths in hash_map.items() if len(paths) > 1}
```

---

## Q4. Вычисление математического выражения

**Подход:** Итеративный разбор с одним стеком. Накапливаем число `num`, при встрече оператора применяем предыдущий оператор к стеку. Скобки обрабатываем рекурсивно (поиск парной скобки).

**Поддерживает:** `+`, `-`, `*`, `/`, скобки. Деление — целочисленное (в сторону нуля, как в C).

**Сложность:** O(n).

```python
def calculate(s: str) -> int:
    s = s.replace(" ", "") + "+"
    i, n = 0, len(s)
    stack: list[int] = []
    num, op = 0, "+"

    while i < n:
        c = s[i]
        if c.isdigit():
            num = num * 10 + int(c)
        elif c == "(":
            # найти парную закрывающую скобку
            depth, j = 1, i + 1
            while depth:
                if s[j] == "(": depth += 1
                elif s[j] == ")": depth -= 1
                j += 1
            num = calculate(s[i+1:j-1])
            i = j - 1
        if c in "+-*/" or i == n - 1:
            if   op == "+": stack.append(num)
            elif op == "-": stack.append(-num)
            elif op == "*": stack[-1] *= num
            elif op == "/": stack[-1] = int(stack[-1] / num)  # truncate toward zero
            op, num = c, 0
        i += 1
    return sum(stack)

# calculate("10 * 4 + (4 + 3) / (2 - 1)")  →  47
```

---

## Q5. malloc / free (распределитель памяти)

**Подход:** Список свободных блоков (free list). Каждый блок хранит `[start, end, is_free]`. При `malloc` — first-fit: первый подходящий свободный блок делится. При `free` — смежные свободные блоки сливаются (coalescing).

```python
class MemoryAllocator:
    def __init__(self, size: int):
        # [start, end, is_free]
        self.blocks: list[list] = [[0, size - 1, True]]

    def malloc(self, size: int) -> int:
        """Возвращает начальный адрес или -1 при нехватке памяти."""
        for i, (start, end, free) in enumerate(self.blocks):
            if free and end - start + 1 >= size:
                alloc_end = start + size - 1
                if alloc_end < end:
                    self.blocks.insert(i + 1, [alloc_end + 1, end, True])
                self.blocks[i] = [start, alloc_end, False]
                return start
        return -1

    def free(self, addr: int) -> None:
        for i, (start, end, free) in enumerate(self.blocks):
            if start == addr and not free:
                self.blocks[i][2] = True
                self._coalesce()
                return

    def _coalesce(self) -> None:
        i = 0
        while i < len(self.blocks) - 1:
            if self.blocks[i][2] and self.blocks[i + 1][2]:
                self.blocks[i][1] = self.blocks[i + 1][1]
                del self.blocks[i + 1]
            else:
                i += 1
```

---

## Q6. Sudoku Solver

**Подход:** Backtracking. Для каждой пустой клетки (`'*'`) пробуем цифры `'1'`–`'9'`, проверяем строку/столбец/блок 3×3. Рекурсия — если дошли без пустых клеток, решение найдено.

**Сложность:** O(9^m), m — число пустых клеток; на практике быстро из-за обрезки.

```python
Board = list[list[str]]

def solve_sudoku(board: Board) -> bool:
    cell = find_empty(board)
    if cell is None:
        return True
    row, col = cell
    for digit in "123456789":
        if is_valid(board, row, col, digit):
            board[row][col] = digit
            if solve_sudoku(board):
                return True
            board[row][col] = "*"
    return False

def find_empty(board: Board) -> tuple[int, int] | None:
    for r in range(9):
        for c in range(9):
            if board[r][c] == "*":
                return r, c
    return None

def is_valid(board: Board, row: int, col: int, digit: str) -> bool:
    if digit in board[row]:
        return False
    if any(board[r][col] == digit for r in range(9)):
        return False
    br, bc = 3 * (row // 3), 3 * (col // 3)
    for r in range(br, br + 3):
        for c in range(bc, bc + 3):
            if board[r][c] == digit:
                return False
    return True
```

---

## Q7. Median of Two Sorted Arrays — O(log(m+n))

**Подход:** Binary search по «разрезу» в меньшем массиве. Ищем позицию разреза так, чтобы все элементы слева от разреза в обоих массивах были ≤ всех справа. Медиана — max левой части / min правой части.

**Сложность:** O(log(min(m, n))).

```python
def find_median_sorted_arrays(nums1: list[int], nums2: list[int]) -> float:
    # Работаем с меньшим массивом
    if len(nums1) > len(nums2):
        nums1, nums2 = nums2, nums1
    m, n = len(nums1), len(nums2)
    lo, hi = 0, m

    while lo <= hi:
        cut1 = (lo + hi) // 2
        cut2 = (m + n + 1) // 2 - cut1

        max_left1  = nums1[cut1 - 1] if cut1 > 0 else float("-inf")
        min_right1 = nums1[cut1]     if cut1 < m else float("inf")
        max_left2  = nums2[cut2 - 1] if cut2 > 0 else float("-inf")
        min_right2 = nums2[cut2]     if cut2 < n else float("inf")

        if max_left1 <= min_right2 and max_left2 <= min_right1:
            if (m + n) % 2 == 1:
                return float(max(max_left1, max_left2))
            return (max(max_left1, max_left2) + min(min_right1, min_right2)) / 2
        elif max_left1 > min_right2:
            hi = cut1 - 1
        else:
            lo = cut1 + 1
    raise ValueError("Входные массивы не отсортированы")

# find_median_sorted_arrays([1, 3], [2])      → 2.0
# find_median_sorted_arrays([1, 2], [3, 4])   → 2.5
```

---

## Q8. Subarray Sum = k — O(N)

**Подход:** Prefix sum + hashmap. Ключевое наблюдение: `sum(arr[i:j]) == k` ⟺ `prefix[j] - prefix[i] == k` ⟺ `prefix[i] == prefix[j] - k`. Для каждого `j` ищем в map количество ранее встреченных значений `prefix[j] - k`.

**Сложность:** O(n). **Память:** O(n).

```python
from collections import defaultdict

def subarray_sum(nums: list[int], k: int) -> int:
    count = 0
    prefix = 0
    freq: dict[int, int] = defaultdict(int)
    freq[0] = 1  # пустой префикс

    for x in nums:
        prefix += x
        count += freq[prefix - k]
        freq[prefix] += 1
    return count

# subarray_sum([1, 1, 1], 2)   → 2
# subarray_sum([1, 2, 3], 3)   → 2
```

---

## Q9. Обход дерева (pre, in, post-order)

**Подход:** Рекурсия. Для итеративного обхода — стек.

**Сложность:** O(n).

```python
from __future__ import annotations
from dataclasses import dataclass, field

@dataclass
class TreeNode:
    val: int
    left: TreeNode | None = None
    right: TreeNode | None = None

def preorder(root: TreeNode | None) -> list[int]:
    """Корень → левое → правое."""
    if root is None:
        return []
    return [root.val] + preorder(root.left) + preorder(root.right)

def inorder(root: TreeNode | None) -> list[int]:
    """Левое → корень → правое. Для BST даёт отсортированный список."""
    if root is None:
        return []
    return inorder(root.left) + [root.val] + inorder(root.right)

def postorder(root: TreeNode | None) -> list[int]:
    """Левое → правое → корень."""
    if root is None:
        return []
    return postorder(root.left) + postorder(root.right) + [root.val]

# Итеративный in-order (избегает рекурсии на глубоких деревьях):
def inorder_iterative(root: TreeNode | None) -> list[int]:
    result, stack, node = [], [], root
    while node or stack:
        while node:
            stack.append(node)
            node = node.left
        node = stack.pop()
        result.append(node.val)
        node = node.right
    return result
```

---

## Q10. Longest Common Subsequence (LCS)

**Подход:** DP. `dp[i][j]` — длина LCS для `s1[:i]` и `s2[:j]`.

**Сложность:** O(m·n). **Память:** O(m·n), оптимизируется до O(min(m,n)) (rolling array).

```python
def lcs_length(s1: str, s2: str) -> int:
    m, n = len(s1), len(s2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if s1[i-1] == s2[j-1]:
                dp[i][j] = dp[i-1][j-1] + 1
            else:
                dp[i][j] = max(dp[i-1][j], dp[i][j-1])
    return dp[m][n]

def lcs_string(s1: str, s2: str) -> str:
    """Восстановление самой подпоследовательности."""
    m, n = len(s1), len(s2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if s1[i-1] == s2[j-1]:
                dp[i][j] = dp[i-1][j-1] + 1
            else:
                dp[i][j] = max(dp[i-1][j], dp[i][j-1])
    # Backtrack
    i, j, result = m, n, []
    while i > 0 and j > 0:
        if s1[i-1] == s2[j-1]:
            result.append(s1[i-1]); i -= 1; j -= 1
        elif dp[i-1][j] > dp[i][j-1]:
            i -= 1
        else:
            j -= 1
    return "".join(reversed(result))

# lcs_string("ABCBDAB", "BDCAB")  → "BCAB" (или другая LCS длины 4)
```

---

## Q11. Longest Increasing Subsequence (LIS)

**Подход O(n²):** `dp[i]` — длина LIS, оканчивающейся в `i`.  
**Подход O(n log n):** Массив `tails` минимальных хвостов подпоследовательностей. Для каждого `x` — binary search (`bisect_left`) для замены или расширения `tails`.

```python
import bisect

def lis_length(nums: list[int]) -> int:
    """O(n log n)."""
    tails: list[int] = []
    for x in nums:
        pos = bisect.bisect_left(tails, x)
        if pos == len(tails):
            tails.append(x)
        else:
            tails[pos] = x
    return len(tails)

def lis_sequence(nums: list[int]) -> list[int]:
    """Восстановление одной из LIS. O(n log n)."""
    n = len(nums)
    tails: list[int] = []
    indices: list[int] = []   # индексы элементов в tails
    predecessors = [-1] * n   # для восстановления пути

    for i, x in enumerate(nums):
        pos = bisect.bisect_left(tails, x)
        if pos == len(tails):
            tails.append(x)
            indices.append(i)
        else:
            tails[pos] = x
            indices[pos] = i
        predecessors[i] = indices[pos - 1] if pos > 0 else -1

    # Восстановить путь
    path, idx = [], indices[-1]
    while idx != -1:
        path.append(nums[idx])
        idx = predecessors[idx]
    return list(reversed(path))

# lis_length([10, 9, 2, 5, 3, 7, 101, 18])  → 4
# lis_sequence([10, 9, 2, 5, 3, 7, 101, 18]) → [2, 3, 7, 18] (или [2, 5, 7, 101])
```

---

## Q12. Реализация сортировки O(N log N)

### Quicksort

```python
def quicksort(arr: list) -> list:
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left  = [x for x in arr if x < pivot]
    mid   = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quicksort(left) + mid + quicksort(right)
```

### Merge sort

```python
def merge_sort(arr: list) -> list:
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    return _merge(merge_sort(arr[:mid]), merge_sort(arr[mid:]))

def _merge(left: list, right: list) -> list:
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i]); i += 1
        else:
            result.append(right[j]); j += 1
    return result + left[i:] + right[j:]
```

### Сравнение

| Алгоритм   | Среднее    | Худшее | Память   | In-place | Стабильный |
|------------|------------|--------|----------|----------|------------|
| Quicksort  | O(n log n) | O(n²)  | O(log n) | Да*      | Нет        |
| Merge sort | O(n log n) | O(n log n) | O(n) | Нет  | Да         |

*Версия выше не in-place из-за list comprehensions — для true in-place нужна lomuto/hoare partition.

---

## Q13. Рекурсивное чтение JSON

```python
import json
from typing import Any

def read_json(path: str) -> Any:
    with open(path, encoding="utf-8") as f:
        return json.load(f)

def walk_json(node: Any, path: str = "root", indent: int = 0) -> None:
    """Рекурсивный обход JSON-структуры с выводом всех путей и значений."""
    prefix = "  " * indent
    if isinstance(node, dict):
        print(f"{prefix}{path}/")
        for key, value in node.items():
            walk_json(value, key, indent + 1)
    elif isinstance(node, list):
        print(f"{prefix}{path}[] ({len(node)} items)")
        for i, item in enumerate(node):
            walk_json(item, f"[{i}]", indent + 1)
    else:
        print(f"{prefix}{path} = {node!r}")

def flatten_json(node: Any, prefix: str = "") -> dict[str, Any]:
    """Сплющить вложенный JSON в плоский dict с точечными ключами."""
    result: dict[str, Any] = {}
    if isinstance(node, dict):
        for key, value in node.items():
            new_key = f"{prefix}.{key}" if prefix else key
            result.update(flatten_json(value, new_key))
    elif isinstance(node, list):
        for i, item in enumerate(node):
            result.update(flatten_json(item, f"{prefix}[{i}]"))
    else:
        result[prefix] = node
    return result

# data = read_json("config.json")
# walk_json(data)
# flat = flatten_json(data)  → {"model.layers[0].size": 128, ...}
```

---
*Источник: [MLIB 6.1](https://huyenchip.com/ml-interviews-book/contents/6.1-algorithms.html)*
