'''
Created on Apr 14, 2012

@author: quandtan
'''

import os
from applicake.framework.interfaces import IApplication
from applicake.framework.confighandler import ConfigHandler
from applicake.utils.dictutils import DictUtils
from glob import glob

class Collector(IApplication):
    '''
    classdocs
    '''

    def main(self,info,log):
        """
        Collects in
        @type info: see super class
        @param info: see super class
        @type log: see super class
        @param log: see super class 
        """ 
        paths = self.get_input_files(info, log)
        for path in paths:
            config = ConfigHandler().read(path)
            info = DictUtils.merge(info, config,priority='flatten_sequence')        
        return 0
    
    def get_input_files(self,info,log):
        """
        Return all input files following a certain file pattern.
        
        The file pattern depends on the workflow manager and follows usually the same as the generator.
        
        @type info: see super class
        @param info: see super class
        @type log: see super class
        @param log: see super class 
         
        @rtype: list
        @return: list of file paths that match the input file pattern 
        """
        raise NotImplementedError("get_input_files() is not implemented.")
    

class GuseCollector(Collector):
    """
    Collector for the gUSE workflow manager
    """
    
    def get_input_files(self,info,log):
        """
        See super class.
        
        @precondition: 'info' object has to contain the 'INPUT' key.
        """
        return glob("%s/%s.[0-9]*" % (os.path.curdir(),info['INPUT']))