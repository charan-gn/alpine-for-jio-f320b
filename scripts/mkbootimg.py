#!/usr/bin/env python3
"""Minimal Android boot image packer (v0 header) - matches Jio F320B stock layout."""
import argparse, struct, os

def align(x, a): return (x + a - 1) // a * a

p = argparse.ArgumentParser()
p.add_argument("--kernel", required=True)
p.add_argument("--ramdisk", required=True)
p.add_argument("--cmdline", default="")
p.add_argument("--base", type=lambda x: int(x, 0), default=0x80000000)
p.add_argument("--kernel_offset", type=lambda x: int(x, 0), default=0x00008000)
p.add_argument("--ramdisk_offset", type=lambda x: int(x, 0), default=0x01000000)
p.add_argument("--second_offset", type=lambda x: int(x, 0), default=0x00000000)
p.add_argument("--tags_offset", type=lambda x: int(x, 0), default=0x00000100)
p.add_argument("--pagesize", type=lambda x: int(x, 0), default=2048)
p.add_argument("--board", default="F320B")
p.add_argument("-o", "--output", required=True)
a = p.parse_args()

kernel = open(a.kernel, "rb").read()
ramdisk = open(a.ramdisk, "rb").read()

hdr = struct.pack(
    "<8s10I16s32s1024s",
    b"ANDROID!",
    len(kernel),
    a.base + a.kernel_offset,
    len(ramdisk),
    a.base + a.ramdisk_offset,
    0,                                  # second size
    0,                                  # second addr (stock keeps it 0 when unused)
    a.base + a.tags_offset,
    a.pagesize,
    0, 0,                               # dt_size (dtb appended to kernel), unused
    a.board.encode()[:16].ljust(16, b"\x00"),
    a.cmdline.encode()[:512].ljust(512, b"\x00"),
    b"\x00" * 1024,                     # id
)

out = bytearray(hdr)
ps = a.pagesize

def put(blob):
    out.extend(blob)
    pad = align(len(out), ps) - len(out)
    out.extend(b"\x00" * pad)

put(kernel)          # dtb is already concatenated by pack.sh
if ramdisk:
    put(ramdisk)

open(a.output, "wb").write(out)
print(f"{a.output}: {len(out)} bytes "
      f"(kernel {len(kernel)}, ramdisk {len(ramdisk)})")
