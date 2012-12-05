'''
Created on Oct 24, 2012

@author: lorenz
'''

import os
from applicake.framework.interfaces import IWrapper
from applicake.framework.templatehandler import BasicTemplateHandler
from applicake.utils.fileutils import FileUtils

class mProphet(IWrapper):
    
    def __init__(self):
        """
        Constructor
        """
        base = self.__class__.__name__
        self._result_base = base # result produced by the application  
            
    def get_template_handler(self):
        """
        See interface
        """
        return mProphetTemplate()
    
    
    def prepare_run(self,info,log):
        
        wd = info[self.WORKDIR]
        info['RESULTBASE'] = os.path.join(wd,self._result_base)
        info['TEMPLATE'] = os.path.join(wd,self._result_base + '.tpl')
        log.debug('get template handler')
        th = self.get_template_handler()
        log.debug('modify template')
        mod_template,info = th.modify_template(info, log)

        prefix = 'R'
        command = '%s %s' % (prefix,mod_template)
        return command,info

    def set_args(self,log,args_handler):
        """
        See interface
        """
        args_handler.add_app_args(log, 'WORKDIR','wd')
        args_handler.add_app_args(log, self.COPY_TO_WD,'cptowd')
        args_handler.add_app_args(log, 'MPR_NUM_XVAL', 'help')
        args_handler.add_app_args(log, 'FEATURETSV', 'featuretsv')
        args_handler.add_app_args(log, 'MPROPHET_BINDIR', 'mProphet binary dir')
        return args_handler

    def validate_run(self,info,log, run_code,out_stream, err_stream):
        
        resultfile = os.path.join(info[self.WORKDIR],'mProphet_all_peakgroups.xls')
        if not FileUtils.is_valid_file(log, resultfile):
            log.critical('%s is not valid',resultfile)
            return 1,info
        else:
            info['MPROPHET_TSV'] = resultfile
        
        info['MPROPHET_STATS'] = []
        for statfile in ['mProphet.pdf','mProphet_classifier.xls','mProphet_raw_stat.xls','mProphet_stat.xls']:
            fullpath = os.path.join(info[self.WORKDIR],statfile)
            if not FileUtils.is_valid_file(log, fullpath):
                log.critical('%s is not valid',fullpath)
                return 1,info
            else:
                info['MPROPHET_STATS'].append(fullpath)
            
        return run_code,info

        
class mProphetTemplate(BasicTemplateHandler):
    """
    Template handler for mprophet.
    """

    def read_template(self, info, log):
        """
        See super class.

        """
        template =  '--slave --file=$MPROPHET_BINDIR/mProphet.R --args bin_dir=$MPROPHET_BINDIR ' \
                    'run_log=FALSE workflow=LABEL_FREE help=0 ' \
                    'num_xval=$MPR_NUM_XVAL write_classifier=1 write_all_pg=1 ' \
                    'working_dir=$WORKDIR project=mProphet mquest=$FEATURETSV'
        return template,info    
    
