import subprocess
import venv
import os

venv_dir = os.path.join(os.getcwd(), ".venv")
venv.create(venv_dir, system_site_packages=True)

if os.name == "nt":
    venv_python = os.path.join(os.getcwd(), ".venv", "Scripts", "python.exe")
    subprocess.check_call([venv_python, "-m", "pip", "install", "-r", "requirements.txt"])

if os.name == "posix":
    venv_python = os.path.join(os.getcwd(), ".venv", "bin", "python")
    subprocess.check_call([venv_python, "-m", "pip", "install", "-r", "requirements.txt"])