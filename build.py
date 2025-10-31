import os
import sys
import subprocess
from PIL import Image, ImageDraw

# -------------------------------------------------------------
# Step 1. 生成标签图标 (tag.ico)
# -------------------------------------------------------------
def make_tag_icon(filename="tag.ico"):
    print("[+] 生成图标:", filename)
    sizes = [256, 48, 32, 16]
    imgs = []
    for size in sizes:
        img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        pad = int(size * 0.12)
        points = [
            (pad, pad + int(size * 0.12)),
            (size - int(size * 0.25), pad),
            (size - pad, size - int(size * 0.25)),
            (int(size * 0.25), size - pad),
        ]
        draw.polygon(points, fill=(220, 100, 40, 255))
        hole_r = max(2, size // 12)
        hole_center = (int(size * 0.75), int(size * 0.18))
        draw.ellipse(
            [
                hole_center[0] - hole_r,
                hole_center[1] - hole_r,
                hole_center[0] + hole_r,
                hole_center[1] + hole_r,
            ],
            fill=(255, 255, 255, 255),
        )
        draw.line(
            [points[0], points[1], points[2], points[3], points[0]],
            fill=(255, 255, 255, 180),
            width=max(1, size // 40),
        )
        imgs.append(img)
    imgs[0].save(filename, sizes=[(s, s) for s in sizes])
    return filename


# -------------------------------------------------------------
# Step 2. 打包 apkeditor_main.py 成 EXE
# -------------------------------------------------------------
def build_exe(script="apkeditor_main.py", icon="tag.ico"):
    if not os.path.exists(script):
        print(f"[!] 找不到 {script}")
        sys.exit(1)

    cmd = [
        "pyinstaller",
        "--onefile",       # 打包为单个exe
        "--noconsole",     # 隐藏黑框
        "--icon", icon,    # 使用图标
        "--name", "ApkEditor",  # EXE 名称
        script
    ]

    print("[+] 正在执行命令：", " ".join(cmd))
    subprocess.run(cmd, check=True)
    print("\n[√] 打包完成！EXE 路径：dist/ApkEditor.exe\n")


if __name__ == "__main__":
    make_tag_icon("tag.ico")
    build_exe("apkeditor_main.py", "tag.ico")
