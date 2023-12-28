import sys
import os
import shutil
from typing import Tuple
import urllib.request
import json
import zipfile
import logging

from utils.constants import const
from utils.config_manager import config

logger = logging.getLogger(__name__)


def _get_backup_loc():
    folder, file_name = os.path.split(sys.executable)
    return os.path.join(folder, "." + file_name + ".old")


def auto_cleanup_old_version():
    # only actually attempt to clean things up when running a PyInstaller-generated windows exe
    if getattr(sys, 'frozen', False):
        backup_loc = _get_backup_loc()
        if os.path.exists(backup_loc):
            logger.info(f"trying to cleanup: {backup_loc}")
            try:
                os.remove(backup_loc)
            except Exception as e:
                logger.error("Failed to cleanup old version:")
                logger.exception(e)


def _extract_version_info(version_string) -> str:
    try:
        [part_one, part_two] = version_string.split(".")
        major_version = int(''.join([x for x in part_one if x.isdigit()]))
        minor_version = int(''.join([x for x in part_two if x.isdigit()]))
        bugfix_version = part_two[-1]

        return major_version, minor_version, bugfix_version
    except Exception:
        return None, None, None


def _get_newer_version(v_one, v_two) -> str:
    # return the newer version
    one_major, one_minor, one_bugfix = _extract_version_info(v_one)
    two_major, two_minor, two_bugfix = _extract_version_info(v_two)

    if one_major is None and two_major is None:
        # if both versions are bad, just return the first, wtv
        return v_one
    elif one_major is None:
        # return valid version if only one is valid
        return v_two
    elif two_major is None:
        # return valid version if only one is valid
        return v_one
    
    if one_major > two_major:
        return v_one
    elif two_major > one_major:
        return v_two
    elif one_minor > two_minor:
        return v_one
    elif two_minor > one_minor:
        return v_two
    elif one_bugfix > two_bugfix:
        return v_one
    else:
        return v_two


def is_upgrade_needed(new_version, old_version):
    return (
        new_version is not None and
        new_version != const.APP_VERSION and 
        new_version == _get_newer_version(new_version, old_version)
    )


def is_upgrade_possible():
    return (
        getattr(sys, 'frozen', False) and
        sys.platform == "win32"
    )


def update(new_version=None, asset_url=None, display_fn=None) -> bool:
    # NOTE: automatic updates are currently only supported for windows
    if not is_upgrade_possible():
        message = "Rejecting automatic update due to non-windows platform"
        if display_fn is not None:
            display_fn(message)
        logger.error(message)
        return False

    if new_version is None or asset_url is None:
        new_version, asset_url = get_new_version_info()

    if is_upgrade_needed(new_version, const.APP_VERSION):
        return extract_and_update_code(asset_url, config.get_user_data_dir(), display_fn=display_fn)
    
    message = "No upgrade necessary, ignoring request for automatic update"
    if display_fn is not None:
        display_fn(message)
    logger.error(message)
    return False


def extract_and_update_code(zip_url, temp_dir, display_fn=None) -> bool:
    if not is_upgrade_possible():
        raise ValueError("Cannot update automatically unless running from an exe on windows")

    temp_zip_loc = os.path.join(temp_dir, "temp.zip")
    temp_extract_loc = os.path.join(temp_dir, "extracted_zip")
    update_loc = sys.executable
    temp_rename_loc = _get_backup_loc()

    def _cleanup():
        logger.info("Beginning cleanup")
        if os.path.exists(temp_zip_loc):
            os.remove(temp_zip_loc)

        if os.path.exists(temp_extract_loc):
            shutil.rmtree(temp_extract_loc)

    try:
        # download zip file to temp location (user data dir, probably?)
        urllib.request.urlretrieve(zip_url, temp_zip_loc)
        if display_fn is not None:
            display_fn(f"New version downloaded")
        logger.info("New version downloaded")

        # unzip zip file into temp folder at temp location
        if not os.path.exists(temp_extract_loc):
            os.mkdir(temp_extract_loc)
        with zipfile.ZipFile(temp_zip_loc) as cur_zip:
            cur_zip.extractall(temp_extract_loc)
        if display_fn is not None:
            display_fn(f"New version zip file extracted")
        logger.info("New version zip file extracted")

        # NOTE: assume that there is only one exe present in the zip file, and that's the exe we want to replace
        # At the time of writing, this folder is named "main", but I'm going to assume the top level will always contain exactly one folder
        # This means we can package other files at the top level, if desired. We can also change the folder name if desired
        extracted_app_loc = None
        for test_inner_loc in os.listdir(temp_extract_loc):
            test_inner_loc = os.path.join(temp_extract_loc, test_inner_loc)
            logger.info(f"testing: {os.path.splitext(test_inner_loc)[1]}")
            if os.path.splitext(test_inner_loc)[1] == ".exe":
                extracted_app_loc = test_inner_loc
                break
        
        if not extracted_app_loc:
            logger.error("Extracted zip did not have the right structure")
            raise ValueError("Extracted zip did not have the right structure")

        # move running app out of the way to allow "in-place" replacement
        os.rename(update_loc, temp_rename_loc)

        # move all extracted data from temp folder to app location, overwriting
        shutil.copy2(extracted_app_loc, update_loc)
        if display_fn is not None:
            display_fn(f"Update completed")
        logger.info("Update completed")

        return True

    except Exception as e:
        logger.error(f"Automatic update failed with exception:")
        logger.exception(e)

        return False
    finally:
        #_cleanup()
        pass


def get_new_version_info(nuzlocke_path=False) -> Tuple[str, str]:
    # NOTE: automatic updates are currently only supported for windows

    # TODO: brittle, and tightly tied to github api not changing. Not sure what to do about it though...
    github_api_url = "https://api.github.com/repos/OttoTonsorialist/pkmn_yellow_xp_router/releases/latest"
    try:
        with urllib.request.urlopen(github_api_url) as response:
            data = json.loads(response.read())

            # find the windows zipfile from all assets
            asset_to_download = None
            for test_asset in data["assets"]:
                if not nuzlocke_path and test_asset["name"].startswith("windows"):
                    asset_to_download = test_asset["browser_download_url"]
                    break
                elif nuzlocke_path and test_asset["name"].startswith("nuzlocke"):
                    asset_to_download = test_asset["browser_download_url"]
                    break

            # return the name, and the download url
            return data["tag_name"], asset_to_download
    except Exception as e:
        logger.error(f"Exception during new version info extraction: {e}")
        logger.exception(e)
        return None, None