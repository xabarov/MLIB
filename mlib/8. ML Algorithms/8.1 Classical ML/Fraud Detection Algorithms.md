# Алгоритмы для прототипа детекции мошенничества

**Вопрос (EN)**: What algorithms would you use when developing the prototype of a fraud detection model?

## Ответ

### Подходы

1. **Logistic Regression** — быстрый baseline, интерпретируемость, вероятности.
2. **Random Forest / XGBoost / LightGBM** — хорошо работают с табличными данными, устойчивы к выбросам, feature importance.
3. **Isolation Forest** — для аномалий; fraud часто редок.
4. **Linear models + engineered features** — скорость, масштабируемость.

### Важные аспекты

- **Дисбаланс классов** — fraud редок; oversampling, class weights, threshold tuning.
- **Features** — агрегаты по транзакциям, время, устройство, геолокация.
- **Latency** — требования к inference для real-time scoring.
- **Interpretability** — для объяснения блокировок.

Для прототипа типично: Logistic Regression или Gradient Boosting + стратификация и учёт дисбаланса.

---
*Источник: [MLIB](https://huyenchip.com/ml-interviews-book/)*
