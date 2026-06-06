#!/usr/bin/env python3
"""Generate SHAD interactive game PNG assets through OpenRouter image chat."""

from __future__ import annotations

import argparse
import base64
import json
import os
import re
import sys
import time
import urllib.request
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from typing import Any

from PIL import Image


REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_OUT_DIR = REPO_ROOT / "SHAD" / "interactive" / "src" / "assets" / "game"
DEFAULT_MODEL = "openai/gpt-5.4-image-2"
DEFAULT_TOOL_CALLER_MODEL = "openai/gpt-5.5"


@dataclass(frozen=True)
class AssetSpec:
    filename: str
    title: str
    prompt: str
    use_reference: bool = False


def model_slug(model: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "-", model).strip("-")


STYLE_SPEC = """
Use case: stylized-concept
Asset type: transparent PNG UI/game asset for a math learning web app.
Visual direction: warm paper-and-ink mathematical workshop, refined toy-like
2.5D cutout, crisp silhouette, subtle coordinate-grid details, charcoal ink
lines, muted accents from this palette: #d97757, #6a9bcc, #788c5d, #7c6ccf,
#f8f3dc.
Background: true transparent background with alpha channel. No white box, no
solid background, no floor, no cast shadow, no contact shadow, no reflection.
Composition: centered single asset, generous transparent padding, readable at
64px and polished at 256px.
Avoid: text, letters, numbers, logos, watermarks, animals, humans, robots,
photorealism, neon glow, busy details, stock-icon style, gradients as the main
look.
""".strip()


