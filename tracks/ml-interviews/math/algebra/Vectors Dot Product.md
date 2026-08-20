# Скалярное произведение векторов

**Вопрос (EN)**: What's the geometric interpretation of the dot product? Given vector u, find unit vector v such that dot product u·v is maximum.

## Ответ

### Геометрическая интерпретация

\[
u \cdot v = \|u\| \|v\| \cos\theta
\]

Скалярное произведение — произведение длин векторов на косинус угла между ними. Оно максимально при \(\theta=0\) (векторы сонаправлены) и равно нулю при \(\theta=90°\) (ортогональность).

### Единичный вектор v, максимизирующий u·v

При \(\|v\|=1\):
\[
u \cdot v = \|u\| \cos\theta
\]
Максимум при \(\cos\theta = 1\), то есть когда \(v\) сонаправлен с \(u\):
\[
v = \frac{u}{\|u\|}
\]

---
*Источник: [MLIB](https://huyenchip.com/ml-interviews-book/)*
