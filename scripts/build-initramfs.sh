#!/usr/bin/env bash
# Bootstrap an Alpine Linux armv7 rootfs on a foreign-arch host (CI-friendly).
# Usage: build-initramfs.sh <output-dir> [alpine branch] [ui binary]
set -euo pipefail

ROOT="${1:?usage: build-initramfs.sh <rootfs-dir> [branch] [ui-binary]}"
BRANCH="${2:-v3.19}"
UI="${3:-}"
ARCH=armv7
MIRROR="https://dl-cdn.alpinelinux.org/alpine"
REPO="$MIRROR/$BRANCH/main"

echo "[*] fetching apk-tools-static for host"
APKFILE=$(curl -sf "$REPO/x86_64/" | grep -oE 'apk-tools-static-[0-9][^"]*\.apk' | sort -V | tail -1)
[ -n "$APKFILE" ] || { echo "apk-tools-static not found"; exit 1; }
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT
curl -sf -o "$TMP/apk.apk" "$REPO/x86_64/$APKFILE"
tar -xzf "$TMP/apk.apk" -C "$TMP" sbin/apk.static

echo "[*] bootstrapping alpine-base ($ARCH, $BRANCH)"
mkdir -p "$ROOT/dev" "$ROOT/proc" "$ROOT/sys" "$ROOT/tmp" "$ROOT/run"
"$TMP/sbin/apk.static" \
    --arch "$ARCH" \
    -X "$REPO/$ARCH" \
    -U --allow-untrusted --clean-protected \
    --root "$ROOT" --initdb \
    add alpine-base

# our world
if [ -n "$UI" ]; then
    install -Dm755 "$UI" "$ROOT/bin/ui"
fi
HERE="$(cd "$(dirname "$0")/.." && pwd)"
install -Dm755 "$HERE/initramfs/init" "$ROOT/init"

echo "[*] rootfs ready: $(du -sh "$ROOT" | cut -f1)"
