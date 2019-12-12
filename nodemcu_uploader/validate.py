from .exceptions import ValidationException

MAX_FS_NAME_LEN = 31


def remotePath(path):
    """Do various checks on the remote file name like max length.
    Raises exception if not valid
    """
    if len(path) > MAX_FS_NAME_LEN:
        raise ValidationException('To long. >{0}'.format(MAX_FS_NAME_LEN), 'path', path)
    if len(path) < 1:
        raise ValidationException('To short', 'path', path)
