#!/usr/bin/env python3
"""
lint_skills.py — Validate every SKILL.md in the repo.

Checks:
  1. Every folder under skills/<category>/<name>/ has a SKILL.md.
  2. SKILL.md starts with YAML frontmatter delimited by `---`.
  3. Frontmatter contains `name` and `description` keys.
  4. `name` matches the folder name (case-sensitive).
  5. `description` is at least 40 characters (after whitespace collapse).
  6. No duplicate skill names across the whole repo.

Exits 0 on success, 1 on validation failure.
Designed to run on stock Python 3.10+ with no third-party deps.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = ROOT / "skills"
MIN_DESC_CHARS = 40

# ---------- ANSI ----------
GREEN, RED, YELLOW, BOLD, RESET = "\033[32m", "\033[31m", "\033[33m", "\033[1m", "\033[0m"
if not sys.stdout.isatty():
    GREEN = RED = YELLOW = BOLD = RESET = ""

errors: list[str] = []
warnings: list[str] = []
seen_names: dict[str, Path] = {}


def parse_frontmatter(text: str) -> dict[str, str] | None:
    """Parse a thin subset of YAML frontmatter: `key: value` or `key: >` block scalar."""
    m = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
    if not m:
        return None
    body = m.group(1)

    fm: dict[str, str] = {}
    lines = body.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        # Match `key: value` or `key: >` (block scalar)
        kv = re.match(r"^([A-Za-z_][\w-]*):\s*(.*)$", line)
        if not kv:
            i += 1
            continue
        key, val = kv.group(1), kv.group(2).strip()
        if val in (">", "|", ">-", "|-"):
            # Collect indented continuation lines
            block: list[str] = []
            i += 1
            while i < len(lines) and (lines[i].startswith((" ", "\t")) or lines[i].strip() == ""):
                block.append(lines[i].strip())
                i += 1
            fm[key] = re.sub(r"\s+", " ", " ".join(block)).strip()
        else:
            fm[key] = val.strip().strip('"').strip("'")
            i += 1
    return fm


def lint_skill(skill_dir: Path, category: str) -> None:
    rel = skill_dir.relative_to(ROOT)
    skill_md = skill_dir / "SKILL.md"

    if not skill_md.exists():
        errors.append(f"{rel}: missing SKILL.md")
        return

    try:
        text = skill_md.read_text(encoding="utf-8")
    except UnicodeDecodeError as e:
        errors.append(f"{rel}/SKILL.md: not valid UTF-8 ({e})")
        return

    fm = parse_frontmatter(text)
    if fm is None:
        errors.append(f"{rel}/SKILL.md: missing or malformed YAML frontmatter (must start with --- ... ---)")
        return

    # Required fields
    if "name" not in fm:
        errors.append(f"{rel}/SKILL.md: frontmatter missing required key 'name'")
    if "description" not in fm:
        errors.append(f"{rel}/SKILL.md: frontmatter missing required key 'description'")

    # Name match
    folder_name = skill_dir.name
    if "name" in fm and fm["name"] != folder_name:
        errors.append(
            f"{rel}/SKILL.md: name '{fm['name']}' does not match folder name '{folder_name}'"
        )

    # Description length
    if "description" in fm:
        desc = fm["description"]
        if len(desc) < MIN_DESC_CHARS:
            errors.append(
                f"{rel}/SKILL.md: description too short ({len(desc)} chars, need >= {MIN_DESC_CHARS})"
            )
        # Soft warning: description should mention trigger keywords
        if not re.search(r"\b(use|trigger|when|whenever)\b", desc, re.IGNORECASE):
            warnings.append(
                f"{rel}/SKILL.md: description has no trigger phrasing (consider 'Use this skill when ...')"
            )

    # Duplicate names
    if "name" in fm:
        if fm["name"] in seen_names:
            errors.append(
                f"{rel}/SKILL.md: duplicate skill name '{fm['name']}' "
                f"(also in {seen_names[fm['name']].relative_to(ROOT)})"
            )
        else:
            seen_names[fm["name"]] = skill_md


def main() -> int:
    if not SKILLS_DIR.exists():
        print(f"{RED}✗ skills/ directory not found at {SKILLS_DIR}{RESET}")
        return 1

    skill_count = 0
    for category_dir in sorted(SKILLS_DIR.iterdir()):
        if not category_dir.is_dir():
            continue
        for skill_dir in sorted(category_dir.iterdir()):
            if not skill_dir.is_dir():
                continue
            skill_count += 1
            lint_skill(skill_dir, category_dir.name)

    print(f"{BOLD}Linted {skill_count} skill(s).{RESET}")

    for w in warnings:
        print(f"{YELLOW}!{RESET} {w}")

    if errors:
        print()
        for e in errors:
            print(f"{RED}✗{RESET} {e}")
        print()
        print(f"{RED}{BOLD}FAILED{RESET}: {len(errors)} error(s), {len(warnings)} warning(s)")
        return 1

    print(f"{GREEN}{BOLD}OK{RESET}: 0 errors, {len(warnings)} warning(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
