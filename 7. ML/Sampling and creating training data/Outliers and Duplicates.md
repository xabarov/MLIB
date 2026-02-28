# Выбросы и дубликаты

**Вопрос (EN)**: How to determine outliers in your data samples? What to do with them? When should you remove duplicate training samples? When shouldn't you? What happens if we accidentally duplicate every data point in train or test set?

## Ответ

### Выбросы (outliers)

**Как определить:**
- IQR: \(x < Q1 - 1.5 \cdot IQR\) или \(x > Q3 + 1.5 \cdot IQR\)
- Z-score: \(|z| > 3\)
- Изоляционный лес (Isolation Forest)
- DBSCAN, LOF (Local Outlier Factor)

**Что делать:**
- Удалять — если явные ошибки ввода
- Winsorization — обрезка экстремумов
- Robust scaling — MinMax/RobustScaler
- Отдельная модель для аномалий (если они — целевые)

### Дубликаты

**Когда удалять:**
- Строгие копии, ошибки сбора
- Случайные дубли при объединении источников

**Когда не удалять:**
- Реальные повторения (одинаковые транзакции)
- Oversampling для дисбаланса классов
- Важно сохранение частот (например, популярные запросы)

**Если продублировать весь train:**
- Оценка ошибки будет optimistic: те же примеры в train и (если утечка) в val/test. Обобщающая способность не улучшается.

**Если продублировать весь test:**
- Метрики останутся корректными, но confidence intervals будут занижены (зависимые повторения).

---
*Источник: [MLIB](https://huyenchip.com/ml-interviews-book/)*
