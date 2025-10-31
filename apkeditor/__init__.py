# __init__.py
"""APKEditor包初始化文件"""

# 导出主GUI类
from .gui import APKEditorGUI

# 导出各个功能模块（可选，便于调试和扩展）
from . import gui_ui
from . import gui_events
from . import gui_console
from . import gui_file_operations
from .command_handler import CommandHandler

__version__ = "1.0.0"
__all__ = ["APKEditorGUI", "CommandHandler"]

# 添加异常处理，确保导入失败不会导致整个程序崩溃
try:
    from .gui import APKEditorGUI
except ImportError as e:
    print(f"导入GUI模块失败: {str(e)}")
    APKEditorGUI = None

try:
    from .command_handler import CommandHandler
except ImportError as e:
    print(f"导入命令处理器失败: {str(e)}")
    CommandHandler = None

try:
    from .syntax_highlighter import ConsoleHighlighter
except ImportError as e:
    print(f"导入语法高亮模块失败: {str(e)}")
    ConsoleHighlighter = None

try:
    from .constants import OP_MAP, OP_DESCRIPTIONS, FILE_FILTERS, DEFAULT_JAR
except ImportError as e:
    print(f"导入常量模块失败: {str(e)}")
    # 提供默认值以防止程序因为缺少常量而崩溃
    OP_MAP = {"反编译 (decompile)": "d", "构建 (build)": "b", "信息 (info)": "info"}
    OP_DESCRIPTIONS = {}
    FILE_FILTERS = {}
    import os
    DEFAULT_JAR = os.path.abspath(os.path.join(".", "lib", "APKEditor.jar"))

__all__ = [
    'APKEditorGUI',
    'CommandHandler', 
    'ConsoleHighlighter',
    'OP_MAP',
    'OP_DESCRIPTIONS',
    'FILE_FILTERS',
    'DEFAULT_JAR'
]