"""
Генерация `lesson.md` и опционально `qa.md` для тем SHAD через OpenRouter.

Переменные окружения (см. `.env`):
  LLM_API_KEY
  LLM_BASE_URL
  LLM_LECTURE_MODEL
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Any, Callable, Dict, List

import requests

PROJECT_ROOT = Path(__file__).resolve().parent
SHAD_ROOT = PROJECT_ROOT / "SHAD"
DEFAULT_DOTENV = PROJECT_ROOT / ".env"
DEFAULT_RULES_FILE = SHAD_ROOT / "lecture_qa_authoring_guide.md"
MAX_FOLDER_SLUG_LEN = 80

BASE_RULES = """
Пиши материал для подготовки к вступительным задачам ШАД.
Жесткие требования:
1) Верни только markdown-файл без пояснений.
2) Русский язык, спокойный и аккуратный тон.
3) Заголовок строго `# Лекция: <название темы>` (для lesson.md).
4) Не используй ссылки на `assets/*`.
5) Для формул соблюдай markdown-ограничения из guide (не использовать отступленные `$$` внутри списков).
6) Названия обязательных разделов должны быть точными, без переименования.
7) Не делай пустых разделов и заглушек вида "будет показано позже".
"""

QA_BASE_RULES = """
Сгенерируй `qa.md` в стиле вступительных задач ШАД.
Жесткие требования:
1) Верни только markdown-файл.
2) Ровно 10 задач, заголовки вида `## Задача N. ...`.
3) У каждой задачи обязательно есть `### Решение` и `### Ответ`.
4) Русский язык, без воды, с пошаговыми решениями.
5) Задачи должны покрывать разные уровни и опираться на тему лекции, а не быть случайным набором.
"""

GUIDE_SECTIONS = {
    "lesson": [
        "## 3. Правила для `lesson.md`",
        "## 5. Стиль изложения",
        "## 6. Правила по LaTeX и Markdown",
        "## 8. Шаблон `lesson.md`",
        "## 10. Чеклист перед завершением темы",
    ],
    "qa": [
        "## 4. Правила для `qa.md`",
        "## 5. Стиль изложения",
        "## 6. Правила по LaTeX и Markdown",
        "## 9. Шаблон `qa.md`",
        "## 10. Чеклист перед завершением темы",
    ],
}

SECTION_SPECS: Dict[str, Dict[str, str]] = {
    "algebra": {"folder": "algebra", "profile": "math-default"},
    "math_analysis": {"folder": "mathematical_analysis", "profile": "math-default"},
    "combinatorics": {"folder": "combinatorics", "profile": "combinatorics"},
    "probability": {"folder": "probability", "profile": "probability"},
    "algorithms": {"folder": "algorithms", "profile": "algo-programming"},
    "data_analysis": {"folder": "data_analysis", "profile": "data-analysis"},
}

PROFILE_SPECS: Dict[str, Dict[str, Any]] = {
    "math-default": {
        "prompt": (
            "Профиль: математика.\n"
            "Обязательные разделы:\n"
            "`## План`, `## 1. Мотивация`, `## 2. Определения`, `## 3. Главные свойства`, "
            "`## 4. Примеры вычислений`, `## 5. Геометрический или интуитивный смысл`, "
            "`## 6. Типичные ошибки`, `## 7. Что важно для поступления в ШАД`, "
            "`## 8. Итоги`, `## 9. Вопросы для самопроверки`.\n"
            "В самопроверке минимум 8 вопросов."
        ),
        "required_markers": [
            "## План",
            "## 1. Мотивация",
            "## 2. Определения",
            "## 3. Главные свойства",
            "## 4. Примеры вычислений",
            "## 5. Геометрический или интуитивный смысл",
            "## 6. Типичные ошибки",
            "## 7. Что важно для поступления в ШАД",
            "## 8. Итоги",
            "## 9. Вопросы для самопроверки",
        ],
        "self_check_heading_regex": r"## 9\.\s*Вопросы для самопроверки(?P<body>[\s\S]*)$",
        "min_questions": 8,
    },
    "combinatorics": {
        "prompt": (
            "Профиль: комбинаторика.\n"
            "Обязательные разделы:\n"
            "`## План`, `## 1. Мотивация`, `## 2. Определения`, `## 3. Комбинаторные тождества и факты`, "
            "`## 4. Примеры подсчета`, `## 5. Типичные ловушки`, "
            "`## 6. Что важно для поступления в ШАД`, `## 7. Итоги`, `## 8. Вопросы для самопроверки`.\n"
            "В самопроверке минимум 8 вопросов."
        ),
        "required_markers": [
            "## План",
            "## 1. Мотивация",
            "## 2. Определения",
            "## 3. Комбинаторные тождества и факты",
            "## 4. Примеры подсчета",
            "## 5. Типичные ловушки",
            "## 6. Что важно для поступления в ШАД",
            "## 7. Итоги",
            "## 8. Вопросы для самопроверки",
        ],
        "self_check_heading_regex": r"## 8\.\s*Вопросы для самопроверки(?P<body>[\s\S]*)$",
        "min_questions": 8,
    },
    "probability": {
        "prompt": (
            "Профиль: теория вероятностей.\n"
            "Обязательные разделы:\n"
            "`## План`, `## 1. Вероятностная модель и мотивация`, `## 2. Определения`, "
            "`## 3. Ключевые формулы`, `## 4. Распределения и примеры`, "
            "`## 5. Типичные ошибки`, `## 6. Что важно для поступления в ШАД`, "
            "`## 7. Итоги`, `## 8. Вопросы для самопроверки`.\n"
            "В самопроверке минимум 8 вопросов."
        ),
        "required_markers": [
            "## План",
            "## 1. Вероятностная модель и мотивация",
            "## 2. Определения",
            "## 3. Ключевые формулы",
            "## 4. Распределения и примеры",
            "## 5. Типичные ошибки",
            "## 6. Что важно для поступления в ШАД",
            "## 7. Итоги",
            "## 8. Вопросы для самопроверки",
        ],
        "self_check_heading_regex": r"## 8\.\s*Вопросы для самопроверки(?P<body>[\s\S]*)$",
        "min_questions": 8,
    },
    "algo-programming": {
        "prompt": (
            "Профиль: программирование/алгоритмы.\n"
            "Обязательные разделы:\n"
            "`## План`, `## 1. Постановка и мотивация`, `## 2. Определения и модель вычислений`, "
            "`## 3. Базовая идея алгоритма`, `## 4. Псевдокод и реализация`, "
            "`## 5. Корректность`, `## 6. Сложность по времени и памяти`, "
            "`## 7. Типичные ошибки и edge cases`, `## 8. Что важно для поступления в ШАД`, "
            "`## 9. Итоги`, `## 10. Вопросы для самопроверки`.\n"
            "В самопроверке минимум 8 вопросов."
        ),
        "required_markers": [
            "## План",
            "## 1. Постановка и мотивация",
            "## 2. Определения и модель вычислений",
            "## 3. Базовая идея алгоритма",
            "## 4. Псевдокод и реализация",
            "## 5. Корректность",
            "## 6. Сложность по времени и памяти",
            "## 7. Типичные ошибки и edge cases",
            "## 8. Что важно для поступления в ШАД",
            "## 9. Итоги",
            "## 10. Вопросы для самопроверки",
        ],
        "self_check_heading_regex": r"## 10\.\s*Вопросы для самопроверки(?P<body>[\s\S]*)$",
        "min_questions": 8,
    },
    "data-analysis": {
        "prompt": (
            "Профиль: анализ данных / ML.\n"
            "Обязательные разделы:\n"
            "`## План`, `## 1. Постановка задачи`, `## 2. Данные и признаки`, "
            "`## 3. Базовые модели и baseline`, `## 4. Метрики и валидация`, "
            "`## 5. Переобучение и регуляризация`, `## 6. Типичные ошибки в экспериментах`, "
            "`## 7. Что важно для поступления в ШАД`, `## 8. Итоги`, `## 9. Вопросы для самопроверки`.\n"
            "В самопроверке минимум 8 вопросов."
        ),
        "required_markers": [
            "## План",
            "## 1. Постановка задачи",
            "## 2. Данные и признаки",
            "## 3. Базовые модели и baseline",
            "## 4. Метрики и валидация",
            "## 5. Переобучение и регуляризация",
            "## 6. Типичные ошибки в экспериментах",
            "## 7. Что важно для поступления в ШАД",
            "## 8. Итоги",
            "## 9. Вопросы для самопроверки",
        ],
        "self_check_heading_regex": r"## 9\.\s*Вопросы для самопроверки(?P<body>[\s\S]*)$",
        "min_questions": 8,
    },
}


def env_required(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"Отсутствует обязательная переменная окружения: {name}")
    return value


def env_optional(name: str, default: str) -> str:
    value = os.getenv(name, "").strip()
    return value if value else default


def load_dotenv_if_available(dotenv_path: Path) -> None:
    try:
        from dotenv import load_dotenv  # type: ignore

        if dotenv_path.exists():
            load_dotenv(dotenv_path)
        return
    except ModuleNotFoundError:
        pass

    if not dotenv_path.exists():
        return

    for raw_line in dotenv_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def slugify(value: str) -> str:
    slug = value.lower().strip()
    slug = re.sub(r"\s+", "_", slug)
    slug = re.sub(r"[^\w\-]+", "", slug)
    slug = slug.strip("_-")
    return slug or "lecture"


def make_safe_slug(value: str, max_length: int = MAX_FOLDER_SLUG_LEN) -> str:
    slug = slugify(value)
    if len(slug) <= max_length:
        return slug

    digest = hashlib.sha1(slug.encode("utf-8")).hexdigest()[:8]
    suffix = f"_{digest}"
    budget = max(8, max_length - len(suffix))
    parts = [part for part in slug.split("_") if part]

    shortened_parts: List[str] = []
    current_length = 0
    for part in parts:
        extra = len(part) if not shortened_parts else len(part) + 1
        if current_length + extra > budget:
            break
        shortened_parts.append(part)
        current_length += extra

    shortened = "_".join(shortened_parts).strip("_")
    if len(shortened) < 8:
        shortened = slug[:budget].rstrip("_-")
    shortened = shortened[:budget].rstrip("_-")
    return f"{shortened}{suffix}" if shortened else f"lecture{suffix}"


def extract_message_content(data: Dict[str, Any]) -> str:
    choices = data.get("choices", [])
    if not choices:
        raise RuntimeError(f"Пустой ответ модели: {json.dumps(data, ensure_ascii=False)[:500]}")

    msg = choices[0].get("message", {})
    content = msg.get("content", "")
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        text_blocks: List[str] = []
        for block in content:
            if isinstance(block, dict) and block.get("type") == "text":
                text = str(block.get("text", "")).strip()
                if text:
                    text_blocks.append(text)
        if text_blocks:
            return "\n\n".join(text_blocks).strip()
    raise RuntimeError(f"Не удалось извлечь текст из ответа: {json.dumps(msg, ensure_ascii=False)[:500]}")


def load_guide_text(rules_file: Path) -> str:
    if not rules_file.exists():
        return ""
    return rules_file.read_text(encoding="utf-8")


def extract_top_level_sections(markdown_text: str) -> Dict[str, str]:
    matches = list(re.finditer(r"^##\s+.+$", markdown_text, flags=re.MULTILINE))
    if not matches:
        return {}

    sections: Dict[str, str] = {}
    for index, match in enumerate(matches):
        start = match.start()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(markdown_text)
        heading = match.group(0).strip()
        sections[heading] = markdown_text[start:end].strip()
    return sections


def extract_guide_excerpt(guide_text: str, kind: str) -> str:
    if not guide_text:
        return ""

    sections = extract_top_level_sections(guide_text)
    selected = [sections[h] for h in GUIDE_SECTIONS[kind] if h in sections]
    return "\n\n".join(selected).strip() or guide_text


def build_lesson_system_prompt(profile: str, guide_text: str) -> str:
    profile_prompt = PROFILE_SPECS[profile]["prompt"]
    lesson_guide = extract_guide_excerpt(guide_text, "lesson")
    if not guide_text:
        return f"{BASE_RULES}\n\n{profile_prompt}"
    return (
        f"{BASE_RULES}\n\n{profile_prompt}\n\n"
        "Ниже официальный guide. Следуй ему при конфликте в сторону более строгого формата.\n\n"
        f"{lesson_guide}"
    )


def build_qa_system_prompt(guide_text: str) -> str:
    qa_guide = extract_guide_excerpt(guide_text, "qa")
    if not guide_text:
        return QA_BASE_RULES
    return (
        f"{QA_BASE_RULES}\n\n"
        "Ниже официальный guide по lesson/qa. Следуй ему:\n\n"
        f"{qa_guide}"
    )


def extract_level2_headings(markdown_text: str) -> List[str]:
    return [m.group(0).strip() for m in re.finditer(r"^##\s+.+$", markdown_text, flags=re.MULTILINE)]


def validate_lesson_markdown(lesson_md: str, profile: str) -> List[str]:
    spec = PROFILE_SPECS[profile]
    stripped = lesson_md.strip()
    errors: List[str] = []
    headings = extract_level2_headings(stripped)
    heading_positions = {heading: index for index, heading in enumerate(headings)}

    if not stripped.startswith("# Лекция:"):
        errors.append("Файл должен начинаться с заголовка `# Лекция: ...`.")
    for marker in spec["required_markers"]:
        if marker not in heading_positions:
            errors.append(f"Не найден обязательный раздел: `{marker}`.")
    if not errors:
        positions = [heading_positions[marker] for marker in spec["required_markers"]]
        if positions != sorted(positions):
            errors.append("Обязательные разделы идут в неправильном порядке.")
    if "assets/" in stripped:
        errors.append("В lesson.md не должно быть ссылок на assets/*.")
    if re.search(r"^\s+[$]{2}", stripped, flags=re.MULTILINE):
        errors.append("Обнаружен блочный `$$` внутри отступа (возможный список).")

    self_check_block = re.search(spec["self_check_heading_regex"], stripped, flags=re.IGNORECASE)
    if not self_check_block:
        errors.append("Не найден блок `Вопросы для самопроверки` с корректным номером раздела.")
        return errors

    body = self_check_block.group("body")
    question_count = len(re.findall(r"^(?:\d+\.|-)\s+\S", body, flags=re.MULTILINE))
    if question_count < int(spec["min_questions"]):
        errors.append(f"В самопроверке должно быть минимум {int(spec['min_questions'])} вопросов.")
    return errors


def validate_qa_markdown(qa_md: str) -> List[str]:
    stripped = qa_md.strip()
    errors: List[str] = []
    task_matches = list(re.finditer(r"^##\s+Задача\s+(\d+)\..*$", stripped, flags=re.MULTILINE | re.IGNORECASE))
    task_count = len(task_matches)
    if task_count != 10:
        errors.append(f"В qa.md должно быть ровно 10 задач, найдено: {task_count}.")

    if task_matches:
        task_numbers = [int(match.group(1)) for match in task_matches]
        if task_numbers != list(range(1, len(task_numbers) + 1)):
            errors.append("Задачи должны быть последовательно пронумерованы, начиная с 1.")

    for index, match in enumerate(task_matches, start=1):
        start = match.start()
        end = task_matches[index].start() if index < len(task_matches) else len(stripped)
        task_block = stripped[start:end]
        if not re.search(r"^###\s+Решение\s*$", task_block, flags=re.MULTILINE):
            errors.append(f"У задачи {index} отсутствует блок `### Решение`.")
        if not re.search(r"^###\s+Ответ\s*$", task_block, flags=re.MULTILINE):
            errors.append(f"У задачи {index} отсутствует блок `### Ответ`.")
    return errors


def request_markdown(
    *,
    model_name: str,
    system_prompt: str,
    user_prompt: str,
    temperature: float,
    timeout_sec: int,
    max_attempts: int,
    validate: Callable[[str], List[str]],
) -> str:
    api_key = env_required("LLM_API_KEY")
    base_url = env_optional("LLM_BASE_URL", "https://openrouter.ai/api/v1").rstrip("/")
    referer = env_optional("LLM_HTTP_REFERER", "https://local/mlib-lecture-generator")
    app_title = env_optional("LLM_APP_TITLE", "MLIB lecture generator")

    dynamic_system = system_prompt
    dynamic_user = user_prompt
    last_error: str | None = None

    for attempt in range(1, max_attempts + 1):
        try:
            response = requests.post(
                f"{base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": referer,
                    "X-Title": app_title,
                },
                json={
                    "model": model_name,
                    "messages": [
                        {"role": "system", "content": dynamic_system},
                        {"role": "user", "content": dynamic_user},
                    ],
                    "temperature": temperature,
                },
                timeout=timeout_sec,
            )
            if response.status_code != 200:
                raise RuntimeError(f"HTTP {response.status_code}: {response.text}")

            try:
                data = response.json()
            except requests.exceptions.JSONDecodeError as exc:
                raise RuntimeError(f"Невалидный JSON от OpenRouter: {exc}") from exc

            text = extract_message_content(data)
            if not text:
                raise RuntimeError("Модель вернула пустой текст.")

            errors = validate(text)
            if not errors:
                return text

            if attempt == max_attempts:
                raise RuntimeError("Нарушены требования:\n- " + "\n- ".join(errors))

            violations = "\n- ".join(errors)
            dynamic_system = (
                f"{system_prompt}\n\n"
                "ВАЖНО: исправь нарушения из последней попытки. Они обязательны.\n"
                f"- {violations}"
            )
            dynamic_user = (
                f"{user_prompt}\n\n"
                "Перегенерируй полностью. Исправь нарушения:\n"
                f"- {violations}"
            )
            time.sleep(min(2 * attempt, 6))
        except (requests.RequestException, RuntimeError) as exc:
            last_error = str(exc)
            if attempt == max_attempts:
                break
            time.sleep(min(2 * attempt, 6))

    raise RuntimeError(last_error or "Неизвестная ошибка генерации.")


def discover_next_topic_number(section_dir: Path) -> int:
    max_index = 0
    if not section_dir.exists():
        return 1
    for child in section_dir.iterdir():
        if not child.is_dir():
            continue
        match = re.match(r"^(\d+)_", child.name)
        if not match:
            continue
        max_index = max(max_index, int(match.group(1)))
    return max_index + 1


def resolve_target_dir(
    *,
    section: str,
    slug: str,
    out_dir: Path | None,
    topic_number: int | None,
) -> tuple[Path, int, str]:
    if out_dir is not None:
        base = out_dir
    else:
        base = SHAD_ROOT / SECTION_SPECS[section]["folder"]
    number = topic_number or discover_next_topic_number(base)
    folder_name = f"{number}_{slug}"
    return base / folder_name, number, folder_name


def read_text_if_exists(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8").strip()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Генерация SHAD lesson.md (и опционально qa.md) через OpenRouter."
    )
    parser.add_argument("lecture_title", help="Название темы лекции.")
    parser.add_argument("--section", choices=tuple(SECTION_SPECS.keys()), required=True)
    parser.add_argument("--slug", default=None, help="Slug темы. По умолчанию из названия.")
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=None,
        help="Опциональный override директории раздела (для отладки).",
    )
    parser.add_argument(
        "--topic-number",
        type=int,
        default=None,
        help="Явно задать номер темы в разделе. По умолчанию max+1.",
    )
    parser.add_argument("--dotenv", type=Path, default=DEFAULT_DOTENV)
    parser.add_argument("--rules-file", type=Path, default=DEFAULT_RULES_FILE)
    parser.add_argument("--model", default=None, help="Переопределить LLM_LECTURE_MODEL.")
    parser.add_argument("--temperature", type=float, default=0.4)
    parser.add_argument("--timeout-sec", type=int, default=240)
    parser.add_argument("--max-attempts", type=int, default=3)
    parser.add_argument("--generate-qa", action="store_true", help="Сгенерировать qa.md.")
    parser.add_argument("--qa-only", action="store_true", help="Генерировать только qa.md.")
    parser.add_argument("--skip-existing", action="store_true", help="Не перегенерировать существующие файлы.")
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    load_dotenv_if_available(args.dotenv.resolve())

    lecture_title = args.lecture_title.strip()
    if not lecture_title:
        print("Пустое название лекции недопустимо.", file=sys.stderr)
        return 2

    if args.qa_only:
        args.generate_qa = True

    profile = SECTION_SPECS[args.section]["profile"]
    requested_slug = (args.slug or lecture_title).strip()
    slug = make_safe_slug(requested_slug)
    target_dir, topic_number, folder_name = resolve_target_dir(
        section=args.section,
        slug=slug,
        out_dir=args.out_dir.resolve() if args.out_dir else None,
        topic_number=args.topic_number,
    )
    lesson_path = target_dir / "lesson.md"
    qa_path = target_dir / "qa.md"

    if args.dry_run:
        guide_text = load_guide_text(args.rules_file.resolve())
        print(f"title: {lecture_title}")
        print(f"section: {args.section}")
        print(f"profile: {profile}")
        print(f"requested_slug: {requested_slug}")
        print(f"safe_slug: {slug}")
        print(f"topic_number: {topic_number}")
        print(f"folder: {folder_name}")
        print(f"model: {args.model or env_optional('LLM_LECTURE_MODEL', '(from env at runtime)')}")
        print(f"rules_file: {args.rules_file.resolve()}")
        print(f"rules_chars: {len(guide_text)}")
        print(f"lesson_output: {lesson_path}")
        if args.generate_qa:
            print(f"qa_output: {qa_path}")
        return 0

    generate_lesson = not args.qa_only
    generate_qa = args.generate_qa

    if generate_lesson and lesson_path.exists() and not args.overwrite and not args.skip_existing:
        print(f"Файл уже существует: {lesson_path}\nДобавьте --overwrite.", file=sys.stderr)
        return 2
    if generate_qa and qa_path.exists() and not args.overwrite and not args.skip_existing:
        print(f"Файл уже существует: {qa_path}\nДобавьте --overwrite.", file=sys.stderr)
        return 2

    model_name = args.model or env_optional("LLM_LECTURE_MODEL", "")
    if not model_name:
        print("Задайте LLM_LECTURE_MODEL в окружении или передайте --model.", file=sys.stderr)
        return 2

    target_dir.mkdir(parents=True, exist_ok=True)
    guide_text = load_guide_text(args.rules_file.resolve())
    lesson_md = ""

    if generate_lesson:
        if lesson_path.exists() and args.skip_existing and not args.overwrite:
            lesson_md = read_text_if_exists(lesson_path)
            print(f"Пропущено (уже существует): {lesson_path}")
        else:
            lesson_md = request_markdown(
                model_name=model_name,
                system_prompt=build_lesson_system_prompt(profile, guide_text),
                user_prompt=(
                    f"Тема: {lecture_title}\n"
                    f"Раздел программы: {args.section}\n"
                    f"Профиль: {profile}\n"
                    "Сгенерируй финальный lesson.md. "
                    "Лекция должна быть содержательной, с рабочими примерами и без пустых разделов."
                ),
                temperature=args.temperature,
                timeout_sec=args.timeout_sec,
                max_attempts=args.max_attempts,
                validate=lambda text: validate_lesson_markdown(text, profile),
            ).strip()
            lesson_path.write_text(lesson_md + "\n", encoding="utf-8")
            print(f"Сгенерировано: {lesson_path}")
    else:
        lesson_md = read_text_if_exists(lesson_path)

    if generate_qa:
        if qa_path.exists() and args.skip_existing and not args.overwrite:
            print(f"Пропущено (уже существует): {qa_path}")
        else:
            qa_context = ""
            if lesson_md:
                qa_context = (
                    "\n\nНиже lesson.md по теме. Сделай задачи согласованными с этой лекцией:\n\n"
                    f"{lesson_md}"
                )
            qa_md = request_markdown(
                model_name=model_name,
                system_prompt=build_qa_system_prompt(guide_text),
                user_prompt=(
                    f"Тема: {lecture_title}\n"
                    f"Раздел программы: {args.section}\n"
                    "Сгенерируй qa.md в формате: 10 задач, у каждой `### Решение` и `### Ответ`."
                    f"{qa_context}"
                ),
                temperature=args.temperature,
                timeout_sec=args.timeout_sec,
                max_attempts=args.max_attempts,
                validate=validate_qa_markdown,
            ).strip()
            qa_path.write_text(qa_md + "\n", encoding="utf-8")
            print(f"Сгенерировано: {qa_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
