#!/usr/bin/env bash
# install.sh — Install Claude skills into ~/.claude/skills (or a custom directory).
#
# Usage:
#   ./scripts/install.sh                          # Install all skills (copy mode)
#   ./scripts/install.sh --symlink                # Symlink instead of copy (live updates)
#   ./scripts/install.sh --category cloud-devops  # Install one category
#   ./scripts/install.sh --skill fastapi-backend  # Install one skill
#   ./scripts/install.sh --dest /custom/path      # Custom destination
#   ./scripts/install.sh --dry-run                # Show what would happen
#   ./scripts/install.sh --list                   # List available skills & exit
#   ./scripts/install.sh --uninstall              # Remove installed skills
#
# Exit codes:
#   0 = success, 1 = usage error, 2 = filesystem error

set -euo pipefail

# ---------- Resolve repo root regardless of where script is invoked from ----------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SKILLS_SRC="$REPO_ROOT/skills"

# ---------- Defaults ----------
DEST="${HOME}/.claude/skills"
MODE="copy"            # copy | symlink
CATEGORY=""
SKILL=""
DRY_RUN=0
LIST_ONLY=0
UNINSTALL=0

# ---------- ANSI colors (disable if not a TTY) ----------
if [[ -t 1 ]]; then
  C_GREEN=$'\033[32m'; C_YELLOW=$'\033[33m'; C_RED=$'\033[31m'
  C_BLUE=$'\033[34m'; C_BOLD=$'\033[1m'; C_RESET=$'\033[0m'
else
  C_GREEN=""; C_YELLOW=""; C_RED=""; C_BLUE=""; C_BOLD=""; C_RESET=""
fi

log()    { echo "${C_BLUE}▶${C_RESET} $*"; }
ok()     { echo "${C_GREEN}✓${C_RESET} $*"; }
warn()   { echo "${C_YELLOW}!${C_RESET} $*"; }
err()    { echo "${C_RED}✗${C_RESET} $*" >&2; }

usage() {
  sed -n '2,15p' "$0" | sed 's/^# \{0,1\}//'
  exit "${1:-0}"
}

# ---------- Parse args ----------
while [[ $# -gt 0 ]]; do
  case "$1" in
    --symlink)    MODE="symlink"; shift ;;
    --copy)       MODE="copy"; shift ;;
    --category)   CATEGORY="${2:-}"; shift 2 ;;
    --skill)      SKILL="${2:-}"; shift 2 ;;
    --dest)       DEST="${2:-}"; shift 2 ;;
    --dry-run)    DRY_RUN=1; shift ;;
    --list)       LIST_ONLY=1; shift ;;
    --uninstall)  UNINSTALL=1; shift ;;
    -h|--help)    usage 0 ;;
    *)            err "Unknown option: $1"; usage 1 ;;
  esac
done

# ---------- Sanity checks ----------
[[ -d "$SKILLS_SRC" ]] || { err "Skills source directory not found: $SKILLS_SRC"; exit 2; }

# ---------- List mode ----------
if [[ "$LIST_ONLY" -eq 1 ]]; then
  echo "${C_BOLD}Available skills in this repo:${C_RESET}"
  for catdir in "$SKILLS_SRC"/*/; do
    cat="$(basename "$catdir")"
    echo ""
    echo "  ${C_BOLD}$cat${C_RESET}"
    for skilldir in "$catdir"*/; do
      [[ -d "$skilldir" ]] || continue
      echo "    - $(basename "$skilldir")"
    done
  done
  exit 0
fi

# ---------- Uninstall mode ----------
if [[ "$UNINSTALL" -eq 1 ]]; then
  if [[ ! -d "$DEST" ]]; then
    warn "Nothing to uninstall — $DEST does not exist."
    exit 0
  fi
  log "Uninstalling skills from $DEST"
  REMOVED=0
  for catdir in "$SKILLS_SRC"/*/; do
    for skilldir in "$catdir"*/; do
      [[ -d "$skilldir" ]] || continue
      target="$DEST/$(basename "$skilldir")"
      if [[ -e "$target" || -L "$target" ]]; then
        if [[ "$DRY_RUN" -eq 1 ]]; then
          echo "  would remove: $target"
        else
          rm -rf "$target"
        fi
        REMOVED=$((REMOVED + 1))
      fi
    done
  done
  ok "Removed $REMOVED skill(s) from $DEST"
  exit 0
fi

# ---------- Build install list ----------
declare -a TO_INSTALL=()
if [[ -n "$SKILL" ]]; then
  # Find the skill across all categories
  match="$(find "$SKILLS_SRC" -maxdepth 2 -mindepth 2 -type d -name "$SKILL" | head -1)"
  if [[ -z "$match" ]]; then
    err "Skill '$SKILL' not found. Use --list to see available skills."
    exit 1
  fi
  TO_INSTALL+=("$match")
elif [[ -n "$CATEGORY" ]]; then
  catdir="$SKILLS_SRC/$CATEGORY"
  if [[ ! -d "$catdir" ]]; then
    err "Category '$CATEGORY' not found. Use --list to see available categories."
    exit 1
  fi
  while IFS= read -r d; do TO_INSTALL+=("$d"); done < <(find "$catdir" -maxdepth 1 -mindepth 1 -type d | sort)
else
  while IFS= read -r d; do TO_INSTALL+=("$d"); done < <(find "$SKILLS_SRC" -maxdepth 2 -mindepth 2 -type d | sort)
fi

[[ "${#TO_INSTALL[@]}" -gt 0 ]] || { err "No skills selected for install."; exit 1; }

# ---------- Install ----------
log "Mode: $MODE"
log "Destination: $DEST"
log "Skills to install: ${#TO_INSTALL[@]}"
[[ "$DRY_RUN" -eq 1 ]] && warn "DRY RUN — no changes will be made."

if [[ "$DRY_RUN" -eq 0 ]]; then
  mkdir -p "$DEST" || { err "Cannot create $DEST"; exit 2; }
fi

INSTALLED=0
SKIPPED=0
for src in "${TO_INSTALL[@]}"; do
  name="$(basename "$src")"
  target="$DEST/$name"

  if [[ "$DRY_RUN" -eq 1 ]]; then
    if [[ "$MODE" == "symlink" ]]; then
      echo "  would symlink: $src -> $target"
    else
      echo "  would copy:    $src -> $target"
    fi
    continue
  fi

  if [[ -e "$target" || -L "$target" ]]; then
    rm -rf "$target"
  fi

  if [[ "$MODE" == "symlink" ]]; then
    ln -s "$src" "$target"
  else
    cp -r "$src" "$target"
  fi
  INSTALLED=$((INSTALLED + 1))
  echo "  ${C_GREEN}+${C_RESET} $name"
done

if [[ "$DRY_RUN" -eq 0 ]]; then
  ok "Installed $INSTALLED skill(s) to $DEST"
  echo ""
  echo "Restart Claude Code (or your client) to pick up the new skills."
fi
