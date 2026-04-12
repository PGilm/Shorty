import json
import os
import tempfile

from flask import current_app


SHORTY_STORAGE_MAP_FILENAME = "shorty_user_storage.json"
SHORTY_ROOT_DIRNAME = "-ShortyTables"
SHORTY_DEFAULT_ROOT_ENV = "SHORTY_DEFAULT_STORAGE_ROOT"
SHORTY_LEGACY_HTML_SUBDIR = "html"
SHORTY_LEGACY_JSON_SUBDIR = "json"
SHORTY_STORAGE_UNAVAILABLE_MESSAGE = (
    "Shorty storage folder unavailable. Reconnect drive or cloud folder and try again."
)


class ShortyStorageUnavailableError(RuntimeError):
    """Raised when a selected storage folder cannot be accessed."""
    pass


def _project_root():
    try:
        return os.path.abspath(os.path.join(current_app.root_path, os.pardir))
    except Exception:
        return os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))


def _legacy_project_shorty_base_folder():
    return os.path.join(_project_root(), SHORTY_ROOT_DIRNAME)


def _desktop_shorty_base_folder():
    return os.path.join(os.path.expanduser("~"), "Desktop", SHORTY_ROOT_DIRNAME)


def _paths_equal(left, right):
    if not left or not right:
        return False
    try:
        left_norm = os.path.normcase(os.path.abspath(os.path.expanduser(str(left))))
        right_norm = os.path.normcase(os.path.abspath(os.path.expanduser(str(right))))
        return left_norm == right_norm
    except Exception:
        return False


def default_shorty_base_folder():
    configured_root = str(os.environ.get(SHORTY_DEFAULT_ROOT_ENV, "") or "").strip()
    if configured_root:
        return os.path.abspath(os.path.expanduser(configured_root))

    return _legacy_project_shorty_base_folder()


def default_user_shorty_folder(username):
    safe_username = (username or "").strip() or "anonymous"
    return os.path.join(default_shorty_base_folder(), safe_username)


def _legacy_default_user_shorty_folder(username):
    safe_username = (username or "").strip() or "anonymous"
    return os.path.join(_legacy_project_shorty_base_folder(), safe_username)


def _desktop_default_user_shorty_folder(username):
    safe_username = (username or "").strip() or "anonymous"
    return os.path.join(_desktop_shorty_base_folder(), safe_username)


def _ensure_default_user_folder(username, preferred_folder):
    try:
        os.makedirs(preferred_folder, exist_ok=True)
        return preferred_folder
    except OSError:
        fallback = _legacy_default_user_shorty_folder(username)
        if not _paths_equal(fallback, preferred_folder):
            current_app.logger.warning(
                "Default Shorty folder unavailable; falling back to project-local folder",
                extra={"preferred_folder": preferred_folder, "fallback_folder": fallback},
            )
            os.makedirs(fallback, exist_ok=True)
            return fallback
        raise


def _normalize_folder_path(folder):
    return os.path.abspath(os.path.expanduser(str(folder or "").strip()))


def _missing_folder_message(folder):
    return f"{SHORTY_STORAGE_UNAVAILABLE_MESSAGE} (Expected folder: {folder})"


def _resolve_user_root_folder(username, create_default=True):
    selected = get_user_selected_shorty_folder(username)
    default_folder = default_user_shorty_folder(username)
    folder = selected or default_folder
    is_default = selected is None

    if is_default:
        if create_default:
            try:
                folder = _ensure_default_user_folder(username, folder)
            except OSError:
                raise ShortyStorageUnavailableError(_missing_folder_message(folder))
        return folder, True

    if os.path.isdir(folder):
        return folder, True

    raise ShortyStorageUnavailableError(_missing_folder_message(folder))


def _normalize_extension(extension):
    ext = (extension or "").strip().lower()
    if ext and not ext.startswith("."):
        ext = f".{ext}"
    return ext


def _legacy_subdir_for_extension(extension):
    ext = _normalize_extension(extension)
    if ext == ".html":
        return SHORTY_LEGACY_HTML_SUBDIR
    if ext == ".json":
        return SHORTY_LEGACY_JSON_SUBDIR
    return None


