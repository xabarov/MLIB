import numpy as np

A = np.array(
    [
        [2, 4, 8],
        [1, 3, 6],
        [8, 0, 1],
    ],
    dtype=float,
)

eigenvalues, C = np.linalg.eig(A)
D3 = np.diag(eigenvalues**3)
A3 = C @ D3 @ np.linalg.inv(C)

elements_sum = int(round(np.sum(A3).real))

print("Сумма элементов матрицы A^3:")
print(elements_sum)
