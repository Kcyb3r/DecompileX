# DecompileX
![image](https://github.com/user-attachments/assets/e33db896-f5dc-4215-b202-006504aa7b5c)

![Python Version](https://img.shields.io/badge/python-3.x-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![GitHub Issues](https://img.shields.io/github/issues/Kcyb3r/DecompileX.svg)
![GitHub Stars](https://img.shields.io/github/stars/Kcyb3r/DecompileX.svg)



DecompileX is a powerful tool for decompiling, analyzing, modifying, and recompiling bytecode from various file formats, including APK, DEX, JAR, CLASS, and AppImage files. This tool is designed for developers, security researchers, and enthusiasts who want to explore the inner workings of bytecode.


## Features

- **Decompile**: Convert bytecode files back to readable source code.
- **Analyze**: Inspect the structure and contents of bytecode files.
- **Modify**: Make changes to the decompiled code and recompile it.
- **Support for Multiple Formats**: Works with Java, Android, Kotlin, Python, and Smali files.
- **Easy Installation**: Automatically installs required tools like dex2jar, JADX, CFR, and Procyon.

## Requirements

- Python 3.x
- Required Python packages (listed in `requirements.txt`)

## Installation

1. Clone the repository or download the `app_extractor.py` file.
2. Install the required Python packages:

   ```bash
   pip3 install -r requirements.txt
   ```

3. Run the tool:

   ```bash
   python3 decompilex.py
   ```

## Usage

1. Launch the tool by running `decompilex.py`.
2. Follow the prompts to enter the path to the bytecode file you want to analyze.
3. The tool will automatically detect the file type and process it accordingly.

## Supported File Types

- APK
- DEX
- JAR
- CLASS
- AppImage
- Smali

## Author

- **Kcyb3r**  
  [Website](https://www.kezai.online/)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue for any suggestions or improvements.

## Acknowledgments

- Thanks to the developers of dex2jar, JADX, CFR, and Procyon for their amazing tools that make this project possible.
