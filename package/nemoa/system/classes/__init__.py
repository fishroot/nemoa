# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import nemoa.system.classes.base
import importlib

def new(*args, **kwargs):
    """Return new nemoa.system.classes.[package].[class] instance."""
    if not 'config' in kwargs: return None
    config = kwargs['config']
    module = importlib.import_module(
        'nemoa.system.classes.' + config['package'])
    if hasattr(module, config['class']):
        return getattr(module, config['class'])(*args, **kwargs)
    return None

#def new(*args, **kwargs):
    #"""Return model instance."""

    #if 'config' in kwargs and kwargs['config']:
        #config = kwargs['config']
    #else: config = {'type': 'base.Model'}
    #if not 'type' in config or not '.' in config['type']:
        #return nemoa.log('error', """could not create model:
            #model type is not given.""")

    #module_name = 'nemoa.model.classes.' + config['type'].split('.')[0]
    #class_name = config['type'].split('.')[1]

    #try:
        #module = importlib.import_module(module_name)
        #if not hasattr(module, class_name): raise ImportError()
        #model = getattr(module, class_name)(**kwargs)
    #except ImportError:
        #return nemoa.log('error', """could not create model:
            #unsupported model type '%s'.""" % (config['type']))

    #return model
