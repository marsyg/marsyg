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

# --- Render animated SVG banner (typing effect) ---
python3 scripts/generate-banner-svg.py "$OUT_FILE" banner.svg

# --- Sync README.md banner block if markers exist ---
README="README.md"
if [ -f "$README" ] && grep -q "ASCII-BANNER:START" "$README" && grep -q "ASCII-BANNER:END" "$README"; then
  python3 - "$OUT_FILE" "$README" <<'PY'
import sys
banner_path, readme_path = sys.argv[1], sys.argv[2]
with open(banner_path) as f:
    banner = f.read().rstrip("\n")
block = "<!-- ASCII-BANNER:START -->\n```\n" + banner + "\n```\n<!-- ASCII-BANNER:END -->"
with open(readme_path) as f:
    content = f.read()
start = "<!-- ASCII-BANNER:START -->"
end = "<!-- ASCII-BANNER:END -->"
pre, _, rest = content.partition(start)
_, _, post = rest.partition(end)
new_content = pre + block + post
with open(readme_path, "w") as f:
    f.write(new_content)
print(f"Updated {readme_path} banner block.")
PY
fi
