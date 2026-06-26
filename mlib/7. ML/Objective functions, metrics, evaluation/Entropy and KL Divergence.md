# Энтропия и измерение близости распределений

**Вопрос (EN)**: Alphabet of 27 characters — maximal entropy? How do we measure how close learned distribution Q is to data distribution P?

## Ответ

### Интуиция энтропии

Энтропия измеряет «разброс» или разнообразие распределения. Чем равномернее распределение, тем выше энтропия и тем сложнее угадать случайный исход. При полной определённости (один исход с вероятностью 1) энтропия равна нулю.

### Максимальная энтропия для 27 символов

При равномерном распределении:
\[
H_{\max} = \log_2(27) \approx 4.75 \text{ бит}
\]

### Метрики близости P и Q

1. **KL Divergence** (Kullback-Leibler):
   \[
   D_{KL}(P \| Q) = \sum_x P(x) \log \frac{P(x)}{Q(x)}
   \]
   Несимметрична; \(D_{KL}(P\|Q) \geq 0\), равенство только при \(P=Q\).

2. **JS Divergence** (Jensen-Shannon) — симметричный вариант на основе KL.

3. **Cross-Entropy** — \(H(P,Q) = -\sum P(x)\log Q(x)\); минимизация cross-entropy эквивалентна минимизации KL при фиксированной P.

4. **Wasserstein distance** — метрика для непрерывных распределений; устойчива при непересекающихся носителях.

5. **MMD** (Maximum Mean Discrepancy) — сравнение в RKHS.

---
*Источник: [MLIB](https://huyenchip.com/ml-interviews-book/)*
