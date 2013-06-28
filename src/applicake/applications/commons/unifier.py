"""
Created on Jun 20, 2012

@author: quandtan
"""
from applicake.framework.keys import Keys
from applicake.framework.interfaces import IApplication
from applicake.utils.sequenceutils import SequenceUtils
from applicake.utils.dictutils import DictUtils
from applicake.framework.informationhandler import IniInformationHandler


class IniUnifier(IApplication):
    """
    Unify the values of a ini file
    """

    def get_info_handler(self):
        return IniInformationHandler()

    def main(self, info, log):
        """
        See interface.
        
        Does the following:
        - check if reduce option is a single value
        - all keys that contain list-values are reduced to lists with unique members
        - if reduce is set, lists with single values are replaced by that value
        - runner specific keys such as INPUTS are not touched as they are not written to the final output.ini
        """
        #TODO: simplify "wholeinfo" apps
        #re-read INPUT to get access to whole info, needs set_args(INPUT). add runnerargs to set_args if modified by runner
        ini = IniInformationHandler().get_info(log, info)
        info = DictUtils.merge(log, info, ini)

        for key in info.keys():
            if isinstance(info[key], list):
                info[key] = SequenceUtils.unify(info[key], reduce=True)
        return 0, info

    def set_args(self, log, args_handler):
        """
        See interface.
        """
        #TODO: simplify "wholeinfo" apps
        args_handler.add_app_args(log, Keys.INPUT, 're-read input to access whole info')
        args_handler.add_app_args(log, Keys.BASEDIR, 'get basedir if set or modified by runner')
        args_handler.add_app_args(log, Keys.JOB_IDX, 'get jobidx if set or modified by runner')
        args_handler.add_app_args(log, Keys.STORAGE, 'get storage if set or modified by runner')
        args_handler.add_app_args(log, Keys.LOG_LEVEL, 'get loglevel if set or modified by runner')
        return args_handler

    #Outlook:
#def CTDUnifier(IniUnifier):
#    def get_info_handler(self):
#        return CTDInformationHandler()
    
