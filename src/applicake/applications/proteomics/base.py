'''
Created on May 27, 2012

@author: quandtan
'''
import os
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
        args_handler.add_app_args(log, 'DBASE', 'Sequence database file with target/decoy entries')
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
 
class PeptideProteinPreprocessing(OpenMs):
    """
    Base class specifically for OpenMS tools dealing with peptide-protein preprocessing
    """

    _input_file = ''
    _result_file = ''

    def __init__(self):
        """
        Constructor
        """
        base = self.__class__.__name__
        self._input_file = '%s.ini' % base # application specific config file
        self._result_file = '%s.idXML' % base # result produced by the application

    def prepare_run(self,info,log):
        """
        See interface.

        - Read the a specific template and replaces variables from the info object.
        - Tool is executed using the pattern: [PREFIX] -ini [TEMPLATE].
        - If there is a result file, it is added with a specific key to the info object.
        """
        wd = info[self.WORKDIR]
        log.debug('reset path of application files from current dir to work dir [%s]' % wd)
        self._input_file = os.path.join(wd,self._input_file)
        info['TEMPLATE'] = self._input_file
        self._result_file = os.path.join(wd,self._result_file)
        # have to temporarily set a key in info to store the original IDXML
        info['ORGIDXML'] = info['IDXML']
        info['IDXML'] = self._result_file
        log.debug('get template handler')
        th = self.get_template_handler()
        log.debug('modify template')
        mod_template,info = th.modify_template(info, log)
        # can delete temporary key as it is not longer needed
        del info['ORGIDXML']
        prefix,info = self._get_prefix(info,log)
        command = '%s -ini %s' % (prefix,self._input_file)
        return command,info

    def set_args(self,log,args_handler):
        """
        See interface
        """
        args_handler = super(PeptideProteinPreprocessing, self).set_args(log,args_handler)
        args_handler.add_app_args(log, 'IDXML', 'The input idXML file ')
        return args_handler
