import numpy as np

a = np.array([1, 1, 1, 0, 1, 0, 1, 0, 0, 0], dtype=float)
b = np.array([0, 1, 0, 1, 1, 0, 0, 0, 1, 0], dtype=float)

cosine_similarity = np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

print("Косинусное сходство векторов a и b:")
print(cosine_similarity)
