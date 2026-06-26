from sympy import symbols, Eq, solve

x, y, z = symbols("x y z")

system_a = (
    Eq(x - y, 50),
    Eq(10 * x - 5 * y, 15),
)

system_b = (
    Eq(4 * x + 6 * y + 10 * z, 20),
    Eq(2 * x + 2 * y + 4 * z, 6),
    Eq(6 * x + 14 * y + 8 * z - 6, 0),
)

solution_a = solve(system_a, (x, y))
solution_b = solve(system_b, (x, y, z))

print(f"Решение для системы 'a':\n{solution_a}\n")
print(f"Решение для системы 'b':\n{solution_b}")
