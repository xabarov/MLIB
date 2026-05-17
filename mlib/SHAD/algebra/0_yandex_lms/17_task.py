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

inverse_B = np.linalg.inv(B)
first_row_sum = round(np.sum(inverse_B[0]), 2)

print("Сумма элементов первой строки обратной матрицы B:")
print(first_row_sum)
