# Contributing to Claude Skills

Thanks for considering a contribution! This repo follows a few conventions to keep skills high-quality and easy for Claude to discover.

## Submitting a New Skill

1. **Pick a category.** Place your skill under `skills/<category>/<skill-name>/`. Use an existing category if it fits; propose a new one in your PR description if not.
2. **Use the skill template** (see below).
3. **Write a great description** — this is the single most important field. See [Writing Descriptions](#writing-descriptions).
4. **Open a PR.** The lint workflow will validate your `SKILL.md` automatically.

## Skill Template

```markdown
---
name: your-skill-name
description: >
  One-sentence summary of what the skill does. Use this skill when the user
  mentions X, Y, Z, or any related keyword. Also trigger for natural-language
  phrasings like "do A", "help me B". Do NOT use for [out-of-scope cases].
---

# Your Skill Title

Brief opening that frames the skill's role and expertise.

## When to use this skill

Concrete situations and triggers.

## Workflow

Step-by-step process Claude should follow.

## References

Point to files under `references/` for deep dives.
```

### Folder Layout

```
your-skill-name/
├── SKILL.md          # required
├── references/       # optional — long-form docs Claude reads on demand
│   ├── topic-1.md
│   └── topic-2.md
└── scripts/          # optional — executable helpers
    └── do-thing.sh
```

## Writing Descriptions

The `description` field tells Claude **when** to load your skill. A bad description means the skill never triggers. A great description triggers on both explicit keywords and natural phrasings.

### Description Style Rules

1. **Lead with what the skill does** (one sentence).
2. **List explicit triggers** — names of tools, frameworks, concepts the user might mention.
3. **List natural-language triggers** — paraphrases the user might use without naming the tool ("help me debug a slow page" should trigger a performance skill).
4. **Exclude out-of-scope cases** with `Do NOT use for ...` so similar-sounding requests route elsewhere.
5. **Keep it under ~300 words.** Tight, scannable, no fluff.

### Good vs. Bad Example

❌ **Bad:** `description: Helps with security stuff.`

✅ **Good:**
```yaml
description: >
  Comprehensive web application security skill covering OWASP Top 10,
  authentication/authorization testing, API security, and security headers.
  Use this skill whenever the user mentions web security, OWASP, XSS, SQL
  injection, CSRF, SSRF, JWT security, CORS, CSP, or any web vulnerability.
  Also trigger for natural phrasing like "is this endpoint safe", "how do I
  secure my login", or "review my API for security issues". Do NOT use for
  network-level security (firewalls, IDS) — use network-security instead.
```

## Linting Locally

The repo includes a Python validator. Run it before submitting:

```bash
python3 scripts/lint_skills.py
```

It checks:

- Every skill folder contains a `SKILL.md`.
- Every `SKILL.md` has valid YAML frontmatter.
- `name` matches the folder name.
- `description` is present and at least 40 characters.
- No duplicate skill names across the repo.

The same checks run automatically on every PR via [`.github/workflows/lint-skills.yml`](.github/workflows/lint-skills.yml).

## Code Style

- Markdown: write in clear, direct prose. Headings in sentence case.
- Scripts: bash scripts use `set -euo pipefail`; Python scripts target 3.10+.
- Keep line length reasonable (~100 chars) for diff readability.

## License

By contributing, you agree your contribution is licensed under the same **CC BY-NC-SA 4.0** as the rest of the repo. See [`LICENSE`](LICENSE).

## Questions

Open an issue or start a discussion. Thanks for helping make Claude better!
