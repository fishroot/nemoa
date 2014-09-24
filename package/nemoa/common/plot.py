# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import nemoa
import numpy
import networkx
import matplotlib
import matplotlib.pyplot
from matplotlib.patches import FancyArrowPatch, Circle

COLOR = {
    'black':      (0.   , 0.   , 0.   , 1.),
    'white':      (1.   , 1.   , 1.   , 1.),
    'red':        (1.   , 0.   , 0.   , 1.),
    'green':      (0.   , 0.5  , 0.   , 1.),
    'blue':       (0.   , 0.0  , 0.7  , 1.),
    'lightgrey':  (0.8  , 0.8  , 0.8  , 1.),
    'lightgreen': (0.6  , 0.8  , 0.196, 1.),
    'lightblue':  (0.439, 0.502, 0.565, 1.),
    'cornflower': (0.27 , 0.51 , 0.7  , 1.),
}

# create A4 figure object figsize = (8.27, 11.69)

def heatmap(array, **kwargs):

    # create figure object
    fig = matplotlib.pyplot.figure()
    fig.patch.set_facecolor(kwargs['backgroundColor'])
    ax = fig.add_subplot(111)
    ax.grid(True)

    # create heatmap
    cax = ax.imshow(array,
        cmap = matplotlib.cm.hot_r,
        interpolation = kwargs['interpolation'],
        extent = (0, array.shape[1], 0, array.shape[0]))

    # create labels for axis
    maxFontSize = 12.
    yLabels = [nemoa.common.strToUnitStr(label.split(':')[1]) \
        for label in kwargs['units'][0]]
    xLabels = [nemoa.common.strToUnitStr(label.split(':')[1]) \
        for label in kwargs['units'][1]]
    fontsize = min(maxFontSize, \
        400. / float(max(len(xLabels), len(yLabels))))
    matplotlib.pyplot.xticks(
        numpy.arange(len(xLabels)) + 0.5,
        tuple(xLabels), fontsize = fontsize, rotation = 65)
    matplotlib.pyplot.yticks(
        len(yLabels) - numpy.arange(len(yLabels)) - 0.5,
        tuple(yLabels), fontsize = fontsize)

    # create colorbar
    cbar = fig.colorbar(cax)
    for tick in cbar.ax.get_yticklabels(): tick.set_fontsize(9)

    return True

def histogram(array, **kwargs):

    # create figure object
    fig = matplotlib.pyplot.figure()
    fig.patch.set_facecolor(kwargs['backgroundColor'])
    ax = fig.add_subplot(111)
    ax.grid(True)

    # create histogram
    cax = ax.hist(array,
        normed    = False,
        bins      = kwargs['bins'],
        facecolor = kwargs['facecolor'],
        histtype  = kwargs['histtype'],
        linewidth = kwargs['linewidth'],
        edgecolor = kwargs['edgecolor'])

    return True

