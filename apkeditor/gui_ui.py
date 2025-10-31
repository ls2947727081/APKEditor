# gui_ui.py
"""APKEditor GUI界面初始化和布局模块"""

from PyQt5.QtWidgets import (
    QWidget, QLabel, QLineEdit, QTextEdit, QPushButton, 
    QHBoxLayout, QVBoxLayout, QGridLayout, QCheckBox, 
    QProgressBar
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

from .constants import OP_MAP


def setup_ui(main_window):
    """设置UI界面
    
    Args:
        main_window: APKEditorUI主窗口实例
    """
    central = QWidget()
    main_window.setCentralWidget(central)
    layout = QVBoxLayout()
    central.setLayout(layout)
    grid = QGridLayout()
    row = 0

    # Jar selector
    main_window.jar_label = QLabel("JAR: 未选择")
    jar_btn = QPushButton("选择 APKEditor jar")
    jar_btn.clicked.connect(main_window.choose_jar)
    grid.addWidget(main_window.jar_label, row, 0, 1, 3)
    grid.addWidget(jar_btn, row, 3)
    row += 1

    # Operation - 改为七个中文按钮
    grid.addWidget(QLabel("操作:"), row, 0)
    ops_layout = QHBoxLayout()
    main_window.op_buttons = {}
    for op_name in OP_MAP.keys():
        btn = QPushButton(op_name)
        btn.clicked.connect(lambda checked, op=op_name: main_window.on_op_button_clicked(op))
        main_window.op_buttons[op_name] = btn
        ops_layout.addWidget(btn)
    grid.addLayout(ops_layout, row, 1, 1, 3)
    row += 1
    # 默认选中第一个操作
    main_window.current_op = list(OP_MAP.keys())[0]

    # Input selector - 添加拖放功能和当前模式显示
    grid.addWidget(QLabel("输入 (文件/目录) [支持拖拽]:"), row, 0)
    input_layout = QHBoxLayout()
    main_window.input_line = QLineEdit()
    main_window._setup_drag_drop(main_window.input_line)
    input_layout.addWidget(main_window.input_line, 2)  # 给予更多宽度
    
    # 当前模式显示标签，替代选择按钮
    main_window.mode_label = QLabel("当前模式: 信息")
    main_window.mode_label.setStyleSheet("background-color: #f0f0f0; padding: 5px; border-radius: 3px;")
    input_layout.addWidget(main_window.mode_label, 1)
    
    grid.addLayout(input_layout, row, 1, 1, 3)
    row += 1

    # 移除输出目录功能，因为不支持指定输出目录
    row += 1

    # Extra flags - 通用选项和签名选项
    # 创建标志并设置布局
    main_window.flag_xml = QCheckBox("XML 反编译 (-t xml)")
    main_window.flag_verbose = QCheckBox("Verbose (-v)")
    main_window.flag_resources = QCheckBox("Resources (-resources)")
    main_window.flag_corex = QCheckBox("使用CoreX Hook (-x)")
    
    # 签名相关标志
    main_window.flag_v1 = QCheckBox("V1 签名 (-v1)")
    main_window.flag_v2 = QCheckBox("V2 签名 (-v2)")
    main_window.flag_v3 = QCheckBox("V3 签名 (-v3)")
    main_window.flag_v4 = QCheckBox("V4 签名 (-v4)")
    
    # 默认勾选V1和V2签名
    main_window.flag_v1.setChecked(True)
    main_window.flag_v2.setChecked(True)
    
    # 创建标志布局
    flags_layout = QHBoxLayout()
    for flag in [main_window.flag_xml, main_window.flag_verbose, main_window.flag_resources,
                 main_window.flag_v1, main_window.flag_v2, main_window.flag_v3, main_window.flag_v4,
                 main_window.flag_corex]:
        flags_layout.addWidget(flag)
    grid.addLayout(flags_layout, row, 0, 1, 4)
    row += 1

    # 签名相关参数 - 添加公钥私钥支持
    # 密钥类型选择
    grid.addWidget(QLabel("密钥类型:"), row, 0)
    main_window.key_type_layout = QHBoxLayout()
    main_window.radio_keystore = QCheckBox("密钥库文件")
    main_window.radio_keystore.setChecked(True)
    main_window.radio_key_pair = QCheckBox("公钥私钥")
    main_window.radio_keystore.stateChanged.connect(main_window.on_key_type_changed)
    main_window.radio_key_pair.stateChanged.connect(main_window.on_key_type_changed)
    main_window.key_type_layout.addWidget(main_window.radio_keystore)
    main_window.key_type_layout.addWidget(main_window.radio_key_pair)
    grid.addLayout(main_window.key_type_layout, row, 1, 1, 3)
    row += 1
    
    # 密钥库文件方式
    # Keystore path - 添加拖拽支持
    grid.addWidget(QLabel("签名密钥文件 (.jks/.keystore):"), row, 0)
    main_window.keystore_path = QLineEdit()
    main_window._setup_drag_drop(main_window.keystore_path)
    main_window.keystore_btn = QPushButton("选择")
    main_window.keystore_btn.clicked.connect(main_window.choose_keystore)
    hbox_keystore = QHBoxLayout()
    hbox_keystore.addWidget(main_window.keystore_path)
    hbox_keystore.addWidget(main_window.keystore_btn)
    grid.addLayout(hbox_keystore, row, 1, 1, 3)
    row += 1
    
    # Keystore alias
    grid.addWidget(QLabel("密钥别名:"), row, 0)
    main_window.keystore_alias = QLineEdit()
    grid.addWidget(main_window.keystore_alias, row, 1)
    
    # Keystore password
    grid.addWidget(QLabel("密钥密码:"), row, 2)
    main_window.keystore_password = QLineEdit()
    main_window.keystore_password.setEchoMode(QLineEdit.Password)
    grid.addWidget(main_window.keystore_password, row, 3)
    row += 1
    
    # 公钥私钥方式
    # Private key path - 添加拖拽支持
    grid.addWidget(QLabel("私钥文件 (PKCS#8格式):"), row, 0)
    main_window.private_key_path = QLineEdit()
    main_window._setup_drag_drop(main_window.private_key_path)
    main_window.private_key_btn = QPushButton("选择")
    main_window.private_key_btn.clicked.connect(main_window.choose_private_key)
    hbox_private_key = QHBoxLayout()
    hbox_private_key.addWidget(main_window.private_key_path)
    hbox_private_key.addWidget(main_window.private_key_btn)
    grid.addLayout(hbox_private_key, row, 1, 1, 3)
    row += 1
    
    # Private key password
    grid.addWidget(QLabel("私钥密码 (可选):"), row, 0)
    main_window.private_key_password = QLineEdit()
    main_window.private_key_password.setEchoMode(QLineEdit.Password)
    grid.addWidget(main_window.private_key_password, row, 1, 1, 3)
    row += 1
    
    # Public key path - 添加拖拽支持
    grid.addWidget(QLabel("公钥文件 (X.509格式):"), row, 0)
    main_window.public_key_path = QLineEdit()
    main_window._setup_drag_drop(main_window.public_key_path)
    main_window.public_key_btn = QPushButton("选择")
    main_window.public_key_btn.clicked.connect(main_window.choose_public_key)
    hbox_public_key = QHBoxLayout()
    hbox_public_key.addWidget(main_window.public_key_path)
    hbox_public_key.addWidget(main_window.public_key_btn)
    grid.addLayout(hbox_public_key, row, 1, 1, 3)
    row += 1
    
    # Custom extra args
    grid.addWidget(QLabel("额外自定义参数 (例如: -i my.apk -o outdir):"), row, 0)
    main_window.custom_args = QLineEdit()
    grid.addWidget(main_window.custom_args, row, 1, 1, 3)
    row += 1

    # Command preview
    grid.addWidget(QLabel("命令预览:"), row, 0)
    main_window.cmd_preview = QLineEdit()
    main_window.cmd_preview.setReadOnly(True)
    grid.addWidget(main_window.cmd_preview, row, 1, 1, 3)
    row += 1

    # Run / Stop buttons
    main_window.run_btn = QPushButton("运行")
    main_window.run_btn.clicked.connect(main_window.on_run)
    main_window.stop_btn = QPushButton("停止")
    main_window.stop_btn.clicked.connect(main_window.on_stop)
    main_window.stop_btn.setEnabled(False)
    btn_layout = QHBoxLayout()
    btn_layout.addWidget(main_window.run_btn)
    btn_layout.addWidget(main_window.stop_btn)
    grid.addLayout(btn_layout, row, 0, 1, 4)
    row += 1

    # Progress bar
    main_window.progress = QProgressBar()
    main_window.progress.setRange(0, 0)  # indeterminate by default
    main_window.progress.setVisible(False)
    grid.addWidget(main_window.progress, row, 0, 1, 4)
    row += 1

    layout.addLayout(grid)

    # Output console - 增强中文支持
    layout.addWidget(QLabel("输出控制台:"))
    main_window.output_console = QTextEdit()
    main_window.output_console.setReadOnly(True)
    main_window.output_console.setLineWrapMode(QTextEdit.NoWrap)
    
    # 设置支持中文的字体
    font = QFont()
    font.setFamily("SimHei, WenQuanYi Micro Hei, Heiti TC, Microsoft YaHei")
    font.setStyleStrategy(QFont.PreferAntialias)
    main_window.output_console.setFont(font)
    
    # 设置语法高亮
    from .syntax_highlighter import ConsoleHighlighter
    main_window.highlighter = ConsoleHighlighter(main_window.output_console.document())
    
    # 添加右键菜单
    main_window._setup_context_menu()
    
    layout.addWidget(main_window.output_console, 2)

    # Bottom tips
    tips = QLabel("提示: 该工具只是封装 jar，所有参数将传给 java -jar APKEditor.jar。")
    tips.setStyleSheet("color: gray;")
    layout.addWidget(tips)

    # Update preview when inputs change - 使用列表遍历简化信号连接
    widgets = [
        main_window.input_line, main_window.flag_xml, main_window.flag_verbose, main_window.flag_resources,
        main_window.flag_v1, main_window.flag_v2, main_window.flag_v3, main_window.flag_v4,
        main_window.flag_corex,
        main_window.keystore_path, main_window.keystore_alias, main_window.keystore_password,
        main_window.private_key_path, main_window.private_key_password, main_window.public_key_path,
        main_window.custom_args
    ]
    for widget in widgets:
        if isinstance(widget, QLineEdit):
            widget.textChanged.connect(main_window.update_preview)
        elif isinstance(widget, QCheckBox):
            widget.stateChanged.connect(main_window.update_preview)
    main_window.radio_keystore.stateChanged.connect(main_window.update_preview)
    main_window.radio_key_pair.stateChanged.connect(main_window.update_preview)