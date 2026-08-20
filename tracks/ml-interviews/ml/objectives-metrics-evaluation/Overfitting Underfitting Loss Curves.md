# Кривые потерь при переобучении и недобучении

**Вопрос (EN)**: Draw the loss curves for overfitting and underfitting.

## Ответ

### Переобучение (overfitting)

- **Train loss** — продолжает уменьшаться.
- **Validation loss** — после какого-то момента растёт.
- Разрыв между train и validation loss растёт.

```
Loss
  ^
  |  Val ---\
  |         \___
  |  Train ----\____
  |                 \_____
  +-------------------------> Epochs
```

### Недобучение (underfitting)

- **Train loss** и **validation loss** высокие и близки друг к другу.
- Обе кривые почти параллельны, мало снижаются.

```
Loss
  ^
  |  Val  ----------------
  |  Train ---------------
  |
  +-------------------------> Epochs
```

### Хорошая ситуация

- Train и val loss снижаются.
- Разрыв между ними небольшой и стабильный.
- Val loss выходит на плато или растёт медленно.

---
*Источник: [MLIB](https://huyenchip.com/ml-interviews-book/)*
