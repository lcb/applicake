'''
Created on Apr 22, 2012

@author: quandtan
'''

import sys
from applicake.framework.interfaces import IArgsHandler
from applicake.utils.dictutils import DictUtils
from argparse import ArgumentParser

class BasicArgsHandler(IArgsHandler):
    """    
    Basic implementation of the IInformationHandler interface.
    
    Provides control for the following command line arguments:
    -- input,
    -- output,
    -- generator,
    -- collector  
    
    Undefined arguments following the scheme ['--key value'] are accepted. (if a key is defined multiple times,
    only the last values is used).
    If the number of undefined keys and values is odd, none of undefined arguments is parsed.
    If one of the undefined keys does not start with '--', the according key/pair value is excluded.   
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
        
    def get_parsed_arguments(self,log):
        """
        See super class.
        """        
        parser = ArgumentParser(description='Basic argument parser for applicake applications')
        self.define_arguments(parser=parser) 
        pargs = parser.parse_known_args(sys.argv[1:])
        defined_args = vars(pargs[0])
        # if optional args are not set, a key = None is created
        # these have to be removed
        defined_args =DictUtils.remove_none_entries(defined_args)
        log.debug('removed arguments that were not set at command line level')        
        undefined_args = pargs[1]
        undefined_keys = undefined_args[::2]
        undefined_vals = undefined_args[1::2]
        if len(undefined_keys) != len(undefined_vals):
            log.error('Only defined args are considered because number of unknown keys [%s] and values [%s] is not even' % (len(undefined_keys),len(undefined_vals)) )
            return defined_args
        for idx,k in enumerate(undefined_keys):
            if k.startswith('--'):
                key_name = k[2:]
                defined_args[key_name] = undefined_vals[idx]
            else:
                log.error('argument [%s] is not considered because it does not start with "--"') 
        return defined_args 


class ApplicationArgsHandler(BasicArgsHandler):
    """    
    Argument handler for the application class.
    
    Extends the BasicArgsHandler by controlling the following command line arguments:
    -- name,
    -- storage,
    -- loglevel
    
    Undefined arguments are not any longer accepted.
    """ 
    
    def define_arguments(self, parser):
        """
        See super class.
        """
        super(ApplicationArgsHandler, self).define_arguments(parser=parser)      
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

    def get_parsed_arguments(self,log):
        """
        See super class.
        """        
        parser = ArgumentParser(description='Applicake application')
        self.define_arguments(parser=parser) 
        pargs = vars(parser.parse_args(sys.argv[1:]))
        # if optional args are not set, a key = None is created
        # these have to be removed
        pargs =DictUtils.remove_none_entries(pargs)
        log.debug('removed arguments that were not set at command line level')
        return pargs                    
            

class WrapperArgsHandler(ApplicationArgsHandler):
    """
    Argument handler for the wrapper class.
    
    Extends the ApplicationArgsHandler by controlling the following command line arguments:
    -- prefix,
    -- template
    """
    
    def define_arguments(self,parser):
        """
        See super class.
        """
        super(WrapperArgsHandler, self).define_arguments(parser=parser)
        parser.add_argument('-p','--prefix',required=False, dest="PREFIX",
                            help="Prefix of the command to execute")      
        parser.add_argument('-t','--template',required=False, dest="TEMPLATE", 
                            help="Name of the workflow node")     
        
        
        
class BasicArgs(object):
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
    """
    
    def __init__(self):
        self._parser = ArgumentParser(description='Applicake application')
        self._define_runner_args() 
    
    def _define_runner_args(self):
        """
        See super class.
        """
        self._parser.add_argument('-i','--input',required=False,dest="INPUTS", 
                            action='append',help="Input (configuration) file(s)")
        self._parser.add_argument('-o','--output',required=False, dest="OUTPUT",
                            action='store',help="Output (configuration) file")
        self._parser.add_argument('-g','--generator',required=False,dest="GENERATORS", 
                            action='append',help="Base name for generating output files (such as for a parameter sweep)")
        self._parser.add_argument('-c','--collector',required=False, dest="COLLECTORS",
                            action='append',help="Base name for collecting output files (e.g. from a parameter sweep")  
        self._parser.add_argument('-n','--name',required=False, dest="NAME", 
                            help="Name of the workflow node")
        self._parser.add_argument('-s','--storage',required=False, dest="STORAGE", 
                            choices=['memory','file'],
                            help="Storage type for produced streams")  
        self._parser.add_argument('-l','--loglevel',required=False, dest="LOG_LEVEL", 
                            choices=['DEBUG','INFO','WARNING',
                                                  'ERROR','CRITICAL'],
                            help="Storage type for produced streams") 

    def define_app_args(self,log,args):                                   
        try:     
            for name in args:
                log.debug('found argument [%s]...' % name)
                vals = args[name]                 
                log.debug('... with values [%s]' % vals)       
                self._parser.add_argument("--%s" % name,required=False, dest=name,                                 
                                help=vals['description'],action=vals['action'])
        except:
            log.fatal('could not parse arguments' % args)
            sys.exit(1)
    
        
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