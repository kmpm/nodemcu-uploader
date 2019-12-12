from .exceptions import PathLengthException

MAX_FS_NAME_LEN = 31


def remotePath(path):
    """Do various checks on the remote file name like max length.
    Raises exception if not valid
    """
    if len(path) > MAX_FS_NAME_LEN:
        raise PathLengthException
    if len(path) < 1:
        raise PathLengthException
