'''
Created on Mar 16, 2012

@author: quandtan
'''


class IApplication(object):
    """
    Interface for application that executes python code 
    """
    def main(self,info,log):
        """
        Entry point used to execute the pyton code
        from the implemented interface
        
        Arguments:
        - info: Configuration object to access file and parameter information 
        - log: Logger to store log messages        
        
        Return: Exit code (0 for successful check).         
        """
        raise NotImplementedError("main() is not implemented") 
    
    
class IWrapper(object):   
    """
    Interface for application that wraps an external application
    """
    def prepare_run(self,info,log):
        """
        Prepare the execution of an external program.
        
        Arguments: 
        - config: Configuration object to access file and parameter information 
        - log: Logger to store log messages
        
        Return: The string that contains the command to execute. 
        """
        raise NotImplementedError("prepare_run() is not implemented")  
       
    def validate_run(self,info,log, run_code,out_stream, err_stream):
        """
        Validate the execution of the external application. 
        (e.g. output parsing)
        
        Arguments:
        - info: Configuration object to access file and parameter information        
        - log: Logger to store log messages        
        - run_code: Exit code of the process prepared with prepare_run()  
        - out_stream: Stream object with the stdout of the executed process
        - err_stream: Stream object with the stderr of the executed process 
        
        Return: Exit code (0 for successful check). 
        """
        raise NotImplementedError("prepare_run() is not implemented")      