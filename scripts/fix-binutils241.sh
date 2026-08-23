#!/usr/bin/env bash
# binutils >= 2.41 rejects "#function"/"#object" in .type/.size directives
# used across old ARM kernels. Rewrite to canonical "%function"/"%object".
set -euo pipefail
TREE="${1:-kernel}"
find "$TREE/arch/arm" "$TREE/kernel" -name '*.S' -o -name '*.s' 2>/dev/null |
while read -r f; do
    if grep -qE '^\s*\.(type|size)\s+[^,]+,\s*#' "$f" ||
       grep -qE '^\s*\.section\s+.*,\s*#' "$f"; then
        sed -i -E 's/^(\s*\.type\s+[^,]+),\s*#/\1, %/;
                   s/^(\s*\.size\s+[^,]+),\s*#/\1, %/' "$f"
        sed -i -E '/^\s*\.section/s/#(alloc|execinstr|write|readonly|progbits)/%\1/g' "$f"
        echo "patched $f"
    fi
done
