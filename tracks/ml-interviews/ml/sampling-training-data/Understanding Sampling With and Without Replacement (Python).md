# Выборка с возвращением и без — подробно

**Вопрос (EN)**: What is the difference between sampling with vs. without replacement? Name an example of when you would use one rather than the other?

## Ответ

### Выборка с возвращением (sampling with replacement)

1. Случайно извлекаем элемент из совокупности.
2. Фиксируем его.
3. Возвращаем обратно перед следующим извлечением.

Вероятность выбора каждого элемента остаётся неизменной на каждом шаге. Используется в бутстрэпе, Random Forest, Bagging.

### 63.2% в бутстрэп-выборке

При выборке \(n\) элементов с возвращением из \(n\) объектов в среднем ~63.2% уникальных строк оказываются в выборке; ~36.8% — ни разу не попадают.

### Выборка без возвращения (sampling without replacement)

Элемент после выбора не возвращается — один объект выбирается только один раз. Используется в train/test split и cross-validation, чтобы избежать пересечения train и test.

### Train/test split

~75% строк случайно (без возвращения) — train, 25% — test. Один объект не может одновременно быть и в train, и в test.

---
*Источник: [MLIB](https://huyenchip.com/ml-interviews-book/)*
