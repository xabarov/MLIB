"""
Генерация иллюстраций для лекций MLIB/SHAD через OpenRouter (image modalities).

Переменные окружения (см. `.env` в корне пакета `mlib`):
  LLM_API_KEY                  — ключ OpenRouter
  LLM_BASE_URL                 — например https://openrouter.ai/api/v1
  LLM_VISUAL_GENERATION_MODEL  — модель с поддержкой image output

Опционально:
  LLM_HTTP_REFERER  — заголовок HTTP-Referer для OpenRouter (по умолчанию file://mlib)
  LLM_APP_TITLE     — заголовок X-Title (по умолчанию MLIB lecture visuals)

Режимы:
  * Пакет из JSON (--jobs)
  * Один кадр из CLI (--prompt / --prompt-file) + --slug

Стиль по умолчанию: суффикс из SHAD/lecture_visual_generation/lecture_visual_prompt_suffix.txt
(см. SHAD/lecture_visual_generation/lecture_visual_design_system.md).
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

import requests

PROJECT_ROOT = Path(__file__).resolve().parent
DEFAULT_DOTENV = PROJECT_ROOT / ".env"
LECTURE_VISUAL_DIR = PROJECT_ROOT / "SHAD" / "lecture_visual_generation"
DEFAULT_STYLE_SUFFIX_FILE = LECTURE_VISUAL_DIR / "lecture_visual_prompt_suffix.txt"
DEFAULT_EXAMPLE_JOBS = LECTURE_VISUAL_DIR / "lecture_images.example.json"
DEFAULT_OUT_DIR = PROJECT_ROOT / "SHAD" / "_generated_lecture_images"


def env_required(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"Отсутствует обязательная переменная окружения: {name}")
    return value


def env_optional(name: str, default: str) -> str:
    value = os.getenv(name, "").strip()
    return value if value else default


def load_dotenv_if_available(dotenv_path: Path) -> None:
    """Загружает .env через python-dotenv либо простым парсером строк KEY=VAL."""
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
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


def read_text_file(path: Path) -> str:
    return path.read_text(encoding="utf-8").strip()


def load_style_suffix(path: Path) -> str:
    if not path.exists():
        return ""
    return read_text_file(path).strip()


@dataclass(frozen=True)
class ImageJob:
    slug: str
    prompt: str
    filename_base: str
    append_style_suffix: bool

    def full_prompt(self, style_suffix: str) -> str:
        p = self.prompt.strip()
        if self.append_style_suffix and style_suffix:
            return f"{p}\n\n{style_suffix}".strip()
        return p


def collect_images_from_chat_response(data: Dict[str, Any]) -> List[str]:
    images: List[str] = []
    for choice in data.get("choices", []):
        msg = choice.get("message", {})
        for img_url in msg.get("images", []):
            if isinstance(img_url, dict):
                url = img_url.get("image_url", {}).get("url", "") or img_url.get("url", "")
                if url:
                    images.append(url)
                    continue
            if isinstance(img_url, str):
                images.append(img_url)
        content = msg.get("content", "")
        if isinstance(content, list):
            for block in content:
                if isinstance(block, dict) and block.get("type") == "image_url":
                    url = block.get("image_url", {}).get("url", "")
                    if url:
                        images.append(url)
    return images


def decode_first_image_payload(img_data_url: str | Dict[str, Any]) -> Tuple[bytes, str]:
    if isinstance(img_data_url, dict):
        if img_data_url.get("type") == "image_url":
            img_data_url = img_data_url.get("image_url", {}).get("url", "") or ""
        else:
            img_data_url = img_data_url.get("url") or img_data_url.get("b64_json") or ""

    if isinstance(img_data_url, dict):
        raise ValueError("Unexpected nested image payload")

    ext = ".png"
    if img_data_url.startswith("data:"):
        header, b64 = img_data_url.split(",", 1)
        if ";base64" in header:
            mime = header[5:].split(";", 1)[0].strip().lower()
            ext = {
                "image/png": ".png",
                "image/jpeg": ".jpg",
                "image/jpg": ".jpg",
                "image/webp": ".webp",
            }.get(mime, ".png")
    else:
        b64 = img_data_url

    return base64.b64decode(b64), ext


def post_openrouter_image(
    *,
    prompt: str,
    timeout_sec: int = 180,
    max_attempts: int = 3,
    model: str | None = None,
) -> Tuple[bytes, str]:
    api_key = env_required("LLM_API_KEY")
    base_url = env_optional("LLM_BASE_URL", "https://openrouter.ai/api/v1").rstrip("/")
    model_name = model or env_required("LLM_VISUAL_GENERATION_MODEL")
    referer = env_optional("LLM_HTTP_REFERER", "https://local/mlib-lecture-visuals")
    title = env_optional("LLM_APP_TITLE", "MLIB lecture visuals")

    last_error: str | None = None
    for attempt in range(1, max_attempts + 1):
        try:
            response = requests.post(
                f"{base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": referer,
                    "X-Title": title,
                },
                json={
                    "model": model_name,
                    "messages": [{"role": "user", "content": prompt}],
                    "modalities": ["image", "text"],
                },
                timeout=timeout_sec,
            )

            if response.status_code != 200:
                raise RuntimeError(f"HTTP {response.status_code}: {response.text}")

            try:
                data = response.json()
            except requests.exceptions.JSONDecodeError as exc:
                snippet = response.text[:500]
                raise RuntimeError(
                    f"Невалидный JSON от OpenRouter (попытка {attempt}/{max_attempts}): {exc}. "
                    f"Фрагмент тела: {snippet!r}"
                ) from exc

            images = collect_images_from_chat_response(data)
            if not images:
                raise RuntimeError(
                    "Изображение не найдено в ответе:\n"
                    f"{json.dumps(data, ensure_ascii=False, indent=2)}"
                )

            return decode_first_image_payload(images[0])
        except (requests.RequestException, RuntimeError, ValueError) as exc:
            last_error = str(exc)
            if attempt == max_attempts:
                break
            time.sleep(min(2 * attempt, 6))

    raise RuntimeError(last_error or "Неизвестная ошибка запроса изображения")


def parse_jobs_file(path: Path) -> Tuple[List[ImageJob], Dict[str, Any]]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    defaults: Dict[str, Any] = {}
    if isinstance(raw, dict) and "jobs" in raw:
        defaults = {k: v for k, v in raw.items() if k != "jobs"}
        items = raw["jobs"]
    elif isinstance(raw, list):
        items = raw
    else:
        raise ValueError("Ожидался JSON-массив заданий или объект с ключом 'jobs'")

    default_append = bool(defaults.get("append_style_suffix", True))
    jobs: List[ImageJob] = []
    for i, item in enumerate(items):
        if not isinstance(item, dict):
            raise ValueError(f"jobs[{i}]: ожидался объект")
        slug = str(item.get("slug", "")).strip()
        if not slug:
            raise ValueError(f"jobs[{i}]: требуется непустой slug")
        prompt = str(item.get("prompt", "")).strip()
        if not prompt:
            raise ValueError(f"jobs[{i}]: требуется prompt")
        filename_base = str(item.get("filename_base", slug)).strip() or slug
        append = bool(item.get("append_style_suffix", default_append))
        jobs.append(
            ImageJob(
                slug=slug,
                prompt=prompt,
                filename_base=filename_base,
                append_style_suffix=append,
            )
        )
    return jobs, defaults


def ensure_directory(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def write_manifest(
    out_dir: Path,
    jobs: Iterable[ImageJob],
    *,
    model_name: str,
    style_suffix_file: str,
    extra: Dict[str, Any] | None = None,
) -> None:
    manifest: Dict[str, Any] = {
        "model": model_name,
        "style_suffix_file": style_suffix_file,
        "generated_at_epoch": int(time.time()),
        "jobs": [
            {
                "slug": j.slug,
                "filename_base": j.filename_base,
                "append_style_suffix": j.append_style_suffix,
            }
            for j in jobs
        ],
    }
    if extra:
        manifest["job_file_metadata"] = extra
    (out_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Генерация иллюстраций для лекций через OpenRouter (LLM_* env)."
    )
    src = p.add_mutually_exclusive_group(required=False)
    src.add_argument(
        "--jobs",
        type=Path,
        metavar="PATH",
        help="JSON со списком заданий (массив или {defaults, jobs}).",
    )
    src.add_argument(
        "--prompt",
        help="Одиночный промпт (строка). Требуется --slug.",
    )
    p.add_argument(
        "--prompt-file",
        type=Path,
        metavar="PATH",
        help="Файл с промптом для одиночной генерации (UTF-8). Имеет приоритет над --prompt.",
    )
    p.add_argument(
        "--slug",
        help="Идентификатор задания и база имени файла при одиночном режиме.",
    )
    p.add_argument(
        "--filename-base",
        help="Имя файла без расширения (одиночный режим); по умолчанию совпадает с --slug.",
    )
    p.add_argument(
        "--out-dir",
        type=Path,
        default=DEFAULT_OUT_DIR,
        help=f"Каталог для PNG/JPG (по умолчанию: {DEFAULT_OUT_DIR}).",
    )
    p.add_argument(
        "--dotenv",
        type=Path,
        default=DEFAULT_DOTENV,
        help=f"Путь к .env (по умолчанию: {DEFAULT_DOTENV}).",
    )
    p.add_argument(
        "--suffix-file",
        type=Path,
        default=DEFAULT_STYLE_SUFFIX_FILE,
        help="Текстовый суффикс стиля; пустой файл или несуществующий — без суффикса.",
    )
    p.add_argument(
        "--no-style-suffix",
        action="store_true",
        help="Не добавлять суффикс стиля ни к одному заданию.",
    )
    p.add_argument(
        "--only",
        action="append",
        default=[],
        metavar="SLUG",
        help="Обработать только указанные slug (можно повторять).",
    )
    p.add_argument(
        "--timeout-sec",
        type=int,
        default=180,
        help="Таймаут HTTP на одно изображение.",
    )
    p.add_argument(
        "--model",
        default=None,
        help="Переопределить LLM_VISUAL_GENERATION_MODEL для этого запуска.",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Только вывести разрешённые промпты и выйти (без сети).",
    )
    p.add_argument(
        "--print-example-path",
        action="store_true",
        help=f"Вывести путь к примеру {DEFAULT_EXAMPLE_JOBS} и выйти.",
    )
    return p.parse_args()


def build_single_job(args: argparse.Namespace, append_suffix: bool) -> ImageJob:
    if not args.slug:
        print("Одиночный режим: укажите --slug (и --prompt или --prompt-file).", file=sys.stderr)
        raise SystemExit(2)
    if args.prompt_file:
        prompt = read_text_file(args.prompt_file)
    elif args.prompt:
        prompt = args.prompt
    else:
        print("Одиночный режим: задайте --prompt или --prompt-file.", file=sys.stderr)
        raise SystemExit(2)
    base = (args.filename_base or args.slug).strip()
    return ImageJob(
        slug=args.slug.strip(),
        prompt=prompt,
        filename_base=base,
        append_style_suffix=append_suffix,
    )


def main() -> int:
    args = parse_args()
    if args.print_example_path:
        print(DEFAULT_EXAMPLE_JOBS)
        return 0

    load_dotenv_if_available(args.dotenv.resolve())

    style_path = args.suffix_file.resolve()
    style_suffix = "" if args.no_style_suffix else load_style_suffix(style_path)

    model_name = args.model or env_optional(
        "LLM_VISUAL_GENERATION_MODEL",
        "",
    )
    if not args.dry_run and not model_name:
        print(
            "Задайте LLM_VISUAL_GENERATION_MODEL в окружении или передайте --model.",
            file=sys.stderr,
        )
        return 2

    jobs: List[ImageJob] = []
    job_file_meta: Dict[str, Any] = {}

    if args.jobs:
        jobs, job_file_meta = parse_jobs_file(args.jobs.resolve())
    elif args.prompt or args.prompt_file:
        append = not args.no_style_suffix
        jobs = [build_single_job(args, append)]
    else:
        print(
            "Укажите --jobs ФАЙЛ.json или пару (--prompt/--prompt-file) + --slug.\n"
            f"Пример заданий: {DEFAULT_EXAMPLE_JOBS}\n"
            f"Стиль по умолчанию: {DEFAULT_STYLE_SUFFIX_FILE}\n"
            f"Документация стиля: {LECTURE_VISUAL_DIR / 'lecture_visual_design_system.md'}",
            file=sys.stderr,
        )
        return 2

    selected = {s.strip() for s in (args.only or []) if s.strip()}
    if selected:
        jobs = [j for j in jobs if j.slug in selected]
        if not jobs:
            print(f"Ни одно задание не совпало с --only={sorted(selected)}", file=sys.stderr)
            return 2

    out_dir = args.out_dir.resolve()
    ensure_directory(out_dir)

    write_manifest(
        out_dir,
        jobs,
        model_name=model_name or "(dry-run)",
        style_suffix_file=str(style_path) if style_suffix else "",
        extra=job_file_meta if job_file_meta else None,
    )

    if args.dry_run:
        for j in jobs:
            print("---", j.slug, "---")
            print(j.full_prompt(style_suffix))
            print()
        return 0

    failures: List[Tuple[str, str]] = []
    for index, job in enumerate(jobs, start=1):
        final_prompt = job.full_prompt(style_suffix)
        print(f"[{index}/{len(jobs)}] {job.slug}  (model={model_name})")
        try:
            image_bytes, ext = post_openrouter_image(
                prompt=final_prompt,
                timeout_sec=args.timeout_sec,
                model=model_name,
            )
            out_path = out_dir / f"{job.filename_base}{ext}"
            out_path.write_bytes(image_bytes)
            print(f"  -> {out_path}")
        except Exception as exc:  # noqa: BLE001
            failures.append((job.slug, str(exc)))
            print(f"  FAILED {job.slug}: {exc}", file=sys.stderr)

    if failures:
        print("\nЗавершено с ошибками:", file=sys.stderr)
        for slug, err in failures:
            print(f"  - {slug}: {err}", file=sys.stderr)
        return 1

    print(f"\nГотово: {len(jobs)} файл(ов) в {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
