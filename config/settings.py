import os

import yaml
from dotenv import load_dotenv

load_dotenv()

CONFIG_PATH = "data/config.yml"

DEFAULT_CONFIG = {
    "channels": {
        "downloads": None,
        "commands": None,
    },
    "notifications": {
        "discord": True,
        "dm_on_complete": True,
    },
}


def load_env(key: str, fallback=None):
    value = os.getenv(key, fallback)

    if isinstance(value, str):
        value = value.strip().strip('"').strip("'")

    if not value:
        raise RuntimeError(f"Required env variable {key} is not set")

    return value


def load_yaml(config_path=CONFIG_PATH):
    os.makedirs(os.path.dirname(config_path), exist_ok=True)

    if not os.path.exists(config_path):
        save_yaml(DEFAULT_CONFIG, config_path)
        return DEFAULT_CONFIG.copy()

    with open(config_path, "r") as f:
        return yaml.safe_load(f) or DEFAULT_CONFIG.copy()


def save_yaml(data, config_path=CONFIG_PATH):
    with open(config_path, "w") as f:
        yaml.safe_dump(data, f)


SETTINGS = load_yaml()


def get_setting(*keys, fallback=None):
    current = SETTINGS

    for key in keys:
        if not isinstance(current, dict):
            return fallback

        current = current.get(key)

        if current is None:
            return fallback

    return current


def set_setting(value, *keys):
    current = SETTINGS

    for key in keys[:-1]:
        if key not in current:
            current[key] = {}

        current = current[key]

    current[keys[-1]] = value

    save_yaml(SETTINGS)


ACCESS_TOKEN = load_env("ACCESS_TOKEN")
ALFRED_URL = load_env("ALFRED_URL")
ENVIRONMENT = load_env("ENVIRONMENT")
