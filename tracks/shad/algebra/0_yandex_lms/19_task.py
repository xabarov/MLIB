import numpy as np

A = np.array(
    [
        [10, 2, 5, 4],
        [2, 3, 7, 10],
        [5, 4, 0, 1],
        [1, 10, 7, 3],
    ],
    dtype=float,
)

eigenvalues, eigenvectors = np.linalg.eig(A)

eigenvalues_sum = int(round(np.sum(eigenvalues).real))
first_eigenvector_length = int(round(np.linalg.norm(eigenvectors[:, 0]).real))

print("Сумма собственных значений:")
print(eigenvalues_sum)
print()
print("Длина первого собственного вектора:")
print(first_eigenvector_length)
