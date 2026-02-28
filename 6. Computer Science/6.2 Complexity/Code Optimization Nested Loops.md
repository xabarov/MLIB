# Векторизация вложенных циклов

**Вопрос (EN)**: Given the code snippet (nested loops over 3D volume, computing distance to ROI). What might be a problem? How would you improve it?

## Ответ

### Проблема

Три вложенных цикла по x, y, z — O(n³) итераций в Python; каждый вызов `within_radius` и `np.linalg.norm` даёт большой оверхед. На чистом Python это очень медленно.

### Идеи улучшения

1. **Векторизация через meshgrid:**
```python
x = np.arange(volume.shape[0])
y = np.arange(volume.shape[1])
z = np.arange(volume.shape[2])
xx, yy, zz = np.meshgrid(x, y, z, indexing='ij')
coords = np.stack([xx, yy, zz], axis=-1)
distances = np.linalg.norm(coords - roi, axis=-1)
mask = (distances < radius).astype(np.float32)
```

2. **Broadcasting** — вместо meshgrid можно использовать `np.arange` с `np.newaxis` и broadcasting при вычитании с `roi`.

3. **scipy.ndimage** — `distance_transform_edt` или подобные функции для расстояний.

4. **Numba/Cython** — если нужен поэлементный цикл, JIT-компиляция даст ускорение на порядки.

5. **GPU (CuPy, PyTorch)** — для очень больших объёмов перенос на GPU.

---
*Источник: [MLIB](https://huyenchip.com/ml-interviews-book/)*
