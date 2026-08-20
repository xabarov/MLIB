# Числовые и текстовые признаки в нейросети

**Вопрос (EN)**: Building a NN with both numerical and textual features. How would you process those different features?

## Ответ

### Числовые признаки

1. **Нормализация** — StandardScaler, MinMaxScaler (fit на train).
2. **Обработка пропусков** — imputation, флаг is_missing.
3. **Handling outliers** — winsorization, clipping, robust scaling.
4. **Конкатенация** в один вектор и подача в dense-слой.

### Текстовые признаки

1. **Токенизация** — разбиение на слова/субслова.
2. **Embedding** — обученный или pretrained (Word2Vec, FastText).
3. **Альтернативы** — CNN/RNN/Transformer поверх embeddings.
4. **Для короткого текста** — усреднение embeddings, pooling.

### Объединение

1. **Early fusion** — конкатенировать числовой вектор и вектор из текста (embedding/pooling), подать в общие слои.
2. **Позднее объединение** — отдельные ветки для числовых и текстовых, объединение на уровне представлений.
3. **Attention** — текстовое представление может модулировать числовые признаки и наоборот.

### Практика

- Embedding для категориальных, scaling для непрерывных.
- BatchNorm/LayerNorm после concatenation.
- Dropout для регуляризации.

---
*Источник: [MLIB](https://huyenchip.com/ml-interviews-book/)*
