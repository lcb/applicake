"""
Created on Jun 19, 2012

@author: quandtan
"""

import os
import subprocess
import shutil
import getpass

from applicake.framework.keys import Keys
from applicake.framework.informationhandler import IniInformationHandler
from applicake.applications.proteomics.openbis.dropbox import Copy2Dropbox

from applicake.utils.dictutils import DictUtils


class Copy2QuantDropbox(Copy2Dropbox):
    """
    Copy files to an Openbis-quantification-dropbox
    """

    def main(self, info, log):
        #TODO: simplify "wholeinfo" apps
        #re-read INPUT to get access to whole info, needs set_args(INPUT). add runnerargs to set_args if modified by runner
        ini = IniInformationHandler().get_info(log, info)
        info = DictUtils.merge(log, info, ini)

        info['DROPBOXSTAGE'] = self._make_stagebox(log, info)

        #copy files        
        keys = ['PEPCSV', 'PROTCSV', 'CONSENSUSXML']
        self._keys_to_dropbox(log, info, keys, info['DROPBOXSTAGE'])

        #compress XML files        
        archive = os.path.join(info['DROPBOXSTAGE'], 'featurexmls.zip')
        subprocess.check_call('zip -jv ' + archive + '  ' + " ".join(info['FEATUREXMLS']), shell=True)

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
        expinfo[Keys.OUTPUT] = os.path.join(info['DROPBOXSTAGE'], 'quantification.properties')
        IniInformationHandler().write_info(expinfo, log)

        #create witolds LFQ report mail
        propcopy = os.path.join(info[Keys.WORKDIR], 'quantification.properties')
        shutil.copy(expinfo[Keys.OUTPUT], propcopy)
        reportcmd = 'mailLFQ.sh ' + propcopy + ' ' + expinfo['PEPCSV'] + ' ' + expinfo[
            'PROTCSV'] + ' ' + getpass.getuser()
        try:
            subprocess.call(reportcmd, shell=True)
            shutil.copy('analyseLFQ.pdf', info['DROPBOXSTAGE'])
        except:
            log.warn("LFQ report command [%s] failed, skipping" % reportcmd)

        self._move_stage_to_dropbox(info['DROPBOXSTAGE'], info['DROPBOX'])

        return 0, info
