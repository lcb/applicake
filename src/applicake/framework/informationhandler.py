'''
Created on Apr 17, 2012

@author: quandtan
'''

from applicake.framework.confighandler import ConfigHandler
from applicake.framework.interfaces import IInformationHandler
from applicake.utils.dictutils import DictUtils 
from applicake.utils.fileutils import FileUtils
import sys

class BasicInformationHandler(IInformationHandler):
    """    
    Basic implementation of the IInformationHandler interface. 
    """      
    
    def get_info(self,log,pargs):
        """
        See super class.
        
        Command line arguments and arguments in the input file(s) are merged.
        Priority is on the command line arguments.
        Input files are identified by the key %s
        If there are multiple input files, they are merged first by creating value lists.
        If there are no input files pargs is returned.  
        """ % self.INPUT
        
        pargs = pargs.copy()
        if not pargs.has_key(self.INPUT):
            log.debug('content of pargs [%s]' % pargs)
            log.info('pargs did not contain the following key [%s]. Therefore pargs is returned' % self.INPUT)
            return pargs
        else:
            inputs = {}
            for path in pargs[self.INPUT]:
                if not FileUtils.is_valid_file(log, path):
                    log.fatal('Exit program because path [%s] is not valid' % path)
                    sys.exit(1)
                else:
                    config = ConfigHandler().read(log, path)
                    inputs = DictUtils.merge(dict_1=inputs, dict_2=config, priority='flatten_sequence')       
            created_files = {self.COPY_TO_WD:[]}
            inputs = DictUtils.merge(inputs, created_files,priority='right')
            log.debug("Add/reset key [%s] in info object" % self.COPY_TO_WD)
#            prefix = {self.prefix_key: None}
#            inputs = DictUtils.merge(inputs, prefix,priority='right')
#            log.debug("Add/reset key [%s] in info object" % self.prefix_key)                    
            return DictUtils.merge(dict_1=pargs, dict_2=inputs, priority='left') 
        
    def write_info(self,info,log):
        """
        See super class 
        
        Info is written to a single file that is following the Windows INI format. 
        """ 
        if info.has_key(self.OUTPUT):
            path = info[self.OUTPUT]
            log.debug('output file [%s]' % path)  
            remove_keys = [self.INPUT,self.OUTPUT,self.LOG_LEVEL,self.COPY_TO_WD,self.GENERATOR,self.COLLECTOR,self.NAME]
            info_write  = DictUtils.extract(info, remove_keys, include=False)
            log.debug('remove following keys [%s] before writing info' % remove_keys)                 
            ConfigHandler().write(info_write, path) 
            valid = FileUtils.is_valid_file(log, path )
            if not valid:
                log.fatal('Exit program because output file [%s] was not valid' % path)
                sys.exit(1)  
        else:
            log.error('info object did not countain key [%s]. Therefore no output is written' % self.OUTPUT)                                                                                                                                    
                                        