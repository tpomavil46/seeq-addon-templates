import json
from datetime import datetime, timezone, timedelta
from pathlib import Path

DEFAULT_DURATION_DAYS = 365
METADATA_FILENAME = "install_metadata.json"

def check_license(base_path: Path) -> str:
    install_file = base_path / METADATA_FILENAME
    now = datetime.now(timezone.utc)

    # Create file on first run
    if not install_file.exists():
        print("⚠️ Writing install metadata file for first use...")
        metadata = {"install_time": now.isoformat()}
        with open(install_file, "w") as f:
            json.dump(metadata, f)
        install_time = now
    else:
        try:
            with open(install_file, "r") as f:
                metadata = json.load(f)
            install_time = datetime.fromisoformat(metadata["install_time"])
        except Exception as e:
            raise RuntimeError(f"❌ Failed to read install metadata: {e}")

    expiry = install_time + timedelta(days=DEFAULT_DURATION_DAYS)
    if now > expiry:
        message = "🚫 Add-on license has expired."
        print(message)
        raise RuntimeError(message)

    days_remaining = (expiry - now).days
    if days_remaining <= 30:
        message = f"⚠️ Add-on license expires in {days_remaining} day(s)."
        print(message)
        return message

    print("✅ License check passed.")
            
    return ""