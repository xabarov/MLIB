# Bagging vs Boosting

**Вопрос (EN)**: Fundamental differences between bagging and boosting? How used in deep learning?

## Ответ

### Bagging (Bootstrap Aggregating)

- Обучение моделей на разных бутстрэп-выборках параллельно.
- Усреднение предсказаний (регрессия) или голосование (классификация).
- Снижает variance.
- Примеры: Random Forest, Extra Trees.

### Boosting

- Последовательное обучение; каждая модель исправляет ошибки предыдущих.
- Усиление веса ошибочных примеров (AdaBoost) или fitting остатков (Gradient Boosting).
- Снижает bias.
- Примеры: AdaBoost, XGBoost, LightGBM.

### В Deep Learning

- **Bagging:** обучение нескольких сетей на разных подвыборках/аугментациях; усреднение предсказаний (ensemble).
- **Boosting:** менее типично; возможны каскады моделей или iterative refinement.

---
*Источник: [MLIB](https://huyenchip.com/ml-interviews-book/)*