ASSETS: list[AssetSpec] = [
    AssetSpec(
        "reference/mebi-model-sheet-v2.png",
        "Mebi friendly canonical model sheet",
        """
Create a canonical model sheet for Mebi, a friendly abstract educational
mascot and invariant guide for an interactive SHAD math/programming learning
app.

Show one consistent character only, repeated on the sheet as: front view,
three-quarter view, small silhouette, and five tiny expression thumbnails
for idle, success, hint, warning, and thinking. Keep all variants visibly the
same character.

Character design: a warm Mobius-ribbon body folded into a small compass-pointer
shape, but with a clear friendly face: two small expressive dot eyes and a
simple tiny mouth. The face must be part of the character, not floating nearby.
Add a small pivot-point core and subtle coordinate-grid etching on the ribbon.
It should look like a kind living mathematical instrument and study companion,
not an animal, not a robot, not a human, not a generic app mascot.

Important: no external emotion icons, no exclamation marks, no question marks,
no speech bubbles, no labels, no text, no numbers, and no watermark. Express
the emotions only through Mebi's eyes, mouth, posture, and ribbon shape.

Arrange the views cleanly with generous transparent padding so the image can
be reused as a reference for later pose generation.
""".strip(),
    ),
    AssetSpec(
        "reference/mebi-model-sheet.png",
        "Mebi canonical model sheet",
        """
Create a canonical model sheet for Mebi, an abstract educational mascot and
invariant guide for an interactive SHAD math/programming learning app.

Show one consistent character only, repeated on the sheet as: front view,
three-quarter view, small silhouette, and five tiny expression thumbnails
for idle, success, hint, warning, and thinking. Keep all variants visibly the
same character.

Character design: a friendly Mobius-ribbon loop folded into a compass pointer,
one tiny bright dot-eye, a small pivot-point core, subtle coordinate-grid
etching on the ribbon, warm paper-and-ink feel. It should look like a living
mathematical instrument, not an animal, not a robot, not a human, not a generic
app mascot.

The sheet must have no labels, no text, no numbers, and no watermark. Arrange
the views cleanly with generous transparent padding so the image can be reused
as a reference for later pose generation.
""".strip(),
    ),
    AssetSpec(
        "mebi-idle-v2.png",
        "Mebi idle guide v2",
        """
Using the attached Mebi model sheet as the strict character reference, create
exactly one large centered Mebi in the idle state. Preserve the same character
identity, ribbon silhouette, proportions, palette, pivot-point core, coordinate
etching, two dot eyes, and small mouth. Calm idle pose, slight curious tilt,
friendly and ready to help. Do not create a model sheet. Do not create copies,
miniatures, thumbnails, extra versions, icons, hands, props, text, labels, or
symbols. One character only.
""".strip(),
        use_reference=True,
    ),
    AssetSpec(
        "mebi-success-v2.png",
        "Mebi success reaction v2",
        """
Using the attached Mebi model sheet as the strict character reference, create
exactly one large centered Mebi in the success state. Preserve identity, silhouette,
proportions, palette, pivot core, two eyes, and small mouth. Mebi looks pleased:
eyes warm, mouth smiling, ribbon posture open and lifted. Do not create a model
sheet. Do not create copies, miniatures, thumbnails, extra versions, checkmarks,
stars, icons, hands, props, text, labels, or symbols. One character only.
""".strip(),
        use_reference=True,
    ),
    AssetSpec(
        "mebi-hint-v2.png",
        "Mebi hint reaction v2",
        """
Using the attached Mebi model sheet as the strict character reference, create
exactly one large centered Mebi in the hint state. Preserve identity, silhouette,
proportions, palette, pivot core, two eyes, and small mouth. Mebi leans gently
as if suggesting the next move using only its own ribbon posture; expression is
kind and encouraging. Do not create a model sheet. Do not create copies,
miniatures, thumbnails, extra versions, speech bubbles, lightbulbs, pointing
hands, icons, props, text, labels, or symbols. One character only.
""".strip(),
        use_reference=True,
    ),
    AssetSpec(
        "mebi-warning-v2.png",
        "Mebi warning reaction v2",
        """
Using the attached Mebi model sheet as the strict character reference, create
exactly one large centered Mebi in the warning state. Preserve identity, silhouette,
proportions, palette, pivot core, two eyes, and small mouth. Mebi looks gently
concerned, with a small worried mouth and a slightly tightened ribbon posture.
Do not create a model sheet. Do not create copies, miniatures, thumbnails,
extra versions, exclamation marks, warning signs, icons, hands, props, text,
labels, or symbols. One character only.
""".strip(),
        use_reference=True,
    ),
    AssetSpec(
        "mebi-thinking-v2.png",
        "Mebi thinking reaction v2",
        """
Using the attached Mebi model sheet as the strict character reference, create
exactly one large centered Mebi in the thinking state. Preserve identity, silhouette,
proportions, palette, pivot core, two eyes, and small mouth. Mebi looks focused:
eyes slightly narrowed, small thoughtful mouth, ribbon curled inward like it is
considering a proof. Do not create a model sheet. Do not create copies,
miniatures, thumbnails, extra versions, question marks, thought bubbles, icons,
hands, props, text, labels, or symbols. One character only.
""".strip(),
        use_reference=True,
    ),
    AssetSpec(
        "variants/mebi-hint-gesture-v3.png",
        "Mebi hint gesture v3",
        """
Using the attached Mebi model sheet as the strict character reference, create
exactly one large centered Mebi in a clearly recognizable hint state. Preserve
identity, silhouette, proportions, palette, pivot core, two eyes, and small
mouth. Make the pose visibly different from idle: the ribbon body leans 25
degrees to the side, one upper ribbon tip curls upward like a gentle pointer,
eyes look toward that raised tip, and the mouth is a small encouraging smile.
No separate hands, no arrows, no speech bubble, no lightbulb, no copies, no
miniatures, no text, no labels, no symbols. One character only.
""".strip(),
        use_reference=True,
    ),
    AssetSpec(
        "variants/mebi-thinking-focused-v3.png",
        "Mebi thinking focused v3",
        """
Using the attached Mebi model sheet as the strict character reference, create
exactly one large centered Mebi in a focused thinking state. Preserve identity,
silhouette, proportions, palette, pivot core, two eyes, and small mouth. The
emotion must be curious concentration, not sadness: eyes look slightly upward
and inward, eyebrows/eyelids are attentive rather than drooping, mouth is a
tiny neutral curved line, ribbon body curls inward like it is considering a
proof. No tears, no frown, no sleepy face, no question mark, no thought bubble,
no copies, no miniatures, no text, no labels, no symbols. One character only.
""".strip(),
        use_reference=True,
    ),
    AssetSpec(
        "invariant-key.png",
        "Invariant key reward",
        """
Create a small reward icon called an invariant-key. It should feel like a
mathematical key made from a pivot point, a short coordinate axis, and a tiny
looped handle. Premium collectible, warm and precise, readable at 32px. No
literal text, no numbers.
""".strip(),
    ),
    AssetSpec(
        "mission-marker.png",
        "Mission marker",
        """
Create a compact mission marker for an interactive math game map. It should be
a compass-pin target built from a small coordinate grid, one highlighted point,
and a folded ribbon accent. Clear active-mission state, but no text, no flag,
no generic map-pin icon.
""".strip(),
    ),
]


