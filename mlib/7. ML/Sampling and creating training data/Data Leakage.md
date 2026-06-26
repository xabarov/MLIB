# Утечка данных (Data Leakage)

**Вопрос (EN)**: Oversample rare class, then split into train/test. Model does well on test but poorly in production — what might have happened? For spam classification with 7 days of data: random split can lead to data leakage. How?

## Ответ

### Oversampling до split

Если oversampling делается до разбиения на train/test:
1. Один и тот же объект может оказаться и в train, и в test (при копировании positive).
2. Тестовая выборка перестаёт быть независимой.
3. Оценка получается слишком оптимистичной; в production нет этих «скопированных» соседей → качество падает.

**Правильно:** сначала split, затем oversampling только на train.

### Random split для временных данных

Для временных рядов (7 дней комментариев) случайный split даёт:
1. **Temporal leakage** — объекты из «будущего» (по времени) попадают в train, а «прошлые» — в test. Модель неявно использует информацию о будущем.
2. ** autocorrelation** — близкие по времени объекты похожи; при random split train и test сильно коррелированы, оценка качества завышена.

**Правильно:** временной split — train на более ранних днях, test на более поздних.

---
*Источник: [MLIB](https://huyenchip.com/ml-interviews-book/)*
