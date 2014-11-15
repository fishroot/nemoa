# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import nemoa
import networkx
import os

def filetypes():
    """Get supported graph description filetypes for network import."""
    return {
        'gml': 'Graph Modelling Language',
        'graphml': 'Graph Markup Language',
        'xml': 'Graph Markup Language',
        'dot': 'GraphViz DOT' }

def load(path, **kwargs):
    """Import network from graph description file."""

    # extract filetype from path
    filetype = nemoa.common.get_file_extension(path).lower()

    # test if filetype is supported
    if not filetype in filetypes():
        return nemoa.log('error', """could not import graph:
            filetype '%s' is not supported.""" % (filetype))

    if filetype == 'gml':
        return Gml(**kwargs).load(path)
    if filetype in ['graphml', 'xml']:
        return Graphml(**kwargs).load(path)
    if filetype == 'dot':
        return Dot(**kwargs).load(path)

    return False

def _graph_decode(graph):

    # no decoding
    if not 'coding' in graph.graph \
        or not graph.graph['coding'] \
        or graph.graph['coding'].lower() == 'none':
        return graph

    # base64 decoding
    elif graph.graph['coding'] == 'base64':
        graph.graph['params'] = \
            nemoa.common.dict_decode_base64(
            graph.graph['params'])

        for node in graph.nodes():
            graph.node[node]['params'] = \
                nemoa.common.dict_decode_base64(
                graph.node[node]['params'])

        for src, tgt in graph.edges():
            graph.edge[src][tgt]['params'] = \
                nemoa.common.dict_decode_base64(
                graph.edge[src][tgt]['params'])

        graph.graph['coding'] == 'none'
        return graph

    else:
        nemoa.log('error', """could not decode graph parameters:
            unsupported coding '%s'.""" % (coding))

    return {}

def _graph_to_dict(graph):
    return {
        'graph': graph.graph,
        'nodes': graph.nodes(data = True),
        'edges': networkx.to_dict_of_dicts(graph) }

class Graphml:
    """Import network from GraphML file."""

    settings = {}

    def __init__(self, **kwargs):
        for key, val in kwargs.items():
            if key in self.settings.keys():
                self.settings[key] = val

    def load(self, path):
        graph = networkx.read_graphml(path)
        graph = _graph_decode(graph)
        graph_dict = _graph_to_dict(graph)
        graph_dict = nemoa.common.dict_convert_string_keys(graph_dict)
        return {
            'config': graph_dict['graph']['params'],
            'graph': graph_dict }

class Gml:
    """Import network from GML file."""

    settings = {}

    def __init__(self, **kwargs):
        for key, val in kwargs.items():
            if key in self.settings.keys():
                self.settings[key] = val

    def load(self, path):
        graph = networkx.read_gml(path, relabel = True)
        graph = _graph_decode(graph)
        graph_dict = _graph_to_dict(graph)
        graph_dict = nemoa.common.dict_convert_string_keys(graph_dict)
        return {
            'config': graph_dict['graph']['params'],
            'graph': graph_dict }
