# constants.py
"""常量定义模块"""

import os
import glob

def find_apkeditor_jar():
    """查找APKEditor jar文件"""
    # 按优先级查找：当前目录 -> lib目录 -> 默认路径
    for directory in [".", os.path.join(".", "lib")]:
        if os.path.isdir(directory):
            matches = glob.glob(os.path.join(directory, "APKEditor*.jar"))
            if matches:
                return os.path.abspath(matches[0])
    # 默认路径
    return os.path.abspath(os.path.join(".", "lib", "APKEditor.jar"))

# 默认JAR路径
DEFAULT_JAR = find_apkeditor_jar()

# 配置选项
PAIRIP_OPTIONS = {}
SUPPORTED_ARCHITECTURES = ("arm64-v8a", "armeabi-v7a", "x86_64", "x86")

# 操作映射字典
OP_MAP = {
    "反编译 (decompile)": "d",
    "构建 (build)": "b",
    "合并 (merge)": "m",
    "重构 (refactor)": "x",
    "保护 (protect)": "p",
    "信息 (info)": "info",
    "签名 (sign)": "sign",
    "Pairip处理 (pairip)": "pairip"
}

# 操作描述
OP_DESCRIPTIONS = {
    "反编译 (decompile)": "将 apk 的资源反编译为人类可读的 json 字符串。\n使用 -t xml 参数可将 apk 的资源反编译为 XML 源代码。\n命令示例: java -jar APKEditor.jar d -i path/to/your-file.apk",
    "构建 (build)": "从反编译的 json/XML 文件构建回 apk。\n命令示例: java -jar APKEditor.jar b -i path/to/decompiled-directory",
    "合并 (merge)": "将多个拆分的 apk 文件（目录、xapk、apkm、apks 等）合并到独立 apk。\n命令示例: java -jar APKEditor.jar m -i path/to/input",
    "重构 (refactor)": "重构混淆的资源条目名称。\n命令示例: java -jar APKEditor.jar x -i path/to/input.apk",
    "保护 (protect)": "保护 apk 资源免受几乎所有已知反编译/修改工具的侵害。\n命令示例: java -jar APKEditor.jar p -i path/to/input.apk",
    "信息 (info)": "打印/转储从 apk 的基本信息到详细信息。\n使用 -v 和 -resources 参数可获取更详细的信息。\n命令示例: java -jar APKEditor.jar info -v -resources -i input.apk",
    "签名 (sign)": "使用 Android 签名工具为 APK 文件签名。\n支持 v1-v4 签名方案，需要指定签名密钥、别名、密码等信息。\n命令示例: java -jar APKEditor.jar sign -i path/to/input.apk -o path/to/output.apk -ks keystore.jks -ksa alias -ksp password",
    "Pairip处理 (pairip)": "处理.apks文件并应用CoreX Hook功能，绕过签名验证和授权检查。\n支持合并.apks文件、应用Smali补丁、CoreX Hook等功能。\n仅支持.apks格式文件，适用于需要特殊处理的APK文件。"
}

# 文件过滤器配置
FILE_FILTERS = {
    "反编译 (decompile)": "APK Files (*.apk *.apks *.xapk *.zip);;All Files (*)",
    "构建 (build)": "文件夹",  # 选择目录
    "合并 (merge)": "APK Files (*.apks *.xapk *.apkm *.zip);;文件夹",  # 支持文件和目录
    "重构 (refactor)": "APK Files (*.apk);;All Files (*)",
    "保护 (protect)": "APK Files (*.apk);;All Files (*)",
    "信息 (info)": "APK Files (*.apk *.apks *.xapk *.zip);;All Files (*)",
    "签名 (sign)": "APK Files (*.apk);;All Files (*)",
    "Pairip处理 (pairip)": "APKS Files (*.apks);;All Files (*)"
}