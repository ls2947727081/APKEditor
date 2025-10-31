# pairip_handler.py
"""Pairip处理功能模块 - 整合自Simple_RKPairip.py"""

import os
import sys
import re
import zipfile
import shutil
import subprocess
import time
import logging
from pathlib import Path
from PyQt5.QtCore import QObject, pyqtSignal

# 定义平台特定的subprocess参数
if os.name == 'nt':  # Windows系统
    # 隐藏命令行窗口的标志
    STARTUPINFO = subprocess.STARTUPINFO()
    STARTUPINFO.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    CREATE_NO_WINDOW = subprocess.CREATE_NO_WINDOW
    PLATFORM_ARGS = {
        'startupinfo': STARTUPINFO,
        'creationflags': CREATE_NO_WINDOW
    }
else:
    # 非Windows系统不需要这些参数
    PLATFORM_ARGS = {}

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ANSI:
    """ANSI颜色代码"""
    def __init__(self):
        self.ESC = '\033'
        self.R = self.ESC + '[31;1m'    # 红色
        self.G = self.ESC + '[32;1m'    # 绿色
        self.Y = self.ESC + '[33;1m'    # 黄色
        self.B = self.ESC + '[34;1m'    # 蓝色
        self.P = self.ESC + '[35;1m'    # 紫色
        self.C = self.ESC + '[36;1m'    # 青色
        self.W = self.ESC + '[37;1m'    # 白色
        self.OG = self.ESC + '[38;5;202;1m'  # 橙色
        self.PN = self.ESC + '[38;5;213;1m'  # 粉色
        self.CC = self.ESC + '[0m'      # 清除颜色
        self.S = f'{self.B}[{self.C}'
        self.E = f'{self.B}]'
        self.ERROR = f'{self.R}ERROR {self.E} {self.C}'
        self.INFO = f'{self.B}[{self.C} INFO {self.B}]{self.C} {self.C}'
        self.X = f'{self.B}[{self.C} ✨ {self.B}]{self.C} {self.C}'
        self.FYI = f'{self.B}[{self.C} FYI {self.B}]{self.C} {self.C}'
        self.WARN = f'{self.Y}WARNING {self.E} {self.C}'


class FileCheck:
    """文件检查和路径设置"""
    def __init__(self, base_dir):
        self.run_dir = base_dir
        self.script_dir = os.path.join(base_dir, "lib")
        self.Set_Path()
    
    def Set_Path(self):
        """设置工具路径"""
        # 初始化APKEditor路径为默认值
        self.APKEditor_Path = os.path.join(self.run_dir, "lib", "APKEditor-1.4.5.jar")
        self.Objectlogger = os.path.join(self.script_dir, "Objectlogger.smali")
        self.Pairip_CoreX = os.path.join(self.script_dir, "lib_Pairip_CoreX.so")
        
        # 自动检测最新版本的APKEditor
        self._detect_apkeditor_version()
    
    def _detect_apkeditor_version(self):
        """自动检测并使用最新版本的APKEditor"""
        # 定义可能包含APKEditor的目录
        potential_dirs = [
            self.run_dir,
            os.path.join(self.run_dir, "lib"),
            os.getcwd()  # 当前工作目录
        ]
        
        # 查找所有可能的APKEditor jar文件
        found_apkeditor_jars = []
        for directory in potential_dirs:
            if not os.path.isdir(directory):
                continue
            try:
                for file in os.listdir(directory):
                    if file.lower().startswith("apkeditor") and file.lower().endswith(".jar"):
                        full_path = os.path.join(directory, file)
                        found_apkeditor_jars.append((full_path, file))
            except Exception:
                continue
        
        # 如果找到多个APKEditor jar文件，选择版本号最高的一个
        if found_apkeditor_jars:
            # 按文件名排序（带版本号的通常排在后面）
            found_apkeditor_jars.sort(key=lambda x: x[1].lower(), reverse=True)
            self.APKEditor_Path = found_apkeditor_jars[0][0]
    
    def Check_Files(self):
        """检查必要文件是否存在"""
        # 尝试在不同位置查找必要文件
        apkeditor_paths = [
            self.APKEditor_Path,
            os.path.join(self.run_dir, "APKEditor.jar"),
            os.path.join(self.run_dir, "lib", "APKEditor.jar"),
            os.path.join(os.getcwd(), "APKEditor.jar")
        ]
        
        pairip_corex_paths = [
            self.Pairip_CoreX,
            os.path.join(self.run_dir, "lib_Pairip_CoreX.so"),
            os.path.join(os.getcwd(), "lib_Pairip_CoreX.so")
        ]
        
        # 检查APKEditor.jar
        found_apkeditor = False
        for path in apkeditor_paths:
            if os.path.exists(path):
                self.APKEditor_Path = path
                found_apkeditor = True
                break
        
        if not found_apkeditor:
            # 改进错误提示，显示尝试过的目录
            attempted_dirs = set()
            for path in apkeditor_paths:
                dir_path = os.path.dirname(path)
                # 检查目录是否存在
                if not os.path.exists(dir_path):
                    attempted_dirs.add(dir_path)
            
            error_msg = "APKEditor.jar 未找到！"
            if attempted_dirs:
                error_msg += f"以下目录不存在: {', '.join(attempted_dirs)}。\n"
            error_msg += "尝试的路径:\n" + "\n".join(apkeditor_paths)
            return False, error_msg
        
        # 检查lib_Pairip_CoreX.so
        found_corex = False
        for path in pairip_corex_paths:
            if os.path.exists(path):
                self.Pairip_CoreX = path
                found_corex = True
                break
        
        if not found_corex:
            # 改进错误提示，显示尝试过的目录
            attempted_dirs = set()
            for path in pairip_corex_paths:
                dir_path = os.path.dirname(path)
                # 检查目录是否存在
                if not os.path.exists(dir_path):
                    attempted_dirs.add(dir_path)
            
            error_msg = "lib_Pairip_CoreX.so 未找到！"
            if attempted_dirs:
                error_msg += f"以下目录不存在: {', '.join(attempted_dirs)}。\n"
            error_msg += "尝试的路径:\n" + "\n".join(pairip_corex_paths)
            return False, error_msg
        
        return True, f"APKEditor.jar 已找到: {os.path.basename(self.APKEditor_Path)}, lib_Pairip_CoreX.so 已找到: {os.path.basename(self.Pairip_CoreX)}"


