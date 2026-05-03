# F1 при дисбалансе: крайние случаи

**Вопрос (EN)**: 99% class A, 1% class B. If model predicts A 100% of the time, what is F1? If model predicts uniformly at random, expected F1?

## Ответ

### Модель всегда предсказывает A

**Если положительный класс — B (1%):**  
- TP=0, FN = все B, FP=0  
- Precision = 0/0 (undefined) → 0, Recall = 0  
- **F1 = 0**

**Если положительный класс — A (99%):**  
- TP = все A, FN=0, FP=0  
- Precision = 1, Recall = 1  
- **F1 = 1**

Результат зависит от того, какой класс выбран положительным.

### Случайные предсказания (uniform, 50/50)

Допустим, модель предсказывает каждый объект как B с вероятностью 0.5 независимо.  
Пусть N примеров: 0.99N класса A, 0.01N класса B.

**Для B как позитивного класса:**

| | Predicted B | Predicted A |
|---|---|---|
| **True B** | E[TP] = 0.5 × 0.01N | E[FN] = 0.5 × 0.01N |
| **True A** | E[FP] = 0.5 × 0.99N | E[TN] = 0.5 × 0.99N |

\[
\text{Precision}_B = \frac{0.005N}{0.005N + 0.495N} = \frac{0.005}{0.5} = 0.01
\]
\[
\text{Recall}_B = \frac{0.005N}{0.005N + 0.005N} = 0.5
\]
\[
F1_B = \frac{2 \times 0.01 \times 0.5}{0.01 + 0.5} = \frac{0.01}{0.51} \approx \mathbf{0.0196 \approx 2\%}
\]

Общая формула: \(F1_B = \dfrac{p_B}{p_B + 0.5}\), где \(p_B\) — доля класса B.  
При \(p_B = 0.01\): \(F1_B = 0.01/0.51 \approx 0.02\).

**Для A как позитивного класса:**

\[
\text{Precision}_A = 0.99, \quad \text{Recall}_A = 0.5, \quad F1_A \approx 0.66
\]

**Macro F1** = (F1_A + F1_B) / 2 = (0.66 + 0.02) / 2 ≈ **0.34**

**Micro F1** = Accuracy = 0.5 (при равномерном угадывании).

### Вывод

При дисбалансе 99/1 и uniform random prediction:
- F1 для редкого класса B ≈ **2%** — крайне низкий.
- Macro F1 ≈ **34%** (доминирует мажоритарный класс).
- Micro F1 = **50%** (= accuracy при равномерном угадывании).

---
*Источник: [MLIB](https://huyenchip.com/ml-interviews-book/)*
