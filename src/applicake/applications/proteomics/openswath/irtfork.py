'''
Created on Oct 24, 2012

@author: lorenz
'''
from applicake.framework.interfaces import IApplication
from applicake.framework.informationhandler import BasicInformationHandler

class IRTFork(IApplication):
    def main(self,info,log):
        irtdic = info.copy()
        irtdic["TRAML"] = irtdic["IRTTRAML"]
        irtdic["OUTSUFFIX"] = irtdic["IRTOUTSUFFIX"]
        irtdic[self.OUTPUT] = irtdic['IRTOUTPUT']
        BasicInformationHandler().write_info(irtdic,log)
        
        info["TRAML"] = info["LIBTRAML"]
        info["OUTSUFFIX"] = info["LIBOUTSUFFIX"]
        return (0,info)

    def set_args(self,log,args_handler):
        """
        See interface
        """
        args_handler.add_app_args(log, "IRTOUTPUT", 'IRT Output (configuration) file', action='store')
        args_handler.add_app_args(log, "IRTTRAML", 'Traml used by chromextractIRT', action='append')
        args_handler.add_app_args(log, "IRTOUTSUFFIX", 'Suffix used by chromextractIRT', action='append')
        args_handler.add_app_args(log, "LIBTRAML", 'Traml used by chromextract ', action='append')
        args_handler.add_app_args(log, "LIBOUTSUFFIX", 'Suffix used by chromextract', action='append')
        return args_handler

