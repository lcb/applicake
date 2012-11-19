'''
Created on Apr 14, 2012

@author: loblum
'''

import os
from applicake.framework.interfaces import IApplication
from applicake.framework.confighandler import ConfigHandler
from applicake.utils.dictutils import DictUtils

class GuseEngineCollector(IApplication):
    """
    Required because 
    1) guse cannot collate, it can only collect all at once
    2) there are some checks if searches went fine or error
    """
     
    
    def main(self,info,log):
        """
        Merge collector files into a single dictionary.
        
        The values of the collector files are flattened. That means if a key value is equal across all
        collector files, the value is kept as single value. If values for the same key differ, a list of
        these values is created.      
        
        @type info: see super class
        @param info: see super class
        @type log: see super class
        @param log: see super class 
        """ 
        
        available_engines = info['ENGINES']
        log.debug("Available engines: %s" % available_engines)
        used_engines = []
        for engine in available_engines:
            key = 'RUN' + engine.upper()
            if key in info and info[key] == 'True':
                used_engines.append(engine)
        
        log.debug("Expected search engine inis: %s" % used_engines)
        
        runs = 1
        infocopy = info.copy()
        infocopy['USED_SEARCHENGINES'] = ' '.join(used_engines)
        del infocopy['ENGINES']
        del infocopy[self.COPY_TO_WD]
        for key,value in infocopy.items():
            if isinstance(value, list):
                log.debug("Runs: %d times %d (key %s)" % (runs,len(value),key))
                runs = runs * len(value)
                
        log.debug("Expected number of inis: %d" % runs)

        for i in range(runs):
            collector_config = {}
            for engine in used_engines:
                path = "%s.ini_%d" % (engine, i)
                if not os.path.exists(path):
                    raise Exception("Required inifile not found "+path)
                config = ConfigHandler().read(log,path)
                collector_config = DictUtils.merge(log,collector_config, config,priority='append')
            
            collector_path = "output.ini_%d" % i   
             
            ConfigHandler().write(collector_config, collector_path)
            log.debug('Wrote outfile '+collector_path)

        return (0,info)
    
    def set_args(self,log,args_handler):
        """
        See interface
        """        
        args_handler.add_app_args(log, 'ENGINES', 'Engines available for doing search',action='append')
        return args_handler