def load_env(path: Path) -> None:
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def data_url_to_bytes(data_url: str) -> bytes:
    if data_url.startswith("data:"):
        _header, payload = data_url.split(",", 1)
        return base64.b64decode(payload)
    if data_url.startswith("http://") or data_url.startswith("https://"):
        with urllib.request.urlopen(data_url, timeout=120) as response:
            return response.read()
    if re.fullmatch(r"[A-Za-z0-9+/=\s]+", data_url[:200]):
        return base64.b64decode(data_url)
    raise ValueError("Unsupported image URL format returned by the model")


def post_openrouter(api_key: str, payload: dict[str, Any]) -> dict[str, Any]:
    request = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=300) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"OpenRouter HTTP {exc.code}: {body}") from exc


def image_file_to_data_url(path: Path) -> str:
    data = path.read_bytes()
    mime = "image/png" if path.suffix.lower() == ".png" else "image/jpeg"
    return f"data:{mime};base64,{base64.b64encode(data).decode('ascii')}"


def extract_image_urls(message: Any) -> list[str]:
    dumped = message.model_dump() if hasattr(message, "model_dump") else message
    images = dumped.get("images") if isinstance(dumped, dict) else None
    urls: list[str] = []
    if images:
        for image in images:
            image_url = image.get("image_url") if isinstance(image, dict) else None
            url = image_url.get("url") if isinstance(image_url, dict) else None
            if url:
                urls.append(url)

    content = dumped.get("content") if isinstance(dumped, dict) else None
    if isinstance(content, list):
        for part in content:
            if not isinstance(part, dict):
                continue
            image_url = part.get("image_url")
            if isinstance(image_url, dict) and image_url.get("url"):
                urls.append(image_url["url"])
            elif part.get("type") in {"image_url", "input_image"} and part.get("url"):
                urls.append(part["url"])
    elif isinstance(content, str):
        urls.extend(re.findall(r"https?://[^\s)\"']+", content))
        urls.extend(re.findall(r"data:image/[^;\s]+;base64,[A-Za-z0-9+/=\s]+", content))
    return urls


def corner_color(image: Image.Image) -> tuple[int, int, int]:
    rgba = image.convert("RGBA")
    width, height = rgba.size
    samples = [
        rgba.getpixel((0, 0)),
        rgba.getpixel((width - 1, 0)),
        rgba.getpixel((0, height - 1)),
        rgba.getpixel((width - 1, height - 1)),
    ]
    return tuple(round(sum(pixel[i] for pixel in samples) / len(samples)) for i in range(3))


