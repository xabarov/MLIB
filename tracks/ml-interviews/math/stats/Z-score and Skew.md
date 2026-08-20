# Z-score и skew

**Вопрос (EN)**: Puppy weight μ=1 lb, σ=0.12. Puppy 1.1 lb — z-score? Weight for top 10%? If distribution is skew, does z-score still make sense?

## Ответ

### Z-score для щенка 1.1 lb

\(z = \frac{x - \mu}{\sigma} = \frac{1.1 - 1}{0.12} = \frac{0.1}{0.12} \approx 0.83\).

### Вес для топ-10%

Нужен квантиль 0.9 стандартного нормального: \(z_{0.9} \approx 1.28\).  
\(x = \mu + z \sigma = 1 + 1.28 \cdot 0.12 \approx 1.15\) lb.

### Z-score при skew

Z-score определён формально: \(z = (x-\mu)/\sigma\). При асимметричном распределении:
- Нормальная интерпретация («сколько σ от среднего») искажена.
- Квантили не соответствуют стандартным нормальным.
- Для асимметричных данных лучше использовать медиану, IQR или квантили.

### Трансформации для right-skewed данных

**Log-трансформация:** \(y = \log(x)\) или \(y = \log(1+x)\). Уменьшает правый хвост (зарплаты, доходы, время отклика). Пример: зарплаты [30k, 50k, 100k, 500k] — после log распределение ближе к нормальному.

**Box-Cox:** \(y = \frac{x^\lambda - 1}{\lambda}\) при λ≠0; \(\log(x)\) при λ=0. λ подбирается по данным (максимизация log-likelihood). Работает только для x > 0. Для x с нулями — Yeo-Johnson (см. [Bayes and Conditional](../5.2%20Probability/Bayes%20and%20Conditional.md)). После Box-Cox данные часто подходят для z-score и параметрических тестов.

---
*Источник: [MLIB](https://huyenchip.com/ml-interviews-book/)*
