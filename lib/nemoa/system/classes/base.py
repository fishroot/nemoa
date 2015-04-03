# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import nemoa
import numpy
import copy

import nemoa.system.commons.units as unitclasses

class System(nemoa.common.classes.ClassesBaseClass):
    """System base class.

    Attributes:
        about (str): Short description of the content of the resource.
            Hint: Read- & writeable wrapping attribute to get('about')
                and set('about', str).
        author (str): A person, an organization, or a service that is
            responsible for the creation of the content of the resource.
            Hint: Read- & writeable wrapping attribute to get('author')
                and set('author', str).
        branch (str): Name of a duplicate of the original resource.
            Hint: Read- & writeable wrapping attribute to get('branch')
                and set('branch', str).
        edges (list of str): List of all edges in the network.
            Hint: Readonly wrapping attribute to get('edges')
        email (str): Email address to a person, an organization, or a
            service that is responsible for the content of the resource.
            Hint: Read- & writeable wrapping attribute to get('email')
                and set('email', str).
        fullname (str): String concatenation of name, branch and
            version. Branch and version are only conatenated if they
            exist.
            Hint: Readonly wrapping attribute to get('fullname')
        layers (list of str): List of all layers in the network.
            Hint: Readonly wrapping attribute to get('layers')
        license (str): Namereference to a legal document giving official
            permission to do something with the resource.
            Hint: Read- & writeable wrapping attribute to get('license')
                and set('license', str).
        name (str): Name of the resource.
            Hint: Read- & writeable wrapping attribute to get('name')
                and set('name', str).
        nodes (list of str): List of all nodes in the network.
            Hint: Readonly wrapping attribute to get('nodes')
        path (str):
            Hint: Read- & writeable wrapping attribute to get('path')
                and set('path', str).
        type (str): String concatenation of module name and class name
            of the instance.
            Hint: Readonly wrapping attribute to get('type')
        version (int): Versionnumber of the resource.
            Hint: Read- & writeable wrapping attribute to get('version')
                and set('version', int).

    """

    _config  = None
    _params  = None
    _default = {'params': {}, 'init': {}, 'optimize': {},
                'schedules': {}}
    _attr    = {'units': 'r', 'links': 'r', 'layers': 'r',
                'mapping': 'rw'}

    def configure(self, network = None):
        """Configure system to network."""

        if not nemoa.common.type.isnetwork(network):
            return nemoa.log('error', """could not configure system:
                network is not valid.""")

        return self._set_params(network = network)

    def initialize(self, dataset = None):
        """Initialize system parameters.

        Initialize all system parameters to dataset.

        Args:
            dataset: nemoa dataset instance

        """

        if not nemoa.common.type.isdataset(dataset):
            return nemoa.log('error', """could not initilize system:
                dataset is not valid.""")

        return self._set_params_init_units(dataset) \
            and self._set_params_init_links(dataset)

    def _check_network(self, network, *args, **kwargs):
        """Check if network is valid for system."""
        if not nemoa.common.type.isnetwork(network): return False
        return True

    def _check_dataset(self, dataset, *args, **kwargs):
        """Check if network is valid for system."""
        if not nemoa.common.type.isdataset(dataset): return False
        return True

    def get(self, key = 'name', *args, **kwargs):
        """Get meta information and content."""

        # meta information
        if key in self._attr_meta: return self._get_meta(key)

        # algorithms
        if key == 'algorithm':
            return self._get_algorithm(*args, **kwargs)
        if key == 'algorithms': return self._get_algorithms(
            attribute = 'about', *args, **kwargs)

        # content
        if key == 'unit': return self._get_unit(*args, **kwargs)
        if key == 'units': return self._get_units(*args, **kwargs)
        if key == 'link': return self._get_link(*args, **kwargs)
        if key == 'links': return self._get_links(*args, **kwargs)
        if key == 'layer': return self._get_layer(*args, **kwargs)
        if key == 'layers': return self._get_layers(*args, **kwargs)
        if key == 'mapping': return self._get_mapping(*args, **kwargs)

        # direct access
        if key == 'copy': return self._get_copy(*args, **kwargs)
        if key == 'config': return self._get_config(*args, **kwargs)
        if key == 'params': return self._get_params(*args, **kwargs)

        return nemoa.log('warning', "unknown key '%s'" % key) or None

    def _get_algorithms(self, category = None, attribute = None):
        """Get algorithms provided by system."""

        # get unstructured dictionary of all algorithms by prefix
        unstructured = nemoa.common.module.getmethods(self, prefix = '')

        # filter algorithms by supported keys and given category
        for ukey, udata in unstructured.items():
            if not isinstance(udata, dict):
                del unstructured[ukey]
                continue
            if attribute and not attribute in udata.keys():
                del unstructured[ukey]
                continue
            if not 'name' in udata.keys():
                del unstructured[ukey]
                continue
            if not 'category' in udata.keys():
                del unstructured[ukey]
                continue
            if category and not udata['category'] == category:
                del unstructured[ukey]

        # create flat structure id category is given
        structured = {}
        if category:
            for ukey, udata in unstructured.iteritems():
                if attribute: structured[udata['name']] = \
                    udata[attribute]
                else: structured[udata['name']] = udata
            return structured

        # create tree structure if category is not given
        categories = {
            ('system', 'evaluation'): None,
            ('system', 'units', 'evaluation'): 'units',
            ('system', 'links', 'evaluation'): 'links',
            ('system', 'relation', 'evaluation'): 'relation' }
        for ukey, udata in unstructured.iteritems():
            if not udata['category'] in categories.keys(): continue
            ckey = categories[udata['category']]
            if ckey == None:
                if attribute: structured[udata['name']] = \
                    udata[attribute]
                else: structured[udata['name']] = udata
            else:
                if not ckey in structured.keys(): structured[ckey] = {}
                if attribute: structured[ckey][udata['name']] = \
                    udata[attribute]
                else: structured[ckey][udata['name']] = udata

        return structured

    def _get_algorithm(self, algorithm = None, *args, **kwargs):
        """Get algorithm."""
        algorithms = self._get_algorithms(*args, **kwargs)
        if not algorithm in algorithms: return None
        return algorithms[algorithm]

    def _get_unit(self, unit):
        """Get unit information."""

        # get layer of unit
        layer_ids = []
        for i in xrange(len(self._params['units'])):
            if unit in self._params['units'][i]['id']:
                layer_ids.append(i)
        if len(layer_ids) == 0: return nemoa.log('error',
            "could not find unit '%s'." % (unit))
        if len(layer_ids) > 1: return nemoa.log('error',
            "unit name '%s' is not unique." % (unit))
        layer_id = layer_ids[0]

        # get parameters of unit
        layer_params = self._params['units'][layer_id]
        layer_units = layer_params['id']
        layer_size = len(layer_units)
        layer_unit_id = layer_units.index(unit)
        unit_params = { 'layer_sub_id': layer_unit_id }
        for param in layer_params.keys():
            layer_param_array = \
                numpy.array(layer_params[param]).flatten()
            if layer_param_array.size == 1:
                unit_params[param] = layer_param_array[0]
            elif layer_param_array.size == layer_size:
                unit_params[param] = layer_param_array[layer_unit_id]

        return unit_params

    def _get_units(self, groupby = None, **kwargs):
        """Get units of system.

        Args:
            groupby (str or 'None): Name of a unit attribute
                used to group units. If groupby is not
                None, the returned units are grouped by the different
                values of this attribute. Grouping is only
                possible if every unit contains the attribute.
            **kwargs: filter parameters of units. If kwargs are given,
                only units that match the filter parameters are
                returned.

        Returns:
            If the argument 'groupby' is not set, a list of strings
            containing name identifiers of units is returned. If
            'groupby' is a valid unit attribute, the units are grouped
            by the values of this attribute.

        Examples:
            Get a list of all units grouped by layers:
                model.system.get('units', groupby = 'layer')
            Get a list of visible units:
                model.system.get('units', visible = True)

        """

        # test if system is initialized to network
        if not isinstance(self._params, dict) \
            or not 'units' in self._params:
            return []

        # filter units to given attributes
        units = []
        for layer in self._params['units']:
            valid = True
            for key in kwargs.keys():
                if not layer[key] == kwargs[key]:
                    valid = False
                    break
            if not valid: continue
            units += layer['id']
        if groupby == None: return units

        # group units by given attribute
        units_params = {}
        for unit in units:
            units_params[unit] = self._get_unit(unit)
        grouping_values = []
        for unit in units:
            if not groupby in units_params[unit].keys():
                return nemoa.log('error', """could not get units:
                    unknown parameter '%s'.""" % (groupby))
            grouping_value = units_params[unit][groupby]
            if not grouping_value in grouping_values:
                grouping_values.append(grouping_value)
        grouped_units = []
        for grouping_value in grouping_values:
            group = []
            for unit in units:
                if units_params[unit][groupby] == grouping_value:
                    group.append(unit)
            grouped_units.append(group)
        return grouped_units

    def _get_layers(self, **kwargs):
        """Get unit layers of system.

        Returns:
            List of strings containing labels of unit layers that match
            a given property. The order is from input to output.

        Examples:
            return visible unit layers:
                model.system.get('layers', visible = True)

            search for unit layer 'test':
                model.system.get('layers', type = 'test')

        """

        # test if system is initialized to network
        if not isinstance(self._params, dict) \
            or not 'units' in self._params:
            return []

        filter_list = []
        for key in kwargs.keys():
            if key in self._params['units'][0].keys():
                filter_list.append((key, kwargs[key]))

        layers = []
        for layer in self._params['units']:
            valid = True
            for key, val in filter_list:
                if not layer[key] == val:
                    valid = False
                    break
            if valid: layers.append(layer['layer'])

        return layers

    def _get_layer(self, layer):
        if not layer in self._units.keys():
            return nemoa.log('error', """could not get layer:
                layers '%s' is unkown.""" % (layer))
        return self._units[layer].params

    def _get_link(self, link):
        if not isinstance(link, tuple):
            return nemoa.log('error', """could not get link:
                link '%s' is unkown.""" % (edge))

        src, tgt = link

        layers = [layer['layer'] for layer in self._params['units']]

        src_unit = self._get_unit(src)
        src_id = src_unit['layer_sub_id']
        src_layer = src_unit['layer']
        src_layer_id = layers.index(src_layer)
        src_layer_params = self._params['units'][src_layer_id]

        tgt_unit = self._get_unit(tgt)
        tgt_id = tgt_unit['layer_sub_id']
        tgt_layer = tgt_unit['layer']
        tgt_layer_id = layers.index(tgt_layer)
        tgt_layer_params = self._params['units'][tgt_layer_id]

        link_layer_params = \
            self._params['links'][(src_layer_id, tgt_layer_id)]
        link_layer_size = \
            len(src_layer_params['id']) * len(tgt_layer_params['id'])

        # get link parameters
        link_params = {}
        for param in link_layer_params.keys():
            layer_param_array = \
                numpy.array(link_layer_params[param])
            if layer_param_array.size == 1:
                link_params[param] = link_layer_params[param]
            elif layer_param_array.size == link_layer_size:
                link_params[param] = layer_param_array[src_id, tgt_id]

        # calculate additional link parameters
        layer_weights = link_layer_params['W']
        layer_adjacency = link_layer_params['A']
        link_weight = link_params['W']
        link_adjacency = link_params['A']

        # calculate normalized weight of link (per link layer)
        if link_weight == 0.0:
            link_norm_weight = 0.0
        else:
            adjacency_sum = numpy.sum(layer_adjacency)
            weight_sum = numpy.sum(
                numpy.abs(layer_adjacency * layer_weights))
            link_norm_weight = link_weight * adjacency_sum / weight_sum

        # calculate intensified weight of link (per link layer)
        if link_norm_weight == 0.0:
            link_intensity = 0.0
        else:
            link_norm_max = numpy.amax(numpy.abs(layer_adjacency
                * layer_weights)) * adjacency_sum / weight_sum
            from nemoa.system.commons.math import intensify
            link_intensity = intensify(
                link_norm_weight, factor = 10.,
                bound = 0.7 * link_norm_max)

        link_params['layer'] = (src_layer, tgt_layer)
        link_params['layer_sub_id'] = (src_id, tgt_id)
        link_params['adjacency'] = link_params['A']
        link_params['weight'] = link_params['W']
        link_params['sign'] = numpy.sign(link_params['W'])
        link_params['normal'] = link_norm_weight
        link_params['intensity'] = link_intensity

        return link_params

    def _get_links(self, groupby = None, **kwargs):
        """Get links of system.

        Args:
            groupby (str or None): Name of a link attribute
                used to group links. If groupby is not
                None, the returned links are grouped by the different
                values of this attribute. Grouping is only
                possible if every link contains the attribute.
            **kwargs: filter attributs of links. If kwargs are given,
                only links that match the filter attributes are
                returned.

        Returns:
            If the argument 'groupby' is not set, a list of strings
            containing name identifiers of links is returned. If
            'groupby' is a valid link attribute, the links are grouped
            by the values of this attribute.

        Examples:
            Get a list of all links grouped by layers:
                model.system.get('links', groupby = 'layer')
            Get a list of links with weight = 0.0:
                model.system.get('links', weight = 0.0)

        """

        # test if system is initialized to network
        if not isinstance(self._params, dict) \
            or not 'links' in self._params:
            return []

        # filter links by given attributes
        layers = self._get_layers()
        if not layers: return False
        links = []
        links_params = {}

        for layer_id in xrange(len(layers) - 1):
            src_layer = layers[layer_id]
            src_units = self._params['units'][layer_id]['id']
            tgt_layer = layers[layer_id + 1]
            tgt_units = self._params['units'][layer_id + 1]['id']
            link_layer_id = (layer_id, layer_id + 1)
            link_layer_params = self._params['links'][link_layer_id]

            for src_unit in src_units:
                for tgt_unit in tgt_units:
                    link = (src_unit, tgt_unit)
                    link_params = self._get_link(link)
                    if not link_params['A']: continue
                    valid = True
                    for key in kwargs.keys():
                        if not link_params[key] == kwargs[key]:
                            valid = False
                            break
                    if not valid: continue
                    links.append(link)
                    links_params[link] = link_params
        if groupby == None: return links

        # group links by given attribute
        grouping_values = []
        for link in links:
            if not groupby in links_params[link].keys():
                return nemoa.log('error', """could not get links:
                    unknown link attribute '%s'.""" % (groupby))
            grouping_value = links_params[link][groupby]
            if not grouping_value in grouping_values:
                grouping_values.append(grouping_value)
        grouped_links = []
        for grouping_value in grouping_values:
            group = []
            for link in links:
                if links_params[link][groupby] == grouping_value:
                    group.append(link)
            grouped_links.append(group)
        return grouped_links

    def _get_mapping(self, src = None, tgt = None):
        """Get mapping of unit layers from source to target.

        Args:
            src: name of source unit layer
            tgt: name of target unit layer

        Returns:
            tuple with names of unit layers from source to target.

        """

        if 'mapping' in self._params: mapping = self._params['mapping']
        else:
            mapping = tuple([l['layer'] for l in self._params['units']])

        sid = mapping.index(src) \
            if isinstance(src, str) and src in mapping else 0
        tid = mapping.index(tgt) \
            if isinstance(tgt, str) and tgt in mapping else len(mapping)

        return mapping[sid:tid + 1] if sid <= tid \
            else mapping[tid:sid + 1][::-1]

    def _get_copy(self, key = None, *args, **kwargs):
        """Get system copy as dictionary."""

        if key == None: return {
            'config': self._get_config(),
            'params': self._get_params() }

        if key == 'config': return self._get_config(*args, **kwargs)
        if key == 'params': return self._get_params(*args, **kwargs)

        return nemoa.log('error', """could not get system copy:
            unknown key '%s'.""" % key)

    def _get_config(self, key = None, *args, **kwargs):
        """Get configuration or configuration value."""

        if key == None: return copy.deepcopy(self._config)

        if isinstance(key, str) and key in self._config.keys():
            if isinstance(self._config[key], dict):
                return self._config[key].copy()
            return self._config[key]

        return nemoa.log('error', """could not get configuration:
            unknown key '%s'.""" % key)

    def _get_params(self, key = None, *args, **kwargs):
        """Get configuration or configuration value."""

        import copy

        if key == None: return copy.deepcopy(self._params)

        if isinstance(key, str) and key in self._params.keys():
            if isinstance(self._params[key], dict):
                return copy.deepcopy(self._params[key])
            return self._params[key]

        return nemoa.log('error', """could not get parameters:
            unknown key '%s'.""" % key)

    def _get_unitexpect(self, data, mapping = None, block = None):
        """Expectation values of target units.

        Args:
            data: numpy array containing source data corresponding to
                the source unit layer (first argument of the mapping)
            mapping: n-tuple of strings containing the mapping
                from source unit layer (first argument of tuple)
                to target unit layer (last argument of tuple)
            block: list of strings containing labels of source units
                that are 'blocked' by setting their values to the means
                of their values.

        Returns:
            Numpy array of shape (data, targets).

        """

        if mapping == None: mapping = self._get_mapping()
        if block == None: idata = data
        else:
            idata = numpy.copy(data)
            for i in block: idata[:, i] = numpy.mean(idata[:, i])
        if len(mapping) == 2: return self._units[mapping[1]].expect(
            idata, self._units[mapping[0]].params)
        odata = numpy.copy(idata)
        for id in xrange(len(mapping) - 1):
            odata = self._units[mapping[id + 1]].expect(
                odata, self._units[mapping[id]].params)

        return odata

    def _get_unitvalues(self, data, mapping = None, block = None,
        expect_last = False):
        """Unit maximum likelihood values of target units.

        Args:
            data: numpy array containing source data corresponding to
                the source unit layer (first argument of the mapping)
            mapping: n-tuple of strings containing the mapping
                from source unit layer (first argument of tuple)
                to target unit layer (last argument of tuple)
            block: list of strings containing labels of source units
                that are 'blocked' by setting their values to the means
                of their values.
            expect_last: return expectation values of the units
                for the last step instead of maximum likelihood values.

        Returns:
            Numpy array of shape (data, targets).

        """

        if mapping == None: mapping = self._get_mapping()
        if block == None: idata = data
        else:
            idata = numpy.copy(data)
            for i in block: idata[:, i] = numpy.mean(idata[:, i])
        if expect_last:
            if len(mapping) == 1:
                return idata
            elif len(mapping) == 2:
                return self._units[mapping[1]].expect(
                    self._units[mapping[0]].get_samples(idata),
                    self._units[mapping[0]].params)
            return self._units[mapping[-1]].expect(
                self._get_unitvalues(data, mapping[0:-1]),
                self._units[mapping[-2]].params)
        else:
            if len(mapping) == 1:
                return self._units[mapping[0]].get_values(idata)
            elif len(mapping) == 2:
                return self._units[mapping[1]].get_values(
                    self._units[mapping[1]].expect(idata,
                    self._units[mapping[0]].params))
            data = numpy.copy(idata)
            for id in xrange(len(mapping) - 1):
                data = self._units[mapping[id + 1]].get_values(
                    self._units[mapping[id + 1]].expect(data,
                    self._units[mapping[id]].params))
            return data

    def _get_unitsamples(self, data, mapping = None,
        block = None, expect_last = False):
        """Sampled unit values of target units.

        Args:
            data: numpy array containing source data corresponding to
                the source unit layer (first argument of the mapping)
            mapping: n-tuple of strings containing the mapping
                from source unit layer (first argument of tuple)
                to target unit layer (last argument of tuple)
            block: list of strings containing labels of source units
                that are 'blocked' by setting their values to the means
                of their values.
            expect_last: return expectation values of the units
                for the last step instead of sampled values

        Returns:
            Numpy array of shape (data, targets).

        """

        if mapping == None: mapping = self._get_mapping()
        if block == None: idata = data
        else:
            idata = numpy.copy(data)
            for i in block: idata[:,i] = numpy.mean(idata[:,i])
        if expect_last:
            if len(mapping) == 1:
                return data
            elif len(mapping) == 2:
                return self._units[mapping[1]].expect(
                    self._units[mapping[0]].get_samples(data),
                    self._units[mapping[0]].params)
            return self._units[mapping[-1]].expect(
                self._get_unitsamples(data, mapping[0:-1]),
                self._units[mapping[-2]].params)
        else:
            if len(mapping) == 1:
                return self._units[mapping[0]].get_samples(data)
            elif len(mapping) == 2:
                return self._units[mapping[1]].get_samples_from_input(
                    data, self._units[mapping[0]].params)
            data = numpy.copy(data)
            for id in xrange(len(mapping) - 1):
                data = \
                    self._units[mapping[id + 1]].get_samples_from_input(
                    data, self._units[mapping[id]].params)
            return data

    def set(self, key = None, *args, **kwargs):
        """Set meta information, configuration and parameters."""

        # set meta information
        if key in self._attr_meta:
            return self._set_meta(key, *args, **kwargs)

        # set configuration and parameters
        #if key == 'units': return self._set_units(*args, **kwargs)
        if key == 'links': return self._set_links(*args, **kwargs)
        if key == 'mapping': return self._set_mapping(*args, **kwargs)

        # import configuration and parameters
        if key == 'copy': return self._set_copy(*args, **kwargs)
        if key == 'config': return self._set_config(*args, **kwargs)
        if key == 'params': return self._set_params(*args, **kwargs)

        return nemoa.log('warning', "unknown key '%s'" % key) or None

    def _set_links(self, links = None, initialize = True):
        """Create link configuration from units."""

        if not self._configure_test_units(self._params):
            return nemoa.log('error', """could not configure links:
                units have not been configured.""")

        if not 'links' in self._params: self._params['links'] = {}
        if not initialize: return self._set_params_create_links()

        # initialize adjacency matrices with default values
        for lid in xrange(len(self._params['units']) - 1):
            src_name = self._params['units'][lid]['layer']
            src_list = self._units[src_name].params['id']
            tgt_name = self._params['units'][lid + 1]['layer']
            tgt_list = self._units[tgt_name].params['id']
            lnk_name = (lid, lid + 1)

            if links:
                lnk_adja = numpy.zeros((len(src_list), len(tgt_list)))
            else:
                lnk_adja = numpy.ones((len(src_list), len(tgt_list)))

            self._params['links'][lnk_name] = {
                'source': src_name,
                'target': tgt_name,
                'A': lnk_adja.astype(float)
            }

        # set adjacency if links are given explicitly
        if links:

            for link in links:
                src, tgt = link

                # get layer id and layers sub id of link source
                src_unit = self._get_unit(src)
                if not src_unit: continue
                src_lid = src_unit['layer_id']
                src_sid = src_unit['layer_sub_id']

                # get layer id and layer sub id of link target
                tgt_unit = self._get_unit(tgt)
                if not tgt_unit: continue
                tgt_lid = tgt_unit['layer_id']
                tgt_sid = tgt_unit['layer_sub_id']

                # set adjacency
                if not (src_lid, tgt_lid) in self._params['links']:
                    continue
                lnk_dict = self._params['links'][(src_lid, tgt_lid)]
                lnk_dict['A'][src_sid, tgt_sid] = 1.0

        return self._set_params_create_links() \
            and self._set_params_init_links()

    def _set_mapping(self, mapping):
        """Set the layer mapping of the system."""
        if not isinstance(mapping, tuple): return nemoa.log('warning',
            "attribute 'mapping' requires datatype 'tuple'.")
        self._params['mapping'] = mapping
        return True

    def _set_copy(self, config = None, params = None):
        """Set configuration and parameters of system.

        Args:
            config (dict or None, optional): system configuration
            params (dict or None, optional): system parameters

        Returns:
            Bool which is True if and only if no error occured.

        """

        retval = True

        if config: retval &= self._set_config(config)
        if params: retval &= self._set_params(params)

        return retval

    def _set_config(self, config = None):
        """Set configuration from dictionary."""

        # initialize or update configuration dictionary
        if not hasattr(self, '_config') or not self._config:
            self._config = self._default.copy()
        if config:
            self._config = nemoa.common.dict.merge(config, self._config)

        # reset consistency check
        self._config['check'] = {
            'config': True, 'network': False, 'dataset': False }
        return True

    def _set_params(self, params = None, network = None, dataset = None):
        """Set system parameters from dictionary."""

        if not self._params:
            self._params = {'units': {}, 'links': {}}

        retval = True

        # get system parameters from dict
        if params:
            self._params = nemoa.common.dict.merge(params, self._params)

            # create instances of units and links
            retval &= self._set_params_create_units()
            retval &= self._set_params_create_links()

        # get system parameters from network
        elif network:
            if not nemoa.common.type.isnetwork(network):
                return nemoa.log('error', """could not configure system:
                    network instance is not valid!""")

            # get unit layers and unit params
            layers = network.get('layers')
            units = [network.get('layer', layer) for layer in layers]

            for layer in units:
                layer['id'] = layer.pop('nodes')
                if 'type' in layer: layer['class'] = layer.pop('type')
                elif layer['visible']: layer['class'] = 'gauss'
                else: layer['class'] = 'sigmoid'

            # get link layers and link params
            links = {}
            for lid in xrange(len(units) - 1):
                src = units[lid]['layer']
                src_list = units[lid]['id']
                tgt = units[lid + 1]['layer']
                tgt_list = units[lid + 1]['id']
                link_layer = (lid, lid + 1)
                link_layer_shape = (len(src_list), len(tgt_list))
                link_layer_adj = numpy.zeros(link_layer_shape)
                links[link_layer] = {
                    'source': src, 'target': tgt,
                    'A': link_layer_adj.astype(float) }
            for link in network.edges:
                src, tgt = link
                found = False
                for lid in xrange(len(units) - 1):
                    if src in units[lid]['id']:
                        src_lid = lid
                        src_sid = units[lid]['id'].index(src)
                        tgt_lid = lid + 1
                        tgt_sid = units[lid + 1]['id'].index(tgt)
                        found = True
                        break
                if not found: continue
                if not (src_lid, tgt_lid) in links: continue
                links[(src_lid, tgt_lid)]['A'][src_sid, tgt_sid] = 1.0

            params = {'units': units, 'links': links}
            self._params = nemoa.common.dict.merge(params, self._params)

            # create instances of units and links
            retval &= self._set_params_create_units()
            retval &= self._set_params_create_links()
            retval &= self._set_params_create_mapping()
            retval &= self._set_params_init_links()


        # initialize system parameters if dataset is given
        if dataset:
            if not nemoa.common.type.isdataset(dataset):
                return nemoa.log('error', """could not initialize
                    system: dataset instance is not valid.""")

            retval &= self._set_params_init_units(dataset)
            retval &= self._set_params_init_links(dataset)

        return retval

    def _set_params_create_units(self):

        # create instances of unit classes
        # and link units params to local params dict
        self._units = {}
        for layer_id in xrange(len(self._params['units'])):
            layer_params = self._params['units'][layer_id]
            layer_class = layer_params['class']
            layer_name = layer_params['layer']

            if layer_class == 'sigmoid':
                self._units[layer_name] \
                    = unitclasses.Sigmoid(layer_params)
            elif layer_class == 'gauss':
                self._units[layer_name] \
                    = unitclasses.Gauss(layer_params)
            else:
                return nemoa.log('error', """could not create system:
                    unit class '%s' is not supported!"""
                    % (layer_class))

        return True

    def _set_params_create_links(self):

        self._links = {units: {'source': {}, 'target': {}}
            for units in self._units.keys()}

        for link_layer_id in self._params['links'].keys():
            link_params = self._params['links'][link_layer_id]

            src = link_params['source']
            tgt = link_params['target']

            self._links[src]['target'][tgt] = link_params
            self._units[src].target = link_params
            self._links[tgt]['source'][src] = link_params
            self._units[tgt].source = link_params

        return True

    def _set_params_create_mapping(self):
        mapping = tuple([l['layer'] for l in self._params['units']])
        self._set_mapping(mapping)

        return True

    def _set_params_init_units(self, dataset = None):
        """Initialize unit parameteres.

        Args:
            dataset: nemoa dataset instance OR None

        """

        if not (dataset == None) and not \
            nemoa.common.type.isdataset(dataset):
            return nemoa.log('error', """could not initilize units:
            invalid dataset argument given!""")

        for layer in self._units.keys():
            if dataset == None:
                data = None
            elif not self._units[layer].params['visible']:
                data = None
            else:
                rows = self._config['params']['samples'] \
                    if 'samples' in self._config['params'] else '*'
                cols = layer \
                    if layer in dataset.get('colgroups') else '*'
                data = dataset.get('data', rows = rows, cols = cols)
            self._units[layer].initialize(data)

        return True

    def _set_params_init_links(self, dataset = None):
        """Initialize link parameteres (weights).

        If dataset is None, initialize weights matrices with zeros
        and all adjacency matrices with ones. if dataset is nemoa
        network instance, use data distribution to calculate random
        initial weights.

        Args:
            dataset (dataset instance OR None):

        Returns:


        """

        if not(dataset == None) and \
            not nemoa.common.type.isdataset(dataset): return nemoa.log(
            'error', """could not initilize link parameters:
            invalid dataset argument given!""")

        for links in self._params['links']:
            source = self._params['links'][links]['source']
            target = self._params['links'][links]['target']
            A = self._params['links'][links]['A']
            x = len(self._units[source].params['id'])
            y = len(self._units[target].params['id'])
            alpha = self._config['init']['w_sigma'] \
                if 'w_sigma' in self._config['init'] else 1.
            sigma = numpy.ones([x, 1], dtype = float) * alpha / x

            if dataset == None:
                random = numpy.random.normal(numpy.zeros((x, y)), sigma)
            elif source in dataset.get('colgroups'):
                rows = self._config['params']['samples'] \
                    if 'samples' in self._config['params'] else '*'
                data = dataset.get('data', 100000, rows = rows,
                    cols = source)
                delta = sigma * data.std(axis = 0).reshape(x, 1) + 0.001
                random = numpy.random.normal(numpy.zeros((x, y)), delta)
            elif dataset.columns \
                == self._units[source].params['id']:
                rows = self._config['params']['samples'] \
                    if 'samples' in self._config['params'] else '*'
                data = dataset.get('data', 100000, rows = rows, cols = '*')
                random = numpy.random.normal(numpy.zeros((x, y)),
                    sigma * numpy.std(data, axis = 0).reshape(1, x).T)
            else: random = \
                numpy.random.normal(numpy.zeros((x, y)), sigma)

            self._params['links'][links]['W'] = A * random

        return True

    #def evaluate(self, data, *args, **kwargs):
        #"""Evaluate system using data."""

        ## default system evaluation
        #if len(args) == 0:
            #return self._evaluate_system(data, **kwargs)

        ## evaluate system units
        #if args[0] == 'units':
            #return self._evaluate_units(data, *args[1:], **kwargs)

        ## evaluate system links
        #if args[0] == 'links':
            #return self._evaluate_links(data, *args[1:], **kwargs)

        ## evaluate system relations
        #if args[0] == 'relations':
            #return self._evaluate_relation(data, *args[1:], **kwargs)

        ## evaluate system
        #algorithms = self._get_algorithms(attribute = 'name',
            #category = ('system', 'evaluation')).values()

        #if args[0] in algorithms:
            #return self._evaluate_system(data, *args, **kwargs)

        #return nemoa.log('warning',
            #"unsupported system evaluation '%s'." % args[0])

    #def _evaluate_system(self, data, func = 'accuracy', **kwargs):
        #"""Evaluation of system.

        #Args:
            #data: 2-tuple of numpy arrays: source data and target data
            #func: string containing the name of a supported system
                #evaluation function. For a full list of available
                #functions use: model.system.get('algorithms')

        #Returns:
            #Scalar system evaluation value (respective to given data).

        #"""

        ## check if data is valid
        #if not isinstance(data, tuple): return nemoa.log('error',
            #'could not evaluate system: invalid data.')

        ## get evaluation algorithms
        #algorithms = self._get_algorithms(
            #category = ('system', 'evaluation'))
        #if not func in algorithms.keys(): return nemoa.log('error',
            #"""could not evaluate system: unknown algorithm
            #'%s'.""" % (func))
        #algorithm = algorithms[func]

        ## prepare (non keyword) arguments for evaluation function
        #evalargs = []
        #if algorithm['args'] == 'none': pass
        #elif algorithm['args'] == 'input': evalargs.append(data[0])
        #elif algorithm['args'] == 'output': evalargs.append(data[1])
        #elif algorithm['args'] == 'all': evalargs.append(data)

        ## prepare keyword arguments for evaluation function
        #evalkwargs = kwargs.copy()
        #if not 'mapping' in evalkwargs.keys() \
            #or evalkwargs['mapping'] == None:
            #evalkwargs['mapping'] = self._get_mapping()

        ## evaluate system
        #return algorithm['reference'](*evalargs, **evalkwargs)

    #def _evaluate_units(self, data, func = 'accuracy', units = None,
        #**kwargs):
        #"""Evaluation of target units.

        #Args:
            #data: 2-tuple with numpy arrays: source and target data
            #func: string containing name of unit evaluation function
                #For a full list of available system evaluation functions
                #see: model.system.get('algorithms')
            #units: list of target unit names (within the same layer). If
                #not given, all output units are selected.

        #Returns:
            #Dictionary with unit evaluation values for target units. The
            #keys of the dictionary are given by the names of the target
            #units, the values depend on the used evaluation function and
            #are ether scalar (float) or vectorially (flat numpy array).

        #"""

        ## check if data is valid
        #if not isinstance(data, tuple): return nemoa.log('error',
            #'could not evaluate system units: invalid data.')

        ## get evaluation algorithms
        #algorithms = self._get_algorithms(
            #category = ('system', 'units', 'evaluation'))
        #if not func in algorithms.keys(): return nemoa.log('error',
            #"""could not evaluate system units:
            #unknown algorithm name '%s'.""" % (func))
        #algorithm = algorithms[func]

        ## prepare (non keyword) arguments for evaluation
        #if algorithm['args'] == 'none': evalargs = []
        #elif algorithm['args'] == 'input': evalargs = [data[0]]
        #elif algorithm['args'] == 'output': evalargs = [data[1]]
        #elif algorithm['args'] == 'all': evalargs = [data]

        ## prepare keyword arguments for evaluation
        #evalkwargs = kwargs.copy()
        #if isinstance(units, str):
            #evalkwargs['mapping'] = self._get_mapping(tgt = units)
        #elif not 'mapping' in evalkwargs.keys() \
            #or evalkwargs['mapping'] == None:
            #evalkwargs['mapping'] = self._get_mapping()

        ## evaluate units
        #try: values = algorithm['reference'](*evalargs, **evalkwargs)
        #except: return nemoa.log('error', 'could not evaluate units')

        ## create dictionary of target units
        #labels = self._get_units(layer = evalkwargs['mapping'][-1])
        #if algorithm['retfmt'] == 'vector': return {unit: \
            #values[:, uid] for uid, unit in enumerate(labels)}
        #elif algorithm['retfmt'] == 'scalar': return {unit:
            #values[uid] for uid, unit in enumerate(labels)}
        #return nemoa.log('warning', """could not evaluate system units:
            #unknown return format '%s'.""" % (algorithm['retfmt']))

    #def _evaluate_links(self, data, func = 'energy', **kwargs):
        #"""Evaluate system links respective to data.

        #Args:
            #data: 2-tuple of numpy arrays containing source and target
                #data corresponding to the first and the last argument
                #of the mapping
            #mapping: n-tuple of strings containing the mapping
                #from source unit layer (first argument of tuple)
                #to target unit layer (last argument of tuple)
            #func: string containing name of link evaluation function
                #For a full list of available link evaluation functions
                #see: model.system.get('algorithms')

        #"""

        ## check if data is valid
        #if not isinstance(data, tuple): return nemoa.log('error',
            #'could not evaluate system links: invalid data.')

        ## get evaluation algorithms
        #algorithms = self._get_algorithms(
            #category = ('system', 'links', 'evaluation'))
        #if not func in algorithms.keys(): return nemoa.log('error',
            #"""could not evaluate system links:
            #unknown algorithm name '%s'.""" % (func))
        #algorithm = algorithms[func]

        ## prepare (non keyword) arguments for evaluation
        #if algorithm['args'] == 'none': evalargs = []
        #elif algorithm['args'] == 'input': evalargs = [data[0]]
        #elif algorithm['args'] == 'output': evalargs = [data[1]]
        #elif algorithm['args'] == 'all': evalargs = [data]

        ## prepare keyword arguments for evaluation
        #evalkwargs = kwargs.copy()
        #if isinstance(units, str):
            #evalkwargs['mapping'] = self._get_mapping(tgt = units)
        #elif not 'mapping' in evalkwargs.keys() \
            #or evalkwargs['mapping'] == None:
            #evalkwargs['mapping'] = self._get_mapping()

        ## perform evaluation
        #try: values = algorithm['reference'](*evalargs, **evalkwargs)
        #except: return nemoa.log('error', 'could not evaluate links')

        ## create link dictionary
        #in_labels = self._get_units(layer = evalkwargs['mapping'][-2])
        #out_labels = self._get_units(layer = evalkwargs['mapping'][-1])
        #if algorithm['retfmt'] == 'scalar':
            #rel_dict = {}
            #for in_id, in_unit in enumerate(in_labels):
                #for out_id, out_unit in enumerate(out_labels):
                    #rel_dict[(in_unit, out_unit)] = \
                        #values[in_id, out_id]
            #return rel_dict
        #return nemoa.log('warning', """could not evaluate system links:
            #unknown return format '%s'.""" % (algorithm['retfmt']))

    #def _evaluate_relation(self, data, func = 'correlation',
        #evalstat = True, **kwargs):
        #"""Evaluate relations between source and target units.

        #Args:
            #data: 2-tuple with numpy arrays: input data and output data
            #func: string containing name of unit relation function
                #For a full list of available unit relation functions
                #see: model.system.get('algorithms')
            #transform: optional formula for transformation of relation
                #which is executed by python eval() function. The usable
                #variables are:
                    #M: for the relation matrix as numpy array with shape
                        #(source, target)
                    #C: for the standard correlation matrix s numpy array
                        #with shape (source, target)
                #Example: 'M**2 - C'
            #format: string describing format of return values
                #'array': return values as numpy array
                #'dict': return values as python dictionary
            #eval_stat: if format is 'dict' and eval_stat is True then
                #the return dictionary includes additional statistical
                #values:
                    #min: minimum value of unit relation
                    #max: maximum value of unit relation
                    #mean: mean value of unit relation
                    #std: standard deviation of unit relation

        #Returns:
            #Python dictionary or numpy array with unit relation values.

        #"""

        ## check if data is valid
        #if not isinstance(data, tuple): return nemoa.log('error',
            #'could not evaluate system unit relation: invalid data.')

        ## get evaluation algorithms
        #algorithms = self._get_algorithms(
            #category = ('system', 'relation', 'evaluation'))
        #if not func in algorithms.keys(): return nemoa.log('error',
            #"""could not evaluate system unit relation:
            #unknown algorithm name '%s'.""" % (func))
        #algorithm = algorithms[func]

        ## prepare (non keyword) arguments for evaluation
        #if algorithm['args'] == 'none': eargs = []
        #elif algorithm['args'] == 'input': eargs = [data[0]]
        #elif algorithm['args'] == 'output': eargs = [data[1]]
        #elif algorithm['args'] == 'all': eargs = [data]

        ## prepare keyword arguments for evaluation
        #if 'transform' in kwargs.keys() \
            #and isinstance(kwargs['transform'], str):
            #transform = kwargs['transform']
            #del kwargs['transform']
        #else: transform = ''
        #if 'format' in kwargs.keys() \
            #and isinstance(kwargs['format'], str):
            #retfmt = kwargs['format']
            #del kwargs['format']
        #else: retfmt = 'dict'
        #ekwargs = kwargs.copy()
        #if not 'mapping' in ekwargs.keys() \
            #or ekwargs['mapping'] == None:
            #ekwargs['mapping'] = self._get_mapping()

        ## perform evaluation
        #values = algorithm['reference'](*eargs, **ekwargs)
        ##try: values = algorithm['reference'](*eargs, **ekwargs)
        ##except: return nemoa.log('error', """
            ##could not evaluate system unit relations""")

        ## create formated return values as matrix or dict
        ## (for scalar relation evaluations)
        #if algorithm['retfmt'] == 'scalar':
            ## (optional) transform relation using 'transform' string
            #if transform:
                #M = values
                ## todo: calc real relation
                #if 'C' in transform:
                    #C = self._algorithm_unitcorrelation(data)
                #try:
                    #T = eval(transform)
                    #values = T
                #except: return nemoa.log('error',
                    #'could not transform relations: invalid syntax!')

            ## create formated return values
            #if retfmt == 'array':
                #retval = values
            #elif retfmt == 'dict':
                #src = self._get_units(layer = ekwargs['mapping'][0])
                #tgt = self._get_units(layer = ekwargs['mapping'][-1])
                #retval = nemoa.common.dict.fromarray(values, (src, tgt))
                #if not evalstat: return retval

                ## (optional) add statistics
                #filtered = []
                #for src, tgt in retval:
                    #sunit = src.split(':')[1] if ':' in src else src
                    #tunit = tgt.split(':')[1] if ':' in tgt else tgt
                    #if sunit == tunit: continue
                    #filtered.append(retval[(src, tgt)])
                #array = numpy.array(filtered)
                #retval['max'] = numpy.amax(array)
                #retval['min'] = numpy.amin(array)
                #retval['mean'] = numpy.mean(array)
                #retval['std'] = numpy.std(array)

                #return retval

            #else: return nemoa.log('warning',
                #'could not perform system unit relation evaluation')

            #return False

    def save(self, *args, **kwargs):
        """Export system to file."""
        return nemoa.system.save(self, *args, **kwargs)

    def show(self, *args, **kwargs):
        """Show system as image."""
        return nemoa.system.show(self, *args, **kwargs)

    def copy(self, *args, **kwargs):
        """Create copy of system."""
        return nemoa.system.copy(self, *args, **kwargs)
