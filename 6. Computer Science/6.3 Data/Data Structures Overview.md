# Структуры данных — обзор

**Контекст (EN)**: Data structures relevant for ML.

## Ответ

### Сложность операций

| Структура | Поиск | Вставка | Удаление | Примечания |
|-----------|-------|---------|----------|------------|
| Array | O(1) по индексу | O(n) | O(n) | — |
| BST (сбаланс.) | O(log n) | O(log n) | O(log n) | AVL, Red-Black |
| Heap | O(1) min/max | O(log n) | O(log n) | extract-min O(log n) |
| HashMap | O(1) среднее | O(1) | O(1) | — |
| Trie | O(m) | O(m) | O(m) | m — длина ключа |
| Queue/Stack | — | O(1) | O(1) | — |

### Деревья

- **Binary Search Tree** — O(log n) поиск при сбалансированности; O(n) в худшем.
- **Heap** — O(log n) insert/extract-min; приоритетная очередь.
- **Trie** — префиксное дерево; O(m) поиск по строке длины m.

### Примеры использования в ML

- **Heap** — top-k элементов (min-heap размера k); streaming quantiles; приоритетная выборка.
- **Trie** — autocomplete, префиксный поиск; хранение словаря для beam search.
- **HashMap** — индексация категорий, кэш embeddings, счётчики (word count).
- **Priority Queue** — Dijkstra, A*; scheduling в distributed training.

### Очереди и стеки

- **Queue** — FIFO; BFS.
- **Stack** — LIFO; DFS, парсинг.
- **Priority Queue** — извлечение по приоритету; Dijkstra.

### Хеш-таблицы

- **HashMap/HashTable** — O(1) в среднем для insert/lookup/delete.
- **Collision handling** — chaining, open addressing.

### Форматы данных

- **Row-based** (CSV, JSON) — эффективная запись; чтение целой строки.
- **Column-based** (Parquet, ORC) — эффективное чтение отдельных колонок; подходит для аналитики и feature extraction.
- **pandas, dask** — ориентированы на колоночные операции.

---
*Источник: [MLIB](https://huyenchip.com/ml-interviews-book/)*
