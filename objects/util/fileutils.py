import os


def list_files(path: str):
    return (file for file in os.listdir(path)
            if os.path.isfile(os.path.join(path, file)))


def delete_file(file) -> bool:
    if os.path.exists(file) and os.path.isfile(file):
        os.remove(file)
        return True

    return False
