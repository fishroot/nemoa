# -*- coding: utf-8 -*-

__author__  = 'Patrick Michl'
__email__   = 'patrick.michl@gmail.com'
__license__ = 'GPLv3'

import nemoa
import copy
import os
import importlib
import imp
import re
import ConfigParser
import glob

class workspace:

    def __init__(self, project = None):
        """Initialize shared configuration."""
        nemoa.workspace.init()
        if not project == None: nemoa.workspace.load(project)

    def load(self, workspace):
        """Import configuration from workspace and update paths and logfile."""
        return nemoa.workspace.load(workspace)

    def name(self, *args, **kwargs):
        """Return name of workspace."""
        return nemoa.workspace.project(*args, **kwargs)

    def list(self, type = None, namespace = None):
        """Return a list of known objects."""
        list = nemoa.workspace.list(type = type, namespace = self.name())
        if not type: names = \
            ['%s (%s)' % (item[2], item[1]) for item in list]
        elif type in ['model']: names = list
        else: names = [item[2] for item in list]
        return names

    def execute(self, name = None, **kwargs):
        """Execute nemoa script."""
        scriptName = name if '.' in name else '%s.%s' % (self.name(), name)
        config = nemoa.workspace.getConfig(
            type = 'script', config = scriptName, **kwargs)

        if not config and not '.' in name:
            scriptName = 'base.' + name
            config = nemoa.workspace.getConfig(
                type = 'script', config = scriptName, **kwargs)
        if not config: return False
        if not os.path.isfile(config['path']): return nemoa.log('error', """
            could not run script '%s': file '%s' not found!
            """ % (scriptName, config['path']))

        script = imp.load_source('script', config['path'])
        return script.main(self, **config['params'])

    def dataset(self, config = None, **kwargs):
        """Return new dataset instance."""
        return self._getInstance('dataset', config, **kwargs)

    def network(self, config = None, **kwargs):
        """Return new network instance."""
        return self._getInstance('network', config, **kwargs)

    def system(self, config = None, **kwargs):
        """Return new system instance."""
        return self._getInstance('system', config, **kwargs)

    def model(self, name = None, **kwargs):
        """Return model instance."""

        # try to import model from file
        if isinstance(name, str) and not kwargs:
            if not name in self.list(type = 'model'): return \
                nemoa.log('error', """could not import model:
                a model with name '%s' does not exists!""" % (name))
            return self._importModelFromFile(name)

        # check keyword arguments
        if not ('network' in kwargs and 'dataset' in kwargs \
            and 'system' in kwargs): return nemoa.log('error',
                """could not create model:
                dataset, network and system parameters needed!""")

        # try to create new model
        return self._createNewModel(name, **kwargs)

    def _getInstance(self, type = None, config = None, empty = False, **kwargs):
        """Return new instance of given object type and configuration."""
        nemoa.log('create%s %s instance' % (' empty' if empty else '', type))
        nemoa.setLog(indent = '+1')

        # import module
        module = importlib.import_module('nemoa.' + str(type))

        # get objects configuration as dictionary
        config = nemoa.workspace.getConfig(type = type,
            config = config, **kwargs)
        if not isinstance(config, dict):
            nemoa.log('error', """could not create %s instance:
                unknown configuration!""" % (type))
            nemoa.setLog(indent = '-1')
            return None

        # create and initialize new instance of given class
        instance = module.empty() if empty \
            else module.new(config = config, **kwargs)

        # check instance class
        if not nemoa.type.isInstanceType(instance, type):
            nemoa.log('error', """could not create %s instance:
                invalid configuration!""" % (type))
            nemoa.setLog(indent = '-1')
            return None

        nemoa.log('name of %s is: \'%s\'' % (type, instance.name()))
        nemoa.setLog(indent = '-1')
        return instance

    def _createNewModel(self, name, config = None,
        dataset = None, network = None, system = None,
        configure = True, initialize = True):
        nemoa.log('create new model')
        nemoa.setLog(indent = '+1')

        model = self._getModelInstance(name = name, config  = config,
            dataset = dataset, network = network, system  = system)

        if not nemoa.type.isModel(model):
            nemoa.log('error', 'could not create new model!')
            nemoa.setLog(indent = '-1')
            return False

        if configure: model.configure() # configure model
        if initialize: model.initialize() # initialize model parameters

        nemoa.setLog(indent = '-1')
        return model

    def _getModelInstance(self, name = None, config = None,
        dataset = None, network = None, system = None):
        """Return new model instance."""

        nemoa.log('create model instance')
        nemoa.setLog(indent = '+1')

        # create dataset instance (if not given)
        if not nemoa.type.isDataset(dataset): dataset = \
            self._getInstance(type = 'dataset', config = dataset)
        if not nemoa.type.isDataset(dataset):
            nemoa.log('error',
                'could not create model instance: dataset is invalid!')
            nemoa.setLog(indent = '-1')
            return None

        # create network instance (if not given)
        if network == None: network = {'type': 'auto'}
        if not nemoa.type.isNetwork(network): network = \
            self._getInstance(type = 'network', config = network)
        if not nemoa.type.isNetwork(network):
            nemoa.log('error',
                'could not create model instance: network is invalid!')
            nemoa.setLog(indent = '-1')
            return None

        # create system instance (if not given)
        if not nemoa.type.isSystem(system): system = \
            self._getInstance(type = 'system', config = system)
        if not nemoa.type.isSystem(system):
            nemoa.log('error',
                'could not create model instance: system is invalid!')
            nemoa.setLog(indent = '-1')
            return None

        # create name string (if not given)
        if name == None: name = '-'.join(
            [dataset.name(), network.name(), system.name()])

        # create model instance
        model = self._getInstance(
            type = 'model', config = config, name = name,
            dataset = dataset, network = network, system = system)

        nemoa.setLog(indent = '-1')
        return model

    def _importModelFromFile(self, file):
        """Return new model instance and set configuration and parameters from file."""

        nemoa.log('import model from file')
        nemoa.setLog(indent = '+1')

        # check file
        if not os.path.exists(file):
            if os.path.exists(
                nemoa.workspace.path('models') + file + '.nmm'):
                file = nemoa.workspace.path('models') + file + '.nmm'
            else: return nemoa.log('error',
                """could not load model '%s':
                file does not exist.""" % file)

        # load model parameters and configuration from file
        nemoa.log("load model: '%s'" % file)
        modelDict = nemoa.common.dictFromFile(file)

        model = self._getModelInstance(
            name    = modelDict['config']['name'],
            config  = modelDict['config'],
            dataset = modelDict['dataset']['cfg'],
            network = modelDict['network']['cfg'],
            system  = modelDict['system']['config'])

        if nemoa.type.isModel(model): model._set(modelDict)
        else: return None

        nemoa.setLog(indent = '-1')
        return model

    def copy(self, model):
        """Return copy of model instance"""
        return self.model(
            config = model.getConfig(),
            dataset = model.dataset.getConfig(),
            network = model.network.getConfig(),
            system = model.system.getConfig(),
            configure = False, initialize = False)._set(model._get())

