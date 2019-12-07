

MAX_FS_NAME_LEN = 31
from .exceptions import PathLengthException


def remotePath(path):
    if len(path) > MAX_FS_NAME_LEN:
        raise PathLengthException
    if len(path) < 1:
        raise PathLengthException
