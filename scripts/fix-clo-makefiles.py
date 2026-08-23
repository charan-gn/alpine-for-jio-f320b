#!/usr/bin/env python3
"""Comment out known-broken CLO vendor objects whose headers are missing
from the public tree. Extend KILLS as new ones surface."""
import sys

tree = sys.argv[1] if len(sys.argv) > 1 else "kernel"

# makefile-relative-to-drivers : object basenames to neutralize
KILLS = [
    ("cpuidle/Makefile", ["lpm-workarounds"]),
    ("soc/qcom/Makefile", ["tracer_pkt"]),
]

for rel, objs in KILLS:
    p = f"{tree}/drivers/{rel}"
    try:
        lines = open(p).read().split("\n")
    except FileNotFoundError:
        continue
    changed = False
    for i, ln in enumerate(lines):
        if any(f"{o}.o" in ln for o in objs) and not ln.lstrip().startswith("#"):
            lines[i] = "# f320b-oss: broken upstream (" + ln.strip() + ")"
            changed = True
    if changed:
        open(p, "w").write("\n".join(lines))
        print(f"neutralized {objs} in {p}")
