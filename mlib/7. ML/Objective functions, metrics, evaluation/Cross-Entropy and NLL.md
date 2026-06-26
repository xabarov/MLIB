# Cross-Entropy и Negative Log-Likelihood

**Вопрос (EN)**: Show that negative log-likelihood and cross-entropy are the same for binary classification. Why is cross-entropy better than MSE for multiclass (e.g. MNIST)?

## Ответ

### NLL = Cross-Entropy для бинарной классификации

Для одного примера с меткой \(y \in \{0,1\}\) и предсказанием \(p = P(y=1|x)\):

\[
\text{NLL} = -\log p(y|x) = -\left[ y \log p + (1-y) \log(1-p) \right]
\]

Это и есть binary cross-entropy между истинным распределением и предсказанием.

### Почему Cross-Entropy лучше MSE для multiclass

1. **Выпуклость** — cross-entropy выпукла по logits; MSE для softmax — нет.
2. **Градиенты** — cross-entropy даёт информативные градиенты; MSE при softmax приводит к затуханию градиентов и медленному обучению.
3. **Вероятностная интерпретация** — cross-entropy соответствует максимизации правдоподобия.
4. **Практика** — cross-entropy стандартно используется в задачах классификации и даёт лучшую сходимость.

---
*Источник: [MLIB](https://huyenchip.com/ml-interviews-book/)*
