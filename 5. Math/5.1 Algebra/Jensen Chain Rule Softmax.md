# Неравенство Йенсена, правило цепи и градиент softmax+cross-entropy

**Вопрос (EN)**: Explain Jensen's inequality. Explain the chain rule. Let L = crossentropy(softmax(x), y), y one-hot. Find ∂L/∂x.

## Ответ

### Неравенство Йенсена

Для выпуклой функции \(f\) и случайной величины \(X\):
\[
f(\mathbb{E}[X]) \leq \mathbb{E}[f(X)]
\]
Для вогнутой — знак обратный. Равенство при линейной \(f\) или при вырожденном \(X\). Используется в EM, вариационном выводе и оценке нижней границы правдоподобия.

### Правило цепи

\((f \circ g)'(x) = f'(g(x)) \cdot g'(x)\). Для нескольких переменных: \(\frac{\partial z}{\partial x} = \frac{\partial z}{\partial y} \frac{\partial y}{\partial x}\). В backprop градиенты идут от выхода к входу по цепочке вычислений.

### ∂L/∂x для L = crossentropy(softmax(x), y)

\(p = \text{softmax}(x)\), \(p_j = e^{x_j} / \sum_k e^{x_k}\). \(L = -\sum_j y_j \log p_j\) (y — one-hot, \(y_c = 1\) для истинного класса c).

Известно: \(\frac{\partial L}{\partial p_j} = -y_j/p_j\). И \(\frac{\partial p_j}{\partial x_i} = p_i(1-p_i)\) при \(i=j\) и \(-p_i p_j\) при \(i \neq j\).

Комбинируя: \(\frac{\partial L}{\partial x_i} = p_i - y_i\). В векторном виде:
\[
\frac{\partial L}{\partial x} = p - y = \text{softmax}(x) - y
\]

---
*Источник: [MLIB](https://huyenchip.com/ml-interviews-book/)*
