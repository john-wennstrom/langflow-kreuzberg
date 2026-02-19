#!/usr/bin/env python3
"""
import_milestones.py — Create GitHub milestones from milestones.yaml.

Usage:
    python import_milestones.py [--repo owner/name] [--file milestones.yaml]

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
    return subprocess.run(cmd, check=True, capture_output=capture, text=True)


def get_existing_milestones(repo: str | None) -> dict[str, int]:
    """Return dict of {title: number} for milestones already on the repo."""
    cmd = ["gh", "api", "repos/{owner}/{repo}/milestones", "--paginate"]
    # Use gh api with dynamic repo resolution when repo is provided
    if repo:
        owner, name = repo.split("/", 1)
        cmd = ["gh", "api", f"repos/{owner}/{name}/milestones", "--paginate"]
    else:
        cmd = ["gh", "api", "repos/{owner}/{repo}/milestones", "--paginate"]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  [warn] Could not fetch milestones: {result.stderr.strip()}")
        return {}
    try:
        data = json.loads(result.stdout)
        return {m["title"]: m["number"] for m in data}
    except (json.JSONDecodeError, KeyError):
        return {}


def create_milestone(
    title: str,
    description: str,
    due_date: str | None,
    repo: str | None,
) -> None:
    cmd = ["gh", "api", "--method", "POST"]

    if repo:
        owner, name = repo.split("/", 1)
        cmd += [f"repos/{owner}/{name}/milestones"]
    else:
        cmd += ["repos/{owner}/{repo}/milestones"]

    cmd += [
        "--field", f"title={title}",
        "--field", f"description={description}",
    ]
    if due_date:
        # GitHub expects ISO 8601 with time: YYYY-MM-DDTHH:MM:SSZ
        due_on = f"{due_date}T23:59:59Z"
        cmd += ["--field", f"due_on={due_on}"]

    run(cmd)


def update_milestone(
    number: int,
    title: str,
    description: str,
    due_date: str | None,
    repo: str | None,
) -> None:
    cmd = ["gh", "api", "--method", "PATCH"]

    if repo:
        owner, name = repo.split("/", 1)
        cmd += [f"repos/{owner}/{name}/milestones/{number}"]
    else:
        cmd += [f"repos/{{owner}}/{{repo}}/milestones/{number}"]

    cmd += [
        "--field", f"title={title}",
        "--field", f"description={description}",
    ]
    if due_date:
        due_on = f"{due_date}T23:59:59Z"
        cmd += ["--field", f"due_on={due_on}"]

    run(cmd)


def main(path: str = "milestones.yaml", repo: str | None = None) -> None:
    items: list[dict] = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    existing = get_existing_milestones(repo)

    created = updated = errors = 0

    for item in items:
        title: str = item["title"]
        description: str = item.get("description", "").strip()
        due_date: str | None = item.get("due_date")

        try:
            if title in existing:
                print(f"[update] {title}")
                update_milestone(existing[title], title, description, due_date, repo)
                updated += 1
            else:
                print(f"[create] {title}")
                create_milestone(title, description, due_date, repo)
                created += 1
        except subprocess.CalledProcessError as exc:
            print(f"  [error] Failed for milestone '{title}': {exc}", file=sys.stderr)
            errors += 1

    print(f"\nDone. created={created}  updated={updated}  errors={errors}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Import milestones from YAML to GitHub.")
    parser.add_argument("--file", default="milestones.yaml", help="Path to milestones YAML file")
    parser.add_argument("--repo", default=None, help="GitHub repo in owner/name format")
    args = parser.parse_args()
    main(path=args.file, repo=args.repo)
