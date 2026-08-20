import numpy as np

A = np.array(
    [
        [20, 15, 30, 40],
        [40, 45, 10, 0],
        [70, 10, 50, 25],
    ],
    dtype=int,
)

B = np.array(
    [
        [1, 5, 10, 3, 2],
        [5, 4, 2, 0, 1],
        [10, 8, 4, 5, 8],
        [5, 0, 2, 7, 12],
    ],
    dtype=int,
)

C = np.dot(A, B)
sum_of_elements = np.sum(C)

print("Сумма элементов матрицы C:")
print(sum_of_elements)
