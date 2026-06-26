# Gradient Descent и оптимизаторы

**Вопросы (EN)**: Vanilla gradient update? GD vs SGD vs mini-batch? Overfit or underfit first? Why epochs instead of sampling with replacement? Weight decay?

## Ответ

### Vanilla gradient update

\[
w_{t+1} = w_t - \eta \nabla_w L(w_t)
\]

### GD vs SGD vs mini-batch

- **GD** — на полном датасете; стабильные градиенты, медленно; O(n) на итерацию.
- **SGD** — один пример; быстрые итерации, большой шум; O(1).
- **Mini-batch** — компромисс; баланс скорости и шума; типичный выбор.

### Overfit или underfit сначала

Сначала добиться overfitting на небольшом подмножестве. Это подтверждает, что модель в принципе способна выучить задачу. Затем добавляют регуляризацию и данные.

### Эпохи vs sampling with replacement

Эпохи (без возвращения) обеспечивают, что каждая точка используется примерно одинаково часто; с заменой некоторые точки могут повторяться чаще. Эпохи дают более однородное покрытие данных.

### Weight decay

После обновления веса умножают на (1 − λ): \(w \leftarrow w(1-\lambda) - \eta \nabla L\). Эквивалент L2-регуляризации при определённых условиях. Ограничивает рост весов.

---
*Источник: [MLIB](https://huyenchip.com/ml-interviews-book/)*
