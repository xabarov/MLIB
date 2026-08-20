# Confusion Matrix: Precision, Recall, F1

**Вопрос (EN)**: Given confusion matrix (TP=30, FN=20, FP=5, TN=40), calculate precision, recall, F1. What can we do to improve?

## Ответ

### Расчёт

- **Precision** = TP / (TP + FP) = 30 / 35 ≈ 0.857  
- **Recall** = TP / (TP + FN) = 30 / 50 = 0.6  
- **F1** = 2 × (0.857 × 0.6) / (0.857 + 0.6) ≈ 0.706  

### Как улучшить модель

1. **Снизить порог** — больше положительных предсказаний, recall растёт, precision может упасть.
2. **Собрать больше данных**, особенно положительных.
3. **Feature engineering** — добавить информативные признаки.
4. **Дисбаланс** — oversampling, class weights, focal loss.
5. **Другая модель** — попробовать более сложную или другую архитектуру.
6. **Устранить data leakage** и ошибки в разметке.
7. **Учёт стоимости ошибок** — выбрать порог по бизнес-метрике (например, максимизация recall при заданном минимуме precision).

---
*Источник: [MLIB](https://huyenchip.com/ml-interviews-book/)*
