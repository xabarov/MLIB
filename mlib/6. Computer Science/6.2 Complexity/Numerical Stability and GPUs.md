# Численная стабильность и GPU/TPU

**Вопрос (EN)**: Causes of numerical instability in DL? Purpose of ε in batch norm? What made GPUs popular? How compare to TPUs?

## Ответ

### Численная нестабильность

- **Overflow/underflow** — слишком большие/малые числа; выход за пределы float32/float16.
- **Vanishing/exploding gradients** — произведение многих матриц Якоби.
- **Catastrophic cancellation** — вычитание близких чисел; потеря значащих разрядов.
- **Ill-conditioning** — большие числа обусловленности матриц.

### ε в Batch Norm

Добавляется в знаменатель: \(\frac{x - \mu}{\sqrt{\sigma^2 + \varepsilon}}\). Защищает от деления на ноль при нулевой дисперсии и улучшает численную стабильность.

### GPU для DL

- Массовый параллелизм (тысячи ядер) для матричных операций.
- Высокая пропускная способность памяти.
- CUDA/cuDNN и экосистема для нейросетей.
- Эффективность для обучения на больших батчах.

### GPU vs TPU

- **TPU** — специализированный ускоритель для матричных операций (TensorFlow); высокая throughput при inference и training; ограниченная поддержка фреймворков.
- **GPU** — универсальнее; развитая экосистема; гибкость.

---
*Источник: [MLIB](https://huyenchip.com/ml-interviews-book/)*
