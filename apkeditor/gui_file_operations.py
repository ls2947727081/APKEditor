# gui_file_operations.py
"""APKEditor GUI文件操作模块"""

import os
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from PyQt5.QtCore import Qt, QUrl


def setup_drag_drop(main_window, line_edit):
    """设置拖放功能
    
    Args:
        main_window: APKEditorUI主窗口实例
        line_edit: 需要启用拖放功能的QLineEdit组件
    """
    line_edit.setAcceptDrops(True)
    line_edit.dragEnterEvent = main_window.dragEnterEvent
    line_edit.dropEvent = lambda e: main_window.dropEvent(e, line_edit)


def choose_file(main_window, title, filter_str):
    """通用文件选择函数
    
    Args:
        main_window: APKEditorUI主窗口实例
        title: 文件对话框标题
        filter_str: 文件过滤器
        
    Returns:
        str: 选择的文件路径
    """
    path, _ = QFileDialog.getOpenFileName(main_window, title, ".", filter_str)
    return path


def choose_input(main_window):
    """选择输入文件/目录
    
    Args:
        main_window: APKEditorUI主窗口实例
    """
    # 支持选择文件或目录
    # 创建自定义对话框
    from PyQt5.QtWidgets import QFileDialog
    
    # 设置文件对话框
    file_dialog = QFileDialog(main_window, "选择输入文件或目录")
    file_dialog.setFileMode(QFileDialog.ExistingFiles)
    file_dialog.setOption(QFileDialog.DontUseNativeDialog, True)
    
    # 添加选择目录按钮
    from PyQt5.QtWidgets import QPushButton
    
    # 执行对话框
    if file_dialog.exec_():
        # 获取选择的文件/目录
        selected_paths = file_dialog.selectedFiles()
        if selected_paths:
            # 如果选择了多个文件，只使用第一个
            main_window.input_line.setText(selected_paths[0])
    else:
        # 如果用户取消，尝试获取目录选择
        dir_path = QFileDialog.getExistingDirectory(main_window, "选择输入目录")
        if dir_path:
            main_window.input_line.setText(dir_path)


def choose_jar(main_window):
    """选择JAR文件
    
    Args:
        main_window: APKEditorUI主窗口实例
    """
    path = choose_file(main_window, "选择 APKEditor JAR 文件", "Jar Files (*.jar);;All Files (*)")
    if path:
        main_window.jar_path = path
        main_window.jar_label.setText(f"JAR: {os.path.abspath(path)}")
        main_window.update_preview()


def choose_keystore(main_window):
    """选择密钥库文件
    
    Args:
        main_window: APKEditorUI主窗口实例
    """
    path = choose_file(main_window, "选择签名密钥文件", "Keystore Files (*.jks *.keystore);;All Files (*)")
    if path:
        main_window.keystore_path.setText(path)


def choose_private_key(main_window):
    """选择私钥文件
    
    Args:
        main_window: APKEditorUI主窗口实例
    """
    path = choose_file(main_window, "选择私钥文件", "Key Files (*.pem *.key);;All Files (*)")
    if path:
        main_window.private_key_path.setText(path)


def choose_public_key(main_window):
    """选择公钥文件
    
    Args:
        main_window: APKEditorUI主窗口实例
    """
    path = choose_file(main_window, "选择公钥文件", "Certificate Files (*.crt *.pem *.der);;All Files (*)")
    if path:
        main_window.public_key_path.setText(path)


def on_key_type_changed(main_window):
    """处理密钥类型变更
    
    Args:
        main_window: APKEditorUI主窗口实例
    """
    # 更新UI元素的可见性
    main_window._update_key_type_visibility()
    # 更新命令预览
    main_window.update_preview()


def update_key_type_visibility(main_window):
    """更新密钥类型相关元素的可见性
    
    Args:
        main_window: APKEditorUI主窗口实例
    """
    keystore_visible = main_window.radio_keystore.isChecked()
    key_pair_visible = main_window.radio_key_pair.isChecked()
    
    # 密钥库方式元素可见性
    keystore_widgets = [main_window.keystore_path, main_window.keystore_alias, main_window.keystore_password, main_window.keystore_btn]
    for widget in keystore_widgets:
        widget.setVisible(keystore_visible)
    
    # 公钥私钥方式元素可见性
    key_pair_widgets = [main_window.private_key_path, main_window.private_key_password, main_window.public_key_path, main_window.private_key_btn, main_window.public_key_btn]
    for widget in key_pair_widgets:
        widget.setVisible(key_pair_visible)
    
    # 更新相关标签的可见性
    for label in main_window.findChildren(QLabel):
        if label.text().startswith("签名密钥") or label.text().startswith("密钥别名") or label.text().startswith("密钥密码:"):
            label.setVisible(keystore_visible)
        elif label.text().startswith("私钥文件") or label.text().startswith("私钥密码") or label.text().startswith("公钥文件"):
            label.setVisible(key_pair_visible)