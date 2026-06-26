# Точность вычислений и численные приёмы

**Вопрос (EN)**: Benefits and problems of reducing model precision? How to solve? How to compute average of 1M floats with minimal precision loss? How to implement batch normalization when batch is spread across GPUs?

## Ответ

### Снижение точности (FP16/BF16)

**Плюсы:**
- Меньше памяти (в 2 раза при переходе с FP32).
- Быстрее вычисления на соответствующих ускорителях.
- Больше моделей или батчей в память.

**Проблемы:**
- Overflow/underflow — малый диапазон FP16.
- Потеря точности при малых градиентах.
- Нестабильность при сложении многих малых чисел.

**Решения:**
- **Mixed precision** — критические части (loss scaling, обновление весов) в FP32.
- **Loss scaling** — умножение loss перед backward, деление градиентов после.
- **BF16** — тот же экспонентный диапазон, что у FP32; меньше precision, реже overflow.

### Среднее 1M float с минимальной потерей точности

- **Kahan summation** — компенсация ошибки округления при последовательном сложении.
- **Pairwise (cascade) summation** — попарное сложение: (a+b)+(c+d)+…; уменьшает накопление ошибки по сравнению с последовательным суммированием.
- **numpy.mean** использует pairwise; для своих реализаций — Kahan или divide-and-conquer.

### Batch norm при батче на нескольких GPU

Батч разбит по GPU — на каждой считается свой μ и σ². Это не эквивалентно одному глобальному BatchNorm.

**Варианты:**
1. **SyncBatchNorm** — AllReduce для μ и σ² по всем GPU; на каждой GPU одинаковые нормализующие статистики.
2. **LayerNorm** — статистики по признакам внутри примера; не зависят от батча, нет проблемы при multi-GPU.
3. **GroupNorm** — компромисс; группы каналов.

---
*Источник: [MLIB](https://huyenchip.com/ml-interviews-book/)*
