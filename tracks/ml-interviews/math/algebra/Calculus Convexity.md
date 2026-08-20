# Исчисление и выпуклость

**Вопрос (EN)**: What does differentiable mean? Example of non-differentiable function? Non-differentiable in ML (ReLU) and backprop? Convexity? Why desirable? Show cross-entropy is convex. Derivative vs gradient vs Jacobian?

## Ответ

### Дифференцируемость

Функция дифференцируема в точке, если существует производная (предел разностного отношения). Пример недифференцируемой точки: \(f(x)=|x|\) в \(x=0\) (угол).

### ReLU и backprop

ReLU: \(f(x)=\max(0,x)\) — в 0 производная не определена. Обычно полагают \(f'(0)=0\) или 1. Subgradient: \([0,1]\) в 0. Backprop передаёт 0 или градиент от следующего слоя в зависимости от выбранной конвенции.

### Выпуклость

Выпуклая функция: отрезок между любыми двумя точками графика лежит не ниже графика. Выпуклость упрощает оптимизацию: локальный минимум — глобальный; градиентный спуск сходится к нему.

### Cross-entropy выпукла

\(L(p) = -\sum y_i \log p_i\) при фиксированных \(y\). Вторые производные по \(p\) неотрицательны; гессиан положительно полуопределён — функция выпукла по \(p\).

### Derivative, Gradient, Jacobian

- **Derivative** — скалярная производная (одномерный случай).
- **Gradient** — вектор частных производных \(\nabla f = (\partial f/\partial x_1, \ldots)\).
- **Jacobian** — матрица частных производных для \(f: \mathbb{R}^n \to \mathbb{R}^m\); строка \(i\) — градиент \(f_i\).

---
*Источник: [MLIB](https://huyenchip.com/ml-interviews-book/)*
