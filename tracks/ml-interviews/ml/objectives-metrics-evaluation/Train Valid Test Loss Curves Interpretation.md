# Интерпретация кривых loss: train, valid, test

**Вопрос (EN)**: Your model's loss curves on train, valid, and test look like [certain pattern on a figure]. What might have been the cause? What would you do?

## Ответ

### Train low, Valid/Test high (overfitting)

**Причины:** модель переобучается на train, плохо обобщается.

**Действия:** регуляризация (L2, dropout), упрощение модели, больше данных, augmentation, early stopping.

### Train high, Valid/Test high (underfitting)

**Причины:** модель слишком простая, не хватает ёмкости.

**Действия:** усложнить модель, добавить признаки, уменьшить регуляризацию, обучать дольше.

### Train и Valid близки, Test выше

**Причины:** distribution shift между validation и test, переобучение на val при подборе гиперпараметров.

**Действия:** проверить representative val split, temporal split, проверить на data leakage.

### Valid ниже Train

**Причины:** dropout/batch norm в train, но не в eval; разные аугментации; regularization эффекты.

**Действия:** это нормально при dropout; убедиться, что eval mode корректен.

### Все три высокие и параллельные

**Причины:** underfitting, недостаточно данных или признаков.

**Действия:** увеличить ёмкость модели, улучшить features, проверить предобработку.

### Train высокий, Valid ещё выше

**Причины:** underfitting плюс возможный distribution shift — модель слаба и к тому же validation/test из другого распределения.

**Действия:** сначала усилить модель (больше ёмкости, признаков); затем проверить согласованность train/val/test, temporal split, отсутствие утечки.

---
*Источник: [MLIB](https://huyenchip.com/ml-interviews-book/)*
