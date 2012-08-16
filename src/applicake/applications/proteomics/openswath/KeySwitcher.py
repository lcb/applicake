'''
Created on Aug 14, 2012

@author: blum, wolski
'''

import os
from applicake.framework.interfaces import IApplication
from applicake.framework.templatehandler import BasicTemplateHandler
from applicake.utils.fileutils import FileUtils
from applicake.utils.xmlutils import XmlValidator

class KeySwitcher(IApplication):
    '''
    Wrapper for the ChromatogramExtractor of OpenSWATH.
    '''
    _template_file = ''
    _result_file = ''
    _default_prefix = 'FileMerger'

    def get_prefix(self,info,log):
        if not info.has_key(self.PREFIX):
            info[self.PREFIX] = self._default_prefix
            log.debug('set [%s] to [%s] because it was not set before.' % (self.PREFIX,info[self.PREFIX]))
        return info[self.PREFIX],info

    def main(self,info,log):
        """
        See interface.

        - Define path to result file (depending on work directory)
        - If a template is used, the template is read variables from the info object are used to set concretes.
        - If there is a result file, it is added with a specific key to the info object.
        """
        traml = info["TRAML"]
        info["TRAML"] = info["TRAMLIRT"]
        info["TRAMLIRT"] = traml
        return 0,info

    def set_args(self,log,args_handler):
        args_handler.add_app_args(log, self.PREFIX, 'Path to the executable')
        args_handler.add_app_args(log, 'TRAML', '.') 
        args_handler.add_app_args(log, 'TRAMLIRT', 'merged chrom.mzml file') 
        
