# Выбор признаков (Feature Selection)

**Вопрос (EN)**: Why feature selection? Algorithms? Pros and cons?

## Ответ

### Зачем нужен

- Уменьшение переобучения и «шума».
- Ускорение обучения и inference.
- Упрощение модели и интерпретируемость.
- Работа при curse of dimensionality.

### Методы

1. **Filter** — оценка по отдельности (correlation, mutual information, chi-squared). Плюсы: быстро, не зависит от модели. Минусы: не учитывает взаимодействия.

2. **Wrapper** — перебор подмножеств с использованием модели (RFE, forward/backward selection). Плюсы: учёт модели. Минусы: дорого, риск переобучения.

3. **Embedded** — встроено в обучение (L1/Lasso, tree-based importance). Плюсы: эффективно, один прогон. Минусы: привязано к модели.

---
*Источник: [MLIB](https://huyenchip.com/ml-interviews-book/)*
