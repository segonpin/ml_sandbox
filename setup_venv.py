import os
import subprocess
import sys

def create_venv(venv_name):
    """Creates a virtual environment."""
    if not os.path.exists(venv_name):
        print(f"Creating virtual environment: {venv_name}...")
        subprocess.check_call([sys.executable, "-m", "venv", venv_name])
    else:
        print(f"Virtual environment '{venv_name}' already exists.")

def install_requirements(venv_name, requirements_file):
    """Installs dependencies from requirements.txt into the virtual environment."""
    pip_path = os.path.join(venv_name, "Scripts", "pip") if os.name == "nt" else os.path.join(venv_name, "bin", "pip")
    
    if not os.path.exists(requirements_file):
        print(f"Requirements file '{requirements_file}' not found.")
        return

    print(f"Installing dependencies from {requirements_file}...")
    subprocess.check_call([pip_path, "install", "-r", requirements_file])

def reminder_to_activate():
    activate_command = f"{VENV_NAME}\\Scripts\\activate" if os.name == "nt" else f"source {VENV_NAME}/bin/activate"

    print("\nSetup complete!")
    print(f"To activate the virtual environment, run:\n    {activate_command}")
    print("\nOr use the Python interpreter in the virtual environment directly:")
    venv_python = os.path.join(VENV_NAME, "Scripts", "python") if os.name == "nt" else os.path.join(VENV_NAME, "bin", "python")
    print(f"    {venv_python}")
    return venv_python


if __name__ == "__main__":
    VENV_NAME = ".venv"  # Change this to customize the virtual environment name
    REQUIREMENTS_FILE = "requirements.txt"  # Ensure this file exists in the current directory

    VENV_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), VENV_NAME))
    FULL_PATH_REQUIREMENTS_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), REQUIREMENTS_FILE))

    create_venv(VENV_PATH)
    install_requirements(VENV_PATH, FULL_PATH_REQUIREMENTS_FILE)
    venv_python = reminder_to_activate()
