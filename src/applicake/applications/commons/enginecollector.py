'''
Created on Apr 14, 2012

@author: loblum
'''

import glob
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
        used_engines = []
        for engine in available_engines:
            key = 'RUN' + engine.upper()
            if key in info and info[key]:
                used_engines.append(engine)
        
        log.debug("Expected search engine inis: %s" % used_engines)
        
        runs = 1
        for key,value in info.items():
            if isinstance(value, list):
                runs = runs * len(value)
                
        log.debug("Expected number of inis: %d" % runs)

        for i in range(runs):
            collector_config = {}
            for engine in used_engines:
                path = engine + '.ini_' + i
                config = ConfigHandler().read(log,path)
                collector_config = DictUtils.merge(log,collector_config, config,priority='append')
            
            collector_path = 'output.ini_' + i       
            ConfigHandler().write(collector_config, collector_path)
            log.debug('Wrote outfile '+collector_path)

        return (0,info)
    
    def set_args(self,log,args_handler):
        """
        See interface
        """        
        args_handler.add_app_args(log, 'ENGINES', 'Engines available for doing search',action='append')
        return args_handler


