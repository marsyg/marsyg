#!/usr/bin/env bash
set -euo pipefail

USERNAME="${GH_USERNAME:-marsyg}"
OUT_FILE="ascii-banner.txt"

# --- Fetch live stats from GitHub API ---
STATS=$(curl -s -H "Authorization: token ${GH_TOKEN:-}" \
  "https://api.github.com/users/${USERNAME}")

FOLLOWERS=$(echo "$STATS" | grep -o '"followers": *[0-9]*' | grep -o '[0-9]*' || echo "0")
PUBLIC_REPOS=$(echo "$STATS" | grep -o '"public_repos": *[0-9]*' | grep -o '[0-9]*' || echo "0")

# --- Generate figlet banner ---
BANNER=$(figlet -f slant "Maaz Ahmad")

# --- Assemble final file ---
{
  echo "$BANNER"
  echo ""
  echo "  followers: ${FOLLOWERS}   |   public repos: ${PUBLIC_REPOS}"
  echo "  last updated: $(date -u '+%Y-%m-%d %H:%M UTC')"
} > "$OUT_FILE"

echo "Wrote $OUT_FILE:"
cat "$OUT_FILE"
