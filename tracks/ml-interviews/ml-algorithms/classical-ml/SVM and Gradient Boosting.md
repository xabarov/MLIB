# SVM и Gradient Boosting

**Вопросы (EN)**: What's linear separation? Why desirable for SVM? How well would vanilla SVM work on [non-linear] datasets? What is gradient boosting? What problems is it good for?

## Ответ

### Линейная разделимость

Классы можно разделить гиперплоскостью. SVM ищет оптимальную разделяющую гиперплоскость с максимальным margin. Линейная разделимость упрощает задачу и даёт хорошую обобщающую способность в линейно разделимом случае.

### Vanilla SVM на нелинейных данных

Линейный SVM плохо справится с нелинейными границами (XOR, круговые границы). Нужны kernel trick (RBF, polynomial) или фичи более высокой размерности.

### Gradient Boosting

Последовательное добавление слабых учеников (обычно деревьев), каждый аппроксимирует отрицательный градиент функции потерь. Итоговая модель — сумма всех learners.

### Где gradient boosting удобен

- Табличные данные
- Смешанные типы признаков
- Пропуски в данных (LightGBM, XGBoost)
- Высокая точность без глубоких сетей
- Интерпретируемость через feature importance

---
*Источник: [MLIB](https://huyenchip.com/ml-interviews-book/)*
