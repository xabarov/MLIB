from sympy import Matrix

matrix_a = Matrix([
    [8, 10, 5, 7, 0],
    [2, 0, 6, 5, 1],
    [1, 8, 10, 2, 0],
    [10, 0, 0, 3, 1],
    [4, 1, 3, 5, 7],
])

matrix_b = Matrix([
    [20, 10, 30, 60],
    [5, 10, 18, 0],
    [40, 7, 25, 2],
])

rref_a = matrix_a.rref()[0]
rref_b = matrix_b.rref()[0]

print(f"Приведенная ступенчатая форма для матрицы 'A':\n{rref_a}\n")
print(f"Приведенная ступенчатая форма для матрицы 'B':\n{rref_b}")

