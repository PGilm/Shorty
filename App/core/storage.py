import json
import os

from flask import current_app


SHORTY_STORAGE_MAP_FILENAME = "shorty_user_storage.json"
SHORTY_ROOT_DIRNAME = "-ShortyTables"


def _project_root():
    try:
        return os.path.abspath(os.path.join(current_app.root_path, os.pardir))
    except Exception:
        return os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))


def default_shorty_base_folder():
    return os.path.join(_project_root(), SHORTY_ROOT_DIRNAME)


def default_user_shorty_folder(username):
    safe_username = (username or "").strip() or "anonymous"
    return os.path.join(default_shorty_base_folder(), safe_username)


def _storage_map_path():
    instance_path = current_app.instance_path
    os.makedirs(instance_path, exist_ok=True)
    return os.path.join(instance_path, SHORTY_STORAGE_MAP_FILENAME)


def _load_storage_map():
    path = _storage_map_path()
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            return {}
        cleaned = {}
        for user, folder in data.items():
            if not isinstance(user, str) or not isinstance(folder, str):
                continue
            folder_text = folder.strip()
            if not folder_text:
                continue
            cleaned[user] = os.path.abspath(os.path.expanduser(folder_text))
        return cleaned
    except Exception:
        current_app.logger.exception("Unable to load Shorty storage map file")
        return {}


def _save_storage_map(mapping):
    path = _storage_map_path()
    tmp_path = f"{path}.tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(mapping, f, indent=2, sort_keys=True)
    os.replace(tmp_path, path)


def get_user_selected_shorty_folder(username):
    if not username:
        return None
    mapping = _load_storage_map()
    selected = mapping.get(username)
    return selected if selected else None


def get_user_shorty_folder(username, create=True):
    selected = get_user_selected_shorty_folder(username)
    folder = selected or default_user_shorty_folder(username)
    if create:
        os.makedirs(folder, exist_ok=True)
    return folder


def get_user_shorty_folder_info(username):
    default_folder = default_user_shorty_folder(username)
    selected = get_user_selected_shorty_folder(username)
    folder = selected or default_folder
    os.makedirs(folder, exist_ok=True)
    return {
        "folder": folder,
        "default_folder": default_folder,
        "is_default": selected is None
    }


def set_user_shorty_folder(username, folder):
    if not username:
        raise ValueError("Missing username")
    candidate = str(folder or "").strip()
    if not candidate:
        raise ValueError("Missing folder path")
    normalized = os.path.abspath(os.path.expanduser(candidate))
    if not os.path.isabs(normalized):
        raise ValueError("Folder path must be absolute")
    os.makedirs(normalized, exist_ok=True)
    if not os.path.isdir(normalized):
        raise ValueError("Selected path is not a folder")
    mapping = _load_storage_map()
    mapping[username] = normalized
    _save_storage_map(mapping)
    return normalized


def clear_user_shorty_folder(username):
    if not username:
        return
    mapping = _load_storage_map()
    if username in mapping:
        del mapping[username]
        _save_storage_map(mapping)


def list_user_shorty_files(username, extension):
    folder = get_user_shorty_folder(username, create=True)
    ext = (extension or "").lower()
    files = []
    for name in os.listdir(folder):
        if not isinstance(name, str):
            continue
        if ext and not name.lower().endswith(ext):
            continue
        files.append(name)
    files.sort(key=lambda item: item.lower())
    return files

