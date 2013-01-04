'''
Created on Dec 4, 2012

@author: lorenz
'''
import os, shutil
from applicake.framework.interfaces import IApplication


class CopyTraml(IApplication):

    
    def set_args(self,log,args_handler):
        args_handler.add_app_args(log, 'TRAML', 'traml')
        args_handler.add_app_args(log, 'TRAML_DIR', 'traml folder')
        args_handler.add_app_args(log, 'TRAML_NAME', 'traml folder')
        return args_handler
    
    def main(self, info, log):
        infile = info['TRAML']
        resultfile = os.path.join(info['TRAML_DIR'],info['TRAML_NAME'])
        if os.path.exists(resultfile):
            log.error('TRAMLfile %s already exists! Copy %s yourself!' % resultfile, infile)
            return 1,info
        
        shutil.copy(infile, resultfile)
        print 'Final TraML: %s' % resultfile
        return 0,info