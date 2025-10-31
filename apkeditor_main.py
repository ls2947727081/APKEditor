# apkeditor_main.py
"""APKEditor GUI主入口文件"""

import sys
import os
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'apkeditor.log'),
    filemode='a'
)
logger = logging.getLogger(__name__)

# 添加当前目录到Python路径，确保可以导入apkeditor包
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def main():
    """主函数"""
    try:
        # 尝试导入PyQt5
        from PyQt5.QtWidgets import QApplication
        from PyQt5.QtCore import Qt
        
        # 设置应用程序信息
        app = QApplication(sys.argv)
        app.setApplicationName("APKEditor")
        app.setApplicationVersion("1.4.5")
        
        # 设置应用程序样式
        try:
            # 尝试使用Windows原生样式（如果在Windows上）
            if sys.platform == 'win32':
                app.setStyle('WindowsVista')
            else:
                # 在其他平台上尝试使用可用的样式
                available_styles = QApplication.style().keys()
                preferred_styles = ['Fusion', 'Windows', 'Plastique', 'Cleanlooks']
                for style in preferred_styles:
                    if style in available_styles:
                        app.setStyle(style)
                        break
        except Exception as e:
            logger.warning(f"设置样式失败: {str(e)}")
        
        # 尝试导入并初始化主窗口
        try:
            from apkeditor.gui import APKEditorGUI
            window = APKEditorGUI()
            window.show()
            
            # 记录启动成功
            logger.info("APKEditor GUI启动成功")
            
            # 运行应用程序
            sys.exit(app.exec_())
            
        except ImportError as e:
            error_msg = f"导入APKEditor模块失败: {str(e)}"
            logger.error(error_msg)
            raise ImportError(error_msg)
        
    except Exception as e:
        logger.error(f"应用程序启动失败: {str(e)}", exc_info=True)
        print(f"应用程序启动失败: {str(e)}")
        
        # 尝试显示错误对话框
        try:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(
                None, 
                "启动失败", 
                f"应用程序启动失败:\n{str(e)}\n\n请检查日志文件获取详细信息。"
            )
        except:
            print("无法显示错误对话框")
            import traceback
            traceback.print_exc()
        
        sys.exit(1)

if __name__ == "__main__":
    main()


# 为了保持向后兼容性，可以创建一个简单的APKEditor-GUI.pyw文件，它只是导入并运行主函数
# 这样用户可以继续使用原来的文件名启动程序