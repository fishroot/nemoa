# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import nemoa
import numpy

def filetypes():
    """Get supported image filetypes."""
    return nemoa.common.plot.filetypes()

def get_plot(dataset, func = None, plot = None, **kwargs):

    import importlib

    # get evaluation function
    fname = func or 'sample'
    fdict = dataset.get('algorithm', fname)
    if not isinstance(fdict, dict):
        return nemoa.log('error',
            "could not plot dataset '%s': "
            "dataset evaluation function '%s' "
            "is not supported." % (dataset.name, fname))

    # get plot type
    plot = plot or fdict.get('plot', None) or 'histogram'

    # get plot class and module name
    cname = plot.lower().title()
    mname = save.__module__
    try:
        module = importlib.import_module(mname)
        if not hasattr(module, cname): raise ImportError()
    except ImportError:
        return nemoa.log('error',
            "could not plot dataset '%s': "
            "plot type '%s' is not supported." % (dataset.name, plot))

    # create plot
    plot = getattr(module, cname)(func = fname, **kwargs)
    if plot.create(dataset): return plot

    plot.release()
    return None

def show(dataset, *args, **kwargs):
    """ """

    # create plot
    plot = get_plot(dataset, *args, **kwargs)
    if plot == None: return None

    plot.show()
    plot.release()

    return True

def save(dataset, path = None, filetype = None, *args, **kwargs):

    # test if filetype is supported
    if not filetype in filetypes(): return nemoa.log('error',
        "could not export plot: "
        "filetype '%s' is not supported." % (filetype))

    plot = get_plot(dataset, *args, **kwargs)
    if plot == None: return None

    plot.save(path)
    plot.release()

    return True

class Heatmap(nemoa.common.plot.Heatmap):

    def create(self, dataset):

        # evaluate function
        fname  = self._config.get('func', 'correlation')
        fdict  = dataset.get('algorithm', fname)
        func   = fdict.get('func', None) or fdict.get('reference', None)
        kwargs = nemoa.common.module.get_func_kwargs(func, self._config)
        array  = dataset.evaluate(fname, **kwargs)

        # check return value
        cols  = dataset.get('columns')
        shape = (len(cols), len(cols))
        if not isinstance(array, numpy.ndarray) or not array.shape == shape:
            return nemoa.log('warning',
                "representation of '%s' as heatmap "
                "is not supported." % (fname))

        # update axes labels
        self._config['x_labels'] = cols
        self._config['y_labels'] = cols

        # update title
        if not isinstance(self._config.get('title', None), str):
            if self._config.get('usetex', False):
                self._config['title'] = fdict.get('title_tex', None) \
                    or fdict.get('title', fname.title())
            else:
                self._config['title'] = fdict.get('title', fname.title())

        # create plot
        return self.plot(array)

class Histogram(nemoa.common.plot.Histogram):

    def create(self, dataset):

        # evaluate function
        fname  = self._config.get('func', 'correlation')
        fdict  = dataset.get('algorithm', fname)
        func   = fdict.get('func', None) or fdict.get('reference', None)
        kwargs = nemoa.common.module.get_func_kwargs(func, self._config)
        array  = dataset.evaluate(fname, **kwargs)

        # check return value
        if not isinstance(array, numpy.ndarray):
            return nemoa.log('warning',
                "representation of '%s' as histogram "
                "is not supported." % (fname))

        # get flat data
        data = array.flatten()

        # update title
        if not isinstance(self._config.get('title', None), str):
            if self._config.get('usetex', False):
                self._config['title'] = fdict.get('title_tex', None) \
                    or fdict.get('title', fname.title())
            else:
                self._config['title'] = fdict.get('title', fname.title())

        # create plot
        return self.plot(data)
