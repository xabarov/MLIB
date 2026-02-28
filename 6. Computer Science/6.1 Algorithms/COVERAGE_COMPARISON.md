# Сверка покрытия ответов — 6.1 Algorithms (MLIB)

Сравнение с [huyenchip.com/ml-interviews-book — 6.1 Algorithms](https://huyenchip.com/ml-interviews-book/contents/6.1-algorithms.html) по состоянию на февраль 2026.

---

## Вводный раздел (алгоритмы, упомянутые в тексте главы)

| Алгоритм / техника               | Покрыт в `Algorithms Overview.md` | Статус |
|----------------------------------|-----------------------------------|--------|
| Quicksort                        | ✅                                | ✅     |
| Merge sort                       | ✅                                | ✅     |
| Radix sort                       | ✅                                | ✅     |
| Dijkstra's algorithm             | ✅                                | ✅     |
| A* search                        | ✅                                | ✅     |
| Tree traversal (pre/in/post)     | ✅                                | ✅     |
| **Stable Marriage Problem**      | ❌                                | ❌ ПРОПУСК |
| **Traveling Salesman Problem**   | ❌                                | ❌ ПРОПУСК |
| Dynamic programming              | ✅ (кратко)                       | ✅     |
| Recursion                        | ✅ (кратко)                       | ✅     |
| String manipulation / KMP / Trie | ✅ (кратко)                       | ✅     |
| Regular expressions              | ✅ (кратко)                       | ✅     |
| Memory allocation                | ✅ (в Coding Problems)            | ✅     |
| **Binary Search**                | ❌ (используется в Q7, Q11)       | ❌ ПРОПУСК |
| **BFS / DFS (граф)**             | ❌                                | ❌ ПРОПУСК |
| **Greedy algorithms**            | ❌                                | ❌ ПРОПУСК |

---

## Задачи 6.1 (13 вопросов книги)

| # (книга) | Формулировка (EN)                                        | Локальный раздел              | Статус  | Качество ответа                     |
|-----------|----------------------------------------------------------|-------------------------------|---------|-------------------------------------|
| 1         | 1M news articles — filter near-duplicates                | Coding Problems § 13          | ✅      | ✅ Хороший; LSH, MinHash, clustering |
| 2         | Justify alignment, configurable line length              | Coding Problems § 12          | ✅      | ⚠️ Подход описан, **кода нет**      |
| 3         | Directory — find files with duplicated content           | Coding Problems § 11          | ✅      | ⚠️ Подход описан, **кода нет**      |
| 4         | Evaluate math expression with `+`, `-`, `*`, `/`, `()`  | Coding Problems § 10          | ✅      | ⚠️ Два подхода описаны, **кода нет**|
| 5         | malloc / free on a memory block (array)                  | Coding Problems § 9           | ✅      | ⚠️ Концептуально, **кода нет**      |
| 6         | Sudoku solver (backtracking)                             | Coding Problems § 8           | ✅      | ⚠️ Подход описан, **кода нет**      |
| 7         | Median of two sorted arrays — O(log(m+n))                | Coding Problems § 7           | ✅      | ⚠️ Алгоритм описан, **кода нет**    |
| 8         | Subarray sum = k — O(N)                                  | Coding Problems § 6           | ✅      | ⚠️ Prefix sum описан, **кода нет**  |
| 9         | Tree traversal: pre, in, post-order                      | Coding Problems § 5           | ✅      | ⚠️ Описан, **кода нет**             |
| 10        | Longest Common Subsequence (LCS)                         | Coding Problems § 4           | ✅      | ⚠️ DP описан, **кода нет**          |
| 11        | Longest Increasing Subsequence (LIS)                     | Coding Problems § 3           | ✅      | ⚠️ O(n²) и O(n log n), **кода нет** |
| 12        | Implement O(N log N) sort (quicksort / merge sort)       | Coding Problems § 2           | ✅      | ⚠️ Описан, **кода нет**             |
| 13        | Recursively read a JSON file (Python function)           | Coding Problems § 1           | ✅      | ⚠️ Описан, **кода нет**             |

---

## Итоговый анализ

### Покрытие вопросов: **13 / 13 ✅ (100%)**

Все 13 задач присутствуют в файле `Algorithms Coding Problems.md`.  
Нумерация в локальном файле **обратная** (13→1 вместо 1→13 как в книге) — не критично, но затрудняет навигацию.

### Критические пробелы

| Проблема | Приоритет |
|----------|-----------|
| **Нет Python-кода ни для одного из 13 вопросов** — книга прямо просит "write a function / implement" | 🔴 Высокий |
| Binary Search не описан как самостоятельный алгоритм | 🟠 Средний |
| BFS / DFS не упомянут в обзоре | 🟠 Средний |
| Stable Marriage Problem — пропущен (упомянут в тексте главы) | 🟡 Низкий |
| Traveling Salesman Problem — пропущен | 🟡 Низкий |
| Greedy algorithms не упомянуты | 🟡 Низкий |

---

## План улучшений

1. **`Algorithms Coding Problems.md`** — добавить Python-реализацию к каждой задаче.
2. **`Algorithms Overview.md`** — добавить: Binary Search, BFS/DFS, Greedy, Stable Marriage, TSP.

---

*Источники: [MLIB 6.1](https://huyenchip.com/ml-interviews-book/contents/6.1-algorithms.html), локальные файлы в `6. Computer Science/6.1 Algorithms/`*
