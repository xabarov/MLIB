# Якобиан и минимизация x^TAx

**Вопрос (EN)**: Weights w∈R^{d×m}, mini-batch x∈R^{n×d}, output y=xw∈R^{n×m}. What's the dimension of Jacobian ∂y/∂x? Large symmetric A, can compute Ax quickly. Find unit vector x minimizing x^TAx.

## Ответ

### Размерность ∂y/∂x

\(y = xw\), где \(x \in \mathbb{R}^{n \times d}\), \(w \in \mathbb{R}^{d \times m}\), \(y \in \mathbb{R}^{n \times m}\).

\(\frac{\partial y}{\partial x}\) — якобиан отображения \(\mathbb{R}^{nd} \to \mathbb{R}^{nm}\). Размерность: **nm × nd** (или в виде тензора: для каждого элемента \(y_{ij}\) — градиент по всем \(x_{kl}\)). На практике в backprop вычисляют \(\frac{\partial L}{\partial x} = \frac{\partial L}{\partial y} w^T\), что даёт матрицу размером \(n \times d\).

### Минимизация x^TAx при ||x||=1

Задача: \(\min_{\|x\|=1} x^TAx\). Это **квадратичная форма Рэлея**. Минимум достигается на собственном векторе, соответствующем **наименьшему собственному значению** \(\lambda_{\min}\).

При невозможности явно найти собственные векторы:

1. **Gradient descent на сфере**: градиент \(\nabla(x^TAx) = 2Ax\); шаг \(x \leftarrow x - \eta \cdot 2Ax\), затем нормализация \(x \leftarrow x/\|x\|\).
2. **Power iteration** для наименьшего собственного значения: для \(B = \lambda_{\max} I - A\) максимум \(x^TBx\) соответствует минимуму \(x^TAx\); итерации \(x \leftarrow Bx / \|Bx\|\).

Использование только \(f(x)=Ax\): можно итерировать \(x \leftarrow x - \eta Ax\) и нормализовать; при малом \(\eta\) сходимость к направлению минимального собственного вектора.

---
*Источник: [MLIB](https://huyenchip.com/ml-interviews-book/)*
