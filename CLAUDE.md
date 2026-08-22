# MLIB — инструкции для Claude

Учебный репозиторий. Корень репозитория — рабочий каталог; всё запускается отсюда.

## Карта репозитория

```
tracks/          учебные планы (контент)
  shad/          лекции для поступления в ШАД: <раздел>/<N_Тема>/{lesson.md,qa.md,assets/}
  ml-interviews/ Q&A по книге huyenchip.com/ml-interviews-book: math/ computer-science/ ml/ ml-algorithms/
  agent-harness/ инженерия систем вокруг LLM: агентный цикл, контекст, инструменты, изоляция
  networks/      компьютерные сети
apps/
  interactive/   React/Vite-тренажёр по темам ШАД
tools/           generate_lecture.py, generate_images.py — генераторы контента и иллюстраций
shared/          общие для всех треков правила: authoring guide, визуальная дизайн-система
essays/          не учебное: эссе о спирали, шаблон PROJECT_BOOTSTRAP
```

Общие для репозитория файлы: `Makefile`, `pyproject.toml`, `.env` (секреты), `.venv/`.

## Треки и статус

### tracks/shad — основной трек

Программа: `tracks/shad/programma_shad.md`

| Раздел | Тем | Статус |
|---|---|---|
| `algebra` | 13 | ✅ lesson + qa |
| `mathematical_analysis` | 11 | ✅ lesson + qa |
| `combinatorics` | 5 | ✅ lesson + qa |
| `probability_theory` | 8 | ✅ lesson + qa |
| `programming_algorithms_data_structures` | 19 | ✅ lesson; qa нет у `1_Fundamentals` |
| `data_analysis` | 6 | ✅ lesson + qa |

`algebra/0_yandex_lms/` и `general/` — вспомогательные материалы (шпаргалки), не лекции.

### tracks/ml-interviews — подготовка к интервью

Трек переводится из конспектов в лекции; рядом живут два формата — плоская
заглушка `Название темы.md` и готовая тема-папка со слагом.

**DoD готовой темы:** развёрнутое объяснение с матчастью + запускаемый код +
иллюстрации. `notebook.ipynb` — по уместности. DoD трека `shad` (ровно 10 задач
в `qa.md`) здесь **не применяется**.

```
<раздел>/<тема-слаг>/
  lesson.md  generate_visuals.py  lecture_llm_images.json  assets/  [notebook.ipynb]
```

Правила диаграмм и hero-иллюстраций — общие, см. раздел «Иллюстрации» ниже.
Кривые на диаграммах **считаются на данных**, а не рисуются по памяти: если прогон
не подтвердил заголовок картинки — меняется заголовок, а не данные.

Готово: `ml/basics/classification-vs-regression`,
`ml-algorithms/deep-learning/computer-vision/object-detection-architectures`,
`ml-algorithms/deep-learning/computer-vision/detection-metrics`,
`…/segmentation-architectures`, `…/segmentation-metrics`, `…/ocr`,
`nlp/tf-idf-and-text-representation`, `nlp/word-embeddings`,
`architectures/self-attention-and-transformers`.

`deep-learning/` разбит на блоки `architectures/` (строительные блоки) и
`computer-vision/`, `nlp/`, `reinforcement-learning/` (применения) — по образцу
самой главы 8.2. Темы вне списка вопросов книги допустимы.
Нумерация глав книги — в `tracks/ml-interviews/README.md`.

### tracks/agent-harness — инженерия харнессов

Формат тот же, что в `ml-interviews` (лекция + код + иллюстрации). Темы
привязаны к инженерным задачам, а не к конкретным инструментам: область
быстро меняется, и лекция про отдельный харнесс устареет.

Источники примеров — шесть открытых харнессов в
`/home/roman/pyprojects/agent-driver-gitlab/agent-driver/reference/`.

Готово: `agent-loop`.

### tracks/networks — компьютерные сети

Пока один файл `junior_qa.md` (10 вопросов уровня Junior). Формат трека ещё не зафиксирован.

---

## Definition of Done — лекция трека `shad`

### Минимальный набор файлов

```
tracks/shad/<раздел>/<N_Тема>/
  lesson.md
  qa.md
  lecture_llm_images.json
  assets/manifest.json
  generate_visuals.py          ← если есть точные математические диаграммы
  assets/<hero>.jpg            ← после генерации
  assets/<диаграммы>.png       ← после генерации
```

### lesson.md — чеклист

