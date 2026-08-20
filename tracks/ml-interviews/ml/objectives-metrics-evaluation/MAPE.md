# MAPE — метрика для прогноза акций

**Вопрос (EN)**: Predict stock price in 8 hours; predicted price should never be off more than 10% from actual. Which metric would you use?

## Ответ

### MAPE (Mean Absolute Percentage Error)

\[
\text{MAPE} = \frac{100\%}{n} \sum_i \left| \frac{y_i - \hat{y}_i}{y_i} \right|
\]

MAPE измеряет ошибку в процентах от фактического значения и хорошо соответствует требованию «не более 10% отклонения».

### Альтернативы

- **Symmetric MAPE (sMAPE)** — при малых знаменателях обычный MAPE нестабилен; sMAPE это сглаживает.
- **WAPE/Weighted MAPE** — нормировка по сумме фактических значений.
- **Ограничение по 10%** — можно оптимизировать loss, penalizing ошибки >10% сильнее, или использовать hinge-like loss.

### Ограничения MAPE

- При \(y_i \approx 0\) MAPE раздувается.
- Асимметрия: переоценка и недооценка штрафуются по-разному.
- Для акций с малыми ценами MAPE может быть нестабильным; тогда лучше WAPE или логарифмические метрики.

---
*Источник: [MLIB](https://huyenchip.com/ml-interviews-book/)*
