# syntax_highlighter.py
"""语法高亮模块"""

import re
from PyQt5.QtGui import QFont, QColor, QSyntaxHighlighter, QTextCharFormat


class ConsoleHighlighter(QSyntaxHighlighter):
    """控制台输出语法高亮器"""
    
    def __init__(self, parent=None):
        try:
            super().__init__(parent)
            
            # 使用字典定义格式化规则
            format_rules = {
                'error': {'color': '#FF6B6B', 'weight': QFont.Bold},
                'success': {'color': '#4ECDC4', 'weight': QFont.Bold},
                'warning': {'color': '#FFD166', 'weight': QFont.Normal},
                'command': {'color': '#118AB2', 'weight': QFont.Bold},
                'info': {'color': '#073B4C', 'weight': QFont.Normal},
                'corex': {'color': '#9C27B0', 'weight': QFont.Bold},
                'progress': {'color': '#2196F3', 'weight': QFont.Normal}
            }
            
            # 批量设置格式化对象
            for format_name, rules in format_rules.items():
                format_obj = QTextCharFormat()
                format_obj.setForeground(QColor(rules['color']))
                format_obj.setFontWeight(rules['weight'])
                setattr(self, f'{format_name}_format', format_obj)
        except Exception as e:
            print(f"初始化ConsoleHighlighter时出错: {str(e)}")
    
    def highlightBlock(self, text):
        """处理文本块的语法高亮"""
        try:
            # 确保text是字符串类型
            if not isinstance(text, str):
                text = str(text)
            
            # 首先移除所有ANSI颜色代码，避免干扰匹配
            text_clean = re.sub(r'\033\[[0-9;]*[mK]', '', text)
            
            # 定义高亮规则 - (格式对象, 正则表达式模式列表)
            highlight_rules = [
                (getattr(self, 'error_format', None), [r'ERROR|错误|失败|Exception|✘|无法|未找到|不存在']),
                (getattr(self, 'success_format', None), [r'SUCCESS|成功|完成|已找到|已添加|已修复|已清理|[✓✔]|提取.*成功|合并成功|反编译成功|重新编译成功']),
                (getattr(self, 'warning_format', None), [r'WARNING|警告|跳过']),
                (getattr(self, 'corex_format', None), [r'CoreX|Hook|lib_Pairip_CoreX|arm64-v8a']),
                (getattr(self, 'info_format', None), [r'\[.*?\]|开始合并拆分APK|使用APKEditor反编译APK|开始应用Smali补丁|处理完成|输出文件:|包名|Flutter应用|耗时|架构'])
            ]
            
            # 应用正则表达式高亮规则
            for format_obj, patterns in highlight_rules:
                if format_obj:  # 确保格式对象存在
                    for pattern in patterns:
                        try:
                            for match in re.finditer(pattern, text_clean):
                                start, end = match.span()
                                self.setFormat(start, end - start, format_obj)
                        except re.error:
                            pass  # 跳过无效的正则表达式
            
            # 特殊规则：命令高亮
            if hasattr(self, 'command_format') and (text_clean.strip().startswith('$') or 'java -jar' in text_clean):
                self.setFormat(0, len(text), self.command_format)
            
            # 特殊规则：进度条或分隔线高亮
            if hasattr(self, 'progress_format') and ('=' * 10 in text_clean or '_' * 10 in text_clean):
                self.setFormat(0, len(text), self.progress_format)
        except Exception as e:
            print(f"应用语法高亮时出错: {str(e)}")