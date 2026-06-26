import numpy as np

v = np.array([1, 2, 3, 11, 12, 13], dtype=int)
w = np.array([255, 325, 370, 110, 223, 178], dtype=int)

dot_result = np.dot(v, w)

print("Скалярное произведение векторов v и w:")
print(dot_result)
