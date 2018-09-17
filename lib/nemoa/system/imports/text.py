# -*- coding: utf-8 -*-

__author__ = 'Patrick Michl'
__email__ = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import nemoa
import os

def filetypes():
    """Get supported text filetypes for system import."""
    return {
        'ini': 'Nemoa System Description',
        'txt': 'Nemoa System Description'}

def load(path, **kwargs):
    """Import system from text file."""

    from nemoa.common import npath

    # extract filetype from path
    filetype = npath.fileext(path).lower()

    # test if filetype is supported
    if filetype not in filetypes():
        raise ValueError("""could not import graph:
            filetype '%s' is not supported.""" % (filetype))

    if filetype in ['ini', 'txt']:
        return Ini(**kwargs).load(path)

    return False

class Ini:
    """Import system configuration from ini file."""

    settings = None
    default = {}

    def __init__(self, **kwargs):
        from nemoa.common import ndict
        self.settings = ndict.merge(kwargs, self.default)

    def load(self, path):
        """Return system configuration as dictionary.

        Args:
            path: configuration file used to generate system
                configuration dictionary.

        """

        from nemoa.common import nini, npath

        # import ini file to dictionary, using ini file structure
        # described with regular expressions
        system = nini.load(path, {
            'system': {
                'name': 'str',
                'type': 'str' },
            'schedule [.0-9a-zA-Z]*': {
                'system [.0-9a-zA-Z]*': 'dict' }})

        if not system \
            or not 'system' in system \
            or not 'type' in system['system']:
            raise ValueError("""could not import system:
                configuration file '%s' is not valid.""" % (path))

        config = system['system'].copy()

        # update / set name
        if 'name' not in config: config['name'] = npath.basename(path)

        # update / set optimization schedules
        schedules = {}
        for key in system:
            if key[:8].lower() != 'schedule': continue
            name = key[9:]
            schedules[name] = { 'name': name }
            for syskey in system[key]:
                if syskey[:6].lower() != 'system': continue
                systype = syskey[7:]
                schedules[name][systype] = system[key][syskey].copy()

        config['schedules'] = schedules

        return { 'config': config }
