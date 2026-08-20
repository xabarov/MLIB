# TF-IDF и базовые концепции NLP

**Вопрос (EN)**: Given 5 documents, rank them by TF-IDF + cosine similarity for query "The early bird gets the worm". What happens to D5 rank if "bird" mentioned 3 times?  
Also: why do some NLP models share weights between embedding layer and pre-softmax layer?

## Ответ

### TF-IDF

**TF (Term Frequency)**: частота термина в документе.
\[
\text{TF}(t, d) = \frac{\text{count}(t \text{ in } d)}{\text{total words in } d}
\]

**IDF (Inverse Document Frequency)**: редкость термина в коллекции.
\[
\text{IDF}(t) = \log \frac{N}{|\{d : t \in d\}|}
\]

**TF-IDF** = TF × IDF. Высокий у частых в документе, но редких в коллекции терминов.

### Влияние увеличения упоминания "bird" в D5

Если "bird" встречается 3 раза вместо 1 → TF(bird, D5) растёт → TF-IDF(bird, D5) растёт → вектор D5 становится ближе к запросу "early bird". **Ранг D5 повышается.**

Это свойство **желательно**: документ, детально рассказывающий о теме запроса, релевантнее. Однако при злоупотреблении (keyword stuffing) — нежелательно. Поэтому в практике применяют сглаживание TF (log-normalization) или BM25.

### Ранжирование через косинусное сходство

Для запроса \(Q\) и документа \(D\):
\[
\text{sim}(Q, D) = \frac{\vec{q} \cdot \vec{d}}{|\vec{q}| \cdot |\vec{d}|}
\]
Векторы строятся по TF-IDF значениям для термов \(\{bird, duck, worm, early, get, love\}\).

Наиболее релевантны документы, в которых часто встречаются термы запроса, а сами эти термы редки по коллекции.

### Разделяемые веса (weight tying): embedding ↔ pre-softmax

Матрица эмбеддингов \(E \in \mathbb{R}^{|V| \times d}\) и матрица перед softmax \(W \in \mathbb{R}^{d \times |V|}\) транспонированы друг другу: используют одну матрицу \(E\), т.е. \(W = E^T\).

**Зачем:**
- Снижает число параметров (особенно при большом словаре \(|V|\)).
- Семантическое согласование: слово в качестве входа и выхода должно иметь одинаковое представление.
- Эмпирически улучшает perplexity (Inan et al., 2017).
- Распространено в language models (GPT, BERT-like: частично).

---
*Источник: [MLIB](https://huyenchip.com/ml-interviews-book/)*
