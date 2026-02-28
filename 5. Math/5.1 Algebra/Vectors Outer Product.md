# Внешнее произведение векторов

**Вопрос (EN)**: Given a=[3,2,1], b=[-1,0,1]. Calculate outer product a^T b. Give ML example.

## Ответ

### Расчёт

\((a^T b)_{ij} = a_i b_j\). Поэлементно:
- Строка 1: \(3 \cdot (-1) = -3\), \(3 \cdot 0 = 0\), \(3 \cdot 1 = 3\)
- Строка 2: \(2 \cdot (-1) = -2\), \(2 \cdot 0 = 0\), \(2 \cdot 1 = 2\)
- Строка 3: \(1 \cdot (-1) = -1\), \(1 \cdot 0 = 0\), \(1 \cdot 1 = 1\)

\[
a^T b = \begin{bmatrix} 3 \\ 2 \\ 1 \end{bmatrix} \begin{bmatrix} -1 & 0 & 1 \end{bmatrix} = \begin{bmatrix} -3 & 0 & 3 \\ -2 & 0 & 2 \\ -1 & 0 & 1 \end{bmatrix}
\]

### Применение в ML

- **Attention** — attention scores как \(Q K^T\): внешнее произведение строк query и key.
- **Word embeddings** — матрица совстречаемости как сумма внешних произведений векторов слов.
- **Свёртки** — представление произведения признаков через внешнее произведение.
- **Low-rank факторизация** — \(A \approx uv^T\) как произведение двух векторов.

---
*Источник: [MLIB](https://huyenchip.com/ml-interviews-book/)*
