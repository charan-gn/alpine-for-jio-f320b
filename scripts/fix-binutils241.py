#!/usr/bin/env python3
"""binutils>=2.41 fixes for old ARM kernels:
   - .type/.size "#function"/"#object"  -> "%function"/"%object"
   - .section NAME, #alloc, #execinstr  -> .section NAME,"ax"
"""
import os, re, sys

tree = sys.argv[1] if len(sys.argv) > 1 else "kernel"
FLAG = {"alloc": "a", "execinstr": "x", "write": "w", "readonly": "r"}
TYPE_RE = re.compile(r"^(\s*\.(?:type|size)\s+[^,]+),\s*#", re.M)
SEC_RE = re.compile(r"^(\s*\.section\s+[^,]+?)\s*,\s*(#.*)$")

def fix_section(mo):
    letters = []
    for tok in mo.group(2).split(","):
        tok = tok.strip().lstrip("#").strip()
        if not tok:
            continue
        letters.append(FLAG.get(tok, tok[0]))
    return f'{mo.group(1)},"{"".join(letters)}"'

patched = []
for root, _, files in os.walk(tree):
    if "/arch/arm" not in root.replace(os.sep, "/") and \
       root.replace(os.sep, "/") != f"{tree}/kernel" and \
       not root.replace(os.sep, "/").startswith(f"{tree}/kernel/"):
        continue
    for fn in files:
        if not fn.endswith((".S", ".s")):
            continue
        p = os.path.join(root, fn)
        src = open(p, encoding="latin1").read()
        out = TYPE_RE.sub(r"\1, %", src)
        out = "\n".join(SEC_RE.sub(fix_section, ln) for ln in out.split("\n"))
        if out != src:
            open(p, "w", encoding="latin1").write(out)
            patched.append(p)

print(f"{len(patched)} files patched")
