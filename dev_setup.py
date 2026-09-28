import subprocess
import venv
import os

# Die virtuelle Umgebung wird im Projektordner als `.venv` angelegt. So bleiben
# die Pakete dieses Projekts von anderen Python-Projekten getrennt.
venv_dir = os.path.join(os.getcwd(), ".venv")
venv.create(venv_dir, system_site_packages=True)

if os.name == "nt":
    # Windows
    venv_python = os.path.join(os.getcwd(), ".venv", "Scripts", "python.exe")
    subprocess.check_call([venv_python, "-m", "pip", "install", "-r", "requirements.txt"])

if os.name == "posix":
    # Linux und macOS
    venv_python = os.path.join(os.getcwd(), ".venv", "bin", "python")
    subprocess.check_call([venv_python, "-m", "pip", "install", "-r", "requirements.txt"])