'''
Created on Apr 22, 2012

@author: quandtan
'''

import sys
from applicake.framework.interfaces import IArgsHandler
from applicake.utils.dictutils import DictUtils
from argparse import ArgumentParser

class ApplicationArgsHandler(IArgsHandler):
    """    
    Argument handler for the application class.
    
    Provides control for the following command line arguments:
    -- input,
    -- output,
    -- generator,
    -- collector,
    -- name,
    -- storage,
    -- loglevel
    """ 
    
    def define_arguments(self, parser):
        """
        See super class.
        """
        parser.add_argument('-i','--input',required=False,dest="INPUTS", 
                            action='append',help="Input (configuration) file(s)")
        parser.add_argument('-o','--output',required=False, dest="OUTPUT",
                            action='store',help="Output (configuration) file")
        parser.add_argument('-g','--generator',required=False,dest="GENERATORS", 
                            action='append',help="Base name for generating output files (such as for a parameter sweep)")
        parser.add_argument('-c','--collector',required=False, dest="COLLECTORS",
                            action='append',help="Base name for collecting output files (e.g. from a parameter sweep")               
        parser.add_argument('-n','--name',required=False, dest="NAME", 
#                            default=self.__class__.__name__,
                            help="Name of the workflow node")
        parser.add_argument('-s','--storage',required=False, dest="STORAGE", 
#                            default=None,
                            choices=['memory','file'],
                            help="Storage type for produced streams")  
        parser.add_argument('-l','--loglevel',required=False, dest="LOG_LEVEL", 
#                            default=None,
                            choices=['DEBUG','INFO','WARNING',
                                                  'ERROR','CRITICAL'],
                            help="Storage type for produced streams") 

    def get_parsed_arguments(self):
        """
        See super class.
        """        
        parser = ArgumentParser(description='Applicake application')
        self.define_arguments(parser=parser) 
        args = vars(parser.parse_args(sys.argv[1:]))
        # if optional args are not set, a key = None is created
        # these have to be removed
        args =DictUtils.remove_none_entries(args)
        return args                

#class BasicArgsHandler(IArgsHandler):
#    """    
#    Basic implementation of the IInformationHandler interface. 
#    """  

class WrapperArgsHandler(ApplicationArgsHandler):
    """
    Argument handler for the wrapper class.
    
    Extends the ApplicationArgsHandler by the following command line arguments:
    -- prefix,
    -- template
    """
    
    def define_arguments(self,parser):
        """
        See super class.
        """
        super(WrapperArgsHandler, self).define_arguments(parser=parser)
        parser.add_argument('-p','--prefix',required=False, dest="prefix",
                            help="Prefix of the command to execute")      
        parser.add_argument('-t','--template',required=False, dest="template", 
                            help="Name of the workflow node")     