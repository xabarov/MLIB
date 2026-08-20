# Candidate Sampling

**Вопрос (EN)**: For classification with many classes (e.g. next word prediction), calculating probabilities for all classes is prohibitively expensive. Instead, we can calculate probabilities for a small set of candidate classes. Name and explain some candidate sampling algorithms.

## Ответ

**Candidate sampling** — оценка loss и градиентов только по небольшому подмножеству классов вместо полного softmax по всем классам.

### Основные методы

1. **Negative sampling (NCE)**  
   Случайно выбирают «негативные» классы; loss сравнивает вероятность положительного класса с вероятностями выбранных негативов. Ускоряет обучение word2vec и других моделей с большим vocab.

2. **Sampled softmax**  
   Для каждого примера сэмплируют \(k\) негативных классов; softmax и loss считают только по целевому классу и этим \(k\). Оценка слегка смещена, но с bias correction становится несмещённой.

3. **Importance sampling**  
   Негативы выбирают из proposal-распределения \(Q\); в loss вводят importance weights \(p/Q\), чтобы компенсировать смещение.

4. **Black-out**  
   Вариант sampled softmax с другой схемой сэмплирования.

### Когда использовать

При очень большом числе классов (десятки и сотни тысяч): язык, рекомендации, large-scale classification. Полный softmax имеет сложность \(O(V)\) по словарю; candidate sampling даёт \(O(k)\), \(k \ll V\).

---
*Источник: [MLIB](https://huyenchip.com/ml-interviews-book/)*
