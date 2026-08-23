#!/usr/bin/env python3
"""Drop-in replacement for CLO's gcc-wrapper.py.

CLO kbuild invokes this two ways:
  1) directly via shebang:      gcc-wrapper.py <flags>
  2) explicitly through python: python gcc-wrapper.py <cross-gcc> <flags>
In case 2 the real compiler name is argv[1]; consume it.
Everything else goes to $REAL_CC (or cross-gcc from PATH).
"""
import os, re, shutil, sys

def find_real_cc():
    cc = os.environ.get("REAL_CC")
    if cc:
        return cc
    for cand in ("arm-linux-gnueabihf-gcc", "aarch64-linux-gnu-gcc", "gcc"):
        p = shutil.which(cand)
        if p:
            return p
    return "gcc"

args = sys.argv[1:]

# case 2: first arg is the compiler binary itself (no leading dash)
if args and not args[0].startswith("-"):
    base = os.path.basename(args[0])
    if base == "gcc-wrapper.py" or re.search(r"(gcc|cc)(-\d+(\.\d+)*)?$", base):
        args = args[1:]

os.execvp(find_real_cc(), [find_real_cc()] + args)
