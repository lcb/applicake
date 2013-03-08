'''
Created on Apr 14, 2012

@author: loblum
'''

import glob
from applicake.framework.interfaces import IApplication
from applicake.framework.confighandler import ConfigHandler
from applicake.utils.dictutils import DictUtils
from applicake.utils.sequenceutils import SequenceUtils

class SequestMerger(IApplication):
    
    def unifyCleanInfo(self,info):
        for key in info.keys():
            if isinstance(info[key], list):
                info[key] = SequenceUtils.unify(info[key], reduce = True)    
            
        if info.has_key(self.WORKDIR):        
            del info[self.WORKDIR]
        if info.has_key('FILE_IDX'):
            info['FILE_IDX'] = 0
        return info  
            
    def main(self,info,log):        
        collector_config = {}
        pattern = "%s_[0-9]*" % info['COLLECTORS']
        for path in glob.glob(pattern):
            config = ConfigHandler().read(log,path)
            collector_config = DictUtils.merge(log,collector_config, config,priority='append')
            
        unified_config = self.unifyCleanInfo(collector_config)
        
        return (0,unified_config)
    
    def set_args(self,log,args_handler):
        """
        See interface
        """        
        args_handler.add_app_args(log, 'COLLECTORS', 'Engines available for doing search')
        return args_handler

