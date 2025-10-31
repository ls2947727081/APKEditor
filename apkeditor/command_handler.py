# command_handler.py
"""命令构建和处理模块"""

import os
import shlex
import glob
from .constants import OP_MAP, DEFAULT_JAR


class CommandHandler:
    """处理命令构建和验证"""
    
    @staticmethod
    def _find_apksigner_jar():
        """查找apksigner.jar文件"""
        # 优先在lib目录下查找以apksigner开头的jar文件
        apksigner_files = glob.glob(os.path.join(".", "lib", "apksigner*.jar"))
        if apksigner_files:
            return apksigner_files[0]
        
        # 回退到原路径
        fallback_path = os.path.join(".", "lib", "build-tools", "36.0.0", "lib", "apksigner.jar")
        return fallback_path if os.path.exists(fallback_path) else None
    
    @staticmethod
    def build_command(current_op, flag_xml, flag_verbose, flag_resources, 
                     flag_v1, flag_v2, flag_v3, flag_v4,
                     radio_keystore, radio_key_pair,
                     keystore_path, keystore_alias, keystore_password,
                     private_key_path, private_key_password, public_key_path,
                     input_line, custom_args, jar_path=None):
        """构建命令预览字符串"""
        op_key = OP_MAP.get(current_op, "d")
        op_text = current_op
        
        # Pairip处理操作特殊处理
        if op_text.startswith("Pairip"):
            inp = input_line.text().strip()
            cmd_preview = f"[内部集成] Pairip处理: {shlex.quote(os.path.abspath(inp))}" if inp else "[内部集成] Pairip处理: <输入.apks文件>"
            
            # 检查CoreX Hook状态
            try:
                if hasattr(flag_xml, 'parentWidget') and flag_xml.parentWidget() and hasattr(flag_xml.parentWidget(), 'flag_corex'):
                    if flag_xml.parentWidget().flag_corex.isChecked():
                        cmd_preview += " [启用CoreX Hook]"
            except Exception as e:
                print(f"检查CoreX Hook状态时出错: {str(e)}")
            
            return cmd_preview
        
        # 签名操作特殊处理
        if op_text.startswith("签名"):
            apksigner_jar = CommandHandler._find_apksigner_jar()
            if not apksigner_jar:
                return f"[错误] 找不到 apksigner.jar: 请确保 lib 目录下存在以 apksigner 开头的 jar 文件"
            
            # 构建命令
            cmd_parts = ["java", "-jar", shlex.quote(apksigner_jar), "sign"]
            
            # 添加签名版本参数
            for version, flag in [(1, flag_v1), (2, flag_v2), (3, flag_v3), (4, flag_v4)]:
                cmd_parts.extend([f"--v{version}-signing-enabled", "true" if flag.isChecked() else "false"])
            
            # 密钥信息映射
            if radio_keystore.isChecked():
                # 密钥库方式
                if keystore_path.text().strip():
                    cmd_parts.extend(["--ks", shlex.quote(keystore_path.text().strip())])
                if keystore_alias.text().strip():
                    cmd_parts.extend(["--ks-key-alias", keystore_alias.text().strip()])
                if keystore_password.text().strip():
                    password = keystore_password.text().strip()
                    cmd_parts.extend(["--ks-pass", f"pass:{password}", "--key-pass", f"pass:{password}"])
            else:
                # 公钥私钥方式
                if private_key_path.text().strip():
                    cmd_parts.extend(["--key", shlex.quote(private_key_path.text().strip())])
                if private_key_password.text().strip():
                    cmd_parts.extend(["--key-pass", f"pass:{private_key_password.text().strip()}"])
                if public_key_path.text().strip():
                    cmd_parts.extend(["--cert", shlex.quote(public_key_path.text().strip())])
            
            # 添加输入APK文件
            if input_line.text().strip():
                cmd_parts.append(shlex.quote(input_line.text().strip()))
            
            # 添加verbose输出标志
            if flag_verbose.isChecked():
                cmd_parts.append("--verbose")
        else:
            # 非签名操作 - 使用原始的 APKEditor.jar
            jar = jar_path or DEFAULT_JAR
            cmd_parts = [f"java -jar {shlex.quote(jar)}"]
            
            # 添加操作子命令
            try:
                # 确保op_key是字符串类型
                op_key_str = str(op_key)
                cmd_parts.append("info" if op_key_str == "info" else op_key_str)
            except Exception as e:
                print(f"添加操作子命令时出错: {str(e)}")
                cmd_parts.append("d")  # 默认使用d操作
            
            # 添加输入参数
            if input_line.text().strip():
                cmd_parts.extend(["-i", shlex.quote(input_line.text().strip())])
            
            # 添加标志
            if flag_xml.isChecked():
                cmd_parts.extend(["-t", "xml"])
            if flag_resources.isChecked():
                cmd_parts.append("-resources")
            if flag_verbose.isChecked():
                cmd_parts.append("-v")

        # 添加自定义参数
        if custom_args.text().strip():
            cmd_parts.append(custom_args.text().strip())

        # 合并为单个命令字符串
        return " ".join(cmd_parts)
    
    @staticmethod
    def validate_before_run(current_op, jar_path, input_line,
                          radio_keystore, radio_key_pair,
                          keystore_path, keystore_alias, keystore_password,
                          private_key_path, public_key_path,
                          flag_v1, flag_v2, flag_v3, flag_v4):
        """运行前验证参数"""
        # 验证APKEditor jar
        jar = jar_path or DEFAULT_JAR
        if not jar or not os.path.exists(jar):
            return False, f"找不到 APKEditor jar: {jar}\n请点击上方按钮选择正确的 jar 文件。"
        
        # 验证输入
        inp = input_line.text().strip()
        if not inp:
            return False, "请输入或选择输入文件/目录（-i）。"
        if not os.path.exists(inp):
            return False, f"指定的输入路径不存在: {inp}"
        
        # 签名操作的额外验证
        if current_op.startswith("签名"):
            # 检查 apksigner.jar
            if not CommandHandler._find_apksigner_jar():
                return False, "找不到 apksigner.jar: 请确保 lib 目录下存在以 apksigner 开头的 jar 文件"
            
            # 根据密钥类型进行不同的验证
            if radio_keystore.isChecked():
                # 密钥库验证
                if not keystore_path.text().strip():
                    return False, "请选择签名密钥文件。"
                if not os.path.exists(keystore_path.text().strip()):
                    return False, f"指定的签名密钥文件不存在: {keystore_path.text().strip()}"
                if not keystore_alias.text().strip():
                    return False, "请输入密钥别名。"
                if not keystore_password.text().strip():
                    return False, "请输入密钥密码。"
            else:
                # 公钥私钥验证
                if not private_key_path.text().strip():
                    return False, "请选择私钥文件。"
                if not os.path.exists(private_key_path.text().strip()):
                    return False, f"指定的私钥文件不存在: {private_key_path.text().strip()}"
                if not public_key_path.text().strip():
                    return False, "请选择公钥文件。"
                if not os.path.exists(public_key_path.text().strip()):
                    return False, f"指定的公钥文件不存在: {public_key_path.text().strip()}"
            
            # 验证至少选择一个签名版本
            if not any(flag.isChecked() for flag in [flag_v1, flag_v2, flag_v3, flag_v4]):
                return False, "请至少选择一个签名版本（V1-V4）。"
        
        return True, ""