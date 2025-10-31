# gui_events.py
"""APKEditor GUI事件处理模块"""

import os
import shlex
from PyQt5.QtWidgets import QMessageBox, QApplication
from PyQt5.QtCore import QProcess

from .command_handler import CommandHandler
from .constants import OP_MAP


def on_run(main_window):
    """运行命令处理函数
    
    Args:
        main_window: APKEditorUI主窗口实例
    """
    # 验证JAR文件
    if not hasattr(main_window, 'jar_path') or not main_window.jar_path:
        QMessageBox.warning(main_window, "错误", "请选择APKEditor JAR文件")
        return
    
    # 验证输入
    if not main_window.input_line.text().strip():
        QMessageBox.warning(main_window, "错误", "请选择输入文件/目录")
        return
    
    # 重置控制台
    main_window.output_console.clear()
    
    # 验证操作
    op_key = OP_MAP.get(main_window.current_op)
    if not op_key:
        QMessageBox.warning(main_window, "错误", f"未知操作: {main_window.current_op}")
        return
    
    # 检查是否需要Pairip处理
    if PairipHandler and main_window.current_op and 'Pairip' in main_window.current_op:
        # Pairip处理逻辑 - 仅当选择的操作是'pairip'时才执行
        try:
            # 创建PairipHandler实例，添加base_dir参数
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            main_window.pairip_handler = PairipHandler(base_dir)
            # 连接信号
            main_window.pairip_handler.progress_updated.connect(main_window.on_pairip_progress)
            main_window.pairip_handler.process_finished.connect(main_window.on_pairip_finished)
            
            # 启动处理
            main_window.run_btn.setEnabled(False)
            main_window.stop_btn.setEnabled(True)
            
            # 使用内部类在单独的线程中运行处理
            from PyQt5.QtCore import QThread
            
            class PairipThread(QThread):
                def __init__(self, handler, input_path, output_path=None):
                    super().__init__()
                    self.handler = handler
                    self.input_path = input_path
                    self.output_path = output_path
                
                def run(self):
                    # 获取主窗口引用并传递参数
                    # 假设主窗口有flag_corex和flag_verbose属性
                    main_window = QApplication.activeWindow()
                    use_corex = hasattr(main_window, 'flag_corex') and main_window.flag_corex.isChecked()
                    verbose = hasattr(main_window, 'flag_verbose') and main_window.flag_verbose.isChecked()
                    
                    # 使用process_apk方法并传递所有必要参数
                    self.handler.process_apk(self.input_path, use_corex_hook=use_corex, verbose=verbose)
            
            # 创建并启动线程
            input_path = main_window.input_line.text().strip()
            main_window.pairip_thread = PairipThread(main_window.pairip_handler, input_path)
            main_window.pairip_thread.start()
            
        except Exception as e:
            QMessageBox.critical(main_window, "错误", f"启动Pairip处理失败: {str(e)}")
            main_window._reset_ui_state()
        return
        
    # 对于非pairip操作，忽略corex标志，正常执行常规命令
    
    # 常规命令执行逻辑
    main_window.run_btn.setEnabled(False)
    main_window.stop_btn.setEnabled(True)
    main_window.progress.setVisible(True)
    
    # 构建命令参数
    args = []
    
    # 处理签名操作
    is_sign_operation = False
    if op_key == 'sign':
        is_sign_operation = True
        # 查找apksigner.jar
        apksigner_jar = _find_apksigner_jar()
        if not apksigner_jar:
            QMessageBox.critical(main_window, "错误", "找不到apksigner.jar文件")
            main_window._reset_ui_state()
            return
        
        # 构建apksigner命令
        args = ['java', '-jar', apksigner_jar, 'sign']
        
        # 添加签名版本标志
        if main_window.flag_v1.isChecked():
            args.append('--v1-signing-enabled')
        if main_window.flag_v2.isChecked():
            args.append('--v2-signing-enabled')
        if main_window.flag_v3.isChecked():
            args.append('--v3-signing-enabled')
        if main_window.flag_v4.isChecked():
            args.append('--v4-signing-enabled')
        
        # 添加密钥信息
        if main_window.radio_keystore.isChecked():
            # 使用密钥库
            if keystore := main_window.keystore_path.text().strip():
                args.extend(['--ks', keystore])
                if alias := main_window.keystore_alias.text().strip():
                    args.extend(['--ks-key-alias', alias])
                if password := main_window.keystore_password.text().strip():
                    args.extend(['--ks-pass', f'pass:{password}'])
        else:
            # 使用公钥私钥
            if private_key := main_window.private_key_path.text().strip():
                args.extend(['--key', private_key])
            if private_key_pass := main_window.private_key_password.text().strip():
                args.extend(['--key-pass', f'pass:{private_key_pass}'])
            if public_key := main_window.public_key_path.text().strip():
                args.extend(['--cert', public_key])
        
        # 添加输入APK文件
        if inp := main_window.input_line.text().strip():
            args.append(inp)
    else:
        # 构建APKEditor命令参数
        jar = os.path.abspath(main_window.jar_path)
        args = ['-jar', jar, 'info' if op_key == 'info' else op_key]
        
        # 添加输入参数
        if inp := main_window.input_line.text().strip():
            args.extend(['-i', inp])
        
        # 添加通用标志
        if main_window.flag_xml.isChecked():
            args.extend(['-t', 'xml'])
        if main_window.flag_resources.isChecked():
            args.append('-resources')
    
    # 添加Verbose标志（适用于所有操作）
    if main_window.flag_verbose.isChecked():
        args.append('-v')

    # 处理自定义参数
    custom = main_window.custom_args.text().strip()
    if custom:
        try:
            args.extend(shlex.split(custom))
        except Exception as e:
            QMessageBox.warning(main_window, "自定义参数解析失败", f"无法解析自定义参数: {e}\n将原样追加。")
            args.append(custom)

    # 设置进程通道模式并启动进程
    main_window.process.setProcessChannelMode(QProcess.MergedChannels)
        
    # 输出命令并启动进程
    java_exec = "java"
    if is_sign_operation:
        command_text = f"> {' '.join(shlex.quote(str(a)) for a in args)}\n"
        main_window.process.start(args[0], args[1:])
    else:
        command_text = f"> {java_exec} {' '.join(shlex.quote(a) for a in args)}\n"
        main_window.process.start(java_exec, args)
    
    main_window.output_console.append(command_text)
    
    # 检查进程是否成功启动
    if not main_window.process.waitForStarted(3000):
        main_window.output_console.append("[错误] 无法启动 java 进程，请确保已安装 Java 并加入 PATH。")
        main_window._reset_ui_state()


def _find_apksigner_jar():
    """查找apksigner.jar文件
    
    Returns:
        str: apksigner.jar文件路径，如果未找到则返回None
    """
    import glob
    
    # 优先在lib目录下查找
    lib_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'lib')
    if os.path.exists(lib_dir):
        # 查找lib目录下所有apksigner开头的jar文件
        matches = glob.glob(os.path.join(lib_dir, 'apksigner*.jar'))
        if matches:
            return matches[0]
        
        # 查找子目录中的apksigner.jar
        matches = glob.glob(os.path.join(lib_dir, '**', 'apksigner.jar'), recursive=True)
        if matches:
            return matches[0]
    
    # 默认路径
    default_path = os.path.join(lib_dir, 'build-tools', '36.0.0', 'lib', 'apksigner.jar')
    if os.path.exists(default_path):
        return default_path
    
    return None

# 尝试导入PairipHandler
try:
    from .pairip_handler import PairipHandler
except ImportError:
    PairipHandler = None