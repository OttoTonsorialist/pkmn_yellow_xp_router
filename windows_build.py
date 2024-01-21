
import os
import sys
import subprocess


def get_all_json_folders(root_path, ignore_dirs):
    result = []

    for test_dir, _, test_files in os.walk(root_path):
        do_ignore = False
        for test_ignore in ignore_dirs:
            if test_dir.startswith(test_ignore):
                do_ignore = True
                break
        
        if do_ignore:
            continue

        for cur_test in test_files:
            if cur_test.endswith(".json"):
                result.append(test_dir[len(root_path) + 1:])
                break
    
    return result


if __name__ == "__main__":
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "main.pyw",
        "--noconfirm",
        "--onefile",
        "--hidden-import=PIL",
        "--hidden-import=appdirs",
        "--hidden-import=signalrcore",
        "--name", "pkmn_xp_router",
        "--add-data", "assets\*.tcl;assets",
        "--add-data", "assets\\theme\\*.tcl;assets\\theme",
        "--add-data", "assets\\theme\\dark\\*;assets\\theme\\dark",
    ]

    root_path = os.path.dirname(os.path.abspath(__file__))
    ignore_dirs = [
        os.path.join(root_path, x) for x in [
            ".git",
            "__pycache__",
            "build",
            "dist",
            "outdated_routes",
            "outputs",
            "route_one_output",
            "saved_routes"
        ]
    ]

    for cur_json_folder in get_all_json_folders(root_path, ignore_dirs):
        cmd.extend([
            "--add-data",
            f"{os.path.join(cur_json_folder, '*.json')};{cur_json_folder}"
        ])

    print(f"cmd: {' '.join(cmd)}")
    subprocess.call(cmd)

