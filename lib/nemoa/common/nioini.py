# -*- coding: utf-8 -*-
"""I/O functions for INI files."""

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'
__docformat__ = 'google'

from configparser import ConfigParser
from io import TextIOWrapper

from nemoa.common import npath
from nemoa.types import (
    BinaryFile, Path, PathLike, OptBool, OptStr, OptStrDict2, StrDict2,
    TextFile, FileOrPathLike)

FILEEXTS = ['.ini', '.cfg']

def load(file: FileOrPathLike, structure: OptStrDict2 = None) -> StrDict2:
    """Import configuration dictionary from INI file.

    Args:
        file: String, Path or Filehandler that points to a valid INI File
        structure: Nested dictionary, which determines the structure of the
            configuration dictionary. If "structure" is None the INI File
            is completely imported and all values are interpreted as strings.
            If "structure" is a dictionary, only those sections and keys are
            imported, that match the structure dictionary. Thereby the sections
            and keys can be given as regular expressions to allow equally
            structured sections. Moreover the values are imported as the types,
            that are given in the structure dictionary, e.g. 'str', 'int' etc.

    Return:
        Structured configuration dictionary

    """
    # Initialize Configuration Parser
    parser = ConfigParser()
    setattr(parser, 'optionxform', lambda key: key)

    # Read configuration from file or path
    if isinstance(file, TextFile):
        parser.read_file(file)
    elif isinstance(file, BinaryFile):
        parser.read_file(TextIOWrapper(file))
    elif isinstance(file, (str, Path)):
        path = npath.getpath(file)
        if not npath.isfile(path):
            raise FileNotFoundError(
                "first argument 'file' is required to be of types 'str', "
                f"'Path' or 'File', not '{type(file)}'")
        parser.read(path)
    else:
        raise TypeError(
            "'file' is required to be of types 'str', 'Path' or 'File'"
            f", not '{type(file)}'")

    # parse sections and create configuration dictionary
    return parse(parser, structure=structure)

def save(
        d: dict, file: FileOrPathLike, flat: OptBool = None,
        header: OptStr = None) -> bool:
    """Save configuration dictionary to INI file.

    Args:
        d: Configuration dictionary
        file: String, Path or Filehandler that points to a writeable INI File.
        flat: Determines if the desired INI format structure contains sections.
            By default sections are used, if the dictionary contains
            subdictionaries.
        header: The Header string is written in the INI file as initial comment.
            By default no header is written.

    Return:
        Bool which is True if no error occured.

    """
    # Convert configuration dictionary to INI formated string
    try:
        text = dumps(d, flat=flat, header=header)
    except Exception as err:
        raise ValueError("dictionary is not valid") from err

    # Write INI formated string to file
    if isinstance(file, TextFile):
        file.write(text)
    elif isinstance(file, BinaryFile):
        file.write(bytes(text))
    elif isinstance(file, (str, Path)):
        path = npath.getpath(file)
        try:
            with open(path, 'w') as newfile:
                newfile.write(text)
        except IOError as err:
            raise IOError(f"file '{path}' can not be written") from err

    return True

def loads(
        string: str, structure: OptStrDict2 = None,
        flat: OptBool = None) -> StrDict2:
    """Load configuration dictionary from INI formated string.

    Args:
        string: INI formated string, that contains the configuration
        structure: Nested dictionary, that determines the structure
            of the configuration dictionary. If "structure" is None the INI File
            is completely imported and all values are interpreted as strings.
            If "structure" is a dictionary, only those sections and keys are
            imported, that match the structure dictionary. Thereby the sections
            and keys can be given as regular expressions to allow equally
            structured sections. Moreover the values are imported as the types,
            that are given in the structure dictionary, e.g. 'str', 'int' etc.
        flat: Determines if the desired INI format structure
            contains sections or not. By default sections are used, if the
            first non empty, non comment line in the string identifies a
            section.

    Return:
        Structured configuration dictionary

    """
    # If the existens of sections is not defined by the argument 'flat'
    # automatically determine the existence by the appearance of a line,
    # that starts with the character '['
    if flat is None:
        flat = True
        for line in [l.lstrip(' ') for l in string.split('\n')]:
            if not line or line.startswith('#'):
                continue
            flat = not line.startswith('[')
            break

    # If no sections are to be used create a temporary [root] section
    # and embed the structure dictionary within a 'root' key
    if flat:
        string = '\n'.join(['[root]', string])
        if isinstance(structure, dict):
            structure = {'root': structure.copy()}

    # Strip leading and trailing white spaces from lines in INI string
    string = '\n'.join([line.strip(' ') for line in string.split('\n')])

    # Parse sections and create dictionary
    parser = ConfigParser()
    parser.read_string(string)
    d = parse(parser, structure)

    # If no sections are to be used collapse the 'root' key
    if flat:
        return d.get('root') or {}

    return d

