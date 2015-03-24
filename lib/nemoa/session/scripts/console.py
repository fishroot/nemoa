# -*- coding: utf-8 -*-
"""nemoa console commands."""

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import nemoa

def about(*args, **kwargs):
    """Wrapping function to nemoa.about()."""
    nemoa.log('note', nemoa.about(*args, **kwargs))
    return None

def create(type = None, *args, **kwargs):
    """ """
    if type == 'model': return nemoa.model.create(*args, **kwargs)
    if type == 'network': return nemoa.model.network(*args, **kwargs)
    if type == 'dataset': return nemoa.model.dataset(*args, **kwargs)
    if type == 'system': return nemoa.model.system(*args, **kwargs)
    return None

def get(*args, **kwargs):
    """Wrapping function to nemoa.get()."""
    nemoa.log('note', nemoa.get(*args, **kwargs))
    return None

def list(*args, **kwargs):
    """Wrapping function to nemoa.list()."""
    retval = nemoa.list(*args, **kwargs)
    if isinstance(retval, dict):
        for key, val in retval.items():
            if not val: continue
            if hasattr(val, '__iter__'):
                nemoa.log('note', '%s: %s' % (key, ', '.join(val)))
            else:
                nemoa.log('note', '%s: %s' % (key, val))
    elif hasattr(retval, '__iter__'):
        nemoa.log('note', ', '.join(retval))

    return None

def open(key = None, *args, **kwargs):
    """Wrapping function to nemoa.open()."""
    if not key: return None
    if not args: nemoa.open(key)
    elif len(args) == 1:
        if key == 'model':
            return nemoa.model.open(args[0], **kwargs)
        if key == 'dataset':
            return nemoa.dataset.open(args[0], **kwargs)
        if key == 'network':
            return nemoa.network.open(args[0], **kwargs)
        if key == 'system':
            return nemoa.system.open(args[0], **kwargs)
        if key == 'workspace': nemoa.open(args[0])
    return None

def path(*args, **kwargs):
    """Wrapping function to nemoa.path()."""
    nemoa.log('note', nemoa.path(*args, **kwargs))
    return None

def run(*args, **kwargs):
    """Wrapping function to nemoa.run()."""
    nemoa.run(*args, **kwargs)
    return None

def show(*args, **kwargs):
    """ """
    return open(*args, **kwargs).show()

def set(*args, **kwargs):
    """Wrapping function to nemoa.set()."""
    nemoa.set(*args, **kwargs)
    return None