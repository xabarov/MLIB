# Batch Norm, Layer Norm, Adam vs SGD

**Вопросы (EN)**: Compare batch norm and layer norm. Adam vs SGD — convergence and generalization? Learning rate and batch size? Why reduce LR during training?

## Ответ

### Batch Norm vs Layer Norm

- **Batch Norm** — нормализация по batch для каждого канала; зависит от batch size; разное поведение в train/eval; чувствителен к маленьким батчам.
- **Layer Norm** — нормализация по каналам внутри одного примера; не зависит от batch; подходит для RNN/Transformer; стабильнее при малых батчах.

### Adam vs SGD

- **Adam** — быстрая сходимость; адаптивный шаг; часто хуже generalization при длительном обучении.
- **SGD + momentum** — медленнее сходимость; часто лучшая финальная обобщающая способность при достаточном обучении.
- На практике: Adam для быстрых экспериментов; SGD для финальных длинных тренировок.

### Learning rate и batch size

При увеличении batch size обычно увеличивают learning rate (линейно или sqrt). При batch=1 — маленький LR; при full batch — можно больший, но итераций меньше.

### Снижение LR

Уменьшение LR в процессе (decay, plateau) позволяет сначала быстро приблизиться к минимуму, затем точнее сходиться. Исключения: cosine annealing без restart, постоянный LR при warmup.

---
*Источник: [MLIB](https://huyenchip.com/ml-interviews-book/)*
