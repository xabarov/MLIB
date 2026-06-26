import numpy as np

prepared = np.array([80, 65, 100, 90, 40], dtype=float)
exacting = np.array([70, 45, 85, 100, 50], dtype=float)
responsive = np.array([60, 30, 95, 55, 65], dtype=float)
tedious = np.array([10, 0, 15, 5, 10], dtype=float)

quality_index = (
    0.45 * prepared
    + 0.3 * exacting
    + 0.35 * responsive
    - 0.3 * tedious
)

mean_quality_index = int(round(np.mean(quality_index)))

print("Среднее значение индекса качества:")
print(mean_quality_index)
