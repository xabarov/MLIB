# Dropout и Backprop в NumPy

**Вопросы (EN)**: Implement vanilla dropout (forward + backward) in NumPy. Implement forward + backward pass for a two-layer feed-forward NN with ReLU in plain NumPy.

## Vanilla Dropout

### Forward pass

```python
import numpy as np

def dropout_forward(x, p_drop, training=True):
    """
    x       : входной тензор
    p_drop  : вероятность обнуления нейрона
    returns : (out, mask)
    """
    if not training:
        return x, None
    mask = (np.random.rand(*x.shape) > p_drop) / (1.0 - p_drop)  # inverted dropout
    return x * mask, mask
```

**Inverted dropout**: делим на \((1-p)\) в train — inference без изменений.

### Backward pass

```python
def dropout_backward(dout, mask):
    """
    dout : градиент от следующего слоя
    mask : маска из forward pass
    """
    return dout * mask
```

Нейроны, обнулённые в forward pass (`mask == 0`), получают нулевой градиент.

---

## Двухслойный FC + ReLU (forward + backward)

Сеть: \(X \xrightarrow{W_1,b_1} h_1 \xrightarrow{\text{ReLU}} a_1 \xrightarrow{W_2,b_2} \text{logits} \xrightarrow{\text{loss}}\)

```python
def relu(x):
    return np.maximum(0, x)

def relu_grad(x):
    return (x > 0).astype(float)

# ---- Forward ----
def forward(X, W1, b1, W2, b2):
    h1 = X @ W1 + b1           # (N, H)
    a1 = relu(h1)               # (N, H)
    out = a1 @ W2 + b2          # (N, C)
    cache = (X, W1, h1, a1, W2)
    return out, cache

# ---- Backward (MSE loss для простоты) ----
def backward(dout, cache):
    """
    dout  : градиент потерь по out, shape (N, C)
    cache : (X, W1, h1, a1, W2)
    """
    X, W1, h1, a1, W2 = cache

    # Слой 2
    dW2 = a1.T @ dout           # (H, C)
    db2 = dout.sum(axis=0)      # (C,)
    da1 = dout @ W2.T           # (N, H)

    # ReLU
    dh1 = da1 * relu_grad(h1)   # (N, H)

    # Слой 1
    dW1 = X.T @ dh1             # (D, H)
    db1 = dh1.sum(axis=0)       # (H,)
    dX  = dh1 @ W1.T            # (N, D)

    return dX, dW1, db1, dW2, db2
```

### Ключевые моменты

- Backprop — цепное правило: градиент «проходит» через каждую операцию в обратном порядке.
- ReLU: производная 1 при x > 0, иначе 0 → маска из forward.
- Bias gradient: сумма по батчу (`axis=0`).
- Инициализация: Xavier (`np.random.randn * sqrt(1/fan_in)`) или He (`* sqrt(2/fan_in)`) для ReLU.

---
*Источник: [MLIB](https://huyenchip.com/ml-interviews-book/)*
