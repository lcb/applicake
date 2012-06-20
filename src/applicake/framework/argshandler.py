'''
Created on Apr 22, 2012

@author: quandtan
'''

import sys
from applicake.utils.dictutils import DictUtils
from argparse import ArgumentParser


        
        
class ArgsHandler(object):
    """    
    Basic implementation of the IInformationHandler interface.
    
    Provides control for the following command line arguments (for the runner):
    -- input,
    -- output,
    -- generator,
    -- collector  
    -- name,
    -- storage,
    -- loglevel
    -- move
    """
    
    def __init__(self):
        self._parser = ArgumentParser(description='Applicake application')
        self._define_runner_args()
        self._app_argnames = [] 
    
    def _define_runner_args(self):
        """
        Define specific arguments needed by the runner
        """
        self._parser.add_argument('-i','--INPUTS',required=False,dest="INPUTS", 
                            action='append',help="Input (configuration) file(s)")
        self._parser.add_argument('-o','--OUTPUT',required=False, dest="OUTPUT",
                            action='store',help="Output (configuration) file") 
        self._parser.add_argument('-n','--NAME',required=False, dest="NAME", 
                            help="Name of the workflow node")
        self._parser.add_argument('-s','--STORAGE',required=False, dest="STORAGE", 
                            choices=['memory','file'],
                            help="Storage type for produced streams")  
        self._parser.add_argument('-l','--LOG_LEVEL',required=False, dest="LOG_LEVEL", 
                            choices=['DEBUG','INFO','WARNING',
                                                  'ERROR','CRITICAL'],
                            help="Storage type for produced streams") 
        self._parser.add_argument('-d','--BASEDIR',required=False, dest="BASEDIR", 
                            help="Base directory used to store files produced by the application")
        # use default=None in order to better control settings of default values in the runner
        self._parser.add_argument('-p','--PRINT_NO_LOG',required=False, dest="PRINT_NO_LOG",
                                  action="store_false",default=None,
                                  help="If set, log is not printed to stderr before exit. (This is independent of the storage type!).")            

    def add_app_args(self,log,name,description,action='store',default=None,choices=None):
        
        name = name.upper()
        self._app_argnames.append(name)
        log.debug('argument name [%s]' % name)
        log.debug('description [%s]' % description)
        log.debug('action [%s]' % action)     
        self._parser.add_argument("--%s" % name,required=False, dest=name,                                 
                        help=description,action=action, default=default, choices=choices)        
    
    
    def get_app_argnames(self):
        return self._app_argnames
            
    def get_parsed_arguments(self,log):
        """
        See super class.
        """       
        pargs = vars(self._parser.parse_args(sys.argv[1:]))
        # if optional args are not set, a key = None is created
        # these have to be removed
        pargs = DictUtils.remove_none_entries(pargs)
        log.debug('removed arguments that were not set at command line level')
        return pargs 
    
    def print_help(self):
        self._parser.print_help()