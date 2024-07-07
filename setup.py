from Cython.Build import cythonize
from setuptools import setup
from setuptools import Extension
import os

current_dir = os.getcwd()
file_src = os.path.join(current_dir, 'src')
file_include = os.path.join(current_dir, 'include')

ext = Extension(
    name="XiaoJu",
    sources=[f"{current_dir}/xiaoju.pyx", f"{file_src}/mqtt.c", f"{file_src}/protocol.c", f"{file_src}/xiaoju.c"],
    include_dirs=[file_include],
)


def remove_file(file_path):
    try:
        os.remove(file_path)
        print(f"{file_path} remove suss")
    except OSError as e:
        print(f"Error: {file_path} - {e.strerror}")


def remove_dir(dir_path):
    try:
        os.rmdir(dir_path)
        print(f"{dir_path} remove suss")
    except OSError as e:
        print(f"Error: {dir_path} - {e.strerror}")


def remove_dir_contents(dir_path):
    try:
        for root, dirs, files in os.walk(dir_path, topdown=False):
            for name in files:
                remove_file(os.path.join(root, name))
            for name in dirs:
                remove_dir(os.path.join(root, name))
        remove_dir(dir_path)
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    setup(ext_modules=cythonize(ext, language_level=3))
    remove_file("XiaoJu.c")
    remove_dir_contents("build")
