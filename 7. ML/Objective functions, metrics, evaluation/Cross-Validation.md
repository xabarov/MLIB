# Кросс-валидация

**Вопрос (EN)**: Explain different methods for cross-validation. Why don't we see more cross-validation in deep learning?

## Ответ

### Методы кросс-валидации

1. **K-Fold** — данные делятся на K фолдов; K раз один фолд — validation, остальные — train.

2. **Stratified K-Fold** — фолды стратифицированы по целевой переменной, сохраняется доля классов.

3. **Leave-One-Out (LOO)** — каждый объект по очереди в validation, остальные в train; K = n.

4. **Time Series CV** — расширяющееся/скользящее окно: train на прошлом, validation на следующем интервале.

5. **Repeated K-Fold** — K-Fold несколько раз с разным random seed.

### Почему в DL CV используют реже

1. **Стоимость** — каждая эпоха тяжёлая; K раз обучать модель слишком дорого.
2. **Много данных** — обычно хватает одного train/val split; val достаточен для оценки.
3. **Зависимость от seed** — variance между запусками больше, чем между фолдами.
4. **Стабильность** — одна фиксированная val выборка часто даёт стабильную оценку при больших данных.

**В deep learning чаще:** фиксированный train/val split и/или несколько запусков с разными seed.

---
*Источник: [MLIB](https://huyenchip.com/ml-interviews-book/)*
