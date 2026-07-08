"""Strip build-time-only glslang static libs + headers from the built wheel(s).

The compiled extension (`_rife_ncnn_vulkan_wrapper.{pyd,so}`) statically links
glslang/ncnn, so the `rife_ncnn_vulkan_python/lib/` (glslang*.lib/.a, ~40MB on
Windows) and `rife_ncnn_vulkan_python/include/` trees that glslang's install()
rules drop into the wheel are dead weight at runtime. Runtime needs only the
compiled extension, the SWIG .py shims, and vcomp140.dll. Removing them shrinks
the wheel ~15-18x. Run BEFORE replace_whl.py so the repacked wheel keeps the
correct platform tag before renaming.
"""

import pathlib
import shutil
import subprocess
import sys

dist = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "dist")
work = dist / "_strip"

for whl in sorted(dist.glob("*.whl")):
    if work.exists():
        shutil.rmtree(work)
    subprocess.check_call(
        [sys.executable, "-m", "wheel", "unpack", str(whl), "-d", str(work)]
    )
    pkg = next(work.glob("*/rife_ncnn_vulkan_python"))
    for junk in ("lib", "include"):
        p = pkg / junk
        if p.exists():
            shutil.rmtree(p)
    vdir = next(d for d in work.glob("*") if d.is_dir())
    whl.unlink()
    subprocess.check_call(
        [sys.executable, "-m", "wheel", "pack", str(vdir), "-d", str(dist)]
    )
    shutil.rmtree(work)

print("stripped:", [p.name for p in sorted(dist.glob("*.whl"))])
