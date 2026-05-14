import numpy as np

p1 = np.array([7, 4, 5, 8, 10, 3, 5], dtype=float)
p2 = np.array([8, 7, 10, 9, 9, 5, 7], dtype=float)

max_total_score = 20
max_grade = 5

final_grades = np.rint((p1 + p2) / max_total_score * max_grade)

print("Оценки студентов за самостоятельную работу:")
print(final_grades)
