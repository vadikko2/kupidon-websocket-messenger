import pathlib


def update_filename_jpeg(file_name: str) -> str:
    return str(pathlib.Path(file_name).with_suffix(".jpg"))
