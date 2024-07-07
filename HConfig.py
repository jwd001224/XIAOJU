import subprocess
import os
import shutil
import sys

GREEN_COLOR = "\033[92m"
RESET_COLOR = "\033[0m"


def copy_output_directory(src_dir, dest_dir):
    for root, dirs, files in os.walk(src_dir):
        for dir_name in dirs:
            if dir_name == "output":
                dest_path = os.path.join(dest_dir, dir_name)
                if os.path.exists(dest_path):
                    shutil.rmtree(dest_path)
                shutil.copytree(os.path.join(root, dir_name), dest_path)


def python_setup():
    command_setup = ["python", "setup.py", "build_ext", "--inplace", "--debug", "--verbose", "-j4"]
    config_dir_setup = "xiaoju"
    subfolder_path = "./xiaoju"

    parent_folder_path = "."

    subprocess.run(command_setup, cwd=config_dir_setup)

    for root, dirs, files in os.walk(subfolder_path):
        for file in files:
            if file.endswith(".so"):
                subfile_path = os.path.join(root, file)
                parent_file_path = os.path.join(parent_folder_path, file)
                if os.path.exists(parent_file_path):
                    os.remove(parent_file_path)
                shutil.copy(subfile_path, parent_folder_path)
                print(GREEN_COLOR + f"File '{file}' copied suss." + RESET_COLOR)


if __name__ == "__main__":
    python_setup()
