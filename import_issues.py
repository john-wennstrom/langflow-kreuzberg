#!/usr/bin/env python3
"""
import_issues.py — Create GitHub issues from issues.yaml.

Usage:
    python import_issues.py [--repo owner/name] [--file issues.yaml] [--dry-run]

Requirements:
    pip install pyyaml
    gh CLI authenticated (gh auth login)

Notes:
    - Labels and milestones must already exist (run import_labels.py and
      import_milestones.py first).
    - If a milestone title is not found on the repo, the issue is created
      without one and a warning is printed.
    - Use --dry-run to preview without creating anything.
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


# ── Helpers ──────────────────────────────────────────────────────────────────

def get_milestone_map(repo: str | None) -> dict[str, str]:
    """Return {title: number_str} for all open milestones."""
    if repo:
        owner, name = repo.split("/", 1)
        endpoint = f"repos/{owner}/{name}/milestones"
    else:
        endpoint = "repos/{owner}/{repo}/milestones"

    result = subprocess.run(
        ["gh", "api", endpoint, "--paginate"],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        print(f"  [warn] Could not fetch milestones: {result.stderr.strip()}")
        return {}
    try:
        data = json.loads(result.stdout)
        return {m["title"]: str(m["number"]) for m in data}
    except (json.JSONDecodeError, KeyError):
        return {}


def issue_exists(title: str, repo: str | None) -> bool:
    """Check whether an open issue with this exact title already exists."""
    cmd = ["gh", "issue", "list", "--search", f'"{title}" in:title',
           "--state", "open", "--json", "title", "--limit", "25"]
    if repo:
        cmd += ["--repo", repo]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return False
    try:
        issues = json.loads(result.stdout)
        return any(i["title"] == title for i in issues)
    except (json.JSONDecodeError, KeyError):
        return False


# ── Core ─────────────────────────────────────────────────────────────────────

def create_issue(
    item: dict,
    milestone_map: dict[str, str],
    repo: str | None,
    dry_run: bool,
) -> None:
    title: str = item["title"]
    body: str = item.get("body", "")
    labels: list[str] = item.get("labels", [])
    milestone_title: str | None = item.get("milestone")

    if issue_exists(title, repo):
        print(f"  [skip] Issue already exists: {title}")
        return

    cmd = ["gh", "issue", "create", "--title", title, "--body", body]

    for label in labels:
        cmd += ["--label", label]

    if milestone_title:
        milestone_number = milestone_map.get(milestone_title)
        if milestone_number:
            cmd += ["--milestone", milestone_number]
        else:
            print(
                "  [warn] Milestone not found: "
                f"'{milestone_title}' — skipping milestone assignment"
            )

    if repo:
        cmd += ["--repo", repo]

    if dry_run:
        print(f"  [dry-run] Would create: {title}")
        return

    try:
        run(cmd)
    except subprocess.CalledProcessError as exc:
        print(f"  [error] Failed for issue '{title}': {exc}", file=sys.stderr)


# ── Entry ─────────────────────────────────────────────────────────────────────

def main(path: str = "issues.yaml", repo: str | None = None, dry_run: bool = False) -> None:
    items: list[dict] = yaml.safe_load(Path(path).read_text(encoding="utf-8"))

    print("Fetching milestone map from GitHub...")
    milestone_map = get_milestone_map(repo)
    print(f"  Found {len(milestone_map)} milestones: {list(milestone_map.keys())}\n")

    total = len(items)
    for idx, item in enumerate(items, start=1):
        title = item.get("title", f"Issue #{idx}")
        print(f"[{idx}/{total}] {title}")
        create_issue(item, milestone_map, repo, dry_run)
        print()

    print("All issues processed.")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Import issues from YAML to GitHub.")
    parser.add_argument("--file", default="issues.yaml", help="Path to issues YAML file")
    parser.add_argument(
        "--repo",
        default=None,
        help="GitHub repo in owner/name format (owner/name)",
    )
    parser.add_argument("--dry-run", action="store_true", help="Preview without creating issues")
    args = parser.parse_args()
    main(path=args.file, repo=args.repo, dry_run=args.dry_run)