- [ ] Заголовок `# Лекция: <тема>`
- [ ] Hero-иллюстрация сразу после заголовка (`assets/hero_*.jpg`)
- [ ] **Нарративный абзац** перед нумерованными разделами — "главная линия лекции", зачем это изучать, на что опирается
- [ ] `## План` — нумерованный список всех разделов
- [ ] Каждая позиция программы ШАД, которую покрывает лекция, — отдельный раздел с определением
- [ ] На каждое новое понятие — минимум **один разобранный пример**
- [ ] Внутри текста — иллюстрации только там, где они помогают (не для каждого раздела)
- [ ] Раздел **"Типичные ошибки"** — не менее 4–5 конкретных ошибок с объяснением
- [ ] Раздел **"Что важно для поступления в ШАД"** — список навыков bullet-ами
- [ ] Раздел **"Итог"** — один абзац, вся лекция в 5–7 предложениях
- [ ] Раздел **"Вопросы для самопроверки"** — ≥ 8 вопросов

### qa.md — чеклист

- [ ] Ровно **10 задач** в стиле вступительного экзамена
- [ ] Каждая задача: условие → `### Решение` с подробными шагами → `### Ответ` в отдельном блоке
- [ ] Задачи идут от простых к сложным
- [ ] Покрыты **все ключевые техники** темы (каждая задача — другой приём)
- [ ] Есть хотя бы одна **"синтезная"** задача (несколько приёмов одновременно)
- [ ] Блок `<details><summary>Что тренируют эти задачи</summary>` в конце

### Иллюстрации — правило выбора инструмента

| Тип иллюстрации | Инструмент |
|---|---|
| Hero / обложка (атмосферная, концептуальная) | LLM → `lecture_llm_images.json` |
| Точная математическая диаграмма (Эйлер, разбиение, график, анимация) | `generate_visuals.py` (matplotlib) |

Диаграммы Эйлера, разбиения пространства, Venn-диаграммы, числовые прямые, графики функций — **всегда matplotlib**. LLM не гарантирует геометрическую точность.

### generate_visuals.py — шаблон

```python
"""Точные схемы для лекции про <тему>."""
from pathlib import Path
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets"

C_BG = "#faf9f5"; C_INK = "#141413"; C_GRAY = "#b0aea5"
C_ORANGE = "#d97757"; C_BLUE = "#6a9bcc"; C_GREEN = "#788c5d"

def _apply_style():
    plt.rcParams.update({"figure.facecolor": C_BG, "axes.facecolor": C_BG,
                          "axes.edgecolor": C_GRAY, "text.color": C_INK, "font.size": 11})

def _save(fig, name):
    ASSETS.mkdir(parents=True, exist_ok=True)
    fig.savefig(ASSETS / name, dpi=180, bbox_inches="tight", facecolor=C_BG)
    plt.close(fig)

def main():
    ASSETS.mkdir(parents=True, exist_ok=True)
    # draw_*() вызовы здесь

if __name__ == "__main__":
    main()
```

### Отметка в программе

После завершения — проставить `[x]` напротив покрытых тем в:
`tracks/shad/programma_shad.md`

---

## Генерация иллюстраций — запускаю сам

После написания лекции **я сам** запускаю оба генератора, не прошу пользователя:

```bash
# 1. matplotlib-диаграммы (без API, только venv)
cd /home/roman/Documents/ML/MLIB
.venv/bin/python tracks/shad/<раздел>/<N_Тема>/generate_visuals.py

# 2. LLM hero (ключ из .env — подгружается автоматически)
.venv/bin/python tools/generate_images.py \
  --jobs tracks/shad/<раздел>/<N_Тема>/lecture_llm_images.json \
  --out-dir tracks/shad/<раздел>/<N_Тема>/assets
```

Ключи: `LLM_API_KEY`, `LLM_BASE_URL`, `LLM_VISUAL_GENERATION_MODEL` — в `.env`.  
LLM генерирует `.png`; ссылки в `lesson.md` должны быть `.png`, не `.jpg`.

---

## Что НЕ нужно делать

- Не добавлять `practice.md` без явной просьбы
- Не менять стиль палитры (`#faf9f5`, `#141413` и т.д.) — он задан в `lecture_visual_design_system.md`
- Не коммитить `.env`, `node_modules/`, `.venv/`, `dist/`, `__pycache__/`
- После написания лекции запустить оба генератора (см. раздел «Генерация иллюстраций» выше)

---

## Визуальный стиль

Детали: `shared/lecture_visual_generation/lecture_visual_design_system.md`  
Суффикс промптов: `shared/lecture_visual_generation/lecture_visual_prompt_suffix.txt`  
Guide по написанию: `shared/lecture_qa_authoring_guide.md`

---

## Прочие команды

```bash
make lint                # ruff по tools/ + eslint по apps/interactive
make interactive-dev     # Vite dev-сервер на 127.0.0.1:5173
make interactive-build   # прод-сборка тренажёра
```
