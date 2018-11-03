# -*- coding: utf-8 -*-
"""Session management.

This module implements session management by a singleton design pattern.

.. References:
.. _file-like object:
    https://docs.python.org/3/glossary.html#term-file-like-object
.. _path-like object:
    https://docs.python.org/3/glossary.html#term-path-like-object

"""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

from pathlib import Path
from nemoa.base import npath
from nemoa.core import log
from nemoa.base.container import ContentAttr, DCMContainer
from nemoa.base.container import TechAttr, VirtualAttr, TransientAttr
from nemoa.base.file import inifile, wsfile
from nemoa.types import (
    Any, BytesLike, CManFileLike, ClassVar, Exc, ExcType, OptBytes, OptPath,
    OptPathLike, OptStr, PathLike, StrDict, StrDict2, StrList, StrOrInt,
    Traceback)

class Session(DCMContainer):
    """Session."""

    #
    # Private Class Variables
    #

    _config_file_path: ClassVar[str] = '%user_config_dir%/nemoa.ini'
    _config_file_struct: ClassVar[StrDict2] = {
        'session': {
            'path': 'path',
            'restore_on_startup': 'bool',
            'autosave_on_exit': 'bool'}}
    _default_config: ClassVar[StrDict] = {
        'path': None,
        'restore_on_startup': False,
        'autosave_on_exit': False}
    _default_paths: StrList = [
        '%user_data_dir%', '%site_data_dir%', '%package_data_dir%']

    #
    # Content Attributes
    #

    workspace: property = ContentAttr(wsfile.WsFile)

    #
    # Metadata Attributes
    #

    config: property = TechAttr(dict)
    config.__doc__ = """Session configuration."""

    paths: property = TechAttr(list)
    paths.__doc__ = """Search paths for workspaces."""

    #
    # Virtual Attributes
    #

    files: property = VirtualAttr(list, getter='_get_files', readonly=True)
    files.__doc__ = """Files within the current workspace."""

    folders: property = VirtualAttr(list, getter='_get_folders', readonly=True)
    folders.__doc__ = """Folders within the current workspace."""

    path: property = VirtualAttr(Path, getter='_get_path', readonly=True)
    path.__doc__ = """Filepath of the current workspace."""

    #
    # Transient Attributes
    #

    logger: property = TransientAttr(log.Logger)
    logger.__doc__ = """Logger instance."""

    #
    # Magic
    #

    def __init__(
            self, workspace: OptPathLike = None, basedir: OptPathLike = None,
            pwd: OptBytes = None) -> None:
        """Initialize instance variables and load workspace from file."""
        super().__init__()

        # Initialize instance variables with default values
        self.config = self._default_config.copy()
        self.workspace = wsfile.WsFile()
        self.paths = [npath.expand(path) for path in self._default_paths]
        self.logger = log.get_instance()

        # Bind session to workspace
        self.parent = self.workspace

        # Load session configuration from file
        if npath.is_file(self._config_file_path):
            self._load_config()

        # Load workspace from file
        filepath: OptPath = None
        if workspace and isinstance(workspace, (Path, str)):
            filepath = Path(workspace)
        elif self.config.get('restore_on_startup'):
            cfg_path = self.config.get('path')
            if isinstance(cfg_path, (Path, str)):
                filepath = Path(cfg_path)
        if isinstance(filepath, Path):
            self.load(workspace=filepath, basedir=basedir, pwd=pwd)

    def __enter__(self) -> 'Session':
        """Enter with statement."""
        return self

    def __exit__(self, Error: ExcType, value: Exc, tb: Traceback) -> None:
        """Exit with statement."""
        self.close() # Close Workspace
        self._save_config() # Save config

    def __del__(self) -> None:
        """Run destructor for instance."""

    #
    # Public Methods
    #

    def load(
            self, workspace: OptPathLike = None, basedir: OptPathLike = None,
            pwd: OptBytes = None) -> None:
        """Load Workspace from file.

        Args:
            workspace:
            basedir:
            pwd: Bytes representing password of workspace file.

        """
        path = self._locate_path(workspace=workspace, basedir=basedir)
        self.workspace = wsfile.WsFile(filepath=path, pwd=pwd)
        self.parent = self.workspace

    def save(self) -> None:
        """Save Workspace to current file."""
        self.workspace.save()

    def saveas(self, filepath: PathLike) -> None:
        """Save the workspace to a file.

        Args:
            filepath: String or `path-like object`_, that represents the name of
                a workspace file.

        """
        self.workspace.saveas(filepath)

    def close(self) -> None:
        """Close current workspace."""
        if self.config.get('autosave_on_exit') and self.workspace.changed:
            self.save()
        if hasattr(self.workspace, 'close'):
            self.workspace.close()

    def open(
            self, filepath: PathLike, workspace: OptPathLike = None,
            basedir: OptPathLike = None, pwd: OptBytes = None, mode: str = '',
            encoding: OptStr = None, is_dir: bool = False) -> CManFileLike:
        """Open file within current or given workspace.

        Args:
            filepath: String or `path-like object`_, that represents a workspace
                member. In reading mode the path has to point to a valid
                workspace file, or a FileNotFoundError is raised. In writing
                mode the path by default is treated as a file path. New
                directories can be written by setting the argument is_dir to
                True.
            workspace:
            basedir:
            mode: String, which characters specify the mode in which the file is
                to be opened. The default mode is reading in text mode. Suported
                characters are:
                'r': Reading mode (default)
                'w': Writing mode
                'b': Binary mode
                't': Text mode (default)
            encoding: In binary mode encoding has not effect. In text mode
                encoding specifies the name of the encoding, which in reading
                and writing mode respectively is used to decode the stream’s
                bytes into strings, and to encode strings into bytes. By default
                the preferred encoding of the operating system is used.
            is_dir: Boolean value which determines, if the path is to be treated
                as a directory or not. This information is required for writing
                directories to the workspace. The default behaviour is not to
                treat paths as directories.

        Returns:
            Context manager for `file-like object`_ in reading or writing mode.

        """
        if workspace:
            path = self._locate_path(workspace=workspace, basedir=basedir)
            ws = wsfile.WsFile(filepath=path, pwd=pwd)
            return ws.open(
                filepath, mode=mode, encoding=encoding, is_dir=is_dir)
        return self.workspace.open(
            filepath, mode=mode, encoding=encoding, is_dir=is_dir)

    def append(self, source: PathLike, target: OptPathLike = None) -> bool:
        """Append file to the current workspace.

        Args:
            source: String or `path-like object`_, that points to a valid file
                in the directory structure if the system. If the file does not
                exist, a FileNotFoundError is raised. If the filepath points to
                a directory, a IsADirectoryError is raised.
            target: String or `path-like object`_, that points to a valid
                directory in the directory structure of the workspace. By
                default the root directory is used. If the directory does not
                exist, a FileNotFoundError is raised. If the target directory
                already contains a file, which name equals the filename of the
                source, a FileExistsError is raised.

        Returns:
            Boolean value which is True if the file has been appended.

        """
        return self.workspace.append(source, target=target)

    def unlink(self, filepath: PathLike, ignore_missing: bool = True) -> bool:
        """Remove file from the current workspace.

        Args:
            filepath: String or `path-like object`_, that points to a file in
                the directory structure of the workspace. If the filapath points
                to a directory, an IsADirectoryError is raised. For the case,
                that the file does not exist, the argument ignore_missing
                determines, if a FileNotFoundError is raised.
            ignore_missing: Boolean value which determines, if FileNotFoundError
                is raised, if the target file does not exist. The default
                behaviour, is to ignore missing files.

        Returns:
            Boolean value, which is True if the given file was removed.

        """
        return self.workspace.unlink(filepath, ignore_missing=ignore_missing)

    def mkdir(self, dirpath: PathLike, ignore_exists: bool = False) -> bool:
        """Create a new directory in current workspace.

        Args:
            dirpath: String or `path-like object`_, that represents a valid
                directory name in the directory structure of the workspace. If
                the directory already exists, the argument ignore_exists
                determines, if a FileExistsError is raised.
            ignore_exists: Boolean value which determines, if FileExistsError is
                raised, if the target directory already exists. The default
                behaviour is to raise an error, if the file already exists.

        Returns:
            Boolean value, which is True if the given directory was created.

        """
        return self.workspace.mkdir(dirpath, ignore_exists=ignore_exists)

    def rmdir(
            self, dirpath: PathLike, recursive: bool = False,
            ignore_missing: bool = False) -> bool:
        """Remove directory from current workspace.

        Args:
            dirpath: String or `path-like object`_, that points to a directory
                in the directory structure of the workspace. If the directory
                does not exist, the argument ignore_missing determines, if a
                FileNotFoundError is raised.
            ignore_missing: Boolean value which determines, if FileNotFoundError
                is raised, if the target directory does not exist. The default
                behaviour, is to raise an error if the directory is missing.
            recursive: Boolean value which determines, if directories are
                removed recursively. If recursive is False, then only empty
                directories can be removed. If recursive, however, is True, then
                all files and subdirectories are alse removed. By default
                recursive is False.

        Returns:
            Boolean value, which is True if the given directory was removed.

        """
        return self.workspace.rmdir(
            dirpath, recursive=recursive, ignore_missing=ignore_missing)

    def search(self, pattern: OptStr = None) -> StrList:
        """Search for files in the current workspace.

        Args:
            pattern: Search pattern that contains Unix shell-style wildcards:
                '*': Matches arbitrary strings
                '?': Matches single characters
                [seq]: Matches any character in seq
                [!seq]: Matches any character not in seq
                By default a list of all files and directories is returned.

        Returns:
            List of files and directories in the directory structure of the
            workspace, that match the search pattern.

        """
        return self.workspace.search(pattern)

    def copy(self, source: PathLike, target: PathLike) -> bool:
        """Copy file within current workspace.

        Args:
            source: String or `path-like object`_, that points to a file in the
                directory structure of the workspace. If the file does not
                exist, a FileNotFoundError is raised. If the filepath points to
                a directory, an IsADirectoryError is raised.
            target: String or `path-like object`_, that points to a new filename
                or an existing directory in the directory structure of the
                workspace. If the target is a directory the target file consists
                of the directory and the basename of the source file. If the
                target file already exists a FileExistsError is raised.

        Returns:
            Boolean value which is True if the file was copied.

        """
        return self.workspace.copy(source, target)

    def move(self, source: PathLike, target: PathLike) -> bool:
        """Move file within current workspace.

        Args:
            source: String or `path-like object`_, that points to a file in the
                directory structure of the workspace. If the file does not
                exist, a FileNotFoundError is raised. If the filepath points to
                a directory, an IsADirectoryError is raised.
            target: String or `path-like object`_, that points to a new filename
                or an existing directory in the directory structure of the
                workspace. If the target is a directory the target file consists
                of the directory and the basename of the source file. If the
                target file already exists a FileExistsError is raised.

        Returns:
            Boolean value which is True if the file has been moved.

        """
        return self.workspace.move(source, target)

    def read_text(self, filepath: PathLike, encoding: OptStr = None) -> str:
        """Read text from file in current workspace.

        Args:
            filepath: String or `path-like object`_, that points to a valid file
                in the directory structure of the workspace. If the file does
                not exist a FileNotFoundError is raised.
            encoding: Specifies the name of the encoding, which is used to
                decode the stream’s bytes into strings. By default the preferred
                encoding of the operating system is used.

        Returns:
            Contents of the given filepath encoded as string.

        """
        return self.workspace.read_text(filepath, encoding=encoding)

    def read_bytes(self, filepath: PathLike) -> bytes:
        """Read bytes from file in current workspace.

        Args:
            filepath: String or `path-like object`_, that points to a valid file
                in the dirctory structure of the workspace. If the file does not
                exist a FileNotFoundError is raised.

        Returns:
            Contents of the given filepath as bytes.

        """
        return self.workspace.read_bytes(filepath)

    def write_text(
            self, text: str, filepath: PathLike,
            encoding: OptStr = None) -> int:
        """Write text to file.

        Args:
            text: String, which has to be written to the given file.
            filepath: String or `path-like object`_, that represents a valid
                filename in the dirctory structure of the workspace.
            encoding: Specifies the name of the encoding, which is used to
                encode strings into bytes. By default the preferred encoding of
                the operating system is used.

        Returns:
            Number of characters, that are written to the file.

        """
        return self.workspace.write_text(text, filepath, encoding=encoding)

    def write_bytes(self, data: BytesLike, filepath: PathLike) -> int:
        """Write bytes to file.

        Args:
            data: Bytes, which are to be written to the given file.
            filepath: String or `path-like object`_, that represents a valid
                filename in the dirctory structure of the workspace.

        Returns:
            Number of bytes, that are written to the file.

        """
        return self.workspace.write_bytes(data, filepath)

    def log(self, level: StrOrInt, msg: str, *args: Any, **kwds: Any) -> None:
        """Log event.

        Args:
            level: Integer value or string, which describes the severity of the
                event. Ordered by ascending severity, the allowed level names
                are: 'DEBUG', 'INFO', 'WARNING', 'ERROR' and 'CRITICAL'. The
                respectively corresponding level numbers are 10, 20, 30, 40 and
                50.
            msg: Message ``format string``_, which may can contain literal text
                or replacement fields delimited by braces. Each replacement
                field contains either the numeric index of a positional
                argument, given by *args, or the name of a keyword argument,
                given by the keyword *extra*.
            *args: Arguments, which can be used by the message format string.
            **kwds: Additional Keywords, used by the function `Logger.log()`_.

        """
        self.logger.log(level, msg, *args, **kwds)

    #
    # Private Methods
    #

    def _load_config(self) -> None:
        config = inifile.load(self._config_file_path, self._config_file_struct)
        if 'session' in config and isinstance(config['session'], dict):
            for key, val in config['session'].items():
                self.config[key] = val

    def _save_config(self) -> None:
        config = {'session': self.config}
        inifile.save(config, self._config_file_path)

    def _get_path(self) -> OptPath:
        return self.workspace.path

    def _get_files(self) -> StrList:
        return self.workspace.search()

    def _get_folders(self) -> StrList:
        return self.workspace.folders

    def _locate_path(
            self, workspace: OptPathLike = None,
            basedir: OptPathLike = None) -> OptPath:
        if not workspace:
            return None
        if not basedir:
            # If workspace is a fully qualified file path in the directory
            # structure of the system, ignore the 'paths' list
            if npath.is_file(workspace):
                return npath.expand(workspace)
            # Use the 'paths' list to find a workspace
            for path in self.paths:
                candidate = Path(path, workspace)
                if candidate.is_file():
                    return candidate
            raise FileNotFoundError(
                f"file {workspace} does not exist")
        return Path(basedir, workspace)

# from nemoa.types import Any
#
# def cur():
#     """Get current session instance."""
#     if '_cur' not in globals():
#         globals()['_cur'] = new()
#     return globals()['_cur']
#
# def get(*args: Any, **kwds: Any) -> Any:
#     """Get meta information and content from current session."""
#     return cur().get(*args, **kwds)
#
# def log(*args, **kwds):
#     """Log message in current session."""
#     return cur().log(*args, **kwds)
#
# def new(*args, **kwds):
#     """Create session instance from session dictionary."""
#     from nemoa.session import classes
#     return classes.new(*args, **kwds)
#
# def open(*args, **kwds):
#     """Open object in current session."""
#     return cur().open(*args, **kwds)
#
# def path(*args: Any, **kwds: Any) -> str:
#     """Get path for given object in current session."""
#     return cur().path(*args, **kwds)
#
# def run(*args, **kwds):
#     """Run script in current session."""
#     return cur().run(*args, **kwds)
#
# def set(*args, **kwds):
#     """Set configuration parameter and env var in current session."""
#     return cur().set(*args, **kwds)