def graph(graph, **kwargs):

    nodeSizeMax      = 800.  # maximum node size
    nodeSizeScale    = 1.85  # node size scale factor
    fontSizeMax      = 18.   # maximum font size
    edgeLineWidthMax = 10.   # maximum edge line with
    edgeArrScale     = 8.    # edge arrow size scale factor
    edgeRadius       = 0.15  # edge radius for fancy edges

    # create figure object
    fig = matplotlib.pyplot.figure()
    fig.patch.set_facecolor(kwargs['backgroundColor'])
    ax = fig.add_subplot(111)
    ax.axis('off')
    matplotlib.pyplot.axes().set_aspect('equal', 'box')

    # calculate positions
    if kwargs['layout'] == 'random':
        pos = networkx.random_layout(graph)
    elif kwargs['layout'] == 'circular':
        pos = networkx.circular_layout(graph)
    elif kwargs['layout'] == 'shell':
        pos = networkx.shell_layout(graph)
    elif kwargs['layout'] == 'spring':
        pos = networkx.spring_layout(graph)
    elif kwargs['layout'] == 'fruchterman_reingold':
        pos = networkx.fruchterman_reingold_layout(graph)
    elif kwargs['layout'] == 'spectral':
        pos = networkx.spectral_layout(graph)
    else:
        # warning unknown layout -> using spring
        pos = networkx.spring_layout(graph)

    # calculate sizes of nodes, fonts and lines depending on graph size
    nCount = float(len(graph))
    nSize = max(nodeSizeMax, nodeSizeScale * nodeSizeMax / nCount)
    nRadius = numpy.sqrt(nSize) / 480.
    fSize = fontSizeMax * numpy.sqrt(nSize / nodeSizeMax)
    nodeFontSizeMax = fSize * 0.9
    lineWidth = 2. / nCount
    edgeLineWidth = edgeLineWidthMax / nCount

    # draw nodes
    for node, attr in graph.nodes(data = True):
        label = attr['label']

        # calculate node fontsize depending on label
        clLabel = label.replace('{', '').replace('}', '')
        if '_' in clLabel: lenLabel = len('_'.split(clLabel)[0]) \
            + 0.5 * len('_'.split(clLabel)[0])
        else: lenLabel = len(clLabel)
        nodeFontSize = nodeFontSizeMax / numpy.sqrt(lenLabel)

        # set backcolor (depending on type) and facecolor
        backcolor = COLOR[attr['color']]
        facecolor = COLOR['black']

        # draw node and node label
        networkx.draw_networkx_nodes(graph, pos,
            node_size   = nSize,
            linewidths  = lineWidth,
            nodelist    = [node],
            node_shape  = 'o',
            node_color  = backcolor)
        networkx.draw_networkx_labels(graph, pos,
            font_size   = nodeFontSize,
            labels      = {node: label},
            font_color  = facecolor,
            font_weight = 'normal')

        # patch node for edges
        c = Circle(pos[node], radius = nRadius, alpha  = 0.)
        ax.add_patch(c)
        graph.node[node]['patch'] = c

    # draw edges using 'fancy arrows'
    seen = {}
    for (u, v, attr) in graph.edges(data = True):
        n1  = graph.node[u]['patch']
        n2  = graph.node[v]['patch']
        rad = edgeRadius
        linewidth = edgeLineWidth * attr['weight']
        linecolor = list(COLOR[attr['color']])

        if (u, v) in seen:
            rad = seen.get((u, v))
            rad = -(rad + float(numpy.sign(rad)) * 0.2)

        arrow = matplotlib.patches.FancyArrowPatch(
            posA            = n1.center,
            posB            = n2.center,
            patchA          = n1,
            patchB          = n2,
            arrowstyle      = '-|>',
            connectionstyle = 'arc3,rad=%s' % rad,
            mutation_scale  = edgeArrScale,
            linewidth       = linewidth,
            color           = linecolor)

        seen[(u, v)] = rad
        ax.add_patch(arrow)

    return True

