'''
Created on Jun 19, 2012

@author: quandtan
'''

import os,subprocess,shutil
from applicake.framework.interfaces import IApplication
from applicake.utils.fileutils import FileUtils
from applicake.framework.informationhandler import BasicInformationHandler

class Copy2Dropbox(IApplication):
    '''
    Copy certain files to the openbis dropbox.
    '''
    
    def _get_experiment_code(self,info):
        ecode = 'E' + info[self.JOB_IDX]  
        if info.has_key(self.PARAM_IDX):
            ecode = '%s_%s' % (ecode,info[self.PARAM_IDX])
        if info.has_key(self.FILE_IDX):
            ecode = '%s_%s' % (ecode,info[self.FILE_IDX])   
        return ecode
    
    def _make_stagebox(self,log,info):
        ecode = self._get_experiment_code(info)  
        dirname = '%s+%s+%s' % (info['SPACE'], info['PROJECT'],ecode)
        dirname = os.path.join(info[self.WORKDIR],dirname)
        
        FileUtils.makedirs_safe(log, dirname,clean=True)
        return dirname
    
    def _keys_to_dropbox(self,log,info,keys,tgt):
        for key in keys:
            if not info.has_key(key):
                raise Exception('key [%s] not found in info' % key)
            files = []
            if isinstance(info[key], list):
                files = info[key]
            else:
                files = [info[key]]
            for file in files:
                try:
                    log.debug('Copy [%s] to [%s]' % (file,tgt))
                    shutil.copy(file,tgt)
                except:
                    if FileUtils.is_valid_file(log, file):
                        log.debug('File [%s] already exists, ignore' % file)
                    else:
                        log.fatal('Stop program because could not copy [%s] to [%s]' % (file,tgt))
                        raise       

    def _move_stage_to_dropbox(self,stage,dropbox,keepCopy=False):
        if keepCopy == True:
            shutil.copytree(stage,stage+'_copy')
        shutil.move(stage,dropbox)
        #subprocess.call( ('chmod -vR 777 '+dropbox).split() )
        
    def set_args(self,log,args_handler): 
        log.info("Arghandler not needed for IniFileRunner")
        return args_handler
    
class Copy2IdentDropbox(Copy2Dropbox):
    
    def main(self,info,log):
        """
        See super class.
        """
        info['DROPBOXSTAGE'] = self._make_stagebox(log, info)
        
        keys = ['PEPXMLS','PEPCSV']
        self._keys_to_dropbox(log, info, keys, info['DROPBOXSTAGE'])
        
        #protxml special naming
        filename = os.path.basename(info['DROPBOXSTAGE']) + '.prot.xml'
        filepath = os.path.join(info['DROPBOXSTAGE'],filename)
        shutil.copy(info['PROTXML'],filepath)
        
        #search.properties
        info['PEPTIDEFDR'] = info['FDR']
        del info['FDR']
        # need to add DBASENAME
        info['DBASENAME'] = os.path.splitext(os.path.split(info['DBASE'])[1])[0]
        # need to set PARENT-DATASET-CODES
        info['PARENT-DATA-SET-CODES']=info[self.DATASET_CODE]
        # set values to NONE if they were e.g. "" before
        check_keys = ['STATIC_MODS','VARIABLE_MODS']
        for key in check_keys:
            if not info.has_key(key) or info[key] == "":
                info[key] = 'NONE'
        info['experiment-code'] = self._get_experiment_code(info)
        
        sinfo = info.copy()
        sinfo[self.OUTPUT] = os.path.join(info['DROPBOXSTAGE'],'search.properties')
        BasicInformationHandler().write_info(sinfo, log)
        
        self._move_stage_to_dropbox(info['DROPBOXSTAGE'], info['DROPBOX'],keepCopy=True)
        
        return 0,info


class Copy2DropboxQuant(Copy2Dropbox):
    """
    Copy files to an Openbis-quantification-dropbox
    """
    
    def main(self,info,log):
        info['DROPBOXSTAGE'] = self._make_stagebox(log, info)
        
        keys = ['PEPCSV','PROTCSV','FEATUREXMLS']
        self._keys_to_dropbox(log, info, keys, info['DROPBOXSTAGE'])
        
        #protxml special naming
        filename = os.path.basename(info['DROPBOXSTAGE']) + '.prot.xml'
        filepath = os.path.join(info['DROPBOXSTAGE'],filename)
        shutil.copy(info['PROTXML'],filepath)

        expinfo = info.copy()
        expinfo['PARENT-DATA-SET-CODES'] = info[self.DATASET_CODE]
        expinfo['BASE_EXPERIMENT'] = info['EXPERIMENT']
        expinfo['QUANTIFICATION_TYPE'] = 'LABEL-FREE'
        expinfo['PEAKPICKER'] = 'YES'
        expinfo['MAPALIGNER'] = 'YES'
        expinfo[self.OUTPUT] = os.path.join(info['DROPBOXSTAGE'],'quantification.properties')
        BasicInformationHandler().write_info(expinfo, log)
        
        subprocess.check_call(('gzip -v '+ info['DROPBOXSTAGE'] + '/*.featureXML'),shell=True)

        reportcmd = 'mailLFQ.sh ' + expinfo[self.OUTPUT] + ' ' + expinfo['PEPCSV'] + ' '+ expinfo['PROTCSV'] + ' '+ expinfo['USERNAME']
        try:
            subprocess.call(reportcmd,shell=True)
            shutil.copy('analyseLFQ.pdf',info['DROPBOXSTAGE'])
        except:
            log.warn("LFQ report command [%s] failed, skipping"%reportcmd)
        
        self._move_stage_to_dropbox(info['DROPBOXSTAGE'], info['DROPBOX'])
     
        return 0,info