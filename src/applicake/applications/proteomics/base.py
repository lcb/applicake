'''
Created on May 27, 2012

@author: quandtan
'''
from applicake.framework.interfaces import IWrapper

class MsMsIdentification(IWrapper):
    '''
    Basic wrapper class for search engines in MS/MS analysis
    '''
    
    STATIC_MODS = 'STATIC_MODS'
    VARIABLE_MODS = 'VARIABLE_MODS'

    def set_args(self,log,args_handler):
        """
        See super class.
        
        Set several arguments shared by the different search engines
        """        
        args_handler.add_app_args(log, self.PREFIX, 'Path to the OpenMS executable')
        args_handler.add_app_args(log, self.TEMPLATE, 'Path to the template file')
        args_handler.add_app_args(log, 'FRAGMASSERR', 'Fragment mass error')
        args_handler.add_app_args(log, 'FRAGMASSUNIT', 'Unit of the fragment mass error')
        args_handler.add_app_args(log, 'PRECMASSERR', 'Precursor mass error')
        args_handler.add_app_args(log, 'PRECMASSUNIT', 'Unit of the precursor mass error')
        args_handler.add_app_args(log, 'MISSEDCLEAVAGE', 'Number of maximal allowed missed cleavages')
        args_handler.add_app_args(log, 'DBASE', 'Sequence database file')
        args_handler.add_app_args(log, self.STATIC_MODS, 'List of static modifications')
        args_handler.add_app_args(log, self.VARIABLE_MODS, 'List of variable modifications')
        args_handler.add_app_args(log, 'THREADS', 'Number of threads used in the process.')
        args_handler.add_app_args(log, self.WORKDIR, 'Directory to store files')  
        args_handler.add_app_args(log, self.COPY_TO_WD, 'List of files to store in the work directory')   
        return args_handler
    
    def validate_run(self,info,log, run_code,out_stream, err_stream):
        """
        See super class.
        
        Return the unaltered run_code from the tool execution as exit_code.
        """  
        if 0 != run_code:
            return run_code,info
        return 0,info 
 
class OpenMs(IWrapper):
    '''
    Basic wrapper class for OpenMS tools
    '''

    def set_args(self,log,args_handler):
        """
        See super class.
        
        Set several arguments shared by the different search engines
        """        
        args_handler.add_app_args(log, self.PREFIX, 'Path to the OpenMS executable')
        args_handler.add_app_args(log, self.TEMPLATE, 'Path to the openMS-template file')
        args_handler.add_app_args(log, 'THREADS', 'Number of threads used in the process.')
        args_handler.add_app_args(log, self.WORKDIR, 'Directory to store files')  
        args_handler.add_app_args(log, self.COPY_TO_WD, 'List of files to store in the work directory')   
        return args_handler
    
    def validate_run(self,info,log, run_code,out_stream, err_stream):
        """
        See super class.
        
        Return the unaltered run_code from the tool execution as exit_code.
        """    
        return(run_code,info)    
    