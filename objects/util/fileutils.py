import os


def get_file(folder: str, file_name: str):
    file = os.path.join(folder, file_name)
    return file if os.path.isfile(file) else None


def list_files(path: str):
    gen = (file for file in os.listdir(path)
           if os.path.isfile(os.path.join(path, file)))

    # Error len() for type Generator
    return list(gen)


def delete_file(file) -> bool:
    if os.path.exists(file) and os.path.isfile(file):
        os.remove(file)
        return True

    return False
