import json
import os
import datetime

def log_error(message):
    log_dir = os.path.join(os.path.expandvars(r"%APPDATA%\DoctorApp"), "logs")
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, "errors.json")
    log_entry = {
        "timestamp": datetime.datetime.now().isoformat(),
        "error": message
    }
    try:
        with open(log_path, "a", encoding="utf-8") as f:
            json.dump(log_entry, f, ensure_ascii=False)
            f.write("\n")
    except Exception:
        pass