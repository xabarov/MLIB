# F1 Score

**Вопрос (EN)**: What's the benefit of F1 over accuracy? Can we use F1 for more than two classes?

## Ответ

### Преимущество F1 перед accuracy

При дисбалансе классов accuracy может быть высокой при плохой работе по редкому классу. F1 учитывает precision и recall и чувствителен к ошибкам по positive классу.

\[
F1 = 2 \cdot \frac{\text{Precision} \cdot \text{Recall}}{\text{Precision} + \text{Recall}}
\]

F1 полезен, когда оба типа ошибок (FP и FN) важны и классы несбалансированы.

### F1 для многоклассовой задачи

1. **Macro-F1** — считаем F1 для каждого класса отдельно и усредняем. Каждый класс учитывается одинаково.

2. **Weighted F1** — усреднение F1 по классам с весами, пропорциональными частоте класса.

3. **Micro-F1** — считаем общие TP, FP, FN по всем классам, затем precision и recall. Эквивалентно accuracy при multilabel, при многоклассовой — чувствителен к частым классам.

4. **Per-class F1** — отдельный F1 для каждого класса, если нужно анализировать классы по отдельности.

---
*Источник: [MLIB](https://huyenchip.com/ml-interviews-book/)*
