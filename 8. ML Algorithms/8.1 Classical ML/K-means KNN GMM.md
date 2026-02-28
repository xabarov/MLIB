# K-means, K-NN, GMM

**Вопросы (EN)**: How to choose k for k-means? Evaluate k-means with/without labels? Compare k-means and GMM? How to choose k for k-NN? Impact of k on bias-variance?

## Ответ

### Выбор k в k-means

- **Elbow method** — график inertia vs k; ищем «изгиб».
- **Silhouette score** — баланс cohesion и separation.
- **Gap statistic** — сравнение с null-распределением.
- Доменные требования (число сегментов).

### Оценка k-means

**С метками:** Adjusted Rand Index, NMI, F1 для кластеров vs классов.

**Без меток:** Silhouette, Davies-Bouldin, Calinski-Harabasz.

### K-means vs GMM

- K-means — жёсткое присвоение; сферические кластеры; EM с дисперсией → 0.
- GMM — мягкое присвоение (вероятности); эллипсоидальные кластеры; разные размеры и ориентации.
- GMM — когда кластеры перекрываются или имеют разную форму.

### K в k-NN

- Малое k — низкий bias, высокий variance; чувствительность к шуму.
- Большое k — высокий bias, низкий variance; более гладкая граница.
- Оптимальное k — кросс-валидация; часто √n как старт.

---
*Источник: [MLIB](https://huyenchip.com/ml-interviews-book/)*
