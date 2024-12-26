# requirements.py

# Standard imports
import os
import subprocess
import sys

REQUIREMENTS = [
    "PyAudio==0.2.14",
    "numpy<2.0",
    "urllib3==1.26.15",
    "pyObjC==9.0.1",
    "torch==2.1.2",
    "PyYAML==6.0.2",
    "requests==2.32.3",
    "openai-whisper==20231117",
    "PyOpenGL==3.1.7",
    "pygame==2.6.1"
]

def check_virtual_env():
    if os.environ.get("VIRTUAL_ENV") is None:
        print("Error: No virtual environment detected.")
        sys.exit(1)

def install_requirements(requirements):
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install"] + requirements)
    except subprocess.CalledProcessError as e:
        print(f"Error: Failed to install requirements. {e}")
        sys.exit(1)

def main():
    # Ensure user is in a virtual environment
    check_virtual_env()
    # Install requirements
    install_requirements(REQUIREMENTS)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
