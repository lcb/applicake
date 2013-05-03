'''
Created on Oct 24, 2012

@author: lorenz
'''

import os
from applicake.framework.interfaces import IWrapper
from applicake.framework.templatehandler import BasicTemplateHandler
from applicake.utils.fileutils import FileUtils

class mProphet(IWrapper):
    _projectname = ''
    def prepare_run(self,info,log):
        
        wd = info[self.WORKDIR]
        info['MPR_PROJECTNAME'] = os.path.splitext(os.path.basename(info['FEATURETSV']))[0]
        self._projectname = info['MPR_PROJECTNAME']
        info['TEMPLATE'] = os.path.join(wd,'mprophet.tpl')
        mod_template,info = mProphetTemplate().modify_template(info, log)
        lda = ''
        if 'MPR_LDA_PATH' in info and info['MPR_LDA_PATH'] != '':
            log.warn("REUSING MPROPHET MODEL")
            lda = 'use_classifier=' + info['MPR_LDA_PATH']
            
        command = 'mProphetScoreSelector.sh %s %s %s && mProphetRunner.sh %s %s' % (info['FEATURETSV'],info['MPR_MAINVAR'],info['MPR_VARS'],mod_template,lda)
        return command,info

    def set_args(self,log,args_handler):
        """
        See interface
        """
        args_handler.add_app_args(log, 'WORKDIR','wd')
        args_handler.add_app_args(log, self.COPY_TO_WD,'cptowd')
        args_handler.add_app_args(log, 'MPR_NUM_XVAL', 'help')
        args_handler.add_app_args(log, 'FEATURETSV', 'featuretsv')
        args_handler.add_app_args(log, 'MPR_LDA_PATH', 'mProphet use existing LDA model')
        args_handler.add_app_args(log, 'MPR_MAINVAR', 'mProphet main score')
        args_handler.add_app_args(log, 'MPR_VARS', 'mProphet other scores')
        return args_handler

    def validate_run(self,info,log, run_code,out_stream, err_stream):
        
        resultfile = os.path.join(info[self.WORKDIR], self._projectname + '_all_peakgroups.xls')
        if not FileUtils.is_valid_file(log, resultfile):
            log.critical('%s is not valid',resultfile)
            return 1,info
        else:
            info['MPROPHET_TSV'] = resultfile
        
        info['MPROPHET_STATS'] = []
        for statfile in ['.pdf','_raw_stat.xls','_stat.xls']:
            fullpath = os.path.join(info[self.WORKDIR],self._projectname + statfile)
            if not FileUtils.is_valid_file(log, fullpath):
                log.critical('%s is not valid',fullpath)
                return 1,info
            else:
                info['MPROPHET_STATS'].append(fullpath)
        
        if info['MPR_LDA_PATH'] != '':
            log.debug("Appending predefined classifier")
            info['MPROPHET_STATS'].append(info['MPR_LDA_PATH'])
        else:
            classifier = os.path.join(info[self.WORKDIR],self._projectname + '_classifier.xls')
            if os.path.exists(classifier):
                info['MPROPHET_STATS'].append(classifier)
            else:
                log.critical("Classifier %s not found" % classifier)
                return 1,info
        
        return run_code,info

        
class mProphetTemplate(BasicTemplateHandler):
    """
    Template handler for mprophet.
    """

    def read_template(self, info, log):
        """
        See super class.

        """
        template =  'run_log=FALSE workflow=LABEL_FREE help=0 ' \
                    'num_xval=$MPR_NUM_XVAL write_classifier=1 write_all_pg=1 ' \
                    'working_dir=$WORKDIR project=$MPR_PROJECTNAME mquest=$FEATURETSV'
        return template,info    
    
