from sympy import symbols, Eq, solve

x, y = symbols("x y")

eq1 = Eq(3 * x - 28, 2)
eq2 = Eq(20 * y + 5, -55)

solution_x = solve(eq1, x)
solution_y = solve(eq2, y)

print(f"Решение для уравнения 'a':\n{solution_x}\n")
print(f"Решение для уравнения 'b':\n{solution_y}")

