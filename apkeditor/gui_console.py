# gui_console.py
"""APKEditor GUI控制台处理模块"""

import re
from PyQt5.QtWidgets import QAction, QMenu


def setup_context_menu(main_window):
    """设置右键菜单
    
    Args:
        main_window: APKEditorUI主窗口实例
    """
    main_window.context_menu = QMenu()
    
    main_window.copy_action = QAction("复制")
    main_window.copy_action.triggered.connect(main_window._copy_selected_text)
    
    main_window.select_all_action = QAction("全选")
    main_window.select_all_action.triggered.connect(main_window._select_all_text)
    
    main_window.clear_action = QAction("清空")
    main_window.clear_action.triggered.connect(main_window._clear_console)
    
    main_window.context_menu.addActions([main_window.copy_action, main_window.select_all_action, main_window.clear_action])
    
    main_window.output_console.setContextMenuPolicy(Qt.CustomContextMenu)
    main_window.output_console.customContextMenuRequested.connect(main_window._show_context_menu)


def append_to_console(main_window, text):
    """在控制台添加文本（确保在主线程执行）
    
    Args:
        main_window: APKEditorUI主窗口实例
        text: 要添加的文本内容
    """
    # 分割文本为多行，便于处理和显示
    lines = text.split('\n')
    for line in lines:
        if line.strip():
            # 文本已经在on_pairip_progress中清理过ANSI颜色代码
            clean_line = line
            
            # 使用模式匹配字典简化消息类型识别
            message_types = [
                ('error', [
                    r'^ERROR:', r'^Error:', r'^错误:', r'^Exception:',
                    r'\bfailed\b', r'\bfailure\b', r'\b失败\b', r'^✘'
                ], False),
                ('success', [
                    r'^SUCCESS:', r'^成功:', r'^完成:', r'\bsuccess\b',
                    r'\b成功\b', r'\b完成\b', r'^✓', r'^✔'
                ], False),
                ('warning', ['WARNING', '警告'], True),
                ('corex', ['corex', 'hook', 'lib_pairip_corex'], True)
            ]
            
            # 检查是否为错误消息
            is_error = any(re.search(pattern, clean_line, re.IGNORECASE) 
                          for pattern in message_types[0][1])
            
            # 检查是否包含日志级别前缀，如果是则不是错误
            log_level_patterns = [
                r'^\d+\.\d+\s+I:', r'^\[MERGE\]',
                r'^\d+\.\d+\s+D:', r'^\[DEBUG\]'
            ]
            
            has_log_level_prefix = any(re.match(pattern, clean_line) for pattern in log_level_patterns)
            
            # 根据消息类型设置不同的颜色
            if is_error and not has_log_level_prefix:
                clean_line = f"<font color='#FF5555'>{clean_line}</font>"
            elif any(re.search(pattern, clean_line, re.IGNORECASE if case_insensitive else 0)
                    for msg_type, patterns, case_insensitive in message_types[1:] for pattern in patterns):
                if 'success' in str(message_types) and any(re.search(pattern, clean_line, re.IGNORECASE) for pattern in message_types[1][1]):
                    clean_line = f"<font color='#50fa7b'>{clean_line}</font>"
                elif 'warning' in str(message_types) and any(re.search(pattern, clean_line) for pattern in message_types[2][1]):
                    clean_line = f"<font color='#FFA500'>{clean_line}</font>"
                elif 'corex' in str(message_types) and any(re.search(pattern, clean_line, re.IGNORECASE) for pattern in message_types[3][1]):
                    clean_line = f"<font color='#BD93F9'>{clean_line}</font>"
            
            # 添加到控制台
            main_window.output_console.append(clean_line)


def on_stdout(main_window):
    """处理标准输出
    
    Args:
        main_window: APKEditorUI主窗口实例
    """
    try:
        text = main_window.process.readAllStandardOutput().data().decode('utf-8', errors='replace')
        append_to_console(main_window, text)
    except Exception as e:
        main_window.output_console.append(f"[错误] 处理输出时发生异常: {str(e)}")


def on_stderr(main_window):
    """处理标准错误
    
    Args:
        main_window: APKEditorUI主窗口实例
    """
    try:
        text = main_window.process.readAllStandardError().data().decode('utf-8', errors='replace')
        append_to_console(main_window, text)
    except Exception as e:
        main_window.output_console.append(f"[错误] 处理错误输出时发生异常: {str(e)}")

# 导入Qt模块
from PyQt5.QtCore import Qt

def on_pairip_progress(self, message):
    """处理Pairip进度更新"""
    # 移除ANSI颜色代码
    ansi_escape = re.compile(r'\x1B(?:[@-Z\-_]|\[[0-?]*[ -/]*[@-~])')
    clean_message = ansi_escape.sub('', message)
    append_to_console(self, clean_message)

# 导出的函数列表
__all__ = ['setup_context_menu', 'append_to_console', 'on_stdout', 'on_stderr', 'on_pairip_progress']