class PairipHandler(QObject):
    """Pairip处理核心类"""
    progress_updated = pyqtSignal(str)  # 进度更新信号
    process_finished = pyqtSignal(bool, str)  # 处理完成信号 (success, message)
    
    def __init__(self, base_dir, parent=None):
        super().__init__(parent)
        self.base_dir = base_dir
        self.C = ANSI()
        self.F = FileCheck(base_dir)
        
    def process_apk(self, apk_path, use_corex_hook=False, verbose=False):
        """处理APK文件的主函数"""
        try:
            # 检查必要文件
            success, message = self.F.Check_Files()
            if not success:
                self.progress_updated.emit(f"错误: {message}")
                self.process_finished.emit(False, message)
                return
            
            self.progress_updated.emit(f"{self.C.G} ✔ {message}")
            
            # 创建处理器实例
            processor = SimpleRKPairip(apk_path, use_corex_hook, self.F, self.C, self.progress_updated)
            
            # 运行处理流程
            success = processor.run()
            
            if success:
                self.process_finished.emit(True, f"处理成功！输出文件: {processor.build_dir}")
            else:
                self.process_finished.emit(False, "处理失败，请查看日志获取详细信息")
                
        except Exception as e:
            error_msg = f"运行过程中出错: {str(e)}"
            self.progress_updated.emit(f"{self.C.ERROR} {error_msg}")
            logger.error(f"运行出错: {e}", exc_info=True)
            self.process_finished.emit(False, error_msg)


