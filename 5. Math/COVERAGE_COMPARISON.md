# Сверка покрытия ответов главы 5. Math с MLIB

Сравнение с [huyenchip.com/ml-interviews-book](https://huyenchip.com/ml-interviews-book/) по состоянию на февраль 2025.

---

## 5.1.1 Vectors (Векторы)

| Вопрос в книге | Локальный файл | Статус |
|----------------|----------------|--------|
| Unit vector v maximizing u·v | `Vectors Dot Product.md` | ✅ |
| Geometric interpretation of dot product | `Vectors Dot Product.md` | ✅ |
| Outer product a=[3,2,1], b=[-1,0,1] | `Vectors Outer Product.md` | ✅ |
| Example of outer product in ML | `Vectors Outer Product.md` | ✅ |
| Linear independence | `Linear Independence and Norms.md` | ✅ |
| Norm vs metric, make metric from norm | `Linear Independence and Norms.md` | ✅ |
| L0, L1, L2, L∞ norms | `Linear Independence and Norms.md` | ✅ |
| Same basis for sets A and B | `Vectors Span and Basis.md` | ✅ |
| Dimension of span of n vectors | `Vectors Span and Basis.md` | ✅ |

**Итог:** Полное покрытие.

---

## 5.1.2 Matrices (Матрицы)

| Вопрос в книге | Локальный файл | Статус |
|----------------|----------------|--------|
| 3×3 matrix determinant (without formula) | `Matrices Determinant Covariance.md` | ✅ |
| Covariance A^TA vs Gram AA^T | `Matrices Determinant Covariance.md` | ✅ |
| Ax=b: find x, unique solution | `Linear Systems Pseudoinverse.md` | ✅ |
| Multiple solutions when cols > rows | `Linear Systems Pseudoinverse.md` | ✅ |
| Pseudoinverse, solve when A no inverse | `Linear Systems Pseudoinverse.md` | ✅ |
| Derivative, gradient, Jacobian | `Matrices Linear Transformations.md` (частично), `Jacobian and Rayleigh Quotient.md` | ✅ |
| Jacobian ∂y/∂x for y=xw | `Jacobian and Rayleigh Quotient.md` | ✅ |
| Large matrix: minimize x^TAx, unit x | `Jacobian and Rayleigh Quotient.md` (Rayleigh) | ✅ |

**Примечание:** В книге на странице 5.1.2 нет явного вопроса про 4×4 eigenvalues → trace, det — это доп. материал в локальной версии.

**Итог:** Полное покрытие вопросов из веб-версии.

---

## 5.1.3 Dimensionality Reduction

| Вопрос в книге | Локальный файл | Статус |
|----------------|----------------|--------|
| When eigendecomposition vs SVD | `Dimensionality Reduction PCA.md` | ✅ |
| PCA and SVD relationship | `Dimensionality Reduction PCA.md` | ✅ |
| t-SNE: how it works, why needed | `Dimensionality Reduction PCA.md` | ✅ |

**Итог:** Полное покрытие.

---

## 5.1.4 Calculus and Convex Optimization

| Вопрос в книге | Локальный файл | Статус |
|----------------|----------------|--------|
| Non-differentiable functions, backprop (ReLU) | `Calculus Convexity.md` | ✅ |
| Convexity: definition, desirable | `Calculus Convexity.md` | ✅ |
| Cross-entropy convex | `Calculus Convexity.md` | ✅ |
| Logistic: p(y=-1), gradient, convexity | `Logistic Regression Derivatives.md` | ✅ |
| Second-order derivatives: pros/cons, why not common | `Second Order Optimization.md` | ✅ |
| Hessian for critical points | `Hessian Critical Points Lagrange.md` | ✅ |
| Jensen's inequality | `Jensen Chain Rule Softmax.md` | ✅ |
| Chain rule | `Jensen Chain Rule Softmax.md` | ✅ |
| ∂L/∂x for L=crossentropy(softmax(x), y) | `Jensen Chain Rule Softmax.md` | ✅ |
| f(x,y)=4x²-y, constraint x²+y²=1 | `Hessian Critical Points Lagrange.md` | ✅ |

**Итог:** Полное покрытие.

---

## 5.2.1 Probability

### 5.2.1.1 Basic concepts to review

| Тема в книге | Локальный файл | Статус |
|--------------|----------------|--------|
| Random variable, distributions | `Probability Basics.md` | ✅ |
| Normal, Binomial, Poisson, Geometric, Beta | `Probability Basics.md` | ✅ |
| Marginal, joint, conditional | `Bayes and Conditional.md` | ✅ |
| Bayes, t-dist, transform to normal | `Bayes and Conditional.md` | ✅ |

### 5.2.1.2 Questions (прикладные задачи)

| # | Вопрос в книге | Локальный файл | Статус |
|---|----------------|----------------|--------|
| 9 | File storage: 5 crashes/year | `Probability Applied Problems.md` | ✅ |
| 10 | Classifier 10 wrong/100 | `Probability Applied Problems.md` | ✅ |
| 11 | — | — | ⚠️ Формулировка в веб-MLIB не найдена |
| 12 | Jason two children, one boy | `Bayes and Conditional.md` | ✅ |
| 13 | Chip manufacturers A/B | `Probability Applied Problems.md` | ✅ |
| 14 | Rare disease, two tests positive | `Probability Applied Problems.md` | ✅ |
| 15 | Dating site: 10/50 adjectives, match ≥5 | `Probability Applied Problems.md` | ✅ |
| 16 | Height: mix male/female Gaussians | `Probability Applied Problems.md` | ✅ |
| 17 | Weather apps: foggy SF | `Probability Applied Problems.md` | ✅ |
| 18 | German tank problem | `Probability Applied Problems.md` | ✅ |
| 19 | Expected days X>0.5 from N(0,1) | `Probability Applied Problems.md` | ✅ |
| 20 | Birthday class size | `Probability Applied Problems.md` | ✅ |
| 21 | Vegas betting (Martingale) | `Probability Applied Problems.md` | ✅ |
| 22 | Expected flips for HH | `Probability Applied Problems.md` | ✅ |
| 23 | Law of small numbers (kidney) | `Probability Applied Problems.md` | ✅ |
| 24 | MLE for exponential | `Probability Applied Problems.md` | ✅ |

**Исключение:** Задача 11 — в веб-версии [5.2.1.2](https://huyenchip.com/ml-interviews-book/contents/5.2.1.2-questions.html) отображаются не все задачи; нумерация может отличаться от полной версии книги.

---

## 5.2.2 Stats

| Вопрос в книге | Локальный файл | Статус |
|----------------|----------------|--------|
| Frequentist vs Bayesian | `Frequentist vs Bayesian.md` | ✅ |
| Mean, median, variance [1,5,3,2,4,4] | `Mean Median Variance.md` | ✅ |
| When median vs mean | `Mean Median Variance.md` | ✅ |
| Moments (zeroth to fourth) | `Moments and Correlation.md` | ✅ |
| Independence vs zero covariance | `Moments and Correlation.md` | ✅ |
| CI puppies: which statement true | `Confidence Intervals.md` | ✅ |
| Unbiased estimate of median | `Estimation and Inference.md` | ✅ |
| Correlation > 1? Interpret 0.3 | `Moments and Correlation.md` | ✅ |
| Z-score, top 10%, skew | `Z-score and Skew.md` | ✅ |
| Coin: 10H 5T ( binomial, chi-squared ) | `Estimation and Inference.md` | ✅ |
| Statistical significance, p-value, war on significance | `Statistical Significance.md` | ✅ |
| Variable correlation: continuous, categorical, multicollinearity | `Variable Correlation Tests.md` | ✅ |
| 10K stocks, spurious correlation | `Multiple Testing Sufficient Stats.md` | ✅ |
| How to avoid accidental patterns | `Multiple Testing Sufficient Stats.md` | ✅ |
| Sufficient statistics, Information Bottleneck | `Multiple Testing Sufficient Stats.md` | ✅ |
| A/B testing pros/cons | `AB Testing and Power.md` | ✅ |
| Ad placement: sample size | `AB Testing and Power.md` | ✅ |
| Double ads for revenue | `AB Testing and Power.md` | ✅ |

**Примечание:** В веб-версии [5.2.2 Stats](https://huyenchip.com/ml-interviews-book/contents/5.2.2-stats.html) отображаются не все подвопросы (e.g. power analysis, unbiased median) — они могут быть в других разделах или полной печатной версии.

**Итог:** Полное покрытие вопросов из веб-версии и расширенное покрытие из `PLAN_IMPROVEMENTS.md`.

---

## Резюме

| Раздел | Покрытие | Пропуски |
|--------|----------|----------|
| 5.1.1 Vectors | 100% | — |
| 5.1.2 Matrices | 100% | — |
| 5.1.3 Dimensionality | 100% | — |
| 5.1.4 Calculus | 100% | — |
| 5.2.1 Probability | ~97% | Задача 11 (формулировка не найдена в веб-MLIB) |
| 5.2.2 Stats | 100% | — |

**Общий вывод:** Покрытие ответов в локальной версии MLIB по главе 5 Math соответствует веб-версии книги. Единственная неочевидность — задача 11 в 5.2.1.2, которую в веб-MLIB не удалось однозначно идентифицировать.

---

*Источники: [MLIB](https://huyenchip.com/ml-interviews-book/), локальные файлы в `5. Math/`*
