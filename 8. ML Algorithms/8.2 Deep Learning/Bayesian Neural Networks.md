# Байесовские нейронные сети

**Вопросы (EN)**: How do Bayesian methods differ from mainstream DL? Pros/cons of Bayesian NNs vs mainstream NNs? Why are Bayesian NNs natural ensembles?

## Ответ

### Байесовский подход vs мейнстримный DL

| | Мейнстримный DL | Байесовские NNs |
|---|---|---|
| Параметры | Точечные оценки (MAP/MLE) | Распределения над весами |
| Предсказание | Один вывод | Усреднение по posterior |
| Uncertainty | Нет из коробки | Встроена (epistemic + aleatoric) |
| Обучение | SGD / Adam | Вариационный вывод, MCMC, dropout |

В обычном DL находим одни веса \(\hat{\theta}\). В байесовском подходе хотим:
\[
p(\theta | \mathcal{D}) \propto p(\mathcal{D} | \theta)\, p(\theta)
\]
и делаем предсказание как:
\[
p(y^* | x^*, \mathcal{D}) = \int p(y^* | x^*, \theta)\, p(\theta | \mathcal{D})\, d\theta
\]

### Почему Bayesian NNs — естественные ансамбли

Маргинализация по posterior \(p(\theta|\mathcal{D})\) эквивалентна усреднению предсказаний **бесконечного числа моделей**, взвешенных по их правдоподобию.

На практике (MC dropout, deep ensembles) делают T выборок параметров и усредняют предсказания — это конечный ансамбль, аппроксимирующий байесовский вывод.

MC Dropout (Gal & Ghahramani, 2016): dropout во время inference при T прогонах → набор предсказаний → mean и variance.

### Плюсы и минусы

**Плюсы Bayesian NNs:**
- Оценка неопределённости (uncertainty quantification) — критично для медицины, автономных систем.
- Защита от переобучения через prior.
- Обобщение на малых данных.

**Минусы Bayesian NNs:**
- Вычислительно дорого (MCMC, вариационный вывод).
- Сложность в выборе prior.
- Вариационные методы дают приближённый posterior.
- Масштабирование на большие сети — нетривиально.

**Плюсы мейнстримных сетей:** быстрее, проще, хорошо отработаны.

---
*Источник: [MLIB](https://huyenchip.com/ml-interviews-book/)*
