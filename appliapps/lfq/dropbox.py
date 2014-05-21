#!/usr/bin/env python
import os
import subprocess
import shutil
import getpass

from applicake.app import BasicApp
from applicake.apputils import dropbox
from applicake.coreutils.arguments import Argument
from applicake.coreutils.info import IniInfoHandler
from applicake.coreutils.keys import Keys, KeyHelp


class Copy2QuantDropbox(BasicApp):
    """
    Copy files to an Openbis-quantification-dropbox
    """

    def add_args(self):
        return [
            Argument(Keys.ALL_ARGS, KeyHelp.ALL_ARGS),
            Argument(Keys.WORKDIR, KeyHelp.WORKDIR)
        ]

    def run(self, log, info):
        info['WORKFLOW'] = dropbox.extendWorkflowID(info['WORKFLOW'])
        info['DROPBOXSTAGE'] = dropbox.make_stagebox(log, info)

        #copy files        
        keys = ['PEPCSV', 'PROTCSV', 'CONSENSUSXML']
        dropbox.keys_to_dropbox(log, info, keys, info['DROPBOXSTAGE'])

        #compress TOPPAS files
        archive = os.path.join(info['DROPBOXSTAGE'], 'toppasfiles.zip')
        subprocess.check_call('zip -v ' + archive + '  ' + " ".join(info['TOPPASFILES']), shell=True)

        #compress XML files        
        archive = os.path.join(info['DROPBOXSTAGE'], 'featurexmls.zip')
        subprocess.check_call('zip -jv ' + archive + '  ' + " ".join(info['FEATUREXML']), shell=True)

        #protxml special naming
        filename = os.path.basename(info['DROPBOXSTAGE']) + '.prot.xml'
        filepath = os.path.join(info['DROPBOXSTAGE'], filename)
        shutil.copy(info['PROTXML'], filepath)

        #properties file
        expinfo = info.copy()
        expinfo['PARENT-DATA-SET-CODES'] = info[Keys.DATASET_CODE]
        expinfo['BASE_EXPERIMENT'] = info['EXPERIMENT']
        expinfo['QUANTIFICATION_TYPE'] = 'LABEL-FREE'
        expinfo['PEAKPICKER'] = 'YES'
        expinfo['MAPALIGNER'] = 'YES'

        proppath = os.path.join(info['DROPBOXSTAGE'], 'quantification.properties')
        IniInfoHandler().write(expinfo, proppath)

        #create witolds LFQ report mail
        reportcmd = 'mailLFQ.sh %s %s %s %s' % (proppath, expinfo['PEPCSV'], expinfo['PROTCSV'], getpass.getuser())
        try:
            subprocess.call(reportcmd, shell=True)
            shutil.copy('analyseLFQ.pdf', info['DROPBOXSTAGE'])
        except:
            log.warn("LFQ report command [%s] failed, skipping" % reportcmd)

        dropbox.move_stage_to_dropbox(log, info['DROPBOXSTAGE'], info['DROPBOX'])

        return info


if __name__ == "__main__":
    Copy2QuantDropbox.main()