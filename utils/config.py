import json
import os
from typing import Dict, Any


def load_config() -> Dict[str, Any]:
    """Загружает конфигурацию из config.json"""
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.json")
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # Возвращаем значения по умолчанию, если файл не найден или поврежден
        return {"max_places": 20, "fake_occupied": 0}


def save_config(config: Dict[str, Any]) -> None:
    """Сохраняет конфигурацию в config.json"""
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.json")
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)


def get_remaining_places() -> int:
    """Возвращает количество оставшихся мест"""
    config = load_config()
    return config["max_places"] - config["fake_occupied"]


def set_fake_occupied(count: int) -> None:
    """Устанавливает количество накрученных мест"""
    config = load_config()
    config["fake_occupied"] = count
    save_config(config)


def get_max_places() -> int:
    """Возвращает максимальное количество мест"""
    config = load_config()
    return config["max_places"]


def set_max_places(count: int) -> None:
    """Устанавливает максимальное количество мест"""
    config = load_config()
    config["max_places"] = count
    save_config(config)
