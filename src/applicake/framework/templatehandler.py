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
    
    def _check_template_key(self,info,log):
        if not info.has_key(self.template_key):
            log.fatal('info does not contain key [%s]: [%s]' % (self.template_key,info))
            sys.exit(1) 

    def read_template(self, info, log):
        """
        Read template from a file location defined in info.
        
        See super class.

        @precondition: info object need the key [%s]
        """ % self.template_key
        
        self._check_template_key(info, log)
        path = info[self.template_key]
        FileUtils.is_valid_file(log, path)
        fh = open(path,'r+')
        template = fh.read()         
        return template
    
    def replace_vars(self, info, log, template):
        """
        See super class.
        """ 
        mod_template = Template(template).safe_substitute(info)
        return mod_template
    
    def write_template(self, info, log, template):
        """
        Write template string to a file location that is defined in\
        the info object
        
        See super class.
        
        @precondition: info object need the key [%s]
        """ % self.template_key
        
        self._check_template_key(info, log)
        path = info[self.template_key]
        FileUtils.is_valid_file(log, path)        
        fh = open(path,'w+')
        fh.write(template)
        fh.close()   
        
             

        