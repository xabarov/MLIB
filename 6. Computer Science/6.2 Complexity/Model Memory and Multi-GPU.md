# Память модели и обучение на нескольких GPU

**Вопрос (EN)**: Is knowing a model's architecture and hyperparameters enough to calculate memory requirements? Your model works fine on a single GPU but gives poor results on 8 GPUs. What might be the cause? What would you do?

## Ответ

### Расчёт памяти модели

Одной архитектуры и гиперпараметров **недостаточно**. Нужно учитывать:

1. **Веса** — число параметров × размер типа (float32/16).
2. **Активации** — зависят от batch size, длины последовательности, размера входа; при backprop их хранят.
3. **Градиенты** — обычно того же размера, что и веса.
4. **Состояние оптимизатора** — Adam хранит два момента на параметр; для SGD с momentum — один.
5. **Временные буферы** — промежуточные результаты в слоях.

Формулы: для CNN — активации по размерам feature maps; для Transformer — квадратично по длине последовательности.

### Multi-GPU: возможные причины и действия

**Причины ухудшения:**
- **Эффективный batch size** — 8× больше → другой dynamics обучения; нужна корректировка learning rate.
- **Gradient accumulation** — если батч разбит на 8 частей, градиенты усредняются; масштабирование LR.
- **BatchNorm** — статистика считается по подбатчу на каждой GPU; несоответствие с single-GPU. Решение: SyncBatchNorm, собирать статистику по всем GPU.
- **Async vs sync SGD** — при асинхронном обновлении градиенты устаревают, сходимость может ухудшиться.
- **Численная нестабильность** — разный порядок операций на GPU даёт небольшой разброс.

**Что делать:**
- Scaling learning rate (linear scaling rule: LR × N_GPUs или sqrt(N_GPUs)).
- SyncBatchNorm или переход на LayerNorm.
- Gradient accumulation при малом батче на GPU.
- Проверка идентичности при deterministic seed.

---
*Источник: [MLIB](https://huyenchip.com/ml-interviews-book/)*