def _migrate_legacy_files(root_folder, extension):
    ext = _normalize_extension(extension)
    legacy_subdir = _legacy_subdir_for_extension(ext)
    if not ext or not legacy_subdir:
        return
    source_folder = os.path.join(root_folder, legacy_subdir)
    if not os.path.isdir(source_folder):
        return
    try:
        for name in os.listdir(source_folder):
            if not isinstance(name, str):
                continue
            if not name.lower().endswith(ext):
                continue
            source = os.path.join(source_folder, name)
            if not os.path.isfile(source):
                continue
            target = os.path.join(root_folder, name)
            if os.path.exists(target):
                continue
            os.replace(source, target)
    except Exception:
        current_app.logger.exception(
            "Unable to migrate legacy Shorty files from subfolder",
            extra={"root_folder": root_folder, "source_folder": source_folder, "extension": ext},
        )


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
    if not selected:
        return None

    # Backward compatibility: older builds persisted whichever default folder
    # was active at the time as if it were a user-selected folder. Treat
    # known defaults as "no explicit selection" so users follow the current
    # default root.
    legacy_default = _legacy_default_user_shorty_folder(username)
    desktop_default = _desktop_default_user_shorty_folder(username)
    active_default = default_user_shorty_folder(username)
    if (
        _paths_equal(selected, legacy_default)
        or _paths_equal(selected, desktop_default)
        or _paths_equal(selected, active_default)
    ):
        if username in mapping:
            del mapping[username]
            try:
                _save_storage_map(mapping)
            except Exception:
                current_app.logger.exception("Unable to clean stale default storage mapping")
        return None

    return selected


def get_user_shorty_folder(username, create=True):
    folder, _ = _resolve_user_root_folder(username, create_default=create)
    return folder


def get_user_shorty_folder_for_extension(username, extension, create=True):
    root_folder = get_user_shorty_folder(username, create=create)
    if create:
        os.makedirs(root_folder, exist_ok=True)
        _migrate_legacy_files(root_folder, extension)
    return root_folder


def get_user_shorty_folder_info(username):
    default_folder = default_user_shorty_folder(username)
    selected = get_user_selected_shorty_folder(username)
    folder = selected or default_folder
    is_default = selected is None
    is_available = True
    unavailable_message = None

    if is_default:
        try:
            folder = _ensure_default_user_folder(username, folder)
            default_folder = folder
        except OSError:
            is_available = False
            unavailable_message = _missing_folder_message(folder)
    else:
        is_available = os.path.isdir(folder)
        if not is_available:
            unavailable_message = _missing_folder_message(folder)

    return {
        "folder": folder,
        "default_folder": default_folder,
        "is_default": is_default,
        "is_available": is_available,
        "unavailable_message": unavailable_message,
    }


def set_user_shorty_folder(username, folder):
    if not username:
        raise ValueError("Missing username")
    candidate = str(folder or "").strip()
    if not candidate:
        raise ValueError("Missing folder path")
    normalized = _normalize_folder_path(candidate)
    if not os.path.isabs(normalized):
        raise ValueError("Folder path must be absolute")
    if not os.path.exists(normalized):
        try:
            os.makedirs(normalized, exist_ok=True)
        except Exception:
            raise ValueError("Unable to create selected folder. Check path and permissions.")
    if not os.path.isdir(normalized):
        raise ValueError("Selected path is not a folder")
    _migrate_legacy_files(normalized, ".html")
    _migrate_legacy_files(normalized, ".json")
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
    folder = get_user_shorty_folder_for_extension(username, extension, create=True)
    ext = _normalize_extension(extension)
    files = []
    for name in os.listdir(folder):
        if not isinstance(name, str):
            continue
        if ext and not name.lower().endswith(ext):
            continue
        files.append(name)
    files.sort(key=lambda item: item.lower())
    return files


def atomic_write_text(path, content, encoding="utf-8"):
    target_path = os.path.abspath(os.path.expanduser(str(path)))
    target_dir = os.path.dirname(target_path) or "."
    os.makedirs(target_dir, exist_ok=True)

    fd, tmp_path = tempfile.mkstemp(prefix=".shorty-tmp-", dir=target_dir)
    try:
        with os.fdopen(fd, "w", encoding=encoding) as handle:
            handle.write(content)
        os.replace(tmp_path, target_path)
    finally:
        if os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except Exception:
                pass


def atomic_write_json(path, payload, indent=2):
    text = json.dumps(payload, indent=indent)
    atomic_write_text(path, f"{text}\n", encoding="utf-8")
