# -*- coding: utf-8 -*-
"""Collection of functions for platform independent filesystem operations."""

__author__ = 'Patrick Michl'
__email__ = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

from pathlib import Path
from nemoa.types import NestPath, OptStr, OptStrDict

def cwd() -> str:
    """Path of current working directory.

    Returns:
        String containing path of current working directory.

    """
    return str(Path.cwd())

def home() -> str:
    """Path of current users home directory.

    Returns:
        String containing path of home directory.

    """
    return str(Path.home())

def clear(fname: str) -> str:
    r"""Clear filename from invalid characters.

    Args:
        fname (str):

    Returns:
        String containing valid path syntax.

    Examples:
        >>> clear('3/\nE{$5}.e')
        '3E5.e'

    """
    import string

    valid = "-_.() " + string.ascii_letters + string.digits
    fname = ''.join(c for c in fname if c in valid).replace(' ', '_')

    return fname

def join(*args: NestPath) -> str:
    r"""Join and normalize path like structure.

    Args:
        *args: Path like arguments, respectively given by a tree of strings,
            which can be joined to a path.

    Returns:
        String containing valid path syntax.

    Examples:
        >>> join(('a', ('b', 'c')), 'd')
        'a\\b\\c\\d'

    """
    # flatten nested path to list and join list using os path seperators
    if not args:
        return ''
    if len(args) == 1 and isinstance(args[0], (str, Path)):
        path = args[0]
    else:
        largs = list(args) # make args mutable
        i = 0
        while i < len(largs):
            while isinstance(largs[i], (list, tuple)):
                if not largs[i]:
                    largs.pop(i)
                    i -= 1
                    break
                else:
                    largs[i:i + 1] = largs[i]
            i += 1
        try:
            path = Path(*largs)
        except Exception as err:
            raise ValueError("nested path is invalid") from err
    if not path:
        return ''

    # normalize path
    path = str(Path(path))

    return path


def expand(
        *args: NestPath, udict: OptStrDict = None, expapp: bool = True,
        expenv: bool = True) -> str:
    r"""Expand path variables.

    Args:
        *args: Path like arguments, respectively given by a tree of strings,
            which can be joined to a path.
        udict: dictionary for user variables.
            Thereby the keys in the dictionary are encapsulated
            by the symbol '%'. The user variables may also include references.
        expapp: determines if application specific environmental
            directories are expanded. For a full list of valid application
            variables see
            'nemoa.common.nappinfo.getdir'. Default is True
        expenv: determines if environmental path variables are expanded.
            For a full list of valid environmental path variables see
            'nemoa.common.npath'. Default is True

    Returns:
        String containing valid path syntax.

    Examples:
        >>> expand('%var1%/c', 'd', udict = {'var1': 'a/%var2%', 'var2': 'b'})
        'a\\b\\c\\d'

    """
    import os
    import sys

    from nemoa.common import nappinfo

    udict = udict or {}
    path = Path(join(*args))

    # create dictionary with variables
    d = {}
    if udict:
        for key, val in udict.items():
            d[key] = join(val)
    if expapp:
        appdirs = nappinfo.getdirs()
        for key, val in appdirs.items():
            d[key] = val
    if expenv:
        d['home'], d['cwd'] = home(), cwd()

    # itereratively expand variables in user dictionary
    update = True
    i = 0
    limit = sys.getrecursionlimit()
    while update:
        update = False
        for key, val in list(d.items()):
            if '%' + key + '%' not in str(path):
                continue
            try:
                path = Path(str(path).replace('%' + key + '%', val))
            except TypeError:
                del d[key]
            update = True
        i += 1
        if i > limit:
            raise RecursionError('cyclic dependency in variables detected')
        path = Path(path)

    # expand environmental paths
    if not expenv:
        return str(path)
    path = path.expanduser()
    path = Path(os.path.expandvars(path))

    return str(path)

def dirname(*args: NestPath) -> str:
    r"""Extract directory name from a path like structure.

    Args:
        *args: Path like arguments, respectively given by a tree of strings,
            which can be joined to a path.

    Returns:
        String containing normalized directory path of file.

    Examples:
        >>> dirname(('a', ('b', 'c'), 'd'), 'base.ext')
        'a\\b\\c\\d'

    """
    path = Path(expand(*args))
    if path.is_dir():
        return str(path)
    return str(path.parent)

