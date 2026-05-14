from sympy import symbols, Eq, solve


x, y, z = symbols('x y z') # определяем символьные переменные

eq1 = Eq(x + y + z, 6) # определяем уравнение
eq2 = Eq(2*x - y + z, 3) # определяем уравнение
eq3 = Eq(x + 2*y - z, 3) # определяем уравнение

solution = solve((eq1, eq2, eq3), (x, y, z)) # решаем систему уравнений

print(solution) # выводим решение