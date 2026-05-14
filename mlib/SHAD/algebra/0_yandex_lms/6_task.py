import numpy as np

joy = np.array([2, 1, 3], dtype=float)
sadness = np.array([1, 2, 1], dtype=float)
anger = np.array([3, 0, 2], dtype=float)


def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


sim_joy_sadness = cosine_similarity(joy, sadness)
sim_joy_anger = cosine_similarity(joy, anger)
sim_sadness_anger = cosine_similarity(sadness, anger)

print(f"similarity(радость, грусть) ≈ {sim_joy_sadness:.4f}")
print(f"similarity(радость, злость) ≈ {sim_joy_anger:.4f}")
print(f"similarity(грусть, злость) ≈ {sim_sadness_anger:.4f}")


