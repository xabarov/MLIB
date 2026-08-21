# Трек: ML Interviews

Разбор вопросов из книги Чипа Хьюена [*Introduction to Machine Learning Interviews*](https://huyenchip.com/ml-interviews-book/).

## Два состояния темы

Трек постепенно переводится из конспектов в полноценные лекции, поэтому рядом
живут два формата:

| Состояние | Как выглядит | Что внутри |
|---|---|---|
| **Заглушка** | один файл `Название темы.md` | краткий конспект ответа на 1–2 экрана |
| **Готовая тема** | папка-слаг с `lesson.md` | развёрнутая лекция с иллюстрациями и кодом |

Состав готовой темы:

```
<тема-слаг>/
  lesson.md                 лекция
  generate_visuals.py       matplotlib-диаграммы (считаются на данных, не рисуются «на глаз»)
  lecture_llm_images.json   задание на hero-иллюстрацию
  assets/                   сгенерированные картинки
  notebook.ipynb            запускаемые эксперименты — если тема того стоит
```

**DoD темы:** развёрнутое объяснение с матчастью + запускаемый код + иллюстрации.
Ноутбук — по уместности, не обязателен. DoD лекций трека `shad` (ровно 10 задач
в `qa.md` и т.д.) здесь **не применяется**.

Готовые темы:

- [`ml/basics/classification-vs-regression/`](ml/basics/classification-vs-regression/)
- [`ml-algorithms/deep-learning/computer-vision/object-detection-architectures/`](ml-algorithms/deep-learning/computer-vision/object-detection-architectures/)
- [`ml-algorithms/deep-learning/computer-vision/detection-metrics/`](ml-algorithms/deep-learning/computer-vision/detection-metrics/)
- [`ml-algorithms/deep-learning/computer-vision/segmentation-architectures/`](ml-algorithms/deep-learning/computer-vision/segmentation-architectures/)
- [`ml-algorithms/deep-learning/computer-vision/segmentation-metrics/`](ml-algorithms/deep-learning/computer-vision/segmentation-metrics/)
- [`ml-algorithms/deep-learning/computer-vision/ocr/`](ml-algorithms/deep-learning/computer-vision/ocr/)

## Соответствие главам книги

| Каталог | Глава книги |
|---|---|
| [`math/algebra/`](math/algebra/) | 5.1 Algebra and (little) calculus |
| [`math/probability/`](math/probability/) | 5.2 Probability |
| [`math/stats/`](math/stats/) | 5.3 Statistics |
| [`computer-science/algorithms/`](computer-science/algorithms/) | 6.1 Algorithms |
| [`computer-science/complexity/`](computer-science/complexity/) | 6.2 Complexity and numerical analysis |
| [`computer-science/data/`](computer-science/data/) | 6.3 Data |
| [`ml/basics/`](ml/basics/) | 7.1 ML basics |
| [`ml/sampling-training-data/`](ml/sampling-training-data/) | 7.2 Sampling and creating training data |
| [`ml/objectives-metrics-evaluation/`](ml/objectives-metrics-evaluation/) | 7.3 Objective functions, metrics, evaluation |
| [`ml-algorithms/classical-ml/`](ml-algorithms/classical-ml/) | 8.1 Classical machine learning |
| [`ml-algorithms/deep-learning/`](ml-algorithms/deep-learning/) | 8.2 Deep learning architectures **and applications** |
| [`ml-algorithms/training-neural-networks/`](ml-algorithms/training-neural-networks/) | 8.3 Training neural networks |

Номера глав вынесены сюда, чтобы каталоги оставались слагами без пробелов и точек.

Раздел `deep-learning/` разбит внутри на блоки — так же, как сама глава 8.2,
которая делится на NLP, computer vision и reinforcement learning:

| Блок | Что внутри |
|---|---|
| [`deep-learning/architectures/`](ml-algorithms/deep-learning/architectures/) | строительные блоки: CNN, RNN/LSTM, трансформеры, GAN, transfer learning |
| [`deep-learning/computer-vision/`](ml-algorithms/deep-learning/computer-vision/) | применения в зрении: детекция, сегментация |
| [`deep-learning/nlp/`](ml-algorithms/deep-learning/nlp/) | применения в тексте: эмбеддинги, TF-IDF |
| [`deep-learning/reinforcement-learning/`](ml-algorithms/deep-learning/reinforcement-learning/) | обучение с подкреплением |

Темы вне списка вопросов книги допустимы: структура книги — ориентир, а не рамка.

## Покрытие

Сверки покрытия относительно книги лежат рядом с материалом:
`math/COVERAGE_COMPARISON.md`, `math/PLAN_IMPROVEMENTS.md`, `ml/COVERAGE_COMPARISON.md`,
`computer-science/algorithms/COVERAGE_COMPARISON.md`.
