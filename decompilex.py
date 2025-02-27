import os
import sys
import pefile
import r2pipe
import magic
import binascii
import zipfile
import javalang
import subprocess
import requests
import shutil
from capstone import *
from pathlib import Path
from colorama import Fore, Style, init
import pyfiglet

# Add decompiler paths
DEX2JAR_PATH = "tools/dex2jar/d2j-dex2jar.sh"  # or .bat for Windows
JADX_PATH = "tools/jadx/bin/jadx"
CFR_PATH = "tools/cfr.jar"
PROCYON_PATH = "tools/procyon-decompiler.jar"

def print_banner():
    banner = f"""{Fore.CYAN}
    
    {Fore.GREEN}[>] Decompile • Analyze • Modify • Recompile{Style.RESET_ALL}
    {Fore.GREEN}[>] Java • Android • Kotlin • Python • Smali{Style.RESET_ALL}
    {Fore.RED}[>] author : Kcyb3r {Style.RESET_ALL} {Fore.YELLOW}https://www.kezai.online/{Style.RESET_ALL}
    """
    print(banner)
Ban_er = pyfiglet.figlet_format("DecompileX")
print(Fore.MAGENTA + Ban_er + Style.RESET_ALL)
class ToolInstaller:
    def __init__(self):
        self.tools_dir = "tools"
        self.temp_dir = "temp"
        
    def install_all(self):
        print(f"{Fore.CYAN}[+] Checking and installing required tools...{Style.RESET_ALL}")
        os.makedirs(self.tools_dir, exist_ok=True)
        os.makedirs(self.temp_dir, exist_ok=True)
        
        self.install_dex2jar()
        self.install_jadx()
        self.install_cfr()
        
        shutil.rmtree(self.temp_dir)
        print(f"{Fore.GREEN}[+] All tools installed successfully{Style.RESET_ALL}")
        
    def install_dex2jar(self):
        dex2jar_dir = os.path.join(self.tools_dir, "dex2jar")
        if os.path.exists(dex2jar_dir):
            return
            
        print(f"{Fore.CYAN}[+] Installing dex2jar...{Style.RESET_ALL}")
        url = "https://github.com/pxb1988/dex2jar/releases/download/v2.4/dex-tools-2.4.zip"
        zip_path = os.path.join(self.temp_dir, "dex2jar.zip")
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, stream=True, verify=True)
            response.raise_for_status()
            
            with open(zip_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            if not zipfile.is_zipfile(zip_path):
                raise Exception("Downloaded file is not a valid zip file")
            
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(self.tools_dir)
            
            if os.path.exists(os.path.join(self.tools_dir, "dex-tools-2.4")):
                if os.path.exists(dex2jar_dir):
                    shutil.rmtree(dex2jar_dir)
                os.rename(os.path.join(self.tools_dir, "dex-tools-2.4"), dex2jar_dir)
            
            if os.name != 'nt':  # For Linux/Mac
                for script in os.listdir(dex2jar_dir):
                    if script.endswith('.sh'):
                        script_path = os.path.join(dex2jar_dir, script)
                        os.chmod(script_path, 0o755)
            
            print(f"{Fore.GREEN}[+] dex2jar installed successfully{Style.RESET_ALL}")
            
        except Exception as e:
            print(f"{Fore.RED}[!] Error installing dex2jar: {str(e)}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}[*] Attempting alternative download method...{Style.RESET_ALL}")
            try:
                # Alternative direct download URL
                alt_url = "https://sourceforge.net/projects/dex2jar/files/latest/download"
                response = requests.get(alt_url, headers=headers, stream=True, allow_redirects=True)
                response.raise_for_status()
                
                with open(zip_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                        
                # Rest of the installation process...
                # ... (same as above)
                
            except Exception as e2:
                print(f"{Fore.RED}[!] Alternative download failed: {str(e2)}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}[*] Please install manually:{Style.RESET_ALL}")
                print("""
                1. Download dex2jar from: https://github.com/pxb1988/dex2jar/releases
                2. Extract it to tools/dex2jar directory
                3. Make .sh files executable (on Linux/Mac):
                   chmod +x tools/dex2jar/*.sh
                """)
                sys.exit(1)
            
    def install_jadx(self):
        jadx_dir = os.path.join(self.tools_dir, "jadx")
        if os.path.exists(jadx_dir):
            return
            
        print(f"{Fore.CYAN}[+] Installing JADX...{Style.RESET_ALL}")
        url = "https://github.com/skylot/jadx/releases/download/v1.4.7/jadx-1.4.7.zip"
        zip_path = os.path.join(self.temp_dir, "jadx.zip")
        
        response = requests.get(url)
        with open(zip_path, 'wb') as f:
            f.write(response.content)
            
        os.makedirs(jadx_dir)
        shutil.unpack_archive(zip_path, jadx_dir)
        
        if os.name != 'nt':
            os.chmod(os.path.join(jadx_dir, "bin", "jadx"), 0o755)
            
    def install_cfr(self):
        cfr_path = os.path.join(self.tools_dir, "cfr.jar")
        if os.path.exists(cfr_path):
            return
            
        print(f"{Fore.CYAN}[+] Installing CFR...{Style.RESET_ALL}")
        url = "https://www.benf.org/other/cfr/cfr-0.152.jar"
        response = requests.get(url)
        with open(cfr_path, 'wb') as f:
            f.write(response.content)

class BytecodeExtractor:
    def __init__(self, target_file):
        self.target = target_file
        self.file_type = magic.from_file(target_file)
        self.output_dir = "bytecode_output"
        self.decompiled_dir = os.path.join(self.output_dir, "decompiled")
        
        # Update tool paths based on current directory
        self.DEX2JAR_PATH = os.path.join("tools", "dex2jar", "d2j-dex2jar.sh" if os.name != 'nt' else "d2j-dex2jar.bat")
        self.JADX_PATH = os.path.join("tools", "jadx", "bin", "jadx")
        self.CFR_PATH = os.path.join("tools", "cfr.jar")
        
    def _decompile_dex(self, dex_path):
        try:
            print(f"{Fore.CYAN}[+] Converting DEX to JAR...{Style.RESET_ALL}")
            jar_path = dex_path.replace('.dex', '-dex2jar.jar')
            subprocess.run([self.DEX2JAR_PATH, dex_path, '-o', jar_path], check=True)
            
            print(f"{Fore.CYAN}[+] Decompiling with JADX...{Style.RESET_ALL}")
            jadx_output = os.path.join(self.decompiled_dir, "jadx_output")
            subprocess.run([self.JADX_PATH, '-d', jadx_output, jar_path], check=True)
            
            print(f"{Fore.CYAN}[+] Decompiling with CFR...{Style.RESET_ALL}")
            cfr_output = os.path.join(self.decompiled_dir, "cfr_output")
            subprocess.run(['java', '-jar', self.CFR_PATH, jar_path, '--outputdir', cfr_output], check=True)
            
            return True
        except Exception as e:
            print(f"{Fore.RED}[!] Decompilation error: {str(e)}{Style.RESET_ALL}")
            return False

    def analyze(self):
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            
        file_ext = self.target.lower().split('.')[-1]
        
        handlers = {
            'apk': self._handle_apk,
            'dex': self._handle_dex,
            'class': self._handle_class,
            'jar': self._handle_jar,
            'smali': self._handle_smali,
            'appimage': self._handle_appimage  # Add AppImage handler
        }
        
        handler = handlers.get(file_ext)
        if handler:
            print(f"{Fore.GREEN}[+] Processing {file_ext.upper()} file...{Style.RESET_ALL}")
            handler()
        else:
            print(f"{Fore.RED}[!] Unsupported file type: {file_ext}{Style.RESET_ALL}")

    def _handle_apk(self):
        try:
            apk_dir = os.path.join(self.output_dir, "apk_contents")
            os.makedirs(apk_dir, exist_ok=True)
            os.makedirs(self.decompiled_dir, exist_ok=True)
            
            print(f"{Fore.CYAN}[+] Extracting APK contents...{Style.RESET_ALL}")
            with zipfile.ZipFile(self.target, 'r') as apk:
                apk.extractall(apk_dir)
            
            # Process manifest
            manifest_path = os.path.join(apk_dir, "AndroidManifest.xml")
            if os.path.exists(manifest_path):
                print(f"{Fore.CYAN}[+] Analyzing AndroidManifest.xml{Style.RESET_ALL}")
                # Add manifest analysis here
                
            # Process DEX files
            dex_files = [f for f in os.listdir(apk_dir) if f.endswith('.dex')]
            for dex in dex_files:
                dex_path = os.path.join(apk_dir, dex)
                print(f"{Fore.CYAN}[+] Processing DEX: {dex}{Style.RESET_ALL}")
                self._decompile_dex(dex_path)
                
            # Process resources
            resources_path = os.path.join(apk_dir, "resources.arsc")
            if os.path.exists(resources_path):
                print(f"{Fore.CYAN}[+] Extracting resources...{Style.RESET_ALL}")
                res_output = os.path.join(self.decompiled_dir, "resources")
                os.makedirs(res_output, exist_ok=True)
                # Add resource extraction here
                
            print(f"{Fore.GREEN}[+] APK analysis complete. Check {self.decompiled_dir} for results{Style.RESET_ALL}")
            
        except Exception as e:
            print(f"{Fore.RED}[!] Error processing APK: {str(e)}{Style.RESET_ALL}")

    def _handle_dex(self):
        try:
            print(f"{Fore.CYAN}[+] Decompiling DEX file{Style.RESET_ALL}")
            # Add dex decompilation logic
        except Exception as e:
            print(f"{Fore.RED}[!] Error processing DEX: {str(e)}{Style.RESET_ALL}")

    def _handle_class(self):
        try:
            print(f"{Fore.CYAN}[+] Decompiling Java class file{Style.RESET_ALL}")
            os.makedirs(self.decompiled_dir, exist_ok=True)
            
            # Decompile with CFR
            cfr_output = os.path.join(self.decompiled_dir, "cfr_output")
            subprocess.run(['java', '-jar', self.CFR_PATH, self.target, '--outputdir', cfr_output], check=True)
            
            # Decompile with Procyon as backup
            procyon_output = os.path.join(self.decompiled_dir, "procyon_output")
            subprocess.run(['java', '-jar', PROCYON_PATH, '-o', procyon_output, self.target], check=True)
            
            print(f"{Fore.GREEN}[+] Class decompilation complete{Style.RESET_ALL}")
            
        except Exception as e:
            print(f"{Fore.RED}[!] Error processing class file: {str(e)}{Style.RESET_ALL}")

    def _handle_jar(self):
        try:
            print(f"{Fore.CYAN}[+] Processing JAR file{Style.RESET_ALL}")
            os.makedirs(self.decompiled_dir, exist_ok=True)
            
            # Decompile with CFR
            print(f"{Fore.CYAN}[+] Decompiling with CFR...{Style.RESET_ALL}")
            cfr_output = os.path.join(self.decompiled_dir, "cfr_output")
            subprocess.run(['java', '-jar', self.CFR_PATH, self.target, '--outputdir', cfr_output], check=True)
            
            # Extract and process class files
            jar_contents = os.path.join(self.output_dir, "jar_contents")
            os.makedirs(jar_contents, exist_ok=True)
            
            with zipfile.ZipFile(self.target, 'r') as jar:
                jar.extractall(jar_contents)
            
            print(f"{Fore.GREEN}[+] JAR processing complete{Style.RESET_ALL}")
            
        except Exception as e:
            print(f"{Fore.RED}[!] Error processing JAR: {str(e)}{Style.RESET_ALL}")

    def _handle_smali(self):
        try:
            print(f"{Fore.CYAN}[+] Processing Smali file{Style.RESET_ALL}")
            # Add smali processing logic
        except Exception as e:
            print(f"{Fore.RED}[!] Error processing Smali: {str(e)}{Style.RESET_ALL}")

    def _handle_appimage(self):
        try:
            print(f"{Fore.CYAN}[+] Extracting AppImage contents...{Style.RESET_ALL}")
            print(f"[*] Using AppImage path: {self.target}")  # Debug print
            output_dir = os.path.join(self.output_dir, "appimage_contents")
            os.makedirs(output_dir, exist_ok=True)

            if not os.path.isfile(self.target):
                print(f"{Fore.RED}[!] AppImage file does not exist: {self.target}{Style.RESET_ALL}")
                return

            # Make the AppImage executable
            subprocess.run(['chmod', '+x', self.target], check=True)

            # Extract AppImage without './'
            result = subprocess.run([self.target, '--appimage-extract'], check=False, capture_output=True, text=True)
            if result.returncode != 0:
                print(f"{Fore.RED}[!] Extraction failed: {result.stderr}{Style.RESET_ALL}")
                return

            # Check if the extraction created the expected directory
            extracted_dir = os.path.join(os.path.dirname(self.target), "squashfs-root")
            if os.path.exists(extracted_dir):
                shutil.move(extracted_dir, output_dir)
                print(f"{Fore.GREEN}[+] AppImage extraction complete. Check {output_dir} for results{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}[!] Extraction failed: {extracted_dir} not found. Output was: {result.stdout}{Style.RESET_ALL}")

        except Exception as e:
            print(f"{Fore.RED}[!] Error processing AppImage: {str(e)}{Style.RESET_ALL}")

def main():
    init()
    print_banner()
    
    # Install required tools first
    installer = ToolInstaller()
    installer.install_all()
    
    while True:
        file_path = input(f"{Fore.CYAN}[*] Enter path to decompile file (APK/DEX/JAR/CLASS/AppImage): {Style.RESET_ALL}").strip()
        
        path = Path(file_path).expanduser().resolve()
        
        if not path.exists():
            print(f"{Fore.RED}[!] File not found: {path}{Style.RESET_ALL}")
            continue
            
        if not path.suffix.lower() in ['.apk', '.dex', '.jar', '.class', '.smali']:
            print(f"{Fore.YELLOW}[!] Warning: Unsupported file type. Continue? (y/n){Style.RESET_ALL}")
            if input().lower() != 'y':
                continue
                
        break

    extractor = BytecodeExtractor(str(path))
    extractor.analyze()

if __name__ == "__main__":
    main() 
