import numpy as np

A = np.array(
    [
        [0, 1, 0, 1],
        [1, 0, 1, 1],
        [0, 1, 0, 1],
        [1, 1, 1, 0],
    ],
    dtype=int,
)

A_cubed = np.linalg.matrix_power(A, 3)
A_fourth = np.linalg.matrix_power(A, 4)
paths_count_3 = A_cubed[0, 2]
paths_count_4 = A_fourth[0, 2]

print("Матрица A^3:")
print(A_cubed)
print("Число путей длины 3 из v1 в v3:")
print(paths_count_3)
print("Правильный ответ: 2")
print()
print("Матрица A^4:")
print(A_fourth)
print("Число путей длины 4 из v1 в v3:")
print(paths_count_4)
print("Правильный ответ для второй задачи: 10")
