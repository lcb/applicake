'''
Created on Apr 14, 2012

@author: quandtan
'''

import glob
from applicake.framework.interfaces import IApplication
from applicake.framework.confighandler import ConfigHandler
from applicake.utils.dictutils import DictUtils

class BasicCollector(IApplication):
    """
    Basic Collector which merges collector files by flatten the value sequence.
    """

    def _get_collector_files(self,info,log):
        """
        Return all input files following a certain file pattern.
        
        The file pattern depends on the workflow manager and follows usually the same as the generator.
        the list of paths is sorted alphabetically. 
        
        @precondition: 'info' object has to contain the '%s' key.        
        
        @type info: see super class
        @param info: see super class
        @type log: see super class
        @param log: see super class 
         
        @rtype: list
        @return:List of file paths that match the input file pattern
        """ % self.COLLECTOR
        
        collectors = info[self.COLLECTOR]
        collector_files = [] 
        for collector in collectors: 
            pattern = self.get_collector_pattern(collector)
            log.debug('pattern used to search for collector files [%s]' % pattern)
            # merges found collector files for each collector into a single list
            collector_files.extend(glob.glob(pattern))
        collector_files.sort()    
        return collector_files

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
        paths = self._get_collector_files(info, log)
        if len(paths) == 0:
            log.critical('no collector files found [%s]' % paths)
            return (1,info)            
        collector_config  = {}
        for path in paths:
            log.debug('path [%s]' % path)
            config = ConfigHandler().read(log,path)
            log.debug('config [%s]' % config)
            collector_config = DictUtils.merge(collector_config, config,priority='flatten_sequence') 
            log.debug('collector_config [%s]' % collector_config)
        info = DictUtils.merge(info, collector_config, priority='left')
        log.debug('info content [%s]' % info)       
        return (0,info)
    
    def set_args(self,log,args_handler):
        """
        See interface
        """        
        args_handler.add_app_args(log, 'collectors', 'Base name for collecting output files (e.g. from a parameter sweep)',action='append')
        return args_handler
        
    
    def get_collector_pattern(self,filename):
        """
        Return a search pattern based on a filename.
        
        The pattern is specific to the applied workflow manager
        
        @type basename: string
        @param basename: Base name of a collector file which is used to generate the pattern.
        
        @rtype: string
        @return: A pattern used to search for specific files.    
        """
        
        raise NotImplementedError("get_collector_pattern() is not implemented.")  
    

class GuseCollector(BasicCollector):
    """
    Basic collector for the gUSE workflow manager
    """
    
    def get_collector_pattern (self,filename):
        """
        See super class.
        """
        return  "%s_[0-9]*" % (filename)
    
    
class PgradeCollector(BasicCollector):
    """
    Basic collector for the P-Grade workflow manager.
    """   
     
    def get_collector_pattern (self,filename):
        """
        See super class.
        """
        return  "%s.[0-9]*" % (filename)    
    