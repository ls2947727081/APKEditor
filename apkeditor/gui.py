# gui.py
"""APKEditor GUI主类模块 - 轻量级入口"""

import os
import sys
import configparser
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QLabel, QPushButton
from PyQt5.QtCore import QProcess, Qt, QThread
from PyQt5.QtGui import QIcon

# 导入命令处理器
from .command_handler import CommandHandler

# 导入功能模块
from .gui_ui import setup_ui
from .gui_events import on_run
from .gui_console import setup_context_menu, append_to_console, on_stdout, on_stderr, on_pairip_progress
from .gui_file_operations import (
    setup_drag_drop, choose_file, choose_input, choose_jar,
    choose_keystore, choose_private_key, choose_public_key,
    on_key_type_changed, update_key_type_visibility
)

# 尝试导入PairipHandler
try:
    from .pairip_handler import PairipHandler
except ImportError as e:
    print(f"导入PairipHandler失败: {str(e)}")
    PairipHandler = None

# 获取应用根目录，支持PyInstaller打包
def get_app_root():
    # PyInstaller打包后会设置_MEIPASS属性
    if hasattr(sys, '_MEIPASS'):
        return sys._MEIPASS
    # 正常运行时返回当前脚本所在目录的父目录
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class APKEditorGUI(QMainWindow):
    """APKEditor GUI主窗口类"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("APKEditor GUI — 封装 APKEditor-1.4.5.jar")
        # 增大默认窗口大小
        self.resize(1200, 800)
        
        # 设置窗口图标
        app_root = get_app_root()
        icon_paths = [
            os.path.join(app_root, 'generated_icons', 'tag.ico'),
            os.path.join(app_root, 'generated_icons', 'tmp_64.png'),
            os.path.join(app_root, 'generated_icons', 'tmp_32.png')
        ]
        
        for icon_path in icon_paths:
            if os.path.exists(icon_path):
                self.setWindowIcon(QIcon(icon_path))
                print(f"已设置窗口图标: {icon_path}")
                break
        
        self.process = QProcess(self)
        self.process.readyReadStandardOutput.connect(self._on_stdout)
        self.process.readyReadStandardError.connect(self._on_stderr)
        self.process.finished.connect(self.on_finished)
        
        # 初始化可能在其他方法中使用的属性
        self._last_key_type = 'keystore'  # 初始化密钥类型
        self.context_menu = None
        self.copy_action = None
        
        # 密钥配置文件路径
        self.key_config_path = os.path.join(get_app_root(), 'lib', 'key.ini')
        
        try:
            # 使用模块的setup_ui函数
            setup_ui(self)
            # 检查JAR文件
            from .constants import DEFAULT_JAR
            self.jar_path = DEFAULT_JAR
            if not os.path.exists(self.jar_path):
                self.jar_label.setText(f"JAR: 未找到默认 jar ({self.jar_path}) - 请手动选择")
            else:
                self.jar_label.setText(f"JAR: {os.path.abspath(self.jar_path)}")
            
            # 加载保存的密钥信息
            self.load_key_info()
            
            # 设置默认操作为反编译
            from .constants import OP_MAP
            # 找到反编译操作对应的键
            decompile_op = next((key for key in OP_MAP.keys() if '反编译' in key), None)
            if decompile_op:
                self.current_op = decompile_op
                # 调用on_op_change来更新UI状态
                self.on_op_change()
            
            # 初始更新模式标签
            self.update_mode_label()
            
        except Exception as e:
            import traceback
            print(f"初始化UI出错: {str(e)}")
            print(traceback.format_exc())
            QMessageBox.critical(self, "初始化错误", f"程序初始化时出错: {str(e)}")

    # 委托给模块的方法
    def _setup_drag_drop(self, line_edit):
        return setup_drag_drop(self, line_edit)
    
    def _setup_context_menu(self):
        return setup_context_menu(self)
    
    def _choose_file(self, title, filter_str):
        return choose_file(self, title, filter_str)
    
    def choose_input(self):
        return choose_input(self)
    
    def choose_jar(self):
        return choose_jar(self)
    
    def choose_keystore(self):
        return choose_keystore(self)
    
    def choose_private_key(self):
        return choose_private_key(self)
    
    def choose_public_key(self):
        return choose_public_key(self)
    
    def on_key_type_changed(self):
        return on_key_type_changed(self)
    
    def _update_key_type_visibility(self):
        return update_key_type_visibility(self)
    
    # 核心方法
    def on_run(self):
        return on_run(self)
    
    def _append_to_console(self, text):
        return append_to_console(self, text)
    
    def _on_stdout(self):
        return on_stdout(self)
    
    def _on_stderr(self):
        return on_stderr(self)
    
    def on_pairip_progress(self, message):
        return on_pairip_progress(self, message)
    
    def on_key_type_changed(self):
        """处理密钥类型变更 - 确保完全互斥选择"""
        try:
            # 使用blockSignals临时阻止信号，避免递归触发
            self.radio_keystore.blockSignals(True)
            self.radio_key_pair.blockSignals(True)
            
            # 确保互斥选择
            if self.sender() == self.radio_keystore and self.radio_keystore.isChecked():
                self.radio_key_pair.setChecked(False)
                self._last_key_type = 'keystore'
            elif self.sender() == self.radio_key_pair and self.radio_key_pair.isChecked():
                self.radio_keystore.setChecked(False)
                self._last_key_type = 'key_pair'
            # 处理没有sender的情况（初始化时）
            elif hasattr(self, '_last_key_type'):
                if self._last_key_type == 'keystore':
                    self.radio_keystore.setChecked(True)
                    self.radio_key_pair.setChecked(False)
                else:
                    self.radio_keystore.setChecked(False)
                    self.radio_key_pair.setChecked(True)
            
            # 恢复信号处理
            self.radio_keystore.blockSignals(False)
            self.radio_key_pair.blockSignals(False)
            
            # 更新可见性
            self._update_key_type_visibility()
            self.update_preview()
        except Exception as e:
            import traceback
            print(f"处理密钥类型变更出错: {str(e)}")
            print(traceback.format_exc())
    
    def _update_key_type_visibility(self):
        """更新密钥类型相关元素的可见性"""
        keystore_visible = self.radio_keystore.isChecked()
        key_pair_visible = self.radio_key_pair.isChecked()
        
        # 密钥库方式元素可见性
        keystore_widgets = [self.keystore_path, self.keystore_alias, self.keystore_password, self.keystore_btn]
        for widget in keystore_widgets:
            widget.setVisible(keystore_visible)
        
        # 公钥私钥方式元素可见性
        key_pair_widgets = [self.private_key_path, self.private_key_password, self.public_key_path, self.private_key_btn, self.public_key_btn]
        for widget in key_pair_widgets:
            widget.setVisible(key_pair_visible)
        
        # 更新相关标签的可见性
        for label in self.findChildren(QLabel):
            if label.text().startswith("签名密钥") or label.text().startswith("密钥别名") or label.text().startswith("密钥密码:"):
                label.setVisible(keystore_visible)
            elif label.text().startswith("私钥文件") or label.text().startswith("私钥密码") or label.text().startswith("公钥文件"):
                label.setVisible(key_pair_visible)
    
    def choose_private_key(self):
        """选择私钥文件"""
        path = self._choose_file("选择私钥文件", "Key Files (*.pem *.key);;All Files (*)")
        if path:
            self.private_key_path.setText(path)
    
    def choose_public_key(self):
        """选择公钥文件"""
        path = self._choose_file("选择公钥文件", "Certificate Files (*.crt *.pem *.der);;All Files (*)")
        if path:
            self.public_key_path.setText(path)
    
    def choose_keystore(self):
        """选择密钥库文件"""
        path = self._choose_file("选择签名密钥文件", "Keystore Files (*.jks *.keystore);;All Files (*)")
        if path:
            self.keystore_path.setText(path)

    def update_preview(self):
        """更新命令预览"""
        self.cmd_preview.setText(CommandHandler.build_command(
            self.current_op, self.flag_xml, self.flag_verbose, self.flag_resources,
            self.flag_v1, self.flag_v2, self.flag_v3, self.flag_v4,
            self.radio_keystore, self.radio_key_pair,
            self.keystore_path, self.keystore_alias, self.keystore_password,
            self.private_key_path, self.private_key_password, self.public_key_path,
            self.input_line, self.custom_args, self.jar_path
        ))
            


    def _reset_ui_state(self):
        """重置UI状态"""
        self.run_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.progress.setVisible(False)

    def on_stop(self):
        """停止进程"""
        if self.process.state() != QProcess.NotRunning:
            self.process.kill()
            self.output_console.append("[已停止]")
        self._reset_ui_state()
        
    def closeEvent(self, event):
        """窗口关闭事件，保存密钥信息"""
        # 保存密钥信息
        self.save_key_info()
        event.accept()
    
    def on_finished(self, exitCode, exitStatus):
        """处理进程完成"""
        self.output_console.append(f"\n[进程结束 - 退出码: {exitCode}]")
        self._reset_ui_state()
    
    def on_pairip_finished(self, success, message):
        """处理Pairip完成"""
        self.output_console.append(f"处理{'成功' if success else '失败'}: {message}")
        if hasattr(self, 'pairip_thread'):
            self.pairip_thread.wait()
        self._reset_ui_state()
    
    def dragEnterEvent(self, event):
        """处理拖放进入事件"""
        # 检查是否是文件拖放
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
    
    def dropEvent(self, event, target_line_edit):
        """处理拖放事件"""
        if event.mimeData().hasUrls():
            path = event.mimeData().urls()[0].toLocalFile()
            target_line_edit.setText(path)
            self.update_preview()
    
    def _show_context_menu(self, position):
        """显示右键菜单"""
        # 更新复制操作的可用性
        self.copy_action.setEnabled(bool(self.output_console.textCursor().selectedText()))
        
        # 检查是否已添加清空密钥记录选项
        if not hasattr(self, 'clear_keys_action'):
            from PyQt5.QtWidgets import QAction
            self.clear_keys_action = QAction("清空密钥记录", self)
            self.clear_keys_action.triggered.connect(self.clear_key_info)
            self.context_menu.addAction(self.clear_keys_action)
            
        self.context_menu.exec_(self.output_console.mapToGlobal(position))
    
    def _clear_console(self):
        """清屏控制台内容"""
        self.output_console.clear()
    
    def _copy_selected_text(self):
        """复制选中的文本"""
        self.output_console.copy()
    
    def _select_all_text(self):
        """全选控制台内容"""
        self.output_console.selectAll()
    
    def on_op_button_clicked(self, op_name):
        """处理操作按钮点击事件"""
        self.current_op = op_name
        # 更新按钮选中状态
        for btn_name, btn in self.op_buttons.items():
            btn.setChecked(btn_name == op_name)
        # 调用原有的操作变更处理逻辑
        self.on_op_change()
    
    def on_op_change(self):
        """处理操作变更逻辑"""
        op_text = self.current_op
        is_signing = op_text.startswith("签名")
        is_pairip = op_text.startswith("Pairip")
        
        # 设置通用标志的可见性和可用性
        self.flag_xml.setVisible(not is_signing and not is_pairip)
        self.flag_xml.setEnabled(op_text.startswith("反编译"))
        self.flag_resources.setVisible(not is_signing and not is_pairip)
        self.flag_resources.setEnabled(True)
        self.flag_corex.setVisible(is_pairip)
        self.flag_corex.setEnabled(is_pairip)
        
        # 设置签名相关标志的可见性
        for flag in [self.flag_v1, self.flag_v2, self.flag_v3, self.flag_v4]:
            flag.setVisible(is_signing)
        
        # 设置签名相关UI元素的可见性
        signing_widgets = [
            self.keystore_path, self.keystore_alias, self.keystore_password,
            self.private_key_path, self.private_key_password, self.public_key_path,
            self.radio_keystore, self.radio_key_pair
        ]
        for widget in signing_widgets:
            widget.setVisible(is_signing)
        
        # 设置签名相关标签的可见性
        signing_labels = ["签名密钥", "密钥别名", "密钥密码", "私钥文件", "私钥密码", "公钥文件", "密钥类型:"]
        for label in self.findChildren(QLabel):
            if any(label.text().startswith(prefix) for prefix in signing_labels):
                label.setVisible(is_signing)
        
        # 设置签名相关选择按钮的可见性
        for btn in self.findChildren(QPushButton):
            if btn.text() == "选择":
                parent = btn.parent()
                if parent in [self.keystore_path.parent(), self.private_key_path.parent(), self.public_key_path.parent()]:
                    btn.setVisible(is_signing)
        
        # 初始设置公钥私钥相关元素的可见性
        if is_signing:
            self._update_key_type_visibility()
        
        # 更新模式标签
        self.update_mode_label()
        
        self.update_preview()
    
    def update_mode_label(self):
        """更新当前模式标签"""
        if hasattr(self, 'mode_label'):
            # 从current_op中提取模式名称（去掉括号内容）
            mode_name = self.current_op.split('(')[0].strip()
            self.mode_label.setText(f"当前模式: {mode_name}")
    
    def load_key_info(self):
        """加载保存的密钥信息"""
        if not os.path.exists(self.key_config_path):
            return
        
        try:
            config = configparser.ConfigParser()
            config.read(self.key_config_path, encoding='utf-8')
            
            # 加载密钥类型
            if config.has_section('KeyType'):
                key_type = config.get('KeyType', 'type', fallback='keystore')
                self._last_key_type = key_type
                if key_type == 'keystore':
                    self.radio_keystore.setChecked(True)
                    self.radio_key_pair.setChecked(False)
                else:
                    self.radio_keystore.setChecked(False)
                    self.radio_key_pair.setChecked(True)
            
            # 加载密钥库信息
            if config.has_section('Keystore'):
                self.keystore_path.setText(config.get('Keystore', 'path', fallback=''))
                self.keystore_alias.setText(config.get('Keystore', 'alias', fallback=''))
                # 密码可选，出于安全考虑不保存
                # self.keystore_password.setText(config.get('Keystore', 'password', fallback=''))
            
            # 加载公钥私钥信息
            if config.has_section('KeyPair'):
                self.private_key_path.setText(config.get('KeyPair', 'private_key', fallback=''))
                # 密码可选，出于安全考虑不保存
                # self.private_key_password.setText(config.get('KeyPair', 'private_key_password', fallback=''))
                self.public_key_path.setText(config.get('KeyPair', 'public_key', fallback=''))
                
        except Exception as e:
            print(f"加载密钥信息出错: {str(e)}")
    
    def save_key_info(self):
        """保存密钥信息"""
        try:
            # 确保lib目录存在
            lib_dir = os.path.dirname(self.key_config_path)
            if not os.path.exists(lib_dir):
                os.makedirs(lib_dir)
            
            config = configparser.ConfigParser()
            
            # 保存密钥类型
            config['KeyType'] = {
                'type': 'keystore' if self.radio_keystore.isChecked() else 'key_pair'
            }
            
            # 保存密钥库信息
            config['Keystore'] = {
                'path': self.keystore_path.text(),
                'alias': self.keystore_alias.text()
                # 密码不保存出于安全考虑
            }
            
            # 保存公钥私钥信息
            config['KeyPair'] = {
                'private_key': self.private_key_path.text(),
                'public_key': self.public_key_path.text()
                # 密码不保存出于安全考虑
            }
            
            # 写入文件
            with open(self.key_config_path, 'w', encoding='utf-8') as f:
                config.write(f)
                
        except Exception as e:
            print(f"保存密钥信息出错: {str(e)}")
    
    def clear_key_info(self):
        """清空密钥信息"""
        # 清空所有密钥相关字段
        self.keystore_path.clear()
        self.keystore_alias.clear()
        self.keystore_password.clear()
        self.private_key_path.clear()
        self.private_key_password.clear()
        self.public_key_path.clear()
        
        # 重置为默认的密钥库模式
        self.radio_keystore.setChecked(True)
        self.radio_key_pair.setChecked(False)
        self._last_key_type = 'keystore'
        
        # 删除配置文件
        if os.path.exists(self.key_config_path):
            try:
                os.remove(self.key_config_path)
                self.output_console.append("[已清空密钥记录]")
            except Exception as e:
                print(f"删除密钥配置文件出错: {str(e)}")