'''
Created on Mar 16, 2012

@author: quandtan
'''
from applicake.framework.enums import KeyEnum

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