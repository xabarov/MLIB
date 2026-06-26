# MLIB — инструкции для Claude

Учебный репозиторий для подготовки к поступлению в ШАД (Яндекс).
Рабочий каталог — `mlib/`. Материалы лекций в `SHAD/<раздел>/<N_Тема>/`.

## Разделы и статус

Программа: `SHAD/Programma_dlya_postupayushhih_v_Shkolu_analiza_dannyh_3_749884e44e.md`

| Раздел | Статус |
|---|---|
| algebra (1–13) | ✅ готово |
| mathematical_analysis (1–11) | ✅ готово |
| combinatorics (1–5) | ✅ готово |
| probability_theory | 2/8 (темы 1–2) |
| programming algorithms and data structures | 0/21 |
| data analysis | 0/6 |

---

## Definition of Done — лекция

### Минимальный набор файлов

```
SHAD/<раздел>/<N_Тема>/
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
`SHAD/Programma_dlya_postupayushhih_v_Shkolu_analiza_dannyh_3_749884e44e.md`

---

## Что НЕ нужно делать

- Не добавлять `practice.md` без явной просьбы
- Не менять стиль палитры (`#faf9f5`, `#141413` и т.д.) — он задан в `lecture_visual_design_system.md`
- Не коммитить `.env`, `node_modules/`, `.venv/`, `dist/`, `__pycache__/`
- Не генерировать изображения самостоятельно — только готовить `lecture_llm_images.json` и `generate_visuals.py`; пользователь запускает сам

---

## Команды для запуска

```bash
# matplotlib-диаграммы
cd mlib && .venv/bin/python SHAD/<раздел>/<N_Тема>/generate_visuals.py

# LLM-иллюстрации (hero и атмосферные)
cd mlib && .venv/bin/python generate_images.py \
  --jobs SHAD/<раздел>/<N_Тема>/lecture_llm_images.json \
  --out-dir SHAD/<раздел>/<N_Тема>/assets
```

---

## Визуальный стиль

Детали: `SHAD/lecture_visual_generation/lecture_visual_design_system.md`  
Суффикс промптов: `SHAD/lecture_visual_generation/lecture_visual_prompt_suffix.txt`  
Guide по написанию: `SHAD/lecture_qa_authoring_guide.md`