def layergraph(G, **kwargs):

    # create node stack (list with lists of nodes)
    layers = G.graph['params']['layer']
    count = {layer: 0 for layer in layers}
    for node in G.nodes(): count[G.node[node]['params']['type']] += 1
    nodes = [range(count[layer]) for layer in layers]
    for node in G.nodes():
        layerId = G.node[node]['params']['layerId']
        layerNodeId = G.node[node]['params']['layerNodeId']
        nodes[layerId][layerNodeId] = node

    # (optional) sort nodes
    if kwargs['nodeSort']:
        for layer, tgtNodes in enumerate(nodes):
            if layer == 0: continue
            sort = []
            for tgtId, tgtNode in enumerate(tgtNodes):
                sortOrder = 0.
                for srcId, srcNode in enumerate(nodes[layer - 1]):
                    if (srcNode, tgtNode) in G.edges():
                        weight = G.edge[srcNode][tgtNode]['weight']
                    elif (tgtNode, srcNode) in G.edges():
                        weight = G.edge[tgtNode][srcNode]['weight']
                    else: weight = 0.
                    sortOrder += float(srcId) * numpy.abs(weight)
                sort.append((sortOrder, tgtNode))
            nodes[layer] = [srcNode[1] for srcNode in \
                sorted(sort, key = lambda x: x[0])]

    # calculate sizes
    nLen  = max([len(layer) for layer in nodes])
    lLen  = len(nodes)
    scale = min(240. / nLen, 150. / lLen, 35.)
    graphNodeSize   = 0.9 * scale ** 2
    graphFontSize   = 0.4 * scale
    graphCaptionPos = -0.0025 * scale
    graphLineWidth  = 0.3

    # calculate node positions for layer graph layout
    pos = {}
    posCap = {}
    for lId, layer in enumerate(nodes):
        for nId, node in enumerate(layer):
            nPos = (nId + 0.5) / len(layer)
            lPos = 1. - lId / (len(nodes) - 1.)
            pos[node] = {
                'down': (nPos, lPos),
                'up': (nPos, 1. - lPos),
                'left': (lPos, nPos),
                'right': (1. - lPos, nPos)}[kwargs['graphDirection']]
            posCap[node] = (pos[node][0], pos[node][1] + graphCaptionPos)

    # create figure and axis objects
    fig = matplotlib.pyplot.figure()
    fig.patch.set_facecolor(kwargs['backgroundColor'])
    ax = fig.add_subplot(111)
    ax.axis('off')
    ax.autoscale()

    # draw labeled nodes
    for layer in nodes:
        for node in layer:
            attr = G.node[node]
            type = attr['params']['type']
            typeid = attr['params']['layerId']
            isVisible = attr['params']['visible']
            labelStr = attr['label'] if isVisible \
                else 'n%d' % (layer.index(node) + 1)
            label = nemoa.common.strToUnitStr(labelStr)

            color = {
                True: {
                    'bg': COLOR['cornflower'],
                    'font': COLOR['black'] },
                False: {
                    'bg': COLOR['lightgrey'],
                    'font': COLOR['black'] }
            }[isVisible]

            # draw node
            networkx.draw_networkx_nodes(G, pos,
                node_size  = graphNodeSize,
                linewidths = graphLineWidth,
                nodelist   = [node],
                node_shape = 'o',
                node_color = color['bg'])

            # draw node label
            nodeFontSize = \
                2. * graphFontSize / numpy.sqrt(max(len(node) - 1, 1))
            networkx.draw_networkx_labels(
                G, pos,
                font_size = nodeFontSize,
                labels = {node: label},
                font_weight = 'normal',
                font_color = color['font'])

            # draw node caption
            if kwargs['nodeCaption'] and isVisible:
                if not 'caption' in G.node[node]: continue
                networkx.draw_networkx_labels(G, posCap,
                    font_size = 0.75 * graphFontSize,
                    labels = {node: G.node[node]['caption']},
                    font_weight = 'normal')

    # draw edges
    for (v, h) in G.edges():

        # get weight
        weight = G.edge[v][h]['weight']

        # get edge color and line width (from weight)
        if kwargs['edgeWeight'] == 'adjacency':
            color = 'black'
            edgeLineWidth = graphLineWidth * kwargs['edgeScale']
        else:
            color = 'green' if weight > 0. else 'red'
            edgeLineWidth = \
                weight * graphLineWidth * kwargs['edgeScale']

        # draw edges
        networkx.draw_networkx_edges(G, pos,
            width      = edgeLineWidth,
            edgelist   = [(v, h)],
            edge_color = color,
            arrows     = False,
            alpha      = 1.)

        # (optional) draw edge labels
        if kwargs['edgeCaption']:
            if 'caption' in G.edge[v][h]:
                networkx.draw_networkx_edge_labels(G, pos,
                    edge_labels = {(v, h): G.edge[v][h]['caption']},
                    font_color  = color,
                    clip_on     = False,
                    font_size   = graphFontSize / 1.5,
                    font_weight = 'normal')

    # draw graph caption
    if kwargs['graphCaption'] and 'caption' in G.graph:
        matplotlib.pyplot.figtext(.5, .11,
            G.graph['caption'], fontsize = 9, ha = 'center')

    return True
