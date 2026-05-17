import numpy as np

coefficients = np.array(
    [
        [1, 2, 3],
        [2, 5, 7],
        [3, 7, 10],
    ],
    dtype=float,
)

determinant = np.linalg.det(coefficients)

if np.isclose(determinant, 0.0):
    print("Матрица необратима")
else:
    inverse_matrix = np.linalg.inv(coefficients)
    print("Элемент в первой строке и первом столбце обратной матрицы:")
    print(inverse_matrix[0, 0])
