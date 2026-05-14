import cmath

# Пример: можно подставить любое n >= 3
n = 7

# Вершины единичной окружности: exp(2*pi*i*k/n), k=0..n-1
vector_sum = sum(cmath.exp(2j * cmath.pi * k / n) for k in range(n))

# Из-за вычислений с плавающей точкой может быть очень малый шум.
eps = 1e-12
x = 0.0 if abs(vector_sum.real) < eps else vector_sum.real
y = 0.0 if abs(vector_sum.imag) < eps else vector_sum.imag

print((x, y))  # (0.0, 0.0) -> нулевой вектор