class config:
    def __init__(self, update = True):
        self.__baseconf = 'nemoa.ini' # base configuration file

        # init tree structure for configuration storage
        self.__store = {'dataset': {}, 'network': {}, 'system': {},
            'plot': {}, 'schedule': {}, 'script': {}}

        self.__index = {}
        self.__path = {}            # reset current path dict
        self.__basepath = None      # reset paths for shared and user
        self.__workspace = None     # reset current workspace
        self.__workspacePath = None # reset current workspace path
        self._updateBasepath()     # update paths for shared and user

        if update: self._importShared() # import shared resources

    def _updateBasepath(self):
        if not os.path.exists(self.__baseconf): return False

        # default basepaths
        self.__basepath = {
            'user': '~/nemoa/',
            'common': '/etc/nemoa/common/' }

        # get basepath configuration
        cfg = ConfigParser.ConfigParser()
        cfg.optionxform = str
        cfg.read(self.__baseconf)

        # [folders]
        if 'folders' in cfg.sections():
            for key in ['user', 'cache', 'common']:
                if not key in cfg.options('folders'): continue
                val  = cfg.get('folders', key)
                path = self._expandPath(val)
                if path: self.__basepath[key] = path

        # [files]
        if 'files' in cfg.sections():
            for key in ['logfile']:
                if not key in cfg.options('files'): continue
                val  = cfg.get('files', key)
                self.__path[key] = self._expandPath(val)

        return True

    def _updatePaths(self, base = 'user'):

        self.__workspacePath = {
            'workspace': '%project%/',
            'datasets': '%project%/data/',
            'models': '%project%/models/',
            'scripts': '%project%/scripts/',
            'networks': '%project%/networks/',
            'plots': '%project%/plots/',
            'cache': '%project%/cache/',
            'logfile': '%project%/nemoa.log'
        }

        if base in ['user', 'common']:
            allowWrite = {'user': True, 'common': False}[base]
            for key in self.__workspacePath:
                self.__path[key] = self._expandPath('%' + base + '%/'
                    + self.__workspacePath[key], create = allowWrite)

    def _listUserWorkspaces(self):
        """Return list of private workspaces."""
        userDir = self._expandPath(self.__basepath['user'])
        return [os.path.basename(w) for w in glob.iglob(userDir + '*')
            if os.path.isdir(w)]

    def _listSharedWorkspaces(self):
        """Return list of shared resources."""
        shared = self._expandPath(self.__basepath['common'])
        return [os.path.basename(w) for w in glob.iglob(shared + '*')
            if os.path.isdir(w)]

    def project(self):
        """Return name of current workspace."""
        return self.__workspace

    def path(self, key = None):
        """Return path."""
        if isinstance(key, str) and key in self.__path.keys():
            if isinstance(self.__path[key], dict):
                return self.__path[key].copy()
            return self.__path[key]
        return self.__path.copy()

    def _importShared(self):
        """Import shared resources."""
        nemoa.log('import shared resources')
        nemoa.setLog(indent = '+1')

        # get current workspace
        curWorkspace = self.__workspace

        # import shared resources and update paths
        for workspace in self._listSharedWorkspaces():
            self.__workspace = workspace
            self._updatePaths(base = 'common')
            self._scanConfigFiles()
            self._scanScripts()
            self._scanNetworks()

        # reset to current workspace
        self.__workspace = curWorkspace

        nemoa.setLog(indent = '-1')
        return True

    def load(self, workspace):
        """Import configuration files from workspace."""
        nemoa.log('import private resources')
        nemoa.setLog(indent = '+1')

        # check if workspace exists
        if not workspace in self._listUserWorkspaces(): return nemoa.log(
            'warning', """could not open workspace '%s':
            workspace folder could not be found in '%s'!
            """ % (workspace, self.__basepath['user']))

        self.__workspace = workspace # set workspace
        self._updatePaths(base = 'user') # update paths
        self._updateCachePaths() # update path of cache
        nemoa.initLogger(logfile = self.__path['logfile']) # update logger
        self._scanConfigFiles() # import configuration files
        self._scanScripts() # scan for scriptfiles
        self._scanNetworks() # scan for network configurations

        nemoa.setLog(indent = '-1')
        return True

    def _updateCachePaths(self):
        """Update dataset cache paths to current workspace."""
        for key in self.__store['dataset']:
            self.__store['dataset'][key]['cache_path'] = self.__path['cache']
        return True

    def _scanConfigFiles(self, files = None):
        """Import configuration files from current workspace."""
        nemoa.log('scanning for configuration files')
        nemoa.setLog(indent = '+1')

        # assert configuration files path
        if files == None: files = self.__path['workspace'] + '*.ini'
        # import configuration files
        for file in glob.iglob(self._expandPath(files)):
            self._importConfigFile(file)

        nemoa.setLog(indent = '-1')
        return True

    def _importConfigFile(self, file):
        """Import configuration file."""
        # search definition file
        if os.path.isfile(file): configFile = file
        elif os.path.isfile(self.__basepath['workspace'] + file):
            configFile = self.__basepath['workspace'] + file
        else: return nemoa.log('warning',
            "configuration file '%s' does not exist!" % (file))

        # logger info
        nemoa.log("parsing configuration file: '" + configFile + "'")
        nemoa.setLog(indent = '+1')

        # import and register objects without testing
        importer = self.configFileImporter(self)
        objConfList = importer.load(configFile)

        for objConf in objConfList: self._addObjToStore(objConf)
        self._check(objConfList)

        nemoa.setLog(indent = '-1')
        return True

    def _scanScripts(self, files = None):
        """Scan for scripts files (current project)."""
        nemoa.log('scanning for script files')
        nemoa.setLog(indent = '+1')

        # assert script files path
        if files == None: files = self.__path['scripts'] + '*.py'
        # import scripts files
        for file in glob.iglob(self._expandPath(files)):
            self._registerScript(file)

        nemoa.setLog(indent = '-1')
        return True

    def _registerScript(self, file):
        """Register script file (current workspace)."""
        if os.path.isfile(file): scriptFile = file
        elif os.path.isfile(self.__path['scripts'] + file):
            scriptFile = self.__path['scripts'] + file
        else: return nemoa.log('warning',
            "script file '%s' does not exist!" % (file))

        # import and register scripts (without testing)
        importer = self.scriptFileImporter(self)
        script = importer.load(scriptFile)
        self._addObjToStore(script)
        return True

    def _scanNetworks(self, files = None):
        """Scan for network configuration files (current workspace)."""
        nemoa.log('scanning for networks')
        nemoa.setLog(indent = '+1')

        # assert network files path
        if files == None: files = self.__path['networks'] + '*.ini'
        # import network files
        for file in glob.iglob(self._expandPath(files)):
            self._registerNetwork(file)

        nemoa.setLog(indent = '-1')
        return True

    def _registerNetwork(self, file, format = None):
        """Register network (current workspace)."""
        if os.path.isfile(file): networkFile = file
        elif os.path.isfile(self.__path['networks'] + file):
            networkFile = self.__path['networks'] + file
        else: return nemoa.log('warning',
            "network file '%s' does not exist!" % (file))

        # if format is not given get format from file extension
        if not format:
            fileName = os.path.basename(file)
            fileExt  = os.path.splitext(fileName)[1]
            format    = fileExt.lstrip('.').strip().lower()

        # get network configuration from file
        if format == 'ini':
            importer = self.networkConfigFileImporter(self)
            return self._addObjToStore(importer.load(networkFile))

        return nemoa.log('error',
            """could not import network '%s':
            network file format '%s' is currently not supported!
            """ % (file, format))

    def _check(self, objConfList):
        """Check and update object configurations."""
        for objConf in objConfList:
            objConf = self._checkObjConf(objConf)
            if not objConf: self._delObjConf(objConf)
        return True

    def _checkObjConf(self, objConf):
        """Check and update object configuration."""
        if not 'class'  in objConf or not objConf['class']: return None
        if not 'name'   in objConf: return None
        if not 'config' in objConf: return None

        if objConf['class'] == 'network':  return self._checkNetwork(objConf)
        if objConf['class'] == 'dataset':  return self._checkDataset(objConf)
        if objConf['class'] == 'system':   return self._checkSystem(objConf)
        if objConf['class'] == 'schedule': return self._checkSchedule(objConf)
        if objConf['class'] == 'plot':     return objConf

        return None

    def _checkNetwork(self, objConf):
        """Check and update network configuration."""
        type = objConf['class']
        name = objConf['name']
        conf = objConf['config']

        # create 'layer', 'visible' and 'hidden' from 'layers'
        if 'layers' in conf:
            conf['layer']   = []
            conf['visible'] = []
            conf['hidden']  = []
            for layer in conf['layers']:
                if '=' in layer:
                    layerName = layer.split('=')[0].strip()
                    layerType = layer.split('=')[1].strip().lower()
                else:
                    layerName = layer.strip()
                    layerType = 'visible'

                conf['layer'].append(layerName)
                if layerType == 'visible': conf['visible'].append(layerName)
                else: conf['hidden'].append(layerName)
            del conf['layers']

        # get config from source file
        if 'source' in conf:
            if not 'file' in conf['source']: return nemoa.log('warning',
                "skipping network '" + name + "': "
                "missing source information! (parameter: 'source:file')")

            file = conf['source']['file']
            if not self._expandPath(file, check = True): return nemoa.log('warning',
                "skipping network '%s': file '%s' not found!" % (name, file))

            objConf['config']['source']['file'] = self._expandPath(file)

            if not 'file_format' in conf['source']:
                objConf['config']['source']['file_format'] = nemoa.common.getFileExt(file)

            format = objConf['config']['source']['file_format']

            # get network config
            networkCfg = self._registerNetwork(file, format)
            if not networkCfg: return nemoa.log('warning',
                "skipping network '%s'" % (name))
            for key in networkCfg: objConf['config'][key] = networkCfg[key]

        return objConf

    def _checkDataset(self, objConf, frac = 1.0, update = True):
        """Check and update dataset configuration."""

        type = objConf['class']
        name = objConf['name']
        conf = objConf['config']

        # check source
        if not 'source' in conf: return nemoa.log('warning',
            "skipping dataset '" + name + "': "
            "missing source information! (parameter 'source')")

        if not 'file' in conf['source'] \
            and not 'datasets' in conf['source']: return nemoa.log('warning',
            "skipping dataset '" + name + "': "
            "missing source information! (parameter: 'source:file' or 'source:datasets')")

        # update for source type: file
        if 'file' in conf['source']:
            file = conf['source']['file']
            if not self._expandPath(file, check = True): return nemoa.log('warning',
                "skipping dataset '%s': file '%s' not found!" % (name, file))

            # update path for file and set type to 'file'
            conf['source']['file'] = self._expandPath(file)
            conf['type'] = 'file'

            # add missing source information
            if not 'file_format' in conf['source']:
                conf['source']['file_format'] = nemoa.common.getFileExt(file)

            # only update in the first call of checkDatasetConf
            if update: conf['cache_path'] = self.__path['cache']

            return objConf

        # update for source type: datasets
        if 'datasets' in conf['source']:

            # add source table to config (on first call)
            if update: conf['table'] = {}

            srcList = nemoa.common.strToList(conf['source']['datasets'], ',')
            for srcName in srcList:

                # search for dataset object in register by name
                if self._isObjKnown('dataset', srcName):
                   srcID = self._getObjIDByName('dataset', srcName)
                elif self._isObjKnown('dataset', "%s.%s" % (objConf['project'], srcName)):
                   srcName = "%s.%s" % (objConf['project'], srcName)
                   srcID = self._getObjIDByName('dataset', srcName)
                else: return nemoa.log('warning',
                    "skipping dataset '" + name + "': "
                    "unknown dataset source '" + srcName + "'" )

                # recursively get object configuration
                srcObjConf = self._checkDataset(
                    self._getObjByID(srcID),
                    frac = frac / len(srcList),
                    update = False)

                # for files create an entry in the dataset table
                if srcObjConf['config']['type'] == 'file':

                    # update auto fraction
                    srcObjConf['config']['fraction'] = frac / len(srcList)

                    # clean up and link config
                    srcObjConf['config'].pop('type')
                    conf['table'][srcName] = srcObjConf['config']

                # 2do: Test!!!
                elif srcObjConf['config']['type'] == 'compound':
                    for child in srcObjConf['source']['config']['table'].keys():
                        childCnf = srcObjConf['config']['config']['table'][child]

                        if child in objConf['config']['table']:
                            objConf['config']['table'][child]['fraction'] = \
                                objConf['config']['table'][child]['fraction'] + \
                                    childCnf['fraction'] * frac / len(srcList)
                        else:
                            objConf['config']['table'][child] = childCnf
                            objConf['config']['table'][child]['fraction'] = \
                                childCnf['fraction'] * frac / len(srcList)

            objConf['config']['type'] = 'compound'

        if update: objConf['config']['cache_path'] = self.__path['cache']

        return objConf

    def _checkSystem(self, objConf):
        """Check and update system configuration"""
        type = objConf['class']
        name = objConf['name']
        conf = objConf['config']

        if not 'package' in conf: return nemoa.log('warning',
            "skipping system '" + name + "': missing parameter 'package'!")
        if not 'class' in conf: return nemoa.log('warning',
            "skipping system '" + name + "': missing parameter 'class'!")

        conf['description'] = conf['description'].replace('\n', '') \
            if 'description' in conf else conf['name']

        # check if system exists
        try: exec "import nemoa.system." + conf['package']
        except: return nemoa.log('warning',
            "skipping system '%s': package 'system.%s' could not be found!" % (name, conf['package']))
        return objConf

    def _checkSchedule(self, objConf):
        """Check and update schedule configuration"""

        type = objConf['class']
        name = objConf['name']
        conf = objConf['config']

        # create 'system'
        if not 'params' in conf or not conf['params']:
            conf['params'] = {}

            # search systems
            reSystem = re.compile('system [0-9a-zA-Z]*')
            for key in conf.keys():
                if reSystem.match(key):
                    name = key[7:].strip()
                    if not '.' in name:
                        name = objConf['project'] + '.' + name
                    conf['params'][name] = conf[key]
                    del conf[key]

        # 2do: allow stages for optimization schedule

        ## create 'stage'
        #if not 'stage' in conf or not conf['stage']:
            #conf['stage'] = []

            ## search stages
            #reStage = re.compile('stage [0-9a-zA-Z]*')
            #for key in conf.keys():
                #if reStage.match(key):
                    #conf['stage'].append(conf[key])
                    #conf['stage'][len(conf['stage']) - 1]['name'] = key[6:]
                    #del conf[key]

            #if not conf['stage'] and (not 'params' in conf or not conf['params']):
                #nemoa.log('warning',
                    #"skipping schedule '" + name + "': "
                    #"missing optimization parameters! ('params' or 'stage [NAME]')!")
                #return None

        return objConf

    def _addObjToStore(self, objConf):
        """link object configuration to object dictionary."""
        if not isinstance(objConf, dict): return False

        type = objConf['class']
        name = objConf['name']
        config = objConf['config']

        nemoa.log('adding %s: %s' % (type, name))

        key = None
        objID = 0

        if not type in self.__store.keys(): return nemoa.log('error',
            """could not register object '%s':
            unsupported object type '%s'!""" % (name, type))

        key = self._getNewKey(self.__store[type], name)
        objID = self._getObjIDByName(type, key)

        # add configuration to object tree
        self.__store[type][key] = config
        self.__store[type][key]['id'] = objID

        # add entry to index
        self.__index[objID] = {
            'type': type, 'name': key, 'project': objConf['project']}

        return objID

    def _delObjConf(self, objConf):
        """Unlink object configuration from object dictionary."""
        if not objConf: return False
        id = self._getObjIDByName(objConf['class'], objConf['name'])
        if not id in self.__index.keys(): return nemoa.log('warning', '2do')

        # delete entry in index
        self.__index.pop(id)
        return True

    def list(self, type = None, namespace = None):
        """List known object configurations."""

        if type == 'model':
            fileExt = 'nmm'
            searchPath = '%s*.%s' % (self.__path['models'], fileExt)
            models = []
            for model in glob.iglob(searchPath):
                if os.path.isdir(model): continue
                name = os.path.basename(model)[:-(len(fileExt) + 1)]
                models.append(name)
            return sorted(models, key = str.lower)

        if type == 'workspace': # 2DO: Something wents wrong if list is executed from inside
            return sorted(self._listUserWorkspaces())

        objList = []
        for id in self.__index:
            if type and type != self.__index[id]['type']: continue
            if namespace and namespace != self.__index[id]['project']: continue
            objList.append((id, self.__index[id]['type'], self.__index[id]['name']))
        return sorted(objList, key = lambda col: col[2])

    def _isObjKnown(self, type, name):
        """Return True if object is registered."""
        return self._getObjIDByName(type, name) in self.__index

    def _getObjIDByName(self, type, name):
        """Return id of object as integer
        calculated as hash from type and name"""
        return nemoa.common.strToHash(str(type) + chr(10) + str(name))

    def _getObjByID(self, id):
        """Return object from store by id."""
        if not id in self.__index:
            nemoa.log('warning', '2DO')
            return None

        oClass = self.__index[id]['type']
        oName  = self.__index[id]['name']
        oPrj   = self.__index[id]['project']
        oConf  = self.__store[oClass][oName].copy()

        return {'class': oClass, 'name': oName, 'project': oPrj, 'config':  oConf}

    def get(self, type = None, name = None, merge = ['params'], params = None, id = None):
        """Return configuration as dictionary for given object."""
        if not type in self.__store.keys(): return nemoa.log('warning',
            """could not get configuration:
            object class '%s' is not known.""" % type)

        cfg = None

        # get configuration from type and name
        if name:
            if not name in self.__store[type].keys(): return False
            cfg = self.__store[type][name].copy()

        # get configuration from type and id
        elif id:
            for name in self.__store[type].keys():
                if not self.__store[type][name]['id'] == id: continue
                cfg = self.__store[type][name]
            if cfg == None: return nemoa.log('warning',
                """could not get configuration:
                no %s with id %i could be found """ % (type, id))

        # could not identify configuration
        else: return nemoa.log('warning',
            """could not get configuration:
            'id' or 'name' of object is needed!""")

        if not cfg: return None

        # optionaly merge sub dictionaries
        # defined by a list of keys and a dictionary
        if params == None \
            or not isinstance(params, dict)\
            or not nemoa.common.isList(merge): return cfg
        subMerge = cfg
        for key in merge:
            if not isinstance(subMerge, dict): return cfg
            if not key in subMerge.keys(): subMerge[key] = {}
            subMerge = subMerge[key]
        for key in params.keys():
            subMerge[key] = params[key]
            cfg['id'] += self._getObjIDByName('.'.join(merge) + '.' + key, params[key])

        return cfg

    def _expandPath(self, str, check = False, create = False):
        """Return string containing expanded path."""

        path = str.strip()                # clean up input string
        path = os.path.expanduser(path)   # expand unix home directory
        path = self._expandPathEnv(path) # expand nemoa env vars
        path = os.path.expandvars(path)   # expand unix env vars

        # (optional) create directory
        if create and not os.path.exists(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path))

        # (optional) check path
        if check and not os.path.exists(path): return nemoa.log(
            'warning', "directory '%s' does not exist!" % (path))

        return path

    def _expandPathEnv(self, path = ''):
        """Expand nemoa environment variables in string"""

        replace = { 'project': self.__workspace }

        update = True
        while update:
            update = False

            # expand path vars (keys of self.__path)
            for var in self.__path.keys():
                if '%' + var + '%' in path:
                    path   = path.replace('%' + var + '%', self.__path[var])
                    path   = path.replace('//', '/')
                    update = True

            # expand basepath variables (keys of self.__basepath)
            for var in self.__basepath.keys():
                if '%' + var + '%' in path:
                    path   = path.replace('%' + var + '%', self.__basepath[var])
                    path   = path.replace('//', '/')
                    update = True

            # expand other variables (keys of replace)
            for var in replace:
                if '%' + var + '%' in path:
                    path   = path.replace('%' + var + '%', replace[var])
                    path   = path.replace('//', '/')
                    update = True

        return path

    def _getNewKey(self, dict, key):

        if not key in dict: return key

        i = 1
        while True:
            i += 1 # start with 2
            new = '%s (%i)' % (key, i)
            if not new in dict: break

        return new

    # import config file
    class configFileImporter:
        generic  = None
        sections = None
        project  = None

        def __init__(self, config):
            self.generic = {
                'name': 'str',
                'description': 'str' }

            self.sections = {
                'network': {'type': 'str', 'layers': 'list', 'labels': 'list', 'source': 'dict', 'params': 'dict'},
                'dataset': {'preprocessing': 'dict', 'source': 'dict', 'params': 'dict'},
                'system': {'package': 'str', 'class': 'str', 'params': 'dict'},
                'schedule': {'stage [0-9a-zA-Z]*': 'dict', 'system [0-9a-zA-Z]*': 'dict', 'params': 'dict'},
                'plot': {'package': 'str', 'class': 'str', 'params': 'dict'} }

            self.__path = config.path()
            self.project = config.project()

        # object definition / configuration files

        def load(self, file):

            # init parser
            cfg = ConfigParser.ConfigParser()
            cfg.optionxform = str
            cfg.read(file)

            # parse sections and create list with objects
            objects = []
            for section in cfg.sections():
                objCfg = self.__readSection(cfg, section)
                if objCfg: objects.append(objCfg)

            return objects

        def __readSection(self, cfg, section):
            """Parse sections."""

            # use regular expression to match sections
            reSection = re.compile('\A' + '|'.join(self.sections.keys()))
            reMatch = reSection.match(section)
            if not reMatch: return None

            type = reMatch.group()
            name = self.project + '.' + section[len(type):].strip()

            if type in self.sections.keys():
                config = {}

                # add generic options
                for key, frmt in self.generic.items():
                    if key in cfg.options(section): config[key] = \
                        self.__convert(cfg.get(section, key), frmt)
                    else: config[key] = self.__convert('', frmt)

                # add special options (use regular expressions)
                for (regExKey, frmt) in self.sections[type].items():
                    reKey = re.compile(regExKey)
                    for key in cfg.options(section):
                        if not reKey.match(key): continue
                        config[key] = self.__convert(cfg.get(section, key), frmt)

            else: return None

            # get name from section name
            if config['name'] == '': config['name'] = name
            else: name = config['name']

            objCfg = {
                'class': type,
                'name': name,
                'project': self.project,
                'config': config}

            return objCfg

        def __convert(self, str, type):
            if type == 'str': return str.strip().replace('\n', '')
            if type == 'list': return nemoa.common.strToList(str)
            if type == 'dict': return nemoa.common.strToDict(str)
            return str

    # import script files
    class scriptFileImporter:

        def __init__(self, config):
            self.project = config.project()

        def load(self, file):
            name = self.project + '.' + os.path.splitext(os.path.basename(file))[0]
            path = file

            return {
                'class': 'script',
                'name': name,
                'project': self.project,
                'config': {
                    'name': name,
                    'path': path }}

    # import network files
    class networkConfigFileImporter:

        project  = None

        def __init__(self, config):
            self.project = config.project()

        def load(self, file):
            """Return network configuration as dictionary.

            Args:
                file -- ini file containing network configuration"""

            netcfg = ConfigParser.ConfigParser()
            netcfg.optionxform = str
            netcfg.read(file)

            name = os.path.splitext(os.path.basename(file))[0]
            fullname = self.project + '.' + name

            network = {
                'class': 'network',
                'name': fullname,
                'project': self.project,
                'config': {
                    'package': 'base',
                    'class': 'network',
                    'type': None,
                    'name': name,
                    'source': {
                        'file': file,
                        'file_format': 'ini' }}}

            # validate 'network' section
            if not 'network' in netcfg.sections(): return nemoa.log(
                'warning', """could not import network configuration:
                file '%s' does not contain section 'network'!""" % (file))

            # 'name': name of network
            if 'name' in netcfg.options('network'):
                network['config']['name'] = \
                    netcfg.get('network', 'name').strip()
                network['name'] = \
                    self.project + '.' + network['config']['name']

            # 'package': python module containing the network class
            if 'package' in netcfg.options('network'):
                network['config']['package'] = \
                    netcfg.get('network', 'package').strip().lower()

            # 'class': network class
            if 'class' in netcfg.options('network'):
                network['config']['class'] = \
                    netcfg.get('network', 'class').strip().lower()

            # 'type': type of network
            if 'type' in netcfg.options('network'):
                network['config']['type'] = \
                    netcfg.get('network', 'type').strip().lower()
            else: network['config']['type'] = 'auto'

            # 'description': description of the network
            if 'description' in netcfg.options('network'):
                network['config']['description'] = netcfg.get('network', 'type').strip()
            else: network['config']['description'] = ''

            #2do: network dependent sections
            # 'labelformat': annotation of nodes, default: 'generic:string'
            if 'labelformat' in netcfg.options('network'):
                network['config']['label_format'] = netcfg.get('network', 'nodes').strip()
            else: network['config']['label_format'] = 'generic:string'

            # depending on network type, use different arguments
            # to describe the network
            if network['config']['type'] in ['layer', 'multilayer', 'auto']:
                return self._getLayerNetwork(file, netcfg, network)

            return nemoa.log('warning',
                """could not import network configuration:
                file '%s' contains unsupported network type '%s'!""" %
                (file, network['config']['type']))

        def _getLayerNetwork(self, file, netcfg, network):

            config = network['config']

            # 'layers': ordered list of network layers
            if not 'layers' in netcfg.options('network'): return nemoa.log(
                'warning', "file '" + file + "' does not contain parameter 'layers'!")
            else: config['layer'] = nemoa.common.strToList(
                netcfg.get('network', 'layers'))

            # init network dictionary
            config['visible'] = []
            config['hidden']  = []
            config['nodes']   = {}
            config['edges']   = {}

            # parse '[layer *]' sections and add nodes
            # and layer types to network dict
            for layer in config['layer']:
                layerSec = 'layer ' + layer
                if not layerSec in netcfg.sections(): return nemoa.log('warning',
                    "file '" + file + "' does not contain information about layer '" + layer + "'!")

                # get 'type' of layer ('visible', 'hidden')
                if not 'type' in netcfg.options(layerSec): return nemoa.log(
                    'warning', "type of layer '" + layer + "' has to be specified ('visible', 'hidden')!")
                if netcfg.get(layerSec, 'type').lower() in ['visible']:
                    config['visible'].append(layer)
                elif netcfg.get(layerSec, 'type').lower() in ['hidden']:
                    config['hidden'].append(layer)
                else: return nemoa.log('warning',
                    "unknown type of layer '" + layer + "'!")

                # get 'nodes' of layer
                if 'nodes' in netcfg.options(layerSec): nodeList = \
                    nemoa.common.strToList(netcfg.get(layerSec, 'nodes'))
                elif 'size' in netcfg.options(layerSec): nodeList = \
                    ['n' + str(i) for i in range(1,
                    int(netcfg.get(layerSec, 'size')) + 1)]
                elif 'file' in netcfg.options(layerSec):
                    listFile = nemoa.workspace._expandPath(
                        netcfg.get(layerSec, 'file'))
                    if not os.path.exists(listFile): return nemoa.log('error',
                        "listfile '%s' does not exists!" % (listFile))
                    with open(listFile, 'r') as listFile:
                        fileLines = listFile.readlines()
                    nodeList = [node.strip() for node in fileLines]
                else: return nemoa.log('warning',
                    "layer '" + layer + "' does not contain node information!")

                config['nodes'][layer] = []
                for node in nodeList:
                    node = node.strip()
                    if node == '': continue
                    if not node in config['nodes'][layer]:
                        config['nodes'][layer].append(node)

            # check network layers
            if config['visible'] == []: return nemoa.log('error',
                "layer network '" + file + "' does not contain visible layers!")
            # 2DO: allow single layer networks (no hidden layer)
            if config['hidden'] == []: return nemoa.log('error',
                "layer network '" + file + "' does not contain hidden layers!")

            # parse '[binding *]' sections and add edges to network dict
            for i in range(len(config['layer']) - 1):
                layerA = config['layer'][i]
                layerB = config['layer'][i + 1]

                edgeType = layerA + '-' + layerB
                config['edges'][edgeType] = []
                edgeSec = 'binding ' + edgeType

                # create full binfing between two layers if not specified
                if not edgeSec in netcfg.sections():
                    for nodeA in config['nodes'][layerA]:
                        for nodeB in config['nodes'][layerB]:
                            config['edges'][edgeType].append((nodeA, nodeB))
                    continue

                # get edges from '[binding *]' section
                for nodeA in netcfg.options(edgeSec):
                    nodeA = nodeA.strip()
                    if nodeA == '' or \
                        not nodeA in config['nodes'][layerA]: continue
                    for nodeB in nemoa.common.strToList(netcfg.get(edgeSec, nodeA)):
                        nodeB = nodeB.strip()
                        if nodeB == '' \
                            or not nodeB in config['nodes'][layerB] \
                            or (nodeA, nodeB) in config['edges'][edgeType]:
                            continue
                        config['edges'][edgeType].append((nodeA, nodeB))

            # check network binding
            for i in range(len(config['layer']) - 1):
                layerA = config['layer'][i]
                layerB = config['layer'][i + 1]

                edgeType = layerA + '-' + layerB
                if config['edges'][edgeType] == []: return nemoa.log('warning',
                    "layer '%s' and layer '%s' are not connected!" % (layerA, layerB))

            return network