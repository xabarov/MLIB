import numpy as np

A = np.array(
    [
        [0, 0, 1, 1, 1, 0],
        [0, 0, 0, 1, 1, 0],
        [1, 0, 0, 0, 1, 1],
        [1, 1, 0, 0, 0, 0],
        [1, 1, 1, 0, 0, 1],
        [0, 0, 1, 0, 1, 0],
    ],
    dtype=int,
)

A_cubed = np.linalg.matrix_power(A, 3)
paths_count = A_cubed[5, 3]

print("Число путей длины 3 от Технологического института до Маяковской:")
print(paths_count)
