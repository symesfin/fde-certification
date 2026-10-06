#!/usr/bin/env bash
# Verify the prerequisites for the AI FDE Certification.
#
# Read-only: this reports, it does not install or change anything. Every failure
# points at the guide that fixes it.
#
#   ./00_Prerequisites/scripts/setup_check.sh

set -uo pipefail

GREEN=$'\033[0;32m'; YELLOW=$'\033[0;33m'; RED=$'\033[0;31m'; DIM=$'\033[2m'; OFF=$'\033[0m'
PASS=0; WARN=0; FAIL=0

ok()   { printf '  %s✓%s %s\n' "$GREEN" "$OFF" "$1"; PASS=$((PASS+1)); }
warn() { printf '  %s!%s %s\n     %s%s%s\n' "$YELLOW" "$OFF" "$1" "$DIM" "$2" "$OFF"; WARN=$((WARN+1)); }
bad()  { printf '  %s✗%s %s\n     %s%s%s\n' "$RED" "$OFF" "$1" "$DIM" "$2" "$OFF"; FAIL=$((FAIL+1)); }
head_() { printf '\n%s\n' "$1"; }

# Prefer the version line a tool actually prints; never fail the script on it.
ver() { "$@" 2>/dev/null | head -1; }

head_ "Tooling  (guide 1)"

for t in git docker python3 uv; do
  name=$t
  if command -v "$t" >/dev/null 2>&1; then
    ok "$name  ${DIM}$(ver "$t" --version)${OFF}"
  elif [ "$t" = python3 ] && command -v python >/dev/null 2>&1; then
    ok "python  ${DIM}$(ver python --version)${OFF}"
  elif [ "$t" = docker ] && { command -v podman >/dev/null 2>&1 || command -v nerdctl >/dev/null 2>&1; }; then
    warn "docker not found, but a substitute is" \
         "podman/nerdctl works for this course. Note which one in use_case/ecosystem.md."
  else
    bad "$name not found" "See 00_Prerequisites/1_Your_Machine/README.md"
  fi
done

# Python version, not just presence.
PY=$(command -v python3 || command -v python || true)
if [ -n "$PY" ]; then
  if "$PY" -c 'import sys; sys.exit(0 if sys.version_info >= (3,12) else 1)' 2>/dev/null; then
    ok "python is 3.12+"
  else
    bad "python is older than 3.12  ${DIM}($("$PY" -c 'import sys;print(sys.version.split()[0])' 2>/dev/null)${OFF})" \
        "Install 3.12+; see 00_Prerequisites/1_Your_Machine/README.md"
  fi
fi

# Docker present but not running is a distinct, very common state.
if command -v docker >/dev/null 2>&1; then
  if docker info >/dev/null 2>&1; then
    ok "docker daemon is running"
  else
    warn "docker is installed but the daemon is not responding" \
         "Start Docker Desktop (or your engine) before Week 1's Step 5."
  fi
fi

head_ "Claude Code  (guide 2)"

if command -v claude >/dev/null 2>&1; then
  ok "claude  ${DIM}$(ver claude --version)${OFF}"
  printf '     %srun `claude doctor` for full diagnostics%s\n' "$DIM" "$OFF"
else
  bad "claude not found" "See 00_Prerequisites/2_Claude_Code/README.md"
fi

head_ "Repository  (guide 3)"

ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
cd "$ROOT" || exit 1

if git -C "$ROOT" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  ok "inside a git repository"
  origin=$(git -C "$ROOT" remote get-url origin 2>/dev/null || echo "")
  case "$origin" in
    *AI-Maker-Space/The-AI-Forward-Deployed-Engineer-Certification*)
      warn "origin is the upstream repository, not your fork" \
           "Fork it and clone your fork -- you need somewhere to commit your work." ;;
    "") warn "no 'origin' remote" "Clone your fork rather than downloading a zip." ;;
    *)  ok "origin is your own fork  ${DIM}${origin}${OFF}" ;;
  esac
else
  bad "not a git repository" "Clone your fork; see 00_Prerequisites/3_Fork_and_Run/README.md"
fi

head_ "Model configuration  (guide 4)"

if [ -f "$ROOT/.env" ]; then
  ok ".env exists at the repo root"
  # Read without sourcing -- .env is not shell and must not be executed.
  model=$(grep -E '^\s*LLM_MODEL=' "$ROOT/.env" | tail -1 | cut -d= -f2- | tr -d '"'"'"' \r')
  if [ -n "$model" ]; then
    ok "LLM_MODEL = ${model}"
  else
    bad "LLM_MODEL is not set in .env" "See 00_Prerequisites/4_Your_Model/README.md"
  fi
  if grep -qE '^\s*OPENAI_API_KEY=sk-\.\.\.\s*$' "$ROOT/.env"; then
    bad "OPENAI_API_KEY is still the placeholder from the template" \
        "Paste a real key, or switch to an endpoint/local model."
  fi
else
  bad ".env not found at the repo root" "cp .env.template .env, then fill it in"
fi

challenge_env="$ROOT/01_Product_Engineering/challenge/.env"
if [ -f "$challenge_env" ]; then
  ok "the Week 1 challenge has its own .env"
else
  warn "the Week 1 challenge has no .env yet" \
       "cp .env.template .env inside challenge/ -- it is a separate file."
fi

head_ "Result"
printf '  %s%d passed%s   %s%d warning(s)%s   %s%d failure(s)%s\n\n' \
  "$GREEN" "$PASS" "$OFF" "$YELLOW" "$WARN" "$OFF" "$RED" "$FAIL" "$OFF"

if [ "$FAIL" -gt 0 ]; then
  cat <<'EOF'
  Fix the ✗ items before Session 1. Each one names the guide that covers it.

  If something is blocked by policy rather than broken, that is a finding, not
  a failure -- write it in use_case/ecosystem.md and carry on. Week 9 needs it.

EOF
  exit 1
fi

if [ "$WARN" -gt 0 ]; then
  printf '  Warnings are not blockers, but read them.\n\n'
fi

printf '  Ready for Session 1.\n\n'
