# Затухание и взрыв градиентов

**Вопросы (EN)**: How do we know gradients are exploding? How to prevent? Why are RNNs especially susceptible?

## Ответ

### Признаки взрыва градиентов

- NaN/Inf в loss или весах.
- Резкие скачки loss.
- Очень большие значения градиентов.
- Нестабильное обучение.

### Как предотвращать

- **Gradient clipping** — ограничение нормы градиента (по value или по global norm).
- Правильная инициализация (Xavier, He).
- Batch/Layer Normalization.
- Короткие пути (skip connections, ResNet).
- Умеренный learning rate.

### RNN и vanishing/exploding

В RNN градиент проходит через длинную цепочку матричных умножений. При |λ| > 1 — взрыв, при |λ| < 1 — затухание. Длинные последовательности усиливают эффект. LSTM/GRU с gate'ами частично решают проблему затухания; clipping — стандарт против взрыва.

---
*Источник: [MLIB](https://huyenchip.com/ml-interviews-book/)*
