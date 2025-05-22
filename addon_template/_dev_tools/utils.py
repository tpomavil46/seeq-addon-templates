# seeq-addon-template/addon_template/_dev_tools/utils.py

import os
import sys
import subprocess
import pathlib
import venv
from datetime import datetime, timezone, timedelta
import json

LICENSE_DURATION_DAYS = None  # To be set dynamically
INSTALL_METADATA_FILE = ".install_metadata.json"

def load_license_config(base_path: pathlib.Path) -> int:
    """
    Load license duration from a JSON config file.

    Args:
        base_path (pathlib.Path): Path to the directory containing the config file

    Returns:
        int: Number of valid days after first use (default: 30)
    """
    config_path = base_path / ".addon_config.json"
    if config_path.exists():
        with open(config_path, "r") as f:
            config = json.load(f)
        return config.get("license_duration_days", 30)
    return 30

def check_install_duration_validity(base_path: pathlib.Path, days_valid: int):
    """
    Check if the license has expired based on the first install timestamp.

    Args:
        base_path (pathlib.Path): Directory to store metadata (e.g., project root)
        days_valid (int): Number of valid days after first use

    Raises:
        RuntimeError: If license duration has expired.
    """
    metadata_path = base_path / INSTALL_METADATA_FILE
    now = datetime.now(timezone.utc)

    if metadata_path.exists():
        with open(metadata_path, "r") as f:
            data = json.load(f)
            first_use = datetime.fromisoformat(data["first_use"])
    else:
        first_use = now
        with open(metadata_path, "w") as f:
            json.dump({"first_use": first_use.isoformat()}, f)

    if now > first_use + timedelta(days=days_valid):
        raise RuntimeError(
            f"⛔ Your license has expired ({days_valid} days from first install)."
            "\nPlease contact IT Vizion to renew your access."
        )

MIN_PYTHON_VERSION = (3, 11)
VENV_NAME = ".venv"
WHEELS_NAME = ".wheels"


def get_venv_paths(element_path: pathlib.Path, path_requested=None):
    venv_path = element_path / VENV_NAME
    wheels_path = element_path / WHEELS_NAME
    windows_os = os.name == "nt"
    path_to_scripts = venv_path / ("Scripts" if windows_os else "bin")
    path_to_pip = path_to_scripts / "pip"
    path_to_python = path_to_scripts / "python"
    path_to_test = path_to_scripts / "pytest"

    if path_requested is None:
        return venv_path, windows_os, path_to_python, path_to_pip, path_to_scripts, wheels_path
    if path_requested == "venv":
        return venv_path
    if path_requested == "windows_os":
        return windows_os
    if path_requested == "path_to_python":
        return path_to_python
    if path_requested == "path_to_pip":
        return path_to_pip
    if path_requested == "path_to_scripts":
        return path_to_scripts
    if path_requested == "wheels":
        return wheels_path
    if path_requested == "test":
        return path_to_test


def create_virtual_environment(
        element_path: pathlib.Path,
        clean: bool = False,
        global_path: pathlib.Path = None,
        hide_stdout: bool = False
):
    if global_path is None:
        global_path = element_path
 
    days_valid = load_license_config(global_path)
    check_install_duration_validity(global_path, days_valid)

    venv_path, windows_os, path_to_python, path_to_pip, path_to_scripts, wheels_path = get_venv_paths(global_path)
    if (
            not clean
            and venv_path.exists()
            and venv_path.is_dir()
    ):
        print("Virtual environment already exists.")
        return
    print(f"Creating virtual environment in {venv_path}")
    venv.EnvBuilder(
        system_site_packages=False, with_pip=True, clear=True, symlinks=not windows_os
    ).create(venv_path)
    stdout = subprocess.DEVNULL if hide_stdout else None
    print("Installing pip...")
    subprocess.run(
        f"{path_to_python} -m pip install --upgrade pip", shell=True, check=True, stdout=stdout
    )
    print("Installing dependencies...")
    pip_install_dependencies(element_path, path_to_pip, wheels_path, hide_stdout)
    print("Virtual environment created.")


def pip_install_dependencies(
        element_path: pathlib.Path,
        path_to_pip: pathlib.Path,
        wheels_path: pathlib.Path,
        upgrade=True,
        hide_stdout: bool = True
):
    upgrade = "--upgrade" if upgrade else ""
    command = f"{path_to_pip} install "
    if (element_path / 'requirements.dev.txt').exists():
        command += f"-r {element_path / 'requirements.dev.txt'} {upgrade} "
    if (element_path / 'requirements.txt').exists():
        command += f" -r {element_path / 'requirements.txt'} {upgrade}"
    if wheels_path.exists():
        command += f" -f {wheels_path}"
    subprocess.run(
        command,
        shell=True,
        check=True,
        stdout=subprocess.DEVNULL if hide_stdout else None
    )


def update_venv(element_path: pathlib.Path, global_path: pathlib.Path = None, hide_stdout: bool = True):
    if global_path is None:
        global_path = element_path
    venv_path, windows_os, path_to_python, path_to_pip, path_to_scripts, wheels_path = get_venv_paths(global_path)
    if not venv_path.exists() or not venv_path.is_dir():
        print("Virtual environment does not exist.")
        return

    print("Updating virtual environment...")
    subprocess.run(
        f"{path_to_python} -m pip install --upgrade pip", shell=True, check=True, stdout=subprocess.DEVNULL
    )

    pip_install_dependencies(element_path, path_to_pip, wheels_path, hide_stdout=hide_stdout)

    print("Virtual environment updated.")


def check_python_version(major, minor):
    python_version = sys.version_info
    if python_version < (major, minor):
        raise Exception(
            f"Python {major}.{minor} or higher is required. Found {python_version.major}.{python_version.minor}.{python_version.micro}"
        )
    print(
        f"Python version: {python_version.major}.{python_version.minor}.{python_version.micro}"
    )
