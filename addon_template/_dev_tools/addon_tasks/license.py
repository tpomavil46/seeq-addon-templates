# license.py - Add this to your generated add-on

import json
from datetime import datetime, timedelta
from pathlib import Path
import warnings

CONFIG_FILENAME = "addon_config.json"
INSTALL_METADATA_FILENAME = ".install_metadata.json"
WARNING_THRESHOLD_DAYS = 30


def load_config(base_path: Path) -> dict:
    path = base_path / CONFIG_FILENAME
    if not path.exists():
        return {}
    with open(path, "r") as f:
        return json.load(f)


def load_install_metadata(base_path: Path) -> dict:
    path = base_path / INSTALL_METADATA_FILENAME
    if not path.exists():
        return {}
    with open(path, "r") as f:
        return json.load(f)


def check_license(base_path: Path):
    config = load_config(base_path)
    metadata = load_install_metadata(base_path)

    license_days = config.get("license_duration_days", 30)
    installed_str = metadata.get("first_use")

    if not installed_str:
        raise RuntimeError("Install time metadata missing; cannot validate license.")

    installed_time = datetime.fromisoformat(installed_str)
    now = datetime.now()
    expires_at = installed_time + timedelta(days=license_days)
    days_left = (expires_at - now).days

    if days_left < 0:
        raise RuntimeError("This add-on license has expired.")

    if days_left <= WARNING_THRESHOLD_DAYS:
        warnings.warn(f"License expires in {days_left} day(s). Please renew or reinstall.")


# Usage example (add this at the top of _seeq_add_on.py or your main runtime file)
# from license import check_license
# check_license(Path(__file__).resolve().parents[2])