def filename(*args: NestPath) -> str:
    """Extract file name from a path like structure.

    Args:
        *args: Path like arguments, respectively given by a tree of strings,
            which can be joined to a path.

    Returns:
        String containing normalized directory path of file.

    Examples:
        >>> filename(('a', ('b', 'c')), 'base.ext')
        'base.ext'

    """
    path = Path(expand(*args))
    if path.is_dir():
        return ''
    return str(path.name)

def basename(*args: NestPath) -> str:
    """Extract file basename from a path like structure.

    Args:
        *args: Path like arguments, respectively given by a tree of strings,
            which can be joined to a path.

    Returns:
        String containing basename of file.

    Examples:
        >>> filename(('a', ('b', 'c')), 'base.ext')
        'base'

    """
    path = Path(expand(*args))
    if path.is_dir():
        return ''
    return str(path.stem)

def fileext(*args: NestPath) -> str:
    """Fileextension of file.

    Args:
        *args: Path like arguments, respectively given by a tree of strings,
            which can be joined to a path.

    Returns:
        String containing fileextension of file.

    Examples:
        >>> fileext(('a', ('b', 'c')), 'base.ext')
        'ext'

    """
    path = Path(expand(*args))
    if path.is_dir():
        return ''
    return str(path.suffix).lstrip('.')

def isdir(path: NestPath) -> bool:
    """Determine if given path points to a directory.

    Wrapper function to pathlib.Path.is_file [1]

    Args:
        path: Path like structure, which is expandable to a valid path

    Returns:
        True if the path points to a regular file (or a symbolic link pointing
        to a regular file), False if it points to another kind of file.

    References:
        [1] https://docs.python.org/3/library/pathlib.html

    """
    return Path(expand(path)).is_dir()

def isfile(path: NestPath) -> bool:
    """Determine if given path points to a file.

    Wrapper function to pathlib.Path.is_file [1]

    Args:
        path: Path like structure, which is expandable to a valid path.

    Returns:
        True if the path points to a directory (or a symbolic link pointing
        to a directory), False if it points to another kind of file.

    References:
        [1] https://docs.python.org/3/library/pathlib.html

    """
    return Path(expand(path)).is_file()

def validfile(filepath: NestPath) -> OptStr:
    """Return normalized filepath, if file is valid.

    Args:
        filepath: Path like structure, which is expandable to a valid path.

    Returns:
        String containing absolute path to a file, if the file exists,
        otherwise None.

    """
    path = expand(filepath)
    if not Path(path).is_file():
        return None
    return str(path)

def cp(source: NestPath, target: NestPath) -> bool:
    """Copy sub directories from given source to destination directory.

    Args:
        source: Path like structure, which comprises the path of a source folder
        target: Path like structure, which comprises the path of a destination
            folder

    Returns:
        True if the operation was successful.

    """
    import shutil

    sdir, ddir = Path(expand(source)), Path(expand(target))

    for s in sdir.glob('*'):
        t = Path(ddir, basename(s))
        if t.exists():
            shutil.rmtree(str(t))
        try:
            shutil.copytree(str(s), str(t))
        except Exception as err:
            raise OSError("could not copy directory") from err

    return True

def mkdir(*args: NestPath) -> bool:
    """Create directory.

    Args:
        *args: Path like structure, which comprises the path of a new directory

    Returns:
        True if the directory already exists, or the operation was successful.

    """
    import os

    path = Path(expand(*args))
    if path.is_dir():
        return True

    try:
        os.makedirs(path)
    except Exception as err:
        raise OSError("could not create directory") from err

    return path.is_dir()

def rmdir(*args: NestPath) -> bool:
    """Remove directory.

    Args:
        *args: Path like structure, which identifies the path of a directory

    Returns:
        True if the directory could be deleted

    """
    import shutil

    path = Path(expand(*args))

    if not path.is_dir():
        return False
    shutil.rmtree(str(path), ignore_errors=True)

    return not path.exists()
