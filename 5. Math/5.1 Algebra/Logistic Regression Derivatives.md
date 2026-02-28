# Производные логистической регрессии

**Вопрос (EN)**: Logistic discriminant: p(y=1|x)=σ(w^Tx). Show p(y=-1|x)=σ(-w^Tx). Show ∇_w L = -y_i(1-p(y_i|x_i))x_i. Show the gradient is convex.

## Ответ

### Обозначения

\(\sigma(z) = (1 + e^{-z})^{-1}\), \(L(y_i, x_i; w) = -\log p(y_i | x_i)\).

### p(y=-1|x) = σ(-w^Tx)

При бинарной классификации \(p(y=1|x) + p(y=-1|x) = 1\). Значит \(p(y=-1|x) = 1 - \sigma(w^Tx) = 1 - \frac{1}{1+e^{-w^Tx}} = \frac{e^{-w^Tx}}{1+e^{-w^Tx}} = \frac{1}{1+e^{w^Tx}} = \sigma(-w^Tx)\).

### Градиент ∇_w L

Используем \(y \in \{-1, 1\}\). Тогда \(p(y|x) = \sigma(y \cdot w^Tx)\) (при y=1: σ(w^Tx); при y=-1: σ(-w^Tx)).

\(L = -\log \sigma(y w^Tx)\). Производная \(\sigma'(z) = \sigma(z)(1-\sigma(z))\). По правилу цепи:
\[
\nabla_w L = -\frac{1}{\sigma(y w^Tx)} \sigma'(y w^Tx) \cdot y \cdot x_i = -\sigma(y w^Tx)(1-\sigma(y w^Tx)) \cdot y \cdot x_i / \sigma(y w^Tx) = -(1-p(y_i|x_i)) y_i x_i.
\]

(При \(y_i=1\): \(p(y_i|x_i)=\sigma(w^Tx)\), градиент \(-(1-p)x\); при \(y_i=-1\): \(p=\sigma(-w^Tx)\), получаем тот же вид.)

### Выпуклость градиента (и функции потерь)

Гессиан \(H = \nabla_w^2 L\). Для логистической потери каждый член суммы даёт вклад вида \(p(1-p) x_i x_i^T\) — положительно полуопределённую матрицу. Сумма таких матриц тоже положительно полуопределена → функция потерь выпукла по \(w\).

---
*Источник: [MLIB](https://huyenchip.com/ml-interviews-book/)*
