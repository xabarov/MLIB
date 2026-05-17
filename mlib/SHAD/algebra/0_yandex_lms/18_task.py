import numpy as np

B = np.array(
    [
        [50, 10, 70, 80],
        [10, 5, 50, 10],
        [20, 0, 10, 20],
        [30, 40, 80, 90],
    ],
    dtype=float,
)

determinant = int(round(np.linalg.det(B)))

print("Определитель матрицы B:")
print(determinant)
