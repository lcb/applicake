"""
Created on 13 May 2013

@author: lorenz
"""

import os
import subprocess
import shutil
import getpass

from applicake.framework.keys import Keys
from applicake.framework.templatehandler import BasicTemplateHandler
from applicake.applications.proteomics.openbis.dropbox import Copy2Dropbox

from applicake.framework.informationhandler import IniInformationHandler
from applicake.utils.dictutils import DictUtils


class Copy2IdentDropbox(Copy2Dropbox):
    def main(self, info, log):
        """
        See super class.
        """
        #TODO: simplify "wholeinfo" apps
        #re-read INPUT to get access to whole info, needs set_args(INPUT). add runnerargs to set_args if modified by runner
        ini = IniInformationHandler().get_info(log, info)
        info = DictUtils.merge(log, info, ini)
        info['DROPBOXSTAGE'] = self._make_stagebox(log, info)

        keys = ['PEPXMLS', 'PEPCSV']
        self._keys_to_dropbox(log, info, keys, info['DROPBOXSTAGE'])

        #protxml special naming
        filename = os.path.basename(info['DROPBOXSTAGE']) + '.prot.xml'
        filepath = os.path.join(info['DROPBOXSTAGE'], filename)
        shutil.copy(info['PROTXML'], filepath)

        #search.properties requires some specific fields
        info['PEPTIDEFDR'] = info['FDR']
        info['DBASENAME'] = os.path.splitext(os.path.split(info['DBASE'])[1])[0]
        info['PARENT-DATA-SET-CODES'] = info[Keys.DATASET_CODE]

        # set values to NONE if they were e.g. "" before
        check_keys = ['STATIC_MODS', 'VARIABLE_MODS']
        for key in check_keys:
            if not info.has_key(key) or info[key] == "":
                info[key] = 'NONE'
        info['experiment-code'] = self._get_experiment_code(info)

        sinfo = info.copy()
        sinfo[Keys.OUTPUT] = os.path.join(info['DROPBOXSTAGE'], 'search.properties')
        IniInformationHandler().write_info(sinfo, log)

        info[Keys.TEMPLATE] = 'mailtext.txt'
        th = MailTemplate()
        _, info = th.modify_template(info, log)
        shutil.copy(info[Keys.TEMPLATE], info['DROPBOXSTAGE'])

        info['DROPBOXSTAGE'] = self._move_stage_to_dropbox(info['DROPBOXSTAGE'], info['DROPBOX'], keepCopy=True)

        return 0, info


class MailTemplate(BasicTemplateHandler):
    def read_template(self, info, log):
        template = ''
        if not 'RUNTANDEM' in info:
            #template is empty if TPP-petunia specific key is not found (e.g. sequest or mascot import)
            log.info("No key RUNTANDEM found, skipping mail creation")
        else:
            tandemver = ''
            if info['RUNTANDEM'] == 'True':
                tandemver = 'tandem (version ' + subprocess.check_output("tandem a | grep TANDEM", shell=True).strip() + ')'
            omssaver = ''
            if info['RUNOMSSA'] == 'True':
                omssaver = 'omssa (version ' + subprocess.check_output(['which', 'omssacl']).split('/')[4] + ')'
            myriver = ''
            if info['RUNMYRIMATCH'] == 'True':
                myriver = 'myrimatch (version ' + subprocess.check_output(['which', 'myrimatch']).split('/')[4] + ')'
            tppver = subprocess.check_output(['which', 'ProteinProphet']).split('/')[4]
            info['EXPERIMENT_CODE'] = info['experiment-code']
            info['USERNAME'] = getpass.getuser()
            if info['RUNPETUNIA'] == 'none':
                runmsg = "RUNPETUNIA was set none. To make the links above work please run first:"
            else:
                runmsg = "In case the links do not work they can be restored with:"
            template = """Dear $USERNAME
    
Your TPP search workflow finished sucessfully!

To visualize the results with Petunia see:
https://imsb-ra-tpp2.ethz.ch/browse/$USERNAME/html/petunia/tpp2viewer_$EXPERIMENT_CODE.pep.shtml
https://imsb-ra-tpp2.ethz.ch/browse/$USERNAME/html/petunia/tpp2viewer_$EXPERIMENT_CODE.prot.shtml
    
%s
[user@imsb-ra-tpp~] # cd ~/html/petunia; tpp2viewer2.py $EXPERIMENT_CODE
    
To cite this workflow use:
The spectra were searched using the search engines %s %s %s
against the $DBASE database using $ENZYME digestion and allowing $MISSEDCLEAVAGE missed cleavages.
Included were '$STATIC_MODS' as static and '$VARIABLE_MODS' as variable modifications. The mass tolerances were set to $PRECMASSERR $PRECMASSUNIT for precursor-ions and $FRAGMASSERR $FRAGMASSUNIT for fragment-ions.
The identified peptides were processed and analyzed through the Trans-Proteomic Pipeline (%s) using PeptideProphet, iProphet and ProteinProphet scoring. Peptide identifications were reported at FDR of $FDR.
    
Yours sincerely,
The iPortal team
    
Please note that this message along with your results are stored in openbis:
https://openbis-phosphonetx.ethz.ch/openbis/#action=BROWSE&entity=EXPERIMENT&project=/$SPACE/$PROJECT""" % (
            runmsg, tandemver, omssaver, myriver, tppver)
        
        return template, info


