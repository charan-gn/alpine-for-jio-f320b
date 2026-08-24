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

# unconditional includes of headers that don't exist in the public tree
SRCKILLS = [
    ("drivers/usb/gadget/configfs.c",
     ["<function/u_ncm.h>", '"function/u_ncm.h"']),
]

# exact-line replacements for unguarded calls into removed code
SRCREPLACE = [
    ("drivers/usb/gadget/configfs.c",
     "value = ncm_ctrlrequest(cdev, c);",
     "value = -EOPNOTSUPP; /* f320b-oss: NCM removed */"),
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

for rel, frags in SRCKILLS:
    p = f"{tree}/{rel}"
    try:
        lines = open(p).read().split("\n")
    except FileNotFoundError:
        continue
    kept = [ln for ln in lines if not any(f in ln for f in frags)]
    if len(kept) != len(lines):
        open(p, "w").write("\n".join(kept))
        print(f"stripped {len(lines)-len(kept)} include(s) from {p}")

for rel, old, new in SRCREPLACE:
    p = f"{tree}/{rel}"
    try:
        s = open(p).read()
    except FileNotFoundError:
        continue
    if old in s:
        open(p, "w").write(s.replace(old, new))
        print(f"patched call in {p}")

# ---- link-time stubs for amputated vendor code ----
STUBS = r"""/* f320b-oss: no-op replacements for vendor objects whose
 * sources/headers are missing from the public CLO tree. */
#include <linux/kernel.h>
#include <linux/export.h>

void tracer_pkt_log_event(void *pkt, const char *event)
{
	(void)pkt; (void)event;
}
EXPORT_SYMBOL(tracer_pkt_log_event);

int register_system_pm_ops(const void *ops)
{
	(void)ops;
	return 0;
}
EXPORT_SYMBOL(register_system_pm_ops);

int unregister_system_pm_ops(const void *ops)
{
	(void)ops;
	return 0;
}
EXPORT_SYMBOL(unregister_system_pm_ops);

void lpm_cpu_hotplug_enter(void)
{
}
EXPORT_SYMBOL(lpm_cpu_hotplug_enter);

void lpm_cpu_pre_pc_cb(void)
{
}
EXPORT_SYMBOL(lpm_cpu_pre_pc_cb);

void lpm_cpu_post_pc_cb(void)
{
}
EXPORT_SYMBOL(lpm_cpu_post_pc_cb);

int lpm_do_suspend(void)
{
	return 0;
}
EXPORT_SYMBOL(lpm_do_suspend);
"""

d = f"{tree}/drivers/soc/qcom"
open(f"{d}/f320b-stubs.c", "w").write(STUBS)
mk = f"{d}/Makefile"
cur = open(mk).read()
if "f320b-stubs.o" not in cur:
    open(mk, "a").write("\nobj-y += f320b-stubs.o\n")
    print("added f320b-stubs.o to soc/qcom")
