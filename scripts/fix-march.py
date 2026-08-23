#!/usr/bin/env python3
"""Hard-pin -march=armv7-a in arch/arm/Makefile.

gcc >= 12 fails kernel-4.9's cc-option probe (old flag soup + -Werror),
which makes kbuild silently fall back to -march=armv5t for C files and
breaks v7 instructions. Skip the probe entirely.
"""
import sys

p = sys.argv[1] if len(sys.argv) > 1 else "kernel/arch/arm/Makefile"
s = open(p).read()
before = s
s = s.replace(
    "$(call cc-option,-march=armv7-a,-march=armv5t -Wa$(comma)-march=armv7-a)",
    "-march=armv7-a",
)
open(p, "w").write(s)
print(f"patched {p}: {'changed' if s != before else 'NO MATCH'}")
