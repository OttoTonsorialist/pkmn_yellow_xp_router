import sys
import os
import shutil
import re
import logging

from utils.constants import const

logger = logging.getLogger(__name__)


def get_path_safe_string(raw_string):
    value = re.sub('[^\w\s-]', '', raw_string).strip().lower()
    value = re.sub('[-\s]+', '-', value)
    return value


def get_safe_path_no_collision(base_folder, name):
    name = get_path_safe_string(name)
    result = os.path.join(base_folder, name)
    if os.path.exists(result):
        counter = 0
        while os.path.exists(result):
            counter += 1
            result = os.path.join(base_folder, f"{name}_{counter}")
    
    return result


def get_existing_route_path(route_name) -> str:
    result = os.path.join(const.SAVED_ROUTES_DIR, f"{route_name}.json")
    if not os.path.exists(result):
        result = os.path.join(const.OUTDATED_ROUTES_DIR, f"{route_name}.json")
    
    return result


def get_existing_route_names(filter_text="", load_backups=False):
    loaded_routes = []
    filter_text = filter_text.lower()

    if os.path.exists(const.SAVED_ROUTES_DIR):
        for fragment in os.listdir(const.SAVED_ROUTES_DIR):
            name, ext = os.path.splitext(fragment)
            if filter_text not in name.lower():
                continue
            if ext != ".json":
                continue
            loaded_routes.append(name)
    
    if load_backups:
        if os.path.exists(const.OUTDATED_ROUTES_DIR):
            for fragment in os.listdir(const.OUTDATED_ROUTES_DIR):
                name, ext = os.path.splitext(fragment)
                if filter_text not in name.lower():
                    continue
                if ext != ".json":
                    continue
                loaded_routes.append(name)

    return sorted(loaded_routes, key=str.casefold)


def change_user_data_location(orig_dir, new_dir) -> bool:
    try:
        # If the orig dir is invalid for some reason, assume this is first time setup
        # just create the new dir, and return
        if not orig_dir or not os.path.exists(orig_dir):
            if not os.path.exists(new_dir):
                os.makedirs(new_dir)
            return True

        if not os.path.exists(new_dir):
            os.makedirs(new_dir)
        
        for orig_inner_dir, new_inner_dir in const.get_potential_user_data_dirs(new_dir):
            if os.path.exists(orig_inner_dir):
                shutil.copytree(orig_inner_dir, new_inner_dir)
        
        # do these separately so we only remove files after everything has been copied to the new location
        for orig_inner_dir, _ in const.get_potential_user_data_dirs(new_dir):
            if os.path.exists(orig_inner_dir):
                shutil.rmtree(orig_inner_dir)
        
        # Only nuke the previous dir if it's now empty
        if len(os.listdir(orig_dir)) == 0:
            shutil.rmtree(orig_dir)

        return True
    except Exception as e:
        logger.error(f"Failed to change data location to: {new_dir}")
        logger.exception(e)
        return False


def open_explorer(path) -> bool:
    try:
        if sys.platform == "linux" or sys.platform == "linux2":
            os.system(f'xdg-open "{path}"')
        elif sys.platform == "darwin":
            os.system(f'open "{path}"')
        elif sys.platform == "win32":
            os.startfile(path)
        else:
            return False
        
        return True
    except Exception as e:
        logger.error(f"Failed to open explorer to location: {path}")
        logger.exception(e)
        return False


def get_default_user_data_dir():
    result = os.path.expanduser("~")
    test = os.path.join(result, "Documents")
    if os.path.exists(test):
        result = test
    
    return os.path.join(result, const.APP_DATA_FOLDER_DEFAULT_NAME)


def backup_file_if_exists(orig_path):
    if os.path.exists(orig_path) and os.path.isfile(orig_path):
        new_backup_loc = get_safe_backup_path(orig_path)
        shutil.move(orig_path, new_backup_loc)


def get_safe_backup_path(orig_path):
    # first thing, convert the original path to the outdated folder, so that we don't clutter the main folder with backups
    _, orig_name = os.path.split(orig_path)
    orig_path = os.path.join(const.OUTDATED_ROUTES_DIR, orig_name)

    # TODO: kind of an awkward place for this... should it go somewhere else?
    if not os.path.exists(const.OUTDATED_ROUTES_DIR):
        os.makedirs(const.OUTDATED_ROUTES_DIR)

    base, ext = os.path.splitext(orig_path)
    counter = 1
    while True:
        result = f"{base}_{counter}{ext}"
        if not os.path.exists(result):
            return result
        counter += 1
