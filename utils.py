import os
import shutil

def backup_file_if_exists(orig_path):
    if os.path.exists(orig_path) and os.path.isfile(orig_path):
        new_backup_loc = get_safe_backup_path(orig_path)
        shutil.move(orig_path, new_backup_loc)

def get_safe_backup_path(orig_path):
    if not os.path.exists(orig_path):
        return orig_path
    
    base, ext = os.path.splitext(orig_path)
    counter = 1
    while True:
        result = f"{base}_{counter}{ext}"
        if not os.path.exists(result):
            return result
        counter += 1
