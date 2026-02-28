# Дисбаланс классов (Class Imbalance)

**Вопрос (EN)**: How would class imbalance affect your model? Why is it hard for ML models to perform well on imbalanced data? For skin lesion detection with 1% positive class and more false negatives than false positives — what techniques would you use?

## Ответ

### Влияние дисбаланса

- Модель смещается к классу большинства: часто предсказывает majority class.
- Accuracy вводит в заблуждение (99% при простом предсказании majority).
- Меньший класс хуже распознаётся → больше ложноотрицательных.

### Почему сложно

- Ошибка на rare class мала в общей loss, градиент слабо реагирует.
- Few-shot learning: мало примеров редкого класса.
- Стоимость FN и FP может быть разной (например, в медицине FN опаснее).

### Методы для skin lesion (1% положительных, много FN)

1. **Перевзвешивание классов** — больший вес loss для positive.
2. **Оversampling** — SMOTE, ADASYN, копирование positive.
3. **Undersampling** — уменьшение majority (осторожно — теряется информация).
4. **Порог принятия решения** — снижение порога для увеличения recall.
5. **Focal Loss** — ослабление вклада easy examples.
6. **Ансамбли** — обучение на сбалансированных подвыборках.
7. **Сбор большего числа positive примеров**.
8. **Метрики** — Precision-Recall, F1, AUC-PR вместо accuracy.

---
*Источник: [MLIB](https://huyenchip.com/ml-interviews-book/)*
