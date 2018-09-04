# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import nemoa
import numpy
import os

def filetypes():
    """Get supported archive filetypes for model export."""
    return {
        'npz': 'Numpy Zipped Archive' }

def save(model, path, filetype, **kwargs):
    """Export model to archive file."""

    # test if filetype is supported
    if filetype not in filetypes():
        raise ValueError(f"filetype '{filetype}' is not supported")

    copy = model.get('copy')
    return Npz(**kwargs).save(copy, path)

class Npz:
    """Export model to numpy zipped archive."""

    settings = None
    default = { 'compress': True }

    def __init__(self, **kwargs):
        from nemoa.common import ndict
        self.settings = ndict.merge(kwargs, self.default)

    def save(self, copy, path):

        # create path if not available
        if not os.path.exists(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path))

        if self.settings['compress']:
            numpy.savez_compressed(path, **copy)
        else:
            numpy.savez(path, **copy)

        return path
