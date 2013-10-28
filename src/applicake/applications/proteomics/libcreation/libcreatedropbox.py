"""
Created on Aug 10, 2012

@author: lorenz
"""
import os,getpass,time
from configobj import ConfigObj
from applicake.framework.keys import Keys
from applicake.applications.proteomics.openbis.dropbox import Copy2Dropbox
from applicake.framework.informationhandler import IniInformationHandler
from applicake.utils.dictutils import DictUtils


class Copy2LibcreateDropbox(Copy2Dropbox):
    def main(self, info, log):
        #TODO: simplify "wholeinfo" apps
        #re-read INPUT to get access to whole info, needs set_args(INPUT). add runnerargs to set_args if modified by runner
        ini = IniInformationHandler().get_info(log, info)
        info = DictUtils.merge(log, info, ini)

        info['WORKFLOW'] = self._extendWorkflowID(info['WORKFLOW'])
        stagebox = self._make_stagebox(log, info)
        
        info['PEPIDX'] = info[Keys.SPLIB].replace(".splib",".pepidx")
        self._keys_to_dropbox(log, info, [Keys.SPLIB,'PEPIDX','TSV', Keys.TRAML], stagebox)

        dsattr = {}
        dsattr['SPACE'] = 'PERSONAL_DB'
        dsattr['PROJECT'] = 'TRAML'
        dsattr['EXPERIMENT'] = getpass.getuser().upper()
        dsattr['EXPERIMENT_TYPE'] = "PLAIN"
        dsattr['DATASET_TYPE'] = 'TRAML_DB'   
        dsattr['PARENT_DATASETS'] = os.path.basename(os.path.dirname(info[Keys.PEPXMLS]))
        dsattr[Keys.OUTPUT] = os.path.join(stagebox, 'dataset.attributes')
        IniInformationHandler().write_info(dsattr, log)
        
        dsprop = {}
        dsprop['VERSION'] = time.strftime("%Y%m%d%H%M%S")
        dsprop['NAME'] = info.get(Keys.COMMENT,"unnamed")
        dsprop['DESCRIPTION'] = info.get('DESCRIPTION',"undescribed")
        dsprop['WORKFLOW'] = info['WORKFLOW']
        dsprop['HASSPLIB'] = "true"
        
        for key in ["PEPTIDEFDR","MS_TYPE","RSQ_THRESHOLD","RTKIT", "APPLYCHAUVENET","PRECURSORLEVEL","SPECTRALEVEL",
                    "TSV_MASS_LIMITS","TSV_ION_LIMITS","TSV_PRECISION","TSV_CHARGE","TSV_REMOVE_DUPLICATES",
                    "TSV_EXACT","TSV_GAIN","TSV_SERIES","CONSENSUS_TYPE","RUNRT"]:
            dsprop[key] = info[key]

        #TODO: Remove unwrapped use of configobj
        config = ConfigObj(dsprop)
        config.filename = os.path.join(stagebox, 'dataset.properties')
        config.write()

        self._move_stage_to_dropbox(stagebox, info['DROPBOX'], keepCopy=False)

        return 0, info
