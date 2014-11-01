# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import nemoa.model.imports.archive
import os

def filetypes(filetype = None):
    """Get supported model import filetypes."""

    type_dict = {}

    # get supported archive filetypes
    archive_types = nemoa.model.imports.archive.filetypes()
    for key, val in archive_types.items():
        type_dict[key] = ('archive', val)

    if filetype == None:
        return {key: val[1] for key, val in type_dict.items()}
    if filetype in type_dict:
        return type_dict[filetype]

    return False

def load(path, filetype = None, workspace = None, **kwargs):
    """Import model from file."""

    # try if path exists or import given workspace and get path from
    # workspace or get path from current workspace
    if not os.path.isfile(path) and workspace:
        current_workspace = nemoa.workspace.name()
        if not workspace == current_workspace:
            if not nemoa.workspace.load(workspace):
                nemoa.log('error', """could not import model:
                    workspace '%s' does not exist""" % (workspace))
                return  {}
        config = nemoa.workspace.find('model', path)
        if not workspace == current_workspace and current_workspace:
            nemoa.workspace.load(current_workspace)
        if not isinstance(config, dict):
            nemoa.log('error', """could not import model:
                workspace '%s' does not contain a model '%s'."""
                % (workspace, path))
            return  {}
        if not 'path' in config:
            return {'config': config}
        path = config['path']
    if not os.path.isfile(path):
        config = nemoa.workspace.find('model', path)
        if not isinstance(config, dict):
            current_workspace = nemoa.workspace.name()
            if current_workspace:
                nemoa.log('error', """could not import model:
                    current workspace '%s' does not contain a model
                    '%s'.""" % (current_workspace, path))
            else:
                nemoa.log('error', """could not import model:
                    file '%s' does not exist.""" % (path))
            return  {}
        if not 'path' in config: return {'config': config}
        path = config['path']
    if not os.path.isfile(path):
        nemoa.log('error', """could not import model:
            file '%s' does not exist.""" % (path))
        return {}

    # if filetype is not given get filtype from file extension
    # and check if filetype is supported
    if not filetype:
        filetype = nemoa.common.get_file_extension(path).lower()
    if not filetype in filetypes().keys():
        return nemoa.log('error', """could not import model:
            filetype '%s' is not supported.""" % (filetype))

    # import and check dictionary
    module_name = filetypes(filetype)[0]
    if module_name == 'archive':
        model = nemoa.model.imports.archive.load(path, **kwargs)
    if not model:
        nemoa.log('error', """could not import model: file '%s' is
            not valid.""" % (path))
        return {}
    if not 'source' in model['config']:
        model['config']['source'] = {}
    model['config']['path'] = path
    model['config']['workspace'] = nemoa.workspace.name()
    model['config']['source']['file'] = path
    model['config']['source']['filetype'] = filetype

    return model
