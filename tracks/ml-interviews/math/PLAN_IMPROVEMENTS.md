# План улучшения главы 5 — Math

Аудит по состоянию ответов и исходным вопросам из [MLIB](https://huyenchip.com/ml-interviews-book/).

---

## 5.1.1 Vectors (Векторы)

| # | Вопрос | Статус | Действие |
|---|--------|--------|----------|
| 1.1 | Geometric interpretation of dot product | ✅ Есть | — |
| 1.2 | Unit vector v maximizing u·v | ✅ Есть | — |
| 2.1 | Outer product a=[3,2,1], b=[-1,0,1] | ✅ Есть | Добавить явный числовой расчёт |
| 2.2 | Example of outer product in ML | ✅ Есть | — |
| 3 | Linear independence | ✅ Есть | — |
| 4 | Same basis for sets A and B | ✅ Есть | — |
| 5 | Dimension of span of n vectors in d dims | ✅ Есть | — |
| 6.1 | Norm, L0, L1, L2, L∞ | ✅ Есть | — |
| 6.2 | Norm vs metric, make metric from norm, norm from metric | ✅ Есть | — |

---

## 5.1.2 Matrices (Матрицы)

| # | Вопрос | Статус | Действие |
|---|--------|--------|----------|
| 1 | Matrices as linear transformations | ✅ Есть | — |
| 2 | Inverse: definition, all have?, unique? | ✅ Есть | — |
| 3 | Determinant meaning | ✅ Есть | — |
| 4 | Determinant when row × scalar t | ✅ Есть | Уточнить: det умножается на t |
| 5 | 4×4 matrix, eigenvalues 3,3,2,-1 → trace, det | ✅ Есть | — |
| 6 | 3×3 matrix, determinant without formula | ✅ Есть | — |
| 7 | Covariance A^TA vs Gram AA^T | ✅ Есть | — |
| 8.1–4 | Ax=b: find x, unique solution, multiple when cols>rows, pseudoinverse | ✅ Есть | — |
| 9 | Derivative, gradient, Jacobian | ✅ Есть (в Calculus) | — |
| 10 | Jacobian ∂y/∂x for y=xw | ✅ Есть | — |
| 11 | Large matrix: minimize x^TAx, unit x | ✅ Есть | — |

---

## 5.1.3 Dimensionality Reduction

| # | Вопрос | Статус | Действие |
|---|--------|--------|----------|
| 1–6 | PCA, SVD, t-SNE, scaling | ✅ Есть | Возможно расширить ответ по eigendecomposition uniqueness |

---

## 5.1.4 Calculus and Convex Optimization

| # | Вопрос | Статус | Действие |
|---|--------|--------|----------|
| 1 | Differentiable, example, ReLU/backprop | ✅ Есть | — |
| 2 | Convexity, desirable, cross-entropy convex | ✅ Есть | — |
| 3 | Logistic: p(y=-1), gradient, convexity | ✅ Есть | — |
| 4 | Second-order derivatives, pros/cons, why not common | ✅ Есть | — |
| 5 | Hessian for critical points | ✅ Есть | — |
| 6 | Jensen's inequality | ✅ Есть | — |
| 7 | Chain rule | ✅ Есть | — |
| 8 | ∂L/∂x for L=crossentropy(softmax(x), y) | ✅ Есть | — |
| 9 | f(x,y)=4x²-y, constraint x²+y²=1 | ✅ Есть | — |

---

## 5.2.1 Probability (Вероятность)

### Basic concepts (обзор)

| Тема | Статус | Действие |
|------|--------|----------|
| Основы (6 вопросов) | ✅ Probability Basics | — |
| Bayes, t-dist, transform to normal | ✅ Bayes and Conditional | — |

### Questions 5.2.1.2 (детальные задачи)

| # | Вопрос | Статус | Действие |
|---|--------|--------|----------|
| 9 | File storage: 5 crashes/year → P(crash next month), P(any moment) | ✅ Есть | Probability Applied Problems |
| 10 | Classifier 10 wrong/100 → P(next 20 all correct) | ✅ Есть | Там же |
| 11 | — | ⚠️ Пропущена | Формулировка в веб-MLIB не найдена, в файле — заглушка |
| 12 | Jason two children, one boy → P(two sons) | ✅ В Bayes | — |
| 13 | Chip manufacturers A/B, defective | ✅ Есть | Probability Applied Problems |
| 14 | Rare disease, Bayes, two tests positive | ✅ Есть | Там же |
| 15 | Dating site: 10/50 adjectives, match ≥5 | ✅ Есть | Там же |
| 16 | Height: mix of male/female Gaussians | ✅ Есть | Там же |
| 17 | Weather apps: independent vs dependent | ✅ Есть | Там же |
| 18 | German tank problem: estimate d | ✅ Есть | Там же |
| 19 | Expected days to draw X>0.5 from N(0,1) | ✅ Есть | Там же |
| 20 | Class size for P(someone same birthday) > 50% | ✅ Есть | Там же |
| 21 | Vegas betting strategy (Martingale) | ✅ Есть | Там же |
| 22 | Expected flips for two consecutive heads | ✅ Есть | Там же |
| 23 | Law of small numbers (kidney failure cities) | ✅ Есть | Там же |
| 24 | MLE for exponential distribution | ✅ Есть | Там же |

---

## 5.2.2 Stats (Статистика)

| # | Вопрос | Статус | Действие |
|---|--------|--------|----------|
| 1 | Frequentist vs Bayesian | ✅ Есть | — |
| 2 | Mean, median, variance for [1,5,3,2,4,4] | ✅ Есть | — |
| 3 | When median vs mean | ✅ В Mean Median | — |
| 4 | Moments (zeroth to fourth) | ✅ Есть | Moments and Correlation |
| 5 | Independence vs zero covariance (counterexample) | ✅ Есть | Там же: X~U[-1,1], Y=X² |
| 6–7 | CI for puppies, interpretation | ✅ Confidence Intervals | — |
| 8 | Unbiased estimate of median | ✅ Есть | Estimation and Inference |
| 9 | Correlation > 1? Interpret 0.3 | ✅ Есть | Moments |
| 10 | Z-score, top 10% weight, skew | ✅ Есть | Z-score and Skew |
| 11 | Coin fairness: 10 heads, 5 tails | ✅ Есть | Binomial test, chi-squared |
| 12 | Statistical significance, p-value distribution, war on significance | ✅ Есть | Statistical Significance |
| 13 | Multicollinearity, categorical independence, continuous independence | ✅ Есть | Variable Correlation Tests |
| 14 | A/B testing pros/cons | ✅ Есть | AB Testing and Power |
| 15 | Ad placement: sample size for 95% confidence | ✅ Есть | Power analysis |
| 16 | Double ads for revenue | ✅ Есть | Selection bias, cannibalization |
| 17 | Curse of big data: 10K stocks, spurious correlation | ✅ Есть | Multiple Testing Sufficient Stats |
| 18 | Sufficient statistics, Information Bottleneck | ✅ Есть | Там же |

---

## Приоритеты

### Высокий (собеседования)

1. **5.1.2** — Determinant 3×3, Covariance vs Gram, Ax=b и pseudoinverse  
2. **5.1.4** — Logistic derivatives, Hessian, chain rule, softmax gradient  
3. **5.2.1** — Bayes (chips, disease), German tank, MLE exponential  
4. **5.2.2** — Correlation, statistical significance, A/B testing  

### Средний

5. **5.1.1** — Span dimension, same basis  
6. **5.1.2** — Jacobian dim, large matrix optimization  
7. **5.2.1** — Applied problems (file storage, classifier, dating, height, weather, birthday, Vegas, consecutive heads, law of small numbers)  
8. **5.2.2** — Moments, independence vs covariance, z-score, variable correlation  

### Низкий

9. Остальные Stats (power analysis, sufficient statistics)  

---

## Рекомендуемая структура новых файлов

```
5. Math/
├── 5.1 Algebra/
│   ├── Vectors Span and Basis.md          (Q4, Q5)
│   ├── Matrices Determinant Covariance.md (Q6, Q7)
│   └── Linear Systems Pseudoinverse.md    (Q8)
├── 5.1.4 (или в Calculus)/
│   ├── Logistic Derivatives.md
│   ├── Second Order Optimization.md
│   ├── Jensen Chain Rule Softmax.md
│   └── Lagrange Constraint.md
├── 5.2 Probability/
│   └── Probability Applied Problems.md    (9,10,11-заглушка,13–24)
└── 5.2 Stats/
    ├── Moments and Correlation.md
    ├── Statistical Significance.md
    ├── Variable Correlation Tests.md
    ├── AB Testing.md
    └── Multiple Testing Sufficient Stats.md
```

---

## Итог

- **Есть:** 5.2.1 и 5.2.2 полностью покрыты (кроме задачи 11 — формулировка в веб-MLIB не найдена).  
- **Нужно добавить/расширить:** задача 11 (при наличии печатной книги), опционально — перекрёстные ссылки, численные примеры Bonferroni/AB-test.  
- **Приоритет:** 5.2 актуализирован.  
