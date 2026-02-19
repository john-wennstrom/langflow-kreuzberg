"""
import_labels.py — Create or update GitHub labels from labels.yaml.

Usage:
    python import_labels.py [--repo owner/name] [--file labels.yaml] [--update]

Requirements:
    pip install pyyaml
    gh CLI authenticated (gh auth login)
"""

import json
import subprocess
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("Missing dependency: pyyaml. Install with: pip install pyyaml", file=sys.stderr)
    sys.exit(1)


def run(cmd: list[str], capture: bool = False) -> subprocess.CompletedProcess:
    print("  $", " ".join(cmd))
    return subprocess.run(
        cmd,
        check=True,
        capture_output=capture,
        text=True,
    )


def get_existing_labels(repo: str | None) -> set[str]:
    """Return a set of label names already on the repo."""
    cmd = ["gh", "label", "list", "--json", "name", "--limit", "500"]
    if repo:
        cmd += ["--repo", repo]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  [warn] Could not fetch existing labels: {result.stderr.strip()}")
        return set()
    try:
        data = json.loads(result.stdout)
        return {item["name"] for item in data}
    except (json.JSONDecodeError, KeyError):
        return set()


def create_label(name: str, color: str, description: str, repo: str | None) -> None:
    cmd = [
        "gh", "label", "create", name,
        "--color", color.lstrip("#"),
        "--description", description,
        "--force",          # update if exists
    ]
    if repo:
        cmd += ["--repo", repo]
    run(cmd)


def main(path: str = "labels.yaml", repo: str | None = None) -> None:
    items: list[dict] = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    existing = get_existing_labels(repo)

    created = updated = skipped = 0

    for item in items:
        name: str = item["name"]
        color: str = item.get("color", "ededed")
        description: str = item.get("description", "")

        if name in existing:
            print(f"[update] {name}")
            updated += 1
        else:
            print(f"[create] {name}")
            created += 1

        try:
            create_label(name, color, description, repo)
        except subprocess.CalledProcessError as exc:
            print(f"  [error] Failed for label '{name}': {exc}", file=sys.stderr)
            skipped += 1

    print(f"\nDone. created={created}  updated={updated}  errors={skipped}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Import labels from YAML to GitHub.")
    parser.add_argument("--file", default="labels.yaml", help="Path to labels YAML file")
    parser.add_argument("--repo", default=None, help="GitHub repo in owner/name format")
    args = parser.parse_args()
    main(path=args.file, repo=args.repo)
