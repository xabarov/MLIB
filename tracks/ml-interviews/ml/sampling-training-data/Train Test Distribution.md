# Проверка: train и test из одного распределения

**Вопрос (EN)**: How to determine whether two sets of samples (e.g. train and test splits) come from the same distribution?

## Ответ

### Статистические тесты

1. **Kolmogorov–Smirnov (KS)** — для одномерных непрерывных признаков; сравнивает эмпирические CDF.
2. **Chi-squared** — для категориальных признаков.
3. **Mann–Whitney U** — непараметрический тест для сравнения двух выборок.
4. **Anderson–Darling** — вариация KS с большим весом хвостов.

### Многомерные подходы

5. **Maximum Mean Discrepancy (MMD)** — сравнивает распределения в Reproducing Kernel Hilbert Space.
6. **Classifier-based test** — модель классифицирует, train это или test; если AUC близка к 0.5, распределения похожи.
7. **PCA/t-SNE визуализация** — проверка наложений и кластеризации по источнику (train vs test).

### Мониторинг в production

- Отслеживание статистик (среднее, дисперсия, квантили) по ключевым признакам.
- Drift-детекторы (PSI, K-L divergence).
- Сравнение распределений predictions между периодами.

---
*Источник: [MLIB](https://huyenchip.com/ml-interviews-book/)*
