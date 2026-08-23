# alpine-for-jio-f320b

Open-source firmware for the Jio/LYF F320B featurephone (Qualcomm MSM8909).
Stock KaiOS replaced by **Alpine Linux (musl, armv7) + a custom C UI** written
against fbdev/evdev. No Android anywhere.

```
PBL(ROM) -> sbl1 -> rpm/tz -> aboot(LK) -> boot.img [ our kernel + Alpine rootfs ]
                                             |
                                             +-- /init -> /bin/ui  (PID1 UI)
```

## Layout
- `files/kernel_config` - full .config extracted from the stock boot image
- `files/jio-f320b.dtb` - board DTB extracted from stock kernel (reference)
- `initramfs/ui.c`      - first-light framebuffer + keypad test app
- `initramfs/init`      - PID 1
- `scripts/`            - apk bootstrap, mkbootimg, packer

## Build
Push to `main` or run the workflow manually. Artifact: `f320b-boot`.

## Flash
```bash
# phone in EDL: hold * while plugging USB
python3 edl.py --loader=prog_emmc_firehose_8909_ddr.mbn w boot out/boot.img
# full backup FIRST:
python3 edl.py --loader=prog_emmc_firehose_8909_ddr.mbn rl backups/
```

Never flash modemst1/2, fsg, fsc, persist - radio calibration lives there.

See docs/firmware-map.md for the full partition/firmware analysis.
