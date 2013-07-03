"""
Created on May 27, 2012

@author: quandtan
"""

from applicake.framework.keys import Keys
from applicake.framework.interfaces import IWrapper
from applicake.applications.proteomics.tpp.searchengines.modifications import ModificationDb
from applicake.applications.proteomics.tpp.searchengines.enzymes import EnzymeDb


class SearchEngine(IWrapper):
    """
    Basic wrapper class for search engines in MS/MS analysis
    """

    STATIC_MODS = 'STATIC_MODS'
    VARIABLE_MODS = 'VARIABLE_MODS'
    ENZYME = 'ENZYME'

    _template_file = ''
    _result_file = ''
    _default_prefix = ''

    def __init__(self):
        """
        Constructor
        """
        base = self.__class__.__name__
        self._template_file = '%s.tpl' % base # application specific config file
        self._result_file = '%s.result' % base # result produced by the application    

    def define_enzyme(self, info, log):
        """
        Convert generic enzyme into the program-specific format
        """
        converted_enzyme = EnzymeDb(log).get(info[self.ENZYME], self.__class__.__name__)
        info[self.ENZYME] = converted_enzyme
        return info

    def define_mods(self, info, log):
        """
        Convert generic static/variable modifications into the program-specific format 
        """
        mod_keys = [self.STATIC_MODS, self.VARIABLE_MODS]
        for key in mod_keys:
            if not info.has_key(key):
                info[key] = ''
            else:
                mods = []
                for mod in info[key].split(';'):
                    log.debug('modification [%s]' % key)
                    log.debug('name [%s]')
                    converted_mod = ModificationDb(log).get(mod, self.__class__.__name__)
                    mods.append(converted_mod)
                info[key] = ','.join(mods)
        return info

    def get_prefix(self, info, log):
        if not info.has_key(Keys.PREFIX):
            info[Keys.PREFIX] = self._default_prefix
            log.debug('set [%s] to [%s] because it was not set before.' % (Keys.PREFIX, info[Keys.PREFIX]))
        return info[Keys.PREFIX], info

    def set_args(self, log, args_handler):
        """
        See super class.
        
        Set several arguments shared by the different search engines
        """
        args_handler.add_app_args(log, Keys.PREFIX, 'Path to the executable')
        args_handler.add_app_args(log, Keys.TEMPLATE, 'Path to the template file')
        args_handler.add_app_args(log, 'FRAGMASSERR', 'Fragment mass error')
        args_handler.add_app_args(log, 'FRAGMASSUNIT', 'Unit of the fragment mass error')
        args_handler.add_app_args(log, 'PRECMASSERR', 'Precursor mass error')
        args_handler.add_app_args(log, 'PRECMASSUNIT', 'Unit of the precursor mass error')
        args_handler.add_app_args(log, 'MISSEDCLEAVAGE', 'Number of maximal allowed missed cleavages')
        args_handler.add_app_args(log, 'DBASE', 'Sequence database file with target/decoy entries')
        args_handler.add_app_args(log, Keys.ENZYME, 'Enzyme used to digest the proteins', choices=EnzymeDb().get_keys())
        args_handler.add_app_args(log, Keys.STATIC_MODS, 'List of static modifications',
                                  choices=ModificationDb().get_keys())
        args_handler.add_app_args(log, Keys.VARIABLE_MODS, 'List of variable modifications',
                                  choices=ModificationDb().get_keys())
        args_handler.add_app_args(log, Keys.THREADS, 'Number of threads used in the process.')
        args_handler.add_app_args(log, Keys.WORKDIR, 'Directory to store files')
        return args_handler

    def validate_run(self, info, log, run_code, out_stream, err_stream):
        """
        See super class.
        
        Return the unaltered run_code from the tool execution as exit_code.
        """
        if 0 != run_code:
            return run_code, info
        return 0, info
