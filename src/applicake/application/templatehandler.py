'''
Created on Apr 23, 2012

@author: quandtan
'''

import sys
from applicake.framework.interfaces import ITemplateHandler
from applicake.utils.fileutils import FileUtils
from string import Template

class BasicTemplateHandler(ITemplateHandler):
    """
    Basic implementation of the ITemplateHandler interface.
    """
    
    def check_template_key(self,info,log):
        """
        Check if info object has key [%s].
        
        If info does not contain key, a log message is written and the execution is stopped.
        """
        if not info.has_key(self.TEMPLATE):
            log.fatal('Stop application because info does not contain key [%s]: [%s]' % (self.TEMPLATE,info))
            sys.exit(1) 

    def read_template(self, info, log):
        """
        Read template from a file location defined in info.
        
        See super class.

        @precondition: info object need the key [%s]
        """ % self.TEMPLATE
        
        self.check_template_key(info, log)
        path = info[self.TEMPLATE]
        FileUtils.is_valid_file(log, path)
        fh = open(path,'r+')
        template = fh.read()         
        return (template,info)
    
    def _replace_vars(self, info, log, template):
        """
        See super class.
        """ 
        mod_template = Template(template).safe_substitute(info)
        return (mod_template,info)
    
    def _write_template(self, info, log, template):
        """
        Write template string to a file location that is defined in
        the info object.
        
        Add the file location as value to the key [%s] in the info object.
        
        See super class.
        
        @precondition: info object need the keys [%s,%s]
        """ % (self.COPY_TO_WD,self.COPY_TO_WD,self.TEMPLATE)
        
        self.check_template_key(info, log)
        path = info[self.TEMPLATE]      
        fh = open(path,'w+')
        fh.write(template)
        fh.close()
        FileUtils.is_valid_file(log, path) 
        info[self.COPY_TO_WD].append(path)
        log.debug('added [%s] to key [%s]' % (path,self.COPY_TO_WD))
        return info         
        
    def modify_template(self, info, log):
        """
        Convenience method that calls all interface methods. 
        
        Read template, replaces variables possible variables and writes modifications back to the source.
        
        @precondition: info object need the keys [%s,%s]

        @type info: dict         
        @param info: Dictionary object with information needed by the class
        @type log: Logger 
        @param log: Logger to store log messages
        
        @rtype: dict
        @return: The modified info object.
        """ % (self.COPY_TO_WD,self.TEMPLATE)
        
        template,info = self.read_template(info, log)
        mod_template,info = self._replace_vars(info, log, template)
        info = self._write_template(info, log, mod_template)
        return mod_template,info
        
             

def modify_template(template, info):
    mod_template =  Template(template).safe_substitute(info)
    return mod_template
        
def write_template(path, info, log, template):
    fh = open(path,'w+')
    fh.write(template)
    fh.close()
    FileUtils.is_valid_file(log, path) 
    return log

def read_template(path, info, log):
    FileUtils.is_valid_file(log, path)
    fh = open(path,'r+')
    template = fh.read()         
    return (template,info)       