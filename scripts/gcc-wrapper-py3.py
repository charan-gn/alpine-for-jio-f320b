#!/usr/bin/env python3
"""Drop-in replacement for CLO's gcc-wrapper.py.

The stock wrapper colorizes warnings using python2 syntax and breaks modern
runners. This passes all arguments straight through to $REAL_CC (or the
cross-gcc found in PATH) preserving exit status via execvp.
"""
import os
import shutil

real_cc = os.environ.get("REAL_CC")
if not real_cc:
    for candidate in (
        "arm-linux-gnueabihf-gcc",
        "aarch64-linux-gnu-gcc",
        "gcc",
    ):
        p = shutil.which(candidate)
        if p:
            real_cc = p
            break

argv = sys_argv = None
import sys
sys_argv = sys.argv[1:]

# strip a leading duplicate of ourselves if make passes it back
if sys_argv and sys_argv[0].endswith("gcc-wrapper.py"):
    sys_argv = sys_argv[1:]

os.execvp(real_cc or "gcc", [real_cc or "gcc"] + sys_argv)