def ensure_transparency(
    image: Image.Image,
    alpha_mode: str,
    rejected_path: Path,
) -> tuple[Image.Image, dict[str, Any]]:
    rgba = image.convert("RGBA")
    width, height = rgba.size
    corners = [
        rgba.getpixel((0, 0))[3],
        rgba.getpixel((width - 1, 0))[3],
        rgba.getpixel((0, height - 1))[3],
        rgba.getpixel((width - 1, height - 1))[3],
    ]
    if max(corners) < 32:
        return rgba, {"alpha_source": "model", "corner_alpha": corners}

    if alpha_mode == "native":
        rejected_path.parent.mkdir(parents=True, exist_ok=True)
        rgba.save(rejected_path, "PNG")
        raise RuntimeError(
            "Model did not return native transparency; "
            f"corner alpha values are {corners}. Saved raw image to {rejected_path}"
        )

    if alpha_mode == "keep":
        return rgba, {"alpha_source": "opaque_or_partial_model", "corner_alpha": corners}

    key = corner_color(rgba)
    pixels = rgba.load()
    changed = 0
    for y in range(height):
        for x in range(width):
            r, g, b, a = pixels[x, y]
            distance = ((r - key[0]) ** 2 + (g - key[1]) ** 2 + (b - key[2]) ** 2) ** 0.5
            if distance < 18:
                pixels[x, y] = (r, g, b, 0)
                changed += 1
            elif distance < 80:
                new_alpha = round(a * min(1.0, (distance - 18) / 62))
                pixels[x, y] = (r, g, b, new_alpha)
                changed += 1
    return rgba, {
        "alpha_source": "corner_key_fallback",
        "corner_rgb": key,
        "changed_pixels": changed,
    }


def build_prompt(asset: AssetSpec) -> str:
    return f"{STYLE_SPEC}\n\nPrimary request:\n{asset.prompt}"


def build_messages(asset: AssetSpec, prompt: str, reference_image: Path | None) -> list[dict[str, Any]]:
    if not asset.use_reference:
        return [{"role": "user", "content": prompt}]
    if reference_image is None:
        raise ValueError(f"{asset.filename} requires --reference-image")
    return [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": (
                        "Use the attached image as the strict character reference for Mebi. "
                        "The new image must preserve the same character identity.\n\n"
                        f"{prompt}"
                    ),
                },
                {
                    "type": "image_url",
                    "image_url": {"url": image_file_to_data_url(reference_image)},
                },
            ],
        }
    ]


def direct_modalities_for(model: str) -> list[str]:
    if model.startswith("x-ai/grok-imagine"):
        return ["image"]
    return ["image", "text"]


def build_server_tool_prompt(asset: AssetSpec, prompt: str, reference_image: Path | None) -> str:
    reference_note = ""
    if asset.use_reference:
        if reference_image is None:
            raise ValueError(f"{asset.filename} requires --reference-image")
        reference_note = (
            "\n\nUse this reference image data URL as the strict character reference. "
            "Preserve the same character identity, proportions, eyes, mouth, palette, and ribbon silhouette:\n"
            f"{image_file_to_data_url(reference_image)}"
        )
    return (
        "Generate exactly one PNG image using the image generation tool. "
        "The image must have a real transparent background/alpha channel. "
        "Do not return only a textual plan; call the image generation tool.\n\n"
        f"{prompt}{reference_note}"
    )


