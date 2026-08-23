# Firmware Map: Jio F320B vs Nokia 6700s (RM-576)

## JIO F320B - Qualcomm MSM8909 (eMMC, GPT)

Source: LYF-F320B-002-02-37-130921 stock package (QFIL format)
Firehose programmer: prog_emmc_firehose_8909_ddr.mbn (unsigned, public)
Boot key for EDL: hold * while plugging USB

Boot chain: PBL(ROM) -> sbl1 -> rpm/tz/devcfg/cmnlib/keymaster -> aboot(LK) -> boot(kernel+ramdisk) -> system

| Partition | Size | Image in package | Notes |
|---|---|---|---|
| modem (NON-HLOS.bin) | 64M | mpss/modem fw | closed, stays |
| sbl1/sbl1bak | 0.5M | sbl1.mbn | keep |
| aboot/abootbak | 1M | emmc_appsboot.mbn (LK) | keep |
| rpm/rpmbak | 0.5M | rpm.mbn | keep |
| tz/tzbak | 2M | tz.mbn | keep |
| devcfg | 0.2M | devcfg.mbn | keep |
| cmnlib/keymaster | 0.2/0.5M | .mbn | keep |
| modemst1/2 fsg fsc ssd | small | radio cal / IMEI data | NEVER FLASH |
| splash | 10M | boot logo | optional |
| boot | 32M | boot.img | OURS |
| recovery | 32M | recovery.img | optional |
| system | 1024M | sparse ext4 (KaiOS/B2G) | future rootfs |
| cache | 256M | | scratch |
| persist | 32M | sensor/drm cal | careful |
| usbmsc | 1000M | mass-storage preload | storage |
| userdata | rest | ext4 | ours later |

boot.img header: kernel@0x80008000 ramdisk@0x81000000 tags@0x80000100 pagesize=2048
Kernel blob = zImage + appended DTBs. Stock kernel: Linux 4.9.249-perf (CAF),
config embedded as IKCFG (extracted to files/kernel_config), board dtb
compatible msm8909-qrd (model MSM8905 QRD SKUB).

## NOKIA 6700s RM-576 - BB5 "CMT" oneNAND

Source: v071.004 product package (FPSX container, BB5 TLV format, big-endian)
Container: sig 0xB2, headerSize u32BE, property TLVs, block chain:
  0x17 BINARY/DATA, 0x27 ROFS_HASH, 0x28 CORE_CERT, 0x2E USER_AREA
  payload length @ hdr[37..40]BE (rofs blocks) / [6..10]BE (binary)
  flash destination address follows length

OneNAND address map:

| Flash addr | Content |
|---|---|
| 0x0000000 | CMT boot hash/table |
| 0x0200000+ | XSR secondary/algo loaders |
| 0x0400000 | ADA adaptation data (ROFS magic a3959780) |
| 0x0480400..0x6CC0000 | CMT MCUSW: monolithic S40 OS + baseband RTOS (single signed ARM blob, ~110MB) |
| 0x04E0000..0x740000 | SOS*ENO APE content variant |
| 0x7800000..0xA740000 | ROFS2 language pack (Euro1) |
| 0xA740000.. | ROFS3 operator/country variant |
| 0xB540000..0xB900000 | UDA user-area preload (EPOC fs + PNG assets) |

No bootloader access: PBL+SBL Nokia-signed; MCUSW monolithic & signed.
OS and radio are one inseparable blob - nothing user-writable exists.

## Verdict

F320B: every layer above the radio is swappable; whole OS lives in one partition.
6700s: design/UI reference only.
