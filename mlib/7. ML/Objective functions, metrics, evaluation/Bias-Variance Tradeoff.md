# Bias-Variance Trade-off

**Вопрос (EN)**: What's the bias-variance trade-off? How's it related to overfitting and underfitting? How do you know high variance/low bias and what to do? Low variance/high bias?

## Ответ

### Суть trade-off

Ошибка модели разлагается на:
- **Bias** — систематическая ошибка от упрощения модели (недостаточная гибкость).
- **Variance** — разброс предсказаний при разных обучающих выборках (избыточная чувствительность к данным).

\[
\text{MSE} = \text{Bias}^2 + \text{Variance} + \text{Irreducible error}
\]

Упрощение модели ↑ bias, ↓ variance; усложнение ↓ bias, ↑ variance.

### Связь с over/underfitting

- **Underfitting** — high bias, low variance (модель слишком простая).
- **Overfitting** — low bias, high variance (модель подстраивается под шум).

### High variance, low bias

**Признаки:** train loss низкий, val loss высокий; большая разница между train и val.

**Что делать:**
- Больше данных
- Регуляризация (L1/L2, dropout)
- Упрощение модели
- Augmentation
- Early stopping

### Low variance, high bias

**Признаки:** train и val loss высокие и близки; модель недообучается.

**Что делать:**
- Усложнить модель (больше слоёв/нейронов)
- Добавить признаки
- Уменьшить регуляризацию
- Обучать дольше

---
*Источник: [MLIB](https://huyenchip.com/ml-interviews-book/)*
