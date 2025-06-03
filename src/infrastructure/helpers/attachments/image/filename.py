import pathlib
import typing


def update_filename_jpeg(file_name: typing.Text) -> typing.Text:
    return str(pathlib.Path(file_name).with_suffix(".jpg"))
