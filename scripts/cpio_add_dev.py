#!/usr/bin/env python3
"""Append static device nodes (console, null, ttyMSM0) to an uncompressed
newc cpio archive. Avoids needing root/mknod on CI runners."""
import struct, sys

NEWC = "070701"
FIELDS = ["ino", "mode", "uid", "gid", "nlink", "mtime", "filesize",
          "devmajor", "devminor", "rdevmajor", "rminor", "namesize", "check"]

def rec(ino, mode, name, data=b"", rdev=(0, 0)):
    name_b = name.encode() + b"\x00"
    vals = dict(zip(FIELDS, [ino, mode, 0, 0, 1, 0, len(data),
                             0, 0, rdev[0], rdev[1], len(name_b), 0]))
    hdr = NEWC + "".join(f"{vals[f]:08X}" for f in FIELDS)
    out = hdr.encode() + name_b
    out += b"\x00" * ((4 - len(out) % 4) % 4)
    out += data
    out += b"\x00" * ((4 - len(data) % 4) % 4)
    return out

S_IFCHR = 0o020000

def main(path):
    blob = open(path, "rb").read()
    # strip previous trailer if rerunning
    marker = blob.find(b"TRAILER!!!")
    if marker != -1:
        cut = (marker // 512 + 1) * 512
        head_end = blob.rfind(b"\x00", 0, marker - 110)
        blob = blob[:head_end + 1]
    ino = 100000
    add = b""
    for i, (name, mode, rdev) in enumerate([
        ("dev/console", 0o0600 | S_IFCHR, (5, 1)),
        ("dev/null",    0o0666 | S_IFCHR, (1, 3)),
        ("dev/ttyMSM0", 0o0600 | S_IFCHR, (4, 64)),
    ]):
        add += rec(ino + i, mode, name, rdev=rdev)
    trailer = rec(0, 0, "TRAILER!!!")
    pad = b"\x00" * ((512 - len(blob + add + trailer) % 512) % 512)
    open(path, "wb").write(blob + add + trailer + pad)
    print(f"appended dev nodes to {path}")

if __name__ == "__main__":
    main(sys.argv[1])
