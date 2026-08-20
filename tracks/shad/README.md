# Трек: ШАД

Материалы для подготовки к вступительному экзамену в Школу анализа данных Яндекса.
Программа-первоисточник: [`programma_shad.md`](programma_shad.md).

## Разделы

| Каталог | Тем | Статус |
|---|---|---|
| [`algebra/`](algebra/) | 13 | lesson + qa по всем темам |
| [`mathematical_analysis/`](mathematical_analysis/) | 11 | lesson + qa по всем темам |
| [`combinatorics/`](combinatorics/) | 5 | lesson + qa по всем темам |
| [`probability_theory/`](probability_theory/) | 8 | lesson + qa по всем темам |
| [`programming_algorithms_data_structures/`](programming_algorithms_data_structures/) | 19 | lesson по всем; нет `qa.md` у `1_Fundamentals` |
| [`data_analysis/`](data_analysis/) | 6 | lesson + qa по всем темам |

Вспомогательное:

- [`general/`](general/) — шпаргалки (тригонометрия, бином Ньютона, квадратные уравнения)
- [`algebra/0_yandex_lms/`](algebra/0_yandex_lms/) — конспекты по курсу Яндекс.LMS

## Структура темы

```
<раздел>/<N_Тема>/
  lesson.md               теория
  qa.md                   10 экзаменационных задач с решениями
  lecture_llm_images.json задание на hero-иллюстрацию
  generate_visuals.py     matplotlib-диаграммы (если нужны точные схемы)
  assets/                 сгенерированные картинки + manifest.json
```

Правила написания: [`../../shared/lecture_qa_authoring_guide.md`](../../shared/lecture_qa_authoring_guide.md).
Визуальный стиль: [`../../shared/lecture_visual_generation/`](../../shared/lecture_visual_generation/).

## Генерация

```bash
# из корня репозитория
.venv/bin/python tools/generate_lecture.py "Название темы" --section algebra --generate-qa
.venv/bin/python tracks/shad/<раздел>/<N_Тема>/generate_visuals.py
.venv/bin/python tools/generate_images.py \
  --jobs tracks/shad/<раздел>/<N_Тема>/lecture_llm_images.json \
  --out-dir tracks/shad/<раздел>/<N_Тема>/assets
```

Допустимые значения `--section`: `algebra`, `math_analysis`, `combinatorics`,
`probability`, `algorithms`, `data_analysis`.

Интерактивный тренажёр по этим темам — [`../../apps/interactive/`](../../apps/interactive/).