def dumps(d: dict, flat: OptBool = None, header: OptStr = None) -> str:
    """Convert configuration dictionary to INI formated string.

    Args:
        d: Configuration dictionary
        flat: Determines if the desired INI format structure
            contains sections or not. By default sections are used, if the
            dictionary contains subdictionaries.
        header: The Header string is written in the INI format
            string as an initial comment. By default no header is written.

    Return:
        String with INI File Structure

    """
    from io import StringIO

    # if the usage of sections is not explicitely given, use sections if
    # the dictionary contains subdictionaries
    if flat is None:
        flat = True
        for key, val in d.items():
            if not isinstance(val, dict):
                continue
            flat = False

    # if no sections are to be used create a temporary [root] section
    if flat:
        d = {'root': d.copy()}

    # succesively pass (key, value) pairs to INI parser
    parser = ConfigParser()
    for sec in d.keys():
        if not isinstance(d[sec], dict):
            continue
        parser.add_section(str(sec))
        for key, val in d[sec].items():
            parser.set(str(sec), str(key), str(val))

    # retrieve INI formated string from INI parser
    with StringIO() as buffer:
        parser.write(buffer)
        string = buffer.getvalue()

    # if no section are to be used remove [root] section from string
    if flat:
        string = string.replace('[root]\n', '')

    # if header is given, write header as comment before string
    if isinstance(header, str):
        hstring = '\n'.join(['# ' + l.strip() for l in header.split('\n')])
        string = hstring + '\n\n' + string

    return string

def getheader(filepath: PathLike) -> str:
    """Get header from INI file.

    Args:
        filepath: Filepath that points to a valid INI file.

    Returns:
        String containing header of INI file or empty string if header
        could not be detected.

    """
    # Validate filepath
    path = npath.validfile(filepath)
    if not path:
        raise TypeError(f"file '{str(filepath)}' does not exist")

    # Scan INI file for header
    hlist = []
    with open(path, 'r') as file:
        for line in [l.lstrip(' ') for l in file]:
            if not line:
                continue
            if line.startswith('#'):
                hlist.append(line[1:].lstrip())
                continue
            break

    # join lines and strip header
    return ''.join(hlist).strip()

def parse(parser: ConfigParser, structure: OptStrDict2 = None) -> StrDict2:
    """Import configuration dictionary from INI formated string.

    Args:
        parser: ConfigParser instance that contains an unstructured
            configuration dictionary
        structure: Nested dictionary, which determines the structure of the
            configuration dictionary. If "structure" is None the INI File
            is completely imported and all values are interpreted as strings.
            If "structure" is a dictionary, only those sections and keys are
            imported, that match the structure dictionary. Thereby the sections
            and keys can be given as regular expressions to allow equally
            structured sections. Moreover the values are imported as the types,
            that are given in the structure dictionary, e.g. 'str', 'int' etc.

    Return:
        Structured configuration dictionary

    """
    import re
    from nemoa.common import ntext

    # if no structure is given retrieve dictionary from INI parser
    if not isinstance(structure, dict):
        d = {}
        for sec in parser.sections():
            d[sec] = {key: parser.get(sec, key) for key in parser.options(sec)}
        return d

    # if structure is given use regular expression to match sections and keys
    d = {}
    rsecs = {key: re.compile(r'\A' + str(key)) for key in structure.keys()}
    for sec in parser.sections():

        # use regular expression to match sections
        rsec = None
        for key in structure.keys():
            if not rsecs[key].match(sec):
                continue
            rsec = key
            break
        if not rsec:
            continue

        # use regular expression to match keys
        dsec = {}
        for regexkey, fmt in getattr(structure[rsec], 'items')():
            rekey = re.compile(regexkey)
            for key in parser.options(sec):
                if not rekey.match(key):
                    continue
                val = parser.get(sec, key)
                dsec[key] = ntext.astype(val, fmt)

        d[sec] = dsec

    return d