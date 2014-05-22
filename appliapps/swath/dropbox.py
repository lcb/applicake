#!/usr/bin/env python
import getpass
import os
import subprocess

from applicake.app import BasicApp
from applicake.apputils import dropbox
from applicake.coreutils.arguments import Argument
from applicake.coreutils.info import IniInfoHandler
from applicake.coreutils.keys import Keys, KeyHelp


class Copy2SwathDropbox(BasicApp):
    """
    Copy files to an Openbis generic dropbox.

    """

    def add_args(self):
        return [
            Argument(Keys.ALL_ARGS, KeyHelp.ALL_ARGS),
            Argument(Keys.WORKDIR, KeyHelp.WORKDIR)
        ]

    def run(self, log, info):

        info['WORKFLOW'] = dropbox.extendWorkflowID(info['WORKFLOW'])
        info['WORKFLOW'] += " msproteomicstools@" + subprocess.check_output(
            "awk 'NR==4' /cluster/apps/imsbtools/stable/msproteomicstools/trunk/.svn/entries", shell=True).strip()
        info['WORKFLOW'] += " openms@" + subprocess.check_output(
            "git --git-dir=/cluster/apps/openms/svn-current/OpenMS/.git rev-parse HEAD", shell=True).strip()

        stagebox = dropbox.make_stagebox(log, info)

        #copy and compress align.csv, but not the matrix
        dropbox.keys_to_dropbox(log, info, ['ALIGNMENT_TSV'], stagebox)
        subprocess.check_call('gzip -v ' + stagebox + '/*', shell=True)
        dropbox.keys_to_dropbox(log, info, ['ALIGNMENT_MATRIX','ALIGNER_STDOUT'], stagebox)

        #compress all mprophet files into one zip
        archive = os.path.join(stagebox, 'pyprophet_stats.zip')
        if not 'MPROPHET_STATS' in info:
            info['MPROPHET_STATS'] = []
        if not isinstance(info['MPROPHET_STATS'], list):
            info['MPROPHET_STATS'] = [info['MPROPHET_STATS']]
        for entry in info['MPROPHET_STATS']:
            subprocess.check_call('zip -j ' + archive + ' ' + entry, shell=True)

        #PATCH: reimport old classifier if existing was used
        if 'MPR_LDA_PATH' in info and info['MPR_LDA_PATH'] != "":
            subprocess.check_call('zip -j ' + archive + ' ' + info['MPR_LDA_PATH'], shell=True)

        #SPACE PROJECT given
        dsinfo = {}
        dsinfo['SPACE'] = info['SPACE']
        dsinfo['PROJECT'] = info['PROJECT']
        dsinfo['PARENT_DATASETS'] = info[Keys.DATASET_CODE]
        if info.get("DB_SOURCE", "") == "PersonalDB":
            if isinstance(dsinfo['PARENT_DATASETS'], list):
                dsinfo['PARENT_DATASETS'].append(info["DBASE"])
            else:
                dsinfo['PARENT_DATASETS'] = [dsinfo['PARENT_DATASETS'], info['DBASE']]

        dsinfo['DATASET_TYPE'] = 'SWATH_RESULT'
        dsinfo['EXPERIMENT_TYPE'] = 'SWATH_SEARCH'
        dsinfo['EXPERIMENT'] = dropbox.get_experiment_code(info)
        path = os.path.join(stagebox, 'dataset.attributes')
        IniInfoHandler().write(dsinfo, path)

        expinfo = {}
        expinfo['PARENT-DATA-SET-CODES'] = dsinfo['PARENT_DATASETS']
        for key in ['WORKFLOW', 'COMMENT', 'TRAML', 'EXTRACTION_WINDOW', 'WINDOW_UNIT', 'RT_EXTRACTION_WINDOW',
                    'MIN_UPPER_EDGE_DIST', 'IRTTRAML', 'MIN_RSQ', 'MIN_COVERAGE', 'MPR_NUM_XVAL',
                    'MPR_LDA_PATH', 'MPR_MAINVAR', 'MPR_VARS', 'ALIGNER_FRACSELECTED', 'ALIGNER_MAX_RT_DIFF',
                    'ALIGNER_METHOD', 'ALIGNER_DSCORE_CUTOFF',
                    'ALIGNER_FDR', 'ALIGNER_MAX_FDRQUAL', 'ALIGNER_TARGETFDR', 'DO_CHROMML_REQUANT']:
            if info.get(key, "") != "":
                expinfo[key] = info[key]
        path = os.path.join(stagebox, 'experiment.properties')
        IniInfoHandler().write(expinfo, path)

        #put a copy of the whole ini into the dropbox. copy() to prevent OUTPUT being removed from main ini
        IniInfoHandler().write(info.copy(), os.path.join(stagebox, 'input.ini'))

        dropbox.move_stage_to_dropbox(log, stagebox, info['DROPBOX'], keepCopy=False)

        try:
            command = 'echo "Your SWATH analysis [%s] finished and will show up in openBIS soon!" | ' \
                      'mail -s "SWATH analysis %s finished" %s@ethz.ch' % (
                          dsinfo['COMMENT'],
                          dsinfo['EXPERIMENT'], getpass.getuser())
            subprocess.check_call(command, shell=True)
        except Exception, e:
            log.warn("Sending mail failed: " + e.message)

        return info


if __name__ == "__main__":
    Copy2SwathDropbox.main()