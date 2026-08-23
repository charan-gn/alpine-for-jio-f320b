#!/usr/bin/env bash
# Pack zImage + board DTB + Alpine initramfs into flashable boot.img (F320B layout)
set -euo pipefail
ZIMAGE="${1:?zImage}"
DTB="${2:?dtb}"
INITRAMFS="${3:?initramfs.cpio.gz}"
OUT="${4:-out/boot.img}"

HERE="$(cd "$(dirname "$0")/.." && pwd)"
mkdir -p "$(dirname "$OUT")"

# stock F320B: dtb concatenated after zImage inside kernel blob
cat "$ZIMAGE" "$DTB" > "$HERE/out/kernel-dtb.bin"

python3 "$HERE/scripts/mkbootimg.py" \
    --kernel  "$HERE/out/kernel-dtb.bin" \
    --ramdisk "$INITRAMFS" \
    --cmdline "console=ttyMSM0,115200,n8 msm_rtb.filter=0x237 ehci-hcd.park=3 lpm_levels.sleep_disabled=1 earlyprintk earlycon=msm_hsl_uart,0x78B0000" \
    --base            0x80000000 \
    --kernel_offset   0x00008000 \
    --ramdisk_offset  0x01000000 \
    --second_offset   0x00000000 \
    --tags_offset     0x00000100 \
    --pagesize        2048 \
    --board           F320B \
    -o "$OUT"
