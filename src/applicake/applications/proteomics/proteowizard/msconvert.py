'''
Created on May 10, 2012

@author: quandtan
'''

import os
from applicake.framework.interfaces import IWrapper
from applicake.framework.templatehandler import BasicTemplateHandler

class Mzxml2Mgf(IWrapper):
    """
    Wrapper for msconvert (mzxml -> mgf)
    """
    
    def __init__(self):
        self._default_prefix = 'msconvert'
        base = self.__class__.__name__
        self._template_file = '%s.tpl' % base 
        self._result_file = '%s.mgf' % base     


    def get_prefix(self,info,log):
        if not info.has_key(self.PREFIX):
            info[self.PREFIX] = self._default_prefix
            log.debug('set [%s] to [%s] because it was not set before.' % (self.PREFIX,info[self.PREFIX]))
        return info[self.PREFIX],info  
    
    def get_template_handler(self):
        """
        return Template handler
        """
        return Mzxml2MgfTemplate()    
    
    def prepare_run(self,info,log):
        """
        See interface.
        
        - 
                
        @precondition: info object need the key [%s]
        """ % self.TEMPLATE
        wd = info[self.WORKDIR]
        log.debug('reset path of application files from current dir to work dir [%s]' % wd)
        self._template_file = os.path.join(wd,self._template_file) 
        info['TEMPLATE'] = self._template_file 
        self._result_file = os.path.join(wd,self._result_file) 
        info['MGF'] = self._result_file  
        log.debug('get template handler')
        th = self.get_template_handler()
        log.debug('modify template')                
        mod_template,info = th.modify_template(info, log)        
        prefix,info = self.get_prefix(info,log)
        command = "%s %s --outfile %s -o %s -c %s" %(prefix,info['MZXML'],self._result_filename, wd,info['TEMPLATE']) 
        return command,info  
    
    def set_args(self,log,args_handler):
        """
        See interface
        """    
        args_handler.add_app_args(log, 'MGF', 'Peak list file in mgf format')    
        args_handler.add_app_args(log, 'MZXML', 'Peak list file in mzXML format') 
        args_handler.add_app_args(log, self.WORKDIR, 'Directory to store files')        
        return args_handler      
    
    def validate_run(self,info,log,run_code, out_stream, err_stream):
        """
        See interface
        """
        if 0 != run_code:
            return run_code
        return 0  

class Mzxml2MgfTemplate(BasicTemplateHandler):
    """
    Template handler for Xtandem.  
    """
    def read_template(self, info, log):
        """
        See super class.
        """
        template = """# example configuration file
mgf=true
filter=titleMaker <RunId>.<ScanNumber>.<ScanNumber>.<ChargeState>

#mzXML=true
#zlib=true
#filter="index [3,7]"
#filter="precursorRecalculation"        
        """        
        log.debug('read template from [%s]' % self.__class__.__name__)
        return template,info        