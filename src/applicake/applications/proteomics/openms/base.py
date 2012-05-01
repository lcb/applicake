'''
Created on Apr 29, 2012

@author: quandtan
'''
from applicake.framework.interfaces import IWrapper

class BasicOpenmsWrapper(IWrapper):
    '''
    Basic wrapper class for tools of OpenMS
    '''

    def prepare_run(self,info,log):
        """
        See super class.
        
        Read the a specific template and replaces variables from the info object.
        Tool is executed using the pattern: tools -ini [inifile]
        
        @precondition: info object need the key [%s]
        """ % self.template_key        
        th = self.get_template_handler()
        log.debug('got template handler')
        info = th.modify_template(info, log)
        log.debug('modified template')
        tool = self.get_tool()
        command = '%s -ini %s' % (tool,info[self.template_key])
        return command,info
  
        
    def validate_run(self,info,log, run_code,out_stream, err_stream):
        """
        See super class.
        
        Return the unaltered run_code from the tool execution as exit_code.
        """    
        return(run_code,info)    

    def get_template_handler(self):
        """
        Interface method to inject specific templates.
        
        @rtype: applicake.framework.interfaces.ITemplateHandler
        @return: Specific template handler used for the tool
        """
        raise NotImplementedError("get_template_handler() is not implemented")
    
    def get_tool(self):
        """
        Interface method to define the specific tool.
        
        @rtype: string
        @return: Name of the OpenMS tool that is going to be executed.
        """
        raise NotImplementedError("get_template_handler() is not implemented")
