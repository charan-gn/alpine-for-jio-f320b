#!/usr/bin/env python3
"""Scan kernel sources for #include targets that don't exist in-tree.
CLO public trees ship some vendor files without their private headers;
this reports every affected file at once so builds can be fixed in bulk."""
import os, re, sys

tree = sys.argv[1] if len(sys.argv) > 1 else "kernel"
INC = re.compile(r'^\s*#include\s+[<"]([^">]+)[">]', re.M)
roots = [f"{tree}/drivers", f"{tree}/sound", f"{tree}/techpack"]

broken = {}
for root in roots:
    if not os.path.isdir(root):
        continue
    for dirpath, _, files in os.walk(root):
        for fn in files:
            if not fn.endswith((".c", ".h")):
                continue
            p = os.path.join(dirpath, fn)
            try:
                src = open(p, encoding="latin1").read()
            except OSError:
                continue
            for inc in INC.findall(src):
                if inc.endswith(".h"):
                    cand = [
                        os.path.join(dirpath, inc),
                        os.path.join(dirpath, "inc", inc),
                        os.path.join(tree, "include", inc),
                        os.path.join(tree, inc),
                        os.path.join(tree, "arch", "arm", "include", inc),
                    ]
                    if not any(os.path.exists(c) for c in cand):
                        broken.setdefault(inc, []).append(os.path.relpath(p, tree))

for h in sorted(broken):
    print(f"MISSING {h}")
    for f in broken[h][:4]:
        print(f"        used by {f}")
print(f"\ntotal missing headers: {len(broken)}")
