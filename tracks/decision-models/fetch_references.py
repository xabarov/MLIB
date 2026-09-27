"""Download pinned upstream sources for reading; never install or execute them."""

import argparse
import json
import re
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def git(*args, cwd=None):
    return subprocess.check_output(["git", *args], cwd=cwd, text=True).strip()


def fetch(item, directory):
    name, repo, commit = (item[k] for k in ("name", "repository", "commit"))
    if not re.fullmatch(r"[a-z0-9-]+", name):
        raise ValueError(f"Invalid local name: {name}")
    if not re.fullmatch(r"[\w.-]+/[\w.-]+", repo) or not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise ValueError(f"Invalid pinned source: {item}")
    destination = directory / name
    url = f"https://github.com/{repo}.git"
    if destination.exists():
        if not (destination / ".git").is_dir():
            raise RuntimeError(f"Existing directory is not a checkout: {destination}")
        if git("remote", "get-url", "origin", cwd=destination) != url:
            raise RuntimeError(f"Different origin; leaving unchanged: {destination}")
        if git("rev-parse", "HEAD", cwd=destination) != commit:
            raise RuntimeError(f"Different revision; leaving unchanged: {destination}")
        if git("status", "--porcelain", cwd=destination):
            raise RuntimeError(f"Local edits; leaving unchanged: {destination}")
        print(f"Already pinned: {name} @ {commit[:12]}", flush=True)
        return
    # A failed fetch cannot leave a half-created destination. Existing work is never reset.
    with tempfile.TemporaryDirectory(prefix=f".{name}-", dir=directory) as temporary:
        checkout = Path(temporary) / "repo"
        git("init", "-q", str(checkout))
        git("remote", "add", "origin", url, cwd=checkout)
        git("-c", "advice.detachedHead=false", "fetch", "--depth=1", "origin", commit, cwd=checkout)
        git("checkout", "--detach", "-q", "FETCH_HEAD", cwd=checkout)
        checkout.rename(destination)
    print(f"Fetched: {name} @ {commit[:12]}", flush=True)


def main():
    manifest = json.loads((ROOT / "upstreams.json").read_text())
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--only", choices=[r["name"] for r in manifest["repositories"]])
    args = parser.parse_args()
    directory = ROOT / "references"
    directory.mkdir(exist_ok=True)
    for item in manifest["repositories"]:
        if args.only is None or args.only == item["name"]:
            fetch(item, directory)


if __name__ == "__main__":
    main()
