import os
import shutil

from utils.constants import const

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