def generate_asset(
    model: str,
    asset: AssetSpec,
    out_dir: Path,
    max_tokens: int,
    reference_image: Path | None,
    alpha_mode: str,
    api_key: str,
    generation_mode: str,
    tool_caller_model: str,
) -> dict[str, Any]:
    prompt = build_prompt(asset)
    if generation_mode == "server-tool":
        response_dump = post_openrouter(
            api_key,
            {
                "model": tool_caller_model,
                "messages": [{"role": "user", "content": build_server_tool_prompt(asset, prompt, reference_image)}],
                "max_tokens": max_tokens,
                "tools": [
                    {
                        "type": "openrouter:image_generation",
                        "parameters": {
                            "model": model,
                            "quality": "high",
                            "size": "1024x1024",
                            "background": "transparent",
                            "output_format": "png",
                        },
                    }
                ],
            },
        )
        message = response_dump["choices"][0]["message"]
        urls = extract_image_urls(message)
    else:
        messages = build_messages(asset, prompt, reference_image)
        response_dump = post_openrouter(
            api_key,
            {
                "model": model,
                "messages": messages,
                "max_tokens": max_tokens,
                "modalities": direct_modalities_for(model),
            },
        )
        message = response_dump["choices"][0]["message"]
        urls = extract_image_urls(message)
    if not urls:
        debug_path = out_dir / "_responses" / model_slug(model) / f"{Path(asset.filename).stem}.response.json"
        debug_path.parent.mkdir(parents=True, exist_ok=True)
        debug_path.write_text(json.dumps(response_dump, ensure_ascii=False, indent=2), encoding="utf-8")
        raise RuntimeError(f"No image returned for {asset.filename}; saved response to {debug_path}")

    raw = data_url_to_bytes(urls[0])
    image = Image.open(BytesIO(raw))
    output_path = out_dir / asset.filename
    output_path.parent.mkdir(parents=True, exist_ok=True)
    rejected_path = out_dir / "_rejected" / model_slug(model) / asset.filename
    final, alpha_info = ensure_transparency(image, alpha_mode, rejected_path)
    final.save(output_path, "PNG")

    return {
        "filename": asset.filename,
        "title": asset.title,
        "model": model,
        "generation_mode": generation_mode,
        "tool_caller_model": tool_caller_model if generation_mode == "server-tool" else None,
        "size": final.size,
        "mode": final.mode,
        "alpha": alpha_info,
        "reference_image": str(reference_image) if asset.use_reference and reference_image else None,
        "prompt": prompt,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--generation-mode", choices=["direct", "server-tool"], default="direct")
    parser.add_argument("--tool-caller-model", default=DEFAULT_TOOL_CALLER_MODEL)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--only", nargs="*", choices=[asset.filename for asset in ASSETS])
    parser.add_argument("--reference-image", type=Path)
    parser.add_argument("--sleep", type=float, default=1.0)
    parser.add_argument("--max-tokens", type=int, default=2048)
    parser.add_argument(
        "--alpha-mode",
        choices=["native", "corner-key", "keep"],
        default="native",
        help=(
            "native: require model-provided alpha; corner-key: remove a flat "
            "corner-colored background; keep: save exactly as RGBA."
        ),
    )
    args = parser.parse_args()

    load_env(REPO_ROOT / ".env")
    api_key = os.environ.get("LLM_API_KEY") or os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        print("LLM_API_KEY or OPENROUTER_API_KEY is required", file=sys.stderr)
        return 2

    args.out_dir.mkdir(parents=True, exist_ok=True)
    selected = [asset for asset in ASSETS if not args.only or asset.filename in args.only]
    if args.reference_image and not args.reference_image.is_absolute():
        args.reference_image = REPO_ROOT / args.reference_image
    if args.reference_image and not args.reference_image.exists():
        print(f"Reference image not found: {args.reference_image}", file=sys.stderr)
        return 2
    manifest_path = args.out_dir / "manifest.openrouter.json"
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    else:
        manifest = []
    manifest_by_filename = {
        item.get("filename"): item
        for item in manifest
        if isinstance(item, dict) and item.get("filename")
    }
    for index, asset in enumerate(selected, start=1):
        print(f"[{index}/{len(selected)}] generating {asset.filename}")
        try:
            manifest_by_filename[asset.filename] = generate_asset(
                args.model,
                asset,
                args.out_dir,
                args.max_tokens,
                args.reference_image,
                args.alpha_mode,
                api_key,
                args.generation_mode,
                args.tool_caller_model,
            )
        except RuntimeError as exc:
            print(f"Generation failed for {asset.filename}: {exc}", file=sys.stderr)
            return 1
        time.sleep(args.sleep)

    manifest = list(manifest_by_filename.values())
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"saved manifest: {manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
