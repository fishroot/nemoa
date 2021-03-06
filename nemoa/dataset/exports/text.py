# -*- coding: utf-8 -*-

__author__ = 'Patrick Michl'
__email__ = 'frootlab@gmail.com'
__license__ = 'GPLv3'

import nemoa
import os

def filetypes():
    """Get supported text filetypes for dataset export."""
    return {
        'csv': 'Comma Separated Values',
        'tsv': 'Tab Separated Values',
        'tab': 'Tab Separated Values'}

def save(dataset, path, filetype, **kwds):
    """Export dataset to archive file."""

    # test if filetype is supported
    if filetype not in filetypes():
        raise ValueError(f"filetype '{filetype}' is not supported")

    # create path if not available
    if not os.path.exists(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))

    if filetype == 'csv':
        return Csv(**kwds).save(dataset, path)
    if filetype in ['tsv', 'tab']:
        return Tsv(**kwds).save(dataset, path)

    return False

class Csv:
    """Export dataset to Comma Separated Values."""

    settings = None
    default = {'delim': ','}

    def __init__(self, **kwds):
        self.settings = {**self.default, **kwds}

    def save(self, dataset, path):

        from nemoa.file import csvfile, inifile

        # Create the configuration which is included in the CSV file
        # as initial comment lines
        keys = ['name', 'branch', 'version', 'about', 'author', 'email',
            'license', 'filetype', 'application', 'preprocessing',
            'type', 'labelformat']
        config = {}
        for key, val in dataset.get('config').items():
            if key in keys: config[key] = val

        # prepare CSV parameters and write CSV file
        comment = inifile.encode(config, flat=True).strip('\n')
        delim = self.settings['delim']
        cols, data = dataset.get('data', output=('cols', 'recarray'))

        return csvfile.save(path, data, comment=comment, delim=delim,
            labels=[''] + cols)

class Tsv(Csv):
    """Export dataset to Tab Separated Values."""

    default = { 'delim': '\t' }
