# Открытые реализации: карта чтения исходников

Зафиксировано **2026-09-26**. Точные commit SHA находятся в
[upstreams.json](upstreams.json). Команда `fetch_references.py` создаёт локальные
checkouts по этим SHA. Онлайн-ссылки ниже тоже зафиксированы: движущаяся ветка
`main` может уже содержать другой код.

Общая постановка следует из официального [интерфейса Jev](https://docs.typesafe.ai/introduction):
state и типизированные вопросы на входе, значения и распределения на выходе.
[Анонс RLCD](https://typesafe.ai/blog/introducing-system-one-models-and-jev)
не раскрывает полный алгоритм обучения. Ни один из репозиториев ниже не служит
подтверждением внутренней архитектуры Jev.

## 1. SemIf: сначала readout, затем prefix reuse

**Версия:** `23cf1f39fc95`, MIT.

| Читаем | На что смотреть |
|---|---|
| [direct.py](https://github.com/TheoLeeCJ/SemIf-OpenJev/blob/23cf1f39fc9534fe81437200959b6dfc7106e45a/src/semif_phase1/direct.py) | `_slot_ids`, `encode_prompt`, `score` |
| [core.py](https://github.com/TheoLeeCJ/SemIf-OpenJev/blob/23cf1f39fc9534fe81437200959b6dfc7106e45a/src/semif_phase1/core.py) | сериализация инструкции и вариантов |
| [shared.py](https://github.com/TheoLeeCJ/SemIf-OpenJev/blob/23cf1f39fc9534fe81437200959b6dfc7106e45a/src/semif_phase1/shared.py) | граница общего префикса, layout suffix, работа с cache |

Локально: `references/semif/src/semif_phase1/`.
Путь данных: prompt → один forward → последние vocabulary logits → разрешённые
слоты → softmax. Проверяются однотокенность кодов и стабильность токенизации на
границе ответа. `direct.py` действительно вычисляет vocabulary logits и затем
выбирает слоты. Наш `TokenReadout` сразу проецирует в нужные строки той же матрицы;
эквивалентность проверяется тестом.

В `shared.py` state-prefill общий, suffix различаются. Обратите внимание на
разветвление и копирование cache; «у меня один объект cache» ещё не означает,
что последовательный вызов не изменяет его. Учебный Transformer реализует
immutability через создание новых K/V при `torch.cat`.

**Отличия лаборатории:** случайные веса и supervised training вместо готовой
instruction LLM; маленький word-level словарь; нет chat template и backend-адаптеров.

## 2. Kev: pointer head и изоляция вопросов

**Версия:** `5920c5fe4ca8`, Apache-2.0.

Начните с [kev/model.py](https://github.com/jaredpalmer/kev/blob/5920c5fe4ca8e0970ed4209ac2c9b8e18bea5109/kev/model.py):
`encode` → `branch_mask_batch` → `rows_of` → `PointerHead` → `DecisionModel`.
Затем прочитайте [kev/train.py](https://github.com/jaredpalmer/kev/blob/5920c5fe4ca8e0970ed4209ac2c9b8e18bea5109/kev/train.py).
Локально те же файлы — в `references/kev/kev/`.

`PointerHead` проецирует `[DECIDE]` и закрывающие option markers в общее пространство.
Разделение вопросов обеспечивается mask на attention-only backbone либо отдельными
строками на гибридной архитектуре. Рекуррентный mixer может переносить состояние
между токенами независимо от attention mask; поэтому просто перенести нашу
упаковку на Qwen с Gated DeltaNet нельзя.

В `forward` и serving-путях могут различаться повторное чтение state и cache reuse;
измерение одного не является измерением другого. Указанная в checkpoint температура
применяется к logits при inference.

**Отличия лаборатории:** вместо pretrained Qwen + LoRA — обучаемый целиком tiny
Transformer; pointer dimension равна D; без GQA, RoPE, DeltaNet и production kernels.
Наш packed example объясняет случай attention-only. Он не эмулирует все Kev backends.

## 3. Laya: marker head, batching и открытый training notebook

**Версия:** `4066d5d5fbf0`, Apache-2.0.

| Читаем | На что смотреть |
|---|---|
| [laya/common.py](https://github.com/NandhaKishorM/laya/blob/4066d5d5fbf08b66c6757ddeedbd797bd7655bc0/laya/common.py) | `build_sequence`, `DecisionModel.forward`, `proper_reward` |
| [laya/agent.py](https://github.com/NandhaKishorM/laya/blob/4066d5d5fbf08b66c6757ddeedbd797bd7655bc0/laya/agent.py) | подготовка строк batch, маскирование и температура |
| [fine-tuning notebook](https://github.com/NandhaKishorM/laya/blob/4066d5d5fbf08b66c6757ddeedbd797bd7655bc0/notebooks/laya_finetune_typed_decisions_2xT4_kaggle.ipynb) | noisy logits, rewards, `loss_rl + loss_ce`, held-out calibration |

Локально: `references/laya/laya/` и `references/laya/notebooks/`.
`build_sequence` располагает инструкцию, `[MASK]`-маркеры вариантов и документ.
После pretrained encoder следуют дополнительные transformer-слои; общая MLP
оценивает маркеры. Есть embedding типа вопроса и отдельная act head.

Один batched forward содержит несколько question/state-последовательностей.
Переиспользование token IDs документа не равно переиспользованию его hidden states.
В учебном `MarkerReadout` оставлены bidirectional attention и shared marker scorer;
убраны отдельный pretrained encoder, type embeddings и act/escalate head.

Открытый fine-tuning notebook сочетает policy-gradient reward с CE и затем
подбирает температуру. Наш `rlcd_loss` использует фиксированный шум и leave-one-out
baseline; upstream — group mean и нормировку advantages. Это разные рецепты.

## 4. Nimble: тот же readout, другой акцент в обучении

**Версия:** `62076b4f2d36`. В зафиксированном репозитории не обнаружено явной лицензии
на код; `license: null` в manifest означает отсутствие подтверждённой лицензии,
а не public domain. Исходники загружены локально для чтения и не включены в MLIB.

| Читаем | На что смотреть |
|---|---|
| [parallel_scorer.py](https://github.com/bespokelabsai/nimble/blob/62076b4f2d365b5879dafcf7f6dd072a1fe76df7/nimble/scoring/parallel_scorer.py) | shared prefix, parallel branches, code→choice |
| [schema_train.py](https://github.com/bespokelabsai/nimble/blob/62076b4f2d365b5879dafcf7f6dd072a1fe76df7/nimble/training/schema_train.py) | loss по разрешённым кандидатам, LoRA |
| [NIMBLE_TRAINING.md](https://github.com/bespokelabsai/nimble/blob/62076b4f2d365b5879dafcf7f6dd072a1fe76df7/docs/NIMBLE_TRAINING.md) | воспроизводимый рецепт исходного релиза |
| [README: methodology](https://github.com/bespokelabsai/nimble/tree/62076b4f2d365b5879dafcf7f6dd072a1fe76df7#methodology) | contrastive data curation |

Локально: `references/nimble/`. Слово contrastive относится к парам данных, где
одно существенное изменение факта переворачивает label. Loss по кандидатам — CE.
Наш token-вариант показывает этот readout, но не воспроизводит policy-dataset,
LoRA или способности Qwen3.5-9B. Поэтому отдельная четвёртая игрушечная архитектура
для Nimble не нужна.

## 5. Статьи и контекст

- [GLiClass, arXiv:2508.07662](https://arxiv.org/abs/2508.07662),
  [код](https://github.com/Knowledgator/GLiClass): совместное кодирование текста и
  описаний классов, zero-shot classification, несколько архитектурных вариантов.
  Хороший академический мост от BERT к этой постановке; работа предшествует Jev.
- [Jev’s Architecture Unmasked](https://archerhume.com/posts/jevs-architecture-unmasked):
  black-box исследование API, на которое ссылается Kev. Автор разделяет наблюдения
  и гипотезы. Предположение о MoE не является раскрытием архитектуры TypeSafe.
- [SalesRLAgent, 2503.23303](https://arxiv.org/abs/2503.23303) и
  [Confidence-Aware Routing, 2510.01237](https://arxiv.org/abs/2510.01237): ранние
  работы автора Laya; не полная спецификация нынешнего checkpoint.
- [On Calibration of Modern Neural Networks](https://arxiv.org/abs/1706.04599):
  основа обсуждения temperature scaling и различия accuracy/calibration.
- [Официальные ограничения Jev](https://docs.typesafe.ai/model-jaggedness/jev-1.13)
  помогают не путать закрытый набор вариантов с отсутствием смысловых ошибок.

## 6. Откуда взят учебный формат

- [nanoGPT/model.py](https://github.com/karpathy/nanoGPT/blob/3adf61e154c3fe3fca428ad6bc3818b27a3b8291/model.py):
  компактная реализация модели, конфигурация рядом, отсутствие лишних обёрток.
- [LLMs-from-scratch](https://github.com/rasbt/LLMs-from-scratch/tree/f49cad747931fe6af0a7d2802cd480d1c1a0ec8e):
  пошаговые notebooks и разбор промежуточных тензоров.

В лаборатории это выражается в небольших классах readout, самостоятельном training
loop и проверяемых экспериментах. Код и рисунки написаны для MLIB; upstream
сохраняет собственное авторство и условия использования.
