import os
import sys
import random
import subprocess
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# ---------------- 配置 ----------------
OUTPUT_DIR = "generated_icons"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 可用 Emoji 表情列表
EMOJI_LIST = ["😀","😎","😡","🤔","🥳","🤯","😂","😅","😴","😇"]

# ---------------- 生成现代化表情图标 ----------------
def draw_modern_emoji(size=256):
    """生成现代化随机表情图标"""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # 背景圆形 + 渐变色
    bg_color = tuple(random.randint(100, 255) for _ in range(3))
    draw.ellipse([0, 0, size, size], fill=bg_color + (255,))

    # 表情文字
    emoji = random.choice(EMOJI_LIST)
    try:
        font = ImageFont.truetype("seguiemj.ttf", size=int(size*0.6))
    except:
        font = ImageFont.load_default()

    # 计算文字宽高
    if hasattr(draw, "textbbox"):
        bbox = draw.textbbox((0, 0), emoji, font=font)
        w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    else:
        w, h = draw.textsize(emoji, font=font)

    draw.text(((size - w)/2, (size - h)/2), emoji, font=font, fill=(255,255,255,255))

    # 投影阴影
    shadow = img.filter(ImageFilter.GaussianBlur(radius=size*0.03))
    final = Image.alpha_composite(shadow, img)
    return final

# ---------------- 生成多尺寸 ICO 和额外图标 ----------------
def generate_icon_files():
    sizes = [256, 128, 64, 48, 32, 16]
    ico_imgs = []

    # 临时生成各尺寸图片
    for s in sizes:
        img = draw_modern_emoji(s)
        tmp_path = os.path.join(OUTPUT_DIR, f"tmp_{s}.png")
        img.save(tmp_path)
        ico_imgs.append(img)

    # 保存多尺寸 ICO
    ico_path = os.path.join(OUTPUT_DIR, "tag.ico")
    ico_imgs[0].save(ico_path, sizes=[(s,s) for s in sizes])
    print(f"[+] 已生成现代化多尺寸 ICO: {ico_path}")

    # 任务栏图标 (128x128)
    draw_modern_emoji(128).save(os.path.join(OUTPUT_DIR, "taskbar.png"))
    # 右上角小图标 (32x32)
    draw_modern_emoji(32).save(os.path.join(OUTPUT_DIR, "corner.png"))

    return ico_path

# ---------------- 打包 EXE ----------------
def build_exe(script="apkeditor_main.py", icon="tag.ico"):
    if not os.path.exists(script):
        print(f"[!] 找不到 {script}")
        sys.exit(1)

    cmd = [
        "pyinstaller",
        "--onefile",       # 单文件
        "--noconsole",     # 隐藏控制台
        "--icon", icon,    # 使用图标
        "--name", "ApkEditor",
        script
    ]

    print("[+] 执行打包命令：", " ".join(cmd))
    subprocess.run(cmd, check=True)
    print("\n[√] 打包完成！EXE 路径：dist/ApkEditor.exe\n")

# ---------------- 主程序 ----------------
if __name__ == "__main__":
    icon_file = generate_icon_files()           # 生成图标
    build_exe("apkeditor_main.py", icon_file)   # 打包 EXE