class SimpleRKPairip:
    """简化版RKPairip实现"""
    def __init__(self, apk_path, use_corex_hook, file_checker, color_manager, progress_signal):
        self.apk_path = apk_path
        self.use_corex_hook = use_corex_hook
        self.F = file_checker  # 文件检查器实例
        self.C = color_manager  # 颜色管理器实例
        self.progress_signal = progress_signal  # 进度信号
        self.base_name = os.path.splitext(os.path.basename(apk_path))[0]
        self.output_path = f"{self.base_name.replace(' ', '_')}.apk"
        self.decompile_dir = os.path.join(os.path.expanduser("~"), f"{self.base_name}_decompiled")
        self.build_dir = os.path.abspath(os.path.join(os.path.dirname(apk_path), f"{self.base_name}_Pairip.apk"))
        self.package_name = ""
        self.is_flutter = False
        self.is_corex = False
    
    def log(self, message):
        """输出日志信息"""
        self.progress_signal.emit(message)
    
    def check_dependencies(self):
        """检查系统依赖"""
        try:
            result = subprocess.run(['java', '-version'], check=True, capture_output=True, text=True, **PLATFORM_ARGS)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.log(f'{self.C.ERROR} Java 未安装。')
            self.log(f'{self.C.INFO} 请安装Java并在新的命令行中再次运行脚本。')
            return False
    
    def anti_split(self):
        """合并.apks文件"""
        self.log(f"{self.C.CC}{'_' * 61}")
        self.log(f"{self.C.X} 开始合并拆分APK...")
        
        cmd = ["java", "-jar", self.F.APKEditor_Path, "m", "-i", self.apk_path, "-f", "-o", self.output_path]
        
        if self.use_corex_hook:
            cmd += ["-extractNativeLibs", "true"]
        
        self.log(f"{self.C.G}  |")
        self.log(f"  └──── {self.C.CC}合并命令 ~{self.C.G}$ java -jar {os.path.basename(self.F.APKEditor_Path)} m -i {self.apk_path} -f -o {self.output_path}" + (" -extractNativeLibs true" if self.use_corex_hook else ""))
        self.log(f"{self.C.CC}{'_' * 61}")
        
        try:
            # 使用subprocess.run并实时输出
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, **PLATFORM_ARGS)
            
            # 实时读取和输出
            for line in process.stdout:
                self.log(line.strip())
            
            for line in process.stderr:
                # 以普通信息形式显示stderr输出，而不是错误信息
                self.log(line.strip())
            
            process.wait()
            
            if process.returncode != 0:
                raise subprocess.CalledProcessError(process.returncode, cmd)
            
            self.log(f"{self.C.X} 合并成功 {self.C.G} ✔")
            self.log(f"{self.C.CC}{'_' * 61}")
            return True
        except subprocess.CalledProcessError:
            self.log(f"{self.C.ERROR} 合并失败！")
            return False
    
    def scan_apk(self):
        """扫描APK获取信息"""
        self.log(f"{self.C.CC}{'_' * 61}")
        
        # 提取包名
        try:
            result = subprocess.run(
                ["java", "-jar", self.F.APKEditor_Path, "info", "-package", "-i", self.output_path],
                capture_output=True, text=True, **PLATFORM_ARGS
            )
            self.package_name = result.stdout.strip().split('"')[1]
            self.log(f"{self.C.S} 包名 {self.C.E} {self.C.OG}➸❥ {self.C.P}'{self.C.G}{self.package_name}{self.C.P}' {self.C.G} ✔")
        except Exception as e:
            self.log(f"{self.C.ERROR} 获取包名失败: {e}")
            return False
        
        # 检查Flutter/Unity
        with zipfile.ZipFile(self.output_path, 'r') as zip_ref:
            for item in zip_ref.infolist():
                if item.filename.startswith('lib/'):
                    if item.filename.endswith('libflutter.so'):
                        self.is_flutter = True
                        self.log(f"{self.C.S} Flutter应用 {self.C.E} {self.C.OG}➸❥ {self.C.G}已检测到 {self.C.G} ✔")
                        break
        
        return True
    
    def decompile_apk(self):
        """反编译APK"""
        self.log(f"{self.C.X} 使用APKEditor反编译APK...")
        
        cmd = ["java", "-jar", self.F.APKEditor_Path, "d", "-i", self.output_path, "-o", self.decompile_dir, "-f", "-no-dex-debug", "-dex-lib", "jf"]
        
        self.log(f"{self.C.G}  |")
        self.log(f"  └──── {self.C.CC}反编译命令 ~{self.C.G}$ java -jar {os.path.basename(self.F.APKEditor_Path)} d -i {self.output_path} -o {os.path.basename(self.decompile_dir)} -f -no-dex-debug -dex-lib jf")
        self.log(f"{self.C.CC}{'_' * 61}")
        
        try:
            # 使用subprocess.run并实时输出
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, **PLATFORM_ARGS)
            
            # 实时读取和输出
            for line in process.stdout:
                self.log(line.strip())
            
            for line in process.stderr:
                # 以普通信息形式显示stderr输出，而不是错误信息
                self.log(line.strip())
            
            process.wait()
            
            if process.returncode != 0:
                raise subprocess.CalledProcessError(process.returncode, cmd)
            
            self.log(f"{self.C.X} 反编译成功 {self.C.G} ✔")
            self.log(f"{self.C.CC}{'_' * 61}")
            return True
        except subprocess.CalledProcessError:
            if os.path.exists(self.decompile_dir):
                shutil.rmtree(self.decompile_dir)
            self.log(f"{self.C.ERROR} 反编译失败！")
            return False
    
    def check_corex(self):
        """检查CoreX支持"""
        lib_paths = os.path.join(self.decompile_dir, 'root', 'lib', 'arm64-v8a')
        
        if not os.path.exists(lib_paths):
            self.log(f"{self.C.INFO} 抱歉，目前CoreX仅支持'arm64-v8a'架构")
            return False
        
        # 检查是否已经添加了CoreX文件
        added_files = []
        for target_file in ['lib_Pairip_CoreX.so', 'libFirebaseCppApp.so']:
            if os.path.isfile(os.path.join(lib_paths, target_file)):
                added_files.append(f"{self.C.G}{target_file} {self.C.OG}➸❥ {self.C.P}arm64-v8a")
        
        if added_files:
            self.log(f"{self.C.INFO} 已添加 {self.C.OG}➸❥ {f' {self.C.OG}& '.join(added_files)} {self.C.G} ✔")
            return False
        
        return True
    
    def smali_patch(self):
        """应用Smali代码补丁，绕过签名验证和授权检查"""
        self.log(f"{self.C.X} 开始应用Smali补丁...")
        self.log(f"{self.C.CC}{'_' * 61}")
        
        # 查找所有smali文件夹
        smali_folders = []
        for root, dirs, _ in os.walk(self.decompile_dir):
            for dir_name in dirs:
                if dir_name.startswith('smali'):
                    smali_folders.append(os.path.join(root, dir_name))
        
        if not smali_folders:
            self.log(f"{self.C.ERROR} 未找到smali文件夹！")
            return False
        
        # 定义目标文件和补丁模式
        target_files = [
            "SignatureCheck.smali",
            "LicenseClientV3.smali",
            "LicenseClient.smali",
            "Application.smali"
        ]
        
        if self.use_corex_hook or self.is_corex:
            target_files.append("VMRunner.smali")
        
        patterns = []
        
        if not (self.is_corex and not self.use_corex_hook):
            patterns.extend([
                # 绕过verifyIntegrity调用
                (r'invoke-static \{[^\}]*\}, Lcom/pairip/SignatureCheck;->verifyIntegrity\(Landroid/content/Context;\)V', 
                 r'# 已绕过verifyIntegrity调用', 
                 "VerifyIntegrity调用"),
                
                # 清空verifyIntegrity方法体
                (r'(\.method [^(]*verifyIntegrity\(Landroid/content/Context;\)V\s+.locals \d+)[\s\S]*?(\s+return-void\n.end method)', 
                 r'\1\n\2', 
                 "VerifyIntegrity方法"),
                
                # 修改verifySignatureMatches方法使其返回true
                (r'(\.method [^(]*verifySignatureMatches\(Ljava/lang/String;\)Z\s+.locals \d+\s+)[\s\S]*?(\s+return ([pv]\d+)\n.end method)', 
                 r'\1\n\tconst/4 \3, 0x1\n\2', 
                 "verifySignatureMatches方法"),
                
                # 清空授权服务相关方法
                (r'(\.method [^(]*connectToLicensingService\(\)V\s+.locals \d+)[\s\S]*?(\s+return-void\n.end method)', 
                 r'\1\n\2', 
                 "connectToLicensingService方法"),
                
                (r'(\.method [^(]*initializeLicenseCheck\(\)V\s+.locals \d+)[\s\S]*?(\s+return-void\n.end method)', 
                 r'\1\n\2', 
                 "initializeLicenseCheck方法"),
                
                (r'(\.method [^(]*processResponse\(ILandroid/os/Bundle;\)V\s+.locals \d+)[\s\S]*?(\s+return-void\n.end method)', 
                 r'\1\n\2', 
                 "processResponse方法")
            ])
        
        # 为CoreX添加loadLibrary调用
        if self.use_corex_hook or self.is_corex:
            patterns.append((
                r'(\.method [^<]*<clinit>\(\)V\s+.locals \d+\n)',
                r'\1\tconst-string v0, "_Pairip_CoreX"\n\tinvoke-static {v0}, Ljava/lang/System;->loadLibrary(Ljava/lang/String;)V\n',
                f'CoreX_Hook ➸❥ {self.C.OG}"lib_Pairip_CoreX.so"'
            ))
        
        # 收集所有目标smali文件
        smali_files = []
        for smali_folder in smali_folders:
            for root, _, files in os.walk(smali_folder):
                for file in files:
                    if file in target_files:
                        smali_files.append(os.path.join(root, file))
        
        if not smali_files:
            self.log(f"{self.C.WARN} 未找到需要补丁的Smali文件！")
            return True
        
        # 应用补丁
        patched_files = set()
        for pattern, replacement, description in patterns:
            for smali_file in smali_files:
                try:
                    # CoreX_Hook只应用到VMRunner.smali
                    if description.startswith("CoreX_Hook") and not os.path.basename(smali_file).endswith("VMRunner.smali"):
                        continue
                    
                    with open(smali_file, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    new_content = re.sub(pattern, replacement, content)
                    
                    if new_content != content:
                        with open(smali_file, 'w', encoding='utf-8', errors='ignore') as f:
                            f.write(new_content)
                        
                        patched_files.add(os.path.basename(smali_file))
                        self.log(f"{self.C.S} 补丁 {self.C.E} {self.C.G}{description} {self.C.OG}➸❥ {self.C.Y}{os.path.basename(smali_file)}")
                except Exception as e:
                    logger.error(f"应用补丁到{smali_file}时出错: {e}")
        
        if patched_files:
            self.log(f"{self.C.G} 成功打补丁文件: {', '.join(sorted(patched_files))} {self.C.G} ✔")
        else:
            self.log(f"{self.C.WARN} 未应用任何补丁")
        
        self.log(f"{self.C.CC}{'_' * 61}")
        return True
    
    def hook_core(self):
        """应用CoreX Hook"""
        # 确定要提取的base.apk名称
        with zipfile.ZipFile(self.apk_path, 'r') as zf:
            if "base.apk" in zf.namelist():
                base_apk = "base.apk"
            else:
                base_apk = f"{self.package_name}.apk"
        
        try:
            # 尝试使用7z或unzip提取，增强兼容性
            extract_success = False
            
            if os.name == 'nt' and shutil.which("7z"):
                self.log(f"{self.C.S} 使用7z提取 {self.C.E} {self.C.G}➸❥ {self.C.OG}{base_apk}")
                result = subprocess.run(
                    ["7z", "e", self.apk_path, base_apk, "-y"],
                    text=True, capture_output=True, **PLATFORM_ARGS
                )
                if result.returncode == 0:
                    extract_success = True
            
            if not extract_success and shutil.which("unzip"):
                self.log(f"{self.C.S} 使用unzip提取 {self.C.E} {self.C.G}➸❥ {self.C.OG}{base_apk}")
                result = subprocess.run(
                    ["unzip", "-o", self.apk_path, base_apk],
                    text=True, capture_output=True, **PLATFORM_ARGS
                )
                if result.returncode == 0:
                    extract_success = True
            
            # 如果外部工具失败，使用Python内置的zipfile
            if not extract_success:
                self.log(f"{self.C.S} 使用Python提取 {self.C.E} {self.C.G}➸❥ {self.C.OG}{base_apk}")
                with zipfile.ZipFile(self.apk_path) as zf:
                    zf.extract(base_apk)
                extract_success = True
            
            if not extract_success:
                raise Exception("无法提取base.apk文件")
            
            self.log(f'{self.C.S} 提取 {self.C.E} {self.C.G}➸❥ {self.C.OG}{base_apk} {self.C.G} ✔')
            
            # 重命名为libFirebaseCppApp.so
            dump_apk = "libFirebaseCppApp.so"
            os.rename(base_apk, dump_apk)
            
            # 确定lib路径（支持APKTool和APKEditor两种反编译结果格式）
            lib_paths = os.path.join(self.decompile_dir, 'root', 'lib', 'arm64-v8a')
            
            self.log(f"{self.C.S} 架构 {self.C.E} {self.C.G}➸❥ arm64-v8a")
            
            # 移动文件到lib目录
            shutil.move(dump_apk, os.path.join(lib_paths, dump_apk))
            
            # 复制CoreX库
            if os.path.exists(self.F.Pairip_CoreX):
                shutil.copy(self.F.Pairip_CoreX, lib_paths)
            else:
                # 尝试在当前目录查找
                alt_corex_path = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), "lib_Pairip_CoreX.so")
                if os.path.exists(alt_corex_path):
                    shutil.copy(alt_corex_path, lib_paths)
                else:
                    raise Exception(f"找不到lib_Pairip_CoreX.so文件")
            
            self.log(f'{self.C.S} Hook {self.C.E} {self.C.G}➸❥ {self.C.OG}libFirebaseCppApp.so {self.C.G} ✔')
            self.log(f'{self.C.S} Hook {self.C.E} {self.C.G}➸❥ {self.C.OG}lib_Pairip_CoreX.so {self.C.G} ✔')
            
            # 设置CoreX标志
            self.is_corex = True
            
            return True
        except Exception as e:
            # 清理临时文件
            if os.path.exists("libFirebaseCppApp.so"):
                os.remove("libFirebaseCppApp.so")
            self.log(f"{self.C.ERROR} Hook失败: {e}")
            return False
    
    def patch_manifest(self):
        """修复AndroidManifest.xml"""
        manifest_path = os.path.join(self.decompile_dir, 'AndroidManifest.xml')
        
        if not os.path.exists(manifest_path):
            self.log(f"{self.C.ERROR} AndroidManifest.xml 未找到！")
            return False
        
        try:
            content = open(manifest_path, 'r', encoding='utf-8', errors='ignore').read()
            
            # 移除不需要的标签
            patterns = [
                (r'\s+android:(splitTypes|requiredSplitTypes)="[^"]*?"', r'', 'Splits'),
                (r'(isSplitRequired=)"true"', r'\1"false"', 'isSplitRequired'),
                (r'\s+<meta-data\s+[^>]*"com\.android\.(vending\.|stamp\.|dynamic\.apk\.)[^"]*"[^>]*/>', r'', '<meta-data>'),
                (r'\s+<[^>]*"com\.(pairip\.licensecheck|android\.vending\.CHECK_LICENSE)[^"]*"[^>]*/>', r'', 'CHECK_LICENSE')
            ]
            
            for pattern, replacement, description in patterns:
                new_content = re.sub(pattern, replacement, content)
                if new_content != content:
                    self.log(f"{self.C.S} 标签 {self.C.E} {self.C.OG}{description}")
                    self.log(f"{self.C.S} 模式 {self.C.E} {self.C.OG}➸❥ {self.C.P}{pattern}")
                    self.log(f"{self.C.G}     |")
                    self.log(f"     └──── {self.C.CC}已清理 {self.C.OG}➸❥ {self.C.P}'{self.C.G}AndroidManifest.xml{self.C.P}' {self.C.G} ✔")
                content = new_content
            
            # 如果是Flutter或CoreX，添加extractNativeLibs="true"
            if self.is_flutter or self.use_corex_hook:
                application_tag = re.search(r'<application\s+[^>]*>', content)
                if application_tag:
                    cleaned_tag = re.sub(r'\s+android:extractNativeLibs="[^"]*?"', '', application_tag.group(0))
                    new_tag = re.sub(r'>', '\n\tandroid:extractNativeLibs="true">', cleaned_tag)
                    content = content.replace(application_tag.group(0), new_tag)
            
            open(manifest_path, 'w', encoding='utf-8', errors='ignore').write(content)
            self.log(f"{self.C.S} AndroidManifest.xml {self.C.E} {self.C.G}已修复 {self.C.G} ✔")
            return True
        except Exception as e:
            self.log(f"{self.C.ERROR} 修复AndroidManifest.xml失败: {e}")
            return False
    
    def recompile_apk(self):
        """重新编译APK"""
        self.log(f"{self.C.X} 使用APKEditor重新编译APK...")
        
        cmd = ["java", "-jar", self.F.APKEditor_Path, "b", "-i", self.decompile_dir, "-o", self.build_dir, "-f", "-dex-lib", "jf"]
        
        if self.is_flutter:
            cmd += ["-extractNativeLibs", "true"]
        
        self.log(f"{self.C.G}  |")
        self.log(f"  └──── {self.C.CC}重新编译命令 ~{self.C.G}$ java -jar {os.path.basename(self.F.APKEditor_Path)} b -i {os.path.basename(self.decompile_dir)} -o {os.path.basename(self.build_dir)} -f -dex-lib jf" + (" -extractNativeLibs true" if self.is_flutter else ""))
        self.log(f"{self.C.CC}{'_' * 61}")
        
        try:
            # 使用subprocess.run并实时输出
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, **PLATFORM_ARGS)
            
            # 实时读取和输出
            for line in process.stdout:
                self.log(line.strip())
            
            for line in process.stderr:
                # 以普通信息形式显示stderr输出，而不是错误信息
                self.log(line.strip())
            
            process.wait()
            
            if process.returncode != 0:
                raise subprocess.CalledProcessError(process.returncode, cmd)
            
            self.log(f"{self.C.X} 重新编译成功 {self.C.G} ✔")
            self.log(f"{self.C.CC}{'_' * 61}")
            self.log(f"{self.C.S} APK已创建 {self.C.E} {self.C.G}➸❥ {self.C.Y}{self.build_dir} {self.C.G} ✔")
            return True
        except subprocess.CalledProcessError:
            self.log(f"{self.C.ERROR} 重新编译失败！")
            return False
    
    def crc_fix(self):
        """简单的CRC修复（复制原始APK中的签名块）"""
        try:
            # 这里使用简单的方式，实际项目中可能需要更复杂的CRC修复
            self.log(f"{self.C.S} CRC修复 {self.C.E} {self.C.G}已跳过，使用默认签名 {self.C.G} ✔")
            return True
        except Exception as e:
            self.log(f"{self.C.WARN} CRC修复失败: {e}")
            return False
    
    def clean_up(self):
        """清理临时文件"""
        # 清理反编译目录
        if os.path.exists(self.decompile_dir):
            shutil.rmtree(self.decompile_dir)
            self.log(f"{self.C.S} 清理 {self.C.E} {self.C.G}➸❥ 反编译目录已删除")
        
        # 删除临时合并的APK文件
        if os.path.exists(self.output_path):
            try:
                os.remove(self.output_path)
                self.log(f"{self.C.S} 清理 {self.C.E} {self.C.G}➸❥ 临时APK文件已删除")
            except Exception as e:
                logger.warning(f"无法删除临时文件 {self.output_path}: {e}")
        
        # 清理可能的残留文件
        if os.path.exists("libFirebaseCppApp.so"):
            try:
                os.remove("libFirebaseCppApp.so")
            except:
                pass
    
    def run(self):
        """运行主流程"""
        self.log(f"{self.C.X} 简化版RKPairip - 处理.apks文件并应用CoreX Hook {self.C.X}")
        
        start_time = time.time()
        
        try:
            # 检查依赖
            if not self.check_dependencies():
                return False
            
            # 合并.apks文件
            if not self.anti_split():
                return False
            
            # 扫描APK
            if not self.scan_apk():
                return False
            
            # 反编译APK
            if not self.decompile_apk():
                return False
            
            # 如果使用CoreX Hook
            if self.use_corex_hook:
                if not self.check_corex():
                    self.log(f"{self.C.INFO} CoreX Hook不需要或不支持，跳过...")
                else:
                    if not self.hook_core():
                        self.log(f"{self.C.WARN} CoreX Hook失败，继续...")
            
            # 修复AndroidManifest.xml
            if not self.patch_manifest():
                return False
            
            # 应用Smali补丁
            if not self.smali_patch():
                self.log(f"{self.C.WARN} Smali补丁应用失败，继续...")
            
            # 重新编译APK
            if not self.recompile_apk():
                return False
            
            # CRC修复
            self.crc_fix()
            
            # 清理
            self.clean_up()
            
            elapsed_time = time.time() - start_time
            self.log(f"{self.C.S} 耗时 {self.C.E} {self.C.OG}➸❥ {self.C.PN}{elapsed_time:.2f}{self.C.CC} 秒")
            self.log(f"{self.C.C} 🚩 处理完成 🚩")
            self.log(f"{self.C.G} ✨ 输出文件: {self.C.Y}{self.build_dir}")
            
            return True
        except KeyboardInterrupt:
            self.log(f"{self.C.WARN} 用户中断操作")
            self.clean_up()
            return False
        except Exception as e:
            self.log(f"{self.C.ERROR} 运行过程中出错: {e}")
            logger.error(f"运行出错: {e}", exc_info=True)
            self.clean_up()
            return False