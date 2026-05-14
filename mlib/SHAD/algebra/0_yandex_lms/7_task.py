import numpy as np

doc = np.array([3, -1, 4, 2, 2], dtype=float)
style = np.array([2, 1, -1, 3, 2], dtype=float)


def projection(v, onto):
    return (np.dot(v, onto) / np.dot(onto, onto)) * onto


proj = projection(doc, style)
orth = doc - proj

print("Проекция doc на style:")
print(proj)
print("Ортогональная составляющая:")
print(orth)

print("\nВариант для проекции: 4")
print("Вариант для ортогональной составляющей: 1")
