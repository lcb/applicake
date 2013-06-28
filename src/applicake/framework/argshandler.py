"""
Created on Apr 22, 2012

@author: quandtan
"""

from argparse import ArgumentParser

from applicake.utils.dictutils import DictUtils


class ArgsHandler(object):
    """    
    Handler for command line arguments
    """

    def __init__(self):
        self._parser = ArgumentParser(description='Applicake application')
        self._app_argnames = []
        self._runner_argnames = {}

    def add_app_args(self, log, name, description, action='store', default=None, choices=None, type=str):
        """
        Define specific arguments needed by the app
        """
        self._app_argnames.append(name)
        if name in self._runner_argnames.values():
            log.debug("application requested RUNNER arg %s" % name)
            return
        if action is 'store_true' or action is 'store_false':
            self._parser.add_argument("--%s" % name, required=False, dest=name, help=description, action=action,
                                      default=default)
        else:
            self._parser.add_argument("--%s" % name, required=False, dest=name, help=description, action=action,
                                      default=default, choices=choices, type=type)

    def add_runner_args(self, *args, **kwargs):
        """
        Define specific arguments needed by the runner
        """
        if not "dest" in kwargs:
            raise Exception("dest= must be set when defining runner args")
        for arg in args:
            self._runner_argnames[arg] = kwargs["dest"]
        self._parser.add_argument(*args, **kwargs)

    def get_app_argnames(self):
        #used for IniApplicationRunner
        return self._app_argnames

    def get_parsed_arguments(self, log, args):
        """
        Returns arguments parsed by the argument parser: the explicitly set args and the default value args
        
        @type log: Logger 
        @param log: Logger to store log messages  
        @type args: list
        @param args: List of arguments. List structure is assumed to follow sys.argv (meaning the first argument is the name of the python script).  
        """
        pargs = vars(self._parser.parse_args(args))
        # if optional args are not set, a key = None is created, remove these
        pargs = DictUtils.remove_none_entries(pargs)
        #differentiate explicitly set arguments and those with default value (lower priority)
        default_args = pargs.copy()
        set_args = {}
        for arg in list(set(args)):
            if arg[2:] in self._app_argnames:
                log.debug("app argument %s overridden with cmdline" % arg)
                sarg = arg[2:]
                set_args[sarg] = default_args[sarg]
                del default_args[sarg]
            if arg in self._runner_argnames.keys():
                sarg = self._runner_argnames[arg]
                set_args[sarg] = default_args[sarg]
                del default_args[sarg]

        return set_args, default_args
