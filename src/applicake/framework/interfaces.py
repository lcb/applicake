'''
Created on Mar 16, 2012

@author: quandtan
'''
from applicake.framework.enums import KeyEnum


class IApplication(KeyEnum):
    """
    Interface for application that executes python code 
    """ 
    
    def main(self,info,log):
        """
        Entry point used to execute the pyton code
        from the implemented interface.
        
        @type info: dict         
        @param info: Dictionary object with information needed by the class
        @type log: Logger 
        @param log: Logger to store log messages       
        
        @rtype: (int,dict)
        @return: Tuple of 2 objects; the exit code and the (updated) info object.
        """
        raise NotImplementedError("main() is not implemented")    
     

class IArgsHandler(object):
    """
    Interface for handlers of command line arguments
    """
    
    def define_arguments(self, parser):        
        """
        Define command line arguments of the application.
        
        Helper method for get_parsed_arguments() to assure better inheritance
        from ArgsHandler.
        
        @type parser: argparse.ArgumentParser 
        @param parser: Parser object to which the arguments are added.
        """        
        raise NotImplementedError("define_arguments() is not implemented.")  
    
    def get_parsed_arguments(self, log):
        """
        Parse command line arguments of the application.
        
        @precondition: sys.argv has to be defined as the method uses sys.argv[1:].
        @type log: Logger 
        @param log: Logger to store log messages       
        
        @rtype: dict
        @return: Dictionary of parsed arguments.        
        """
        raise NotImplementedError("get_parsed_arguments() is not implemented.")         

class IInformationHandler(KeyEnum):
    """
    Interface for applications that use a dictionary to provide all necessary information about the application.
    """

    def get_info(self,log,pargs):
        """
        Generate a dictionary with the application information.

        @type log: Logger 
        @param log: Logger to store log messages 
        @type pargs: dict
        @param pargs: Dictionary with the parsed command line arguments
        @rtype: dict
        @return: Dictionary with all information needed to run the application      
        """ 
        raise NotImplementedError("get_info() is not implemented")
    
    def write_info(self,info,log):
        """
        Write info object to new destination such as a file
        
        @type info: dict         
        @param info: Dictionary object with information needed by the class
        @type log: Logger 
        @param log: Logger to store log messages  
        """
        raise NotImplementedError("write_info() is not implemented")


class ITemplateHandler(KeyEnum):
    """
    Interface for handling template files in applications.
    """         
    
    def read_template(self,info,log):
        """
        Read a template from a source.
        
        @type info: dict         
        @param info: Dictionary object with information needed by the class
        @type log: Logger 
        @param log: Logger to store log messages 
        
        @rtype: string
        @return: The template as string.
        """    
        raise NotImplementedError("read_template() is not implemented")    
    
    def replace_vars(self,info,log,template):    
        """
        Replace possible variables in the template string with values from the info object.
        
        @type info: dict         
        @param info: Dictionary object with information needed by the class
        @type log: Logger 
        @param log: Logger to store log messages 
        @type template: string
        @param template: The template as string.  
        
        @rtype: string
        @return: The modified template string.
        """        
        
        raise NotImplementedError("replace_vars() is not implemented")  
        
    def write_template(self,info,log,template):
        """
        Write a template string to a destination defined in the info object
        
        @precondition: info object need the key [%s]
        @type info: dict         
        @param info: Dictionary object with information needed by the class
        @type log: Logger 
        @param log: Logger to store log messages
        @type template: string
        @param template: Write template string to a destination
        """ % self.template_key
        
        raise NotImplementedError("write_template() is not implemented") 
        
    
class IWrapper(KeyEnum):   
    """
    Interface for application that wraps an external application
    """
        
    def prepare_run(self,info,log):
        """
        Prepare the execution of an external program.
        
        @type info: dict         
        @param info: Dictionary object with information needed by the class
        @type log: Logger 
        @param log: Logger to store log messages 
        
        @rtype: (string,dict)
        @return: Tuple of 2 objects; the command to execute and the (updated) info object.
        """
        raise NotImplementedError("prepare_run() is not implemented")  
       
    def validate_run(self,info,log, run_code,out_stream, err_stream):
        """
        Validate the execution of the external application. 
        (e.g. output parsing)
        
        @type info: dict         
        @param info: Dictionary object with information needed by the class
        @type log: Logger 
        @param log: Logger to store log messages 
        @type run_code: int
        @param run_code: Exit code of the process prepared with prepare_run() 
        @type out_stream: Stream
        @param out_stream: Stream object with the stdout of the executed process
        @type err_stream: Stream 
        @param err_stream: Stream object with the stderr of the executed process 
        
        @rtype: (int,dict)
        @return: Tuple of 2 objects; the exit code and the (updated) info object. 
        """
        raise NotImplementedError("prepare_run() is not implemented")      