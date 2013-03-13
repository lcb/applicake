'''
Created on Jun 19, 2012

@author: quandtan
'''

import os,subprocess,shutil
from applicake.framework.interfaces import IApplication
from applicake.utils.fileutils import FileUtils
from applicake.framework.informationhandler import BasicInformationHandler
from applicake.framework.templatehandler import BasicTemplateHandler

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
        
        info[self.TEMPLATE] = 'mailtext.txt'
        _,info = MailTemplate().modify_template(info, log)
        shutil.copy(info[self.TEMPLATE],info['DROPBOXSTAGE'])
        
        self._move_stage_to_dropbox(info['DROPBOXSTAGE'], info['DROPBOX'],keepCopy=True)
        
        return 0,info


class MailTemplate(BasicTemplateHandler):
    """
    Template handler for Mzxml2Mzml.
    """

    def read_template(self, info, log):
        try:
            tandemver = ''
            if info['RUNTANDEM'] == True:
                tandemver = subprocess.check_output(['which','tandem.exe']).split('/')[4]
            omssaver = ''
            if info['RUNOMSSA'] == True:
                omssaver = subprocess.check_output(['which','omssacl']).split('/')[4]
            myriver = ''
            if info['RUNMYRIMATCH'] == True:
                myriver = subprocess.check_output(['which','myrimatch']).split('/')[4]
            tppver = subprocess.check_output(['which','ProteinProphet']).split('/')[4]
            info['EXPERIMENT_CODE'] = info['experiment-code']
            template = """Dear $USERNAME
    
Your TPP search workflow finished sucessfully!
    
To visualize the results with Petunia see:
https://imsb-ra-tpp.ethz.ch/browse/$USERNAME/html/tpp2viewer_$EXPERIMENT_CODE.pep.shtml
https://imsb-ra-tpp.ethz.ch/browse/$USERNAME/html/tpp2viewer_$EXPERIMENT_CODE.prot.shtml
    
In case the links do not work (i.e. you chose RUNPETUNIA=none, or the files were already deleted) you can restore the data using the command:
[user@imsb-ra-tpp~] % cd html; tpp2viewer2.py $EXPERIMENT_CODE
    
To cite this workflow use:
The spectra were searched using the search engines %s %s %s
against the $DBASE database using $ENZYME digestion and allowing $MISSEDCLEAVAGE missed cleavages.
Included were '$STATIC_MODS' as static and '$VARIABLE_MODS' as variable modifications. The mass tolerances were set to $PRECMASSERR $PRECMASSUNIT for precursor-ions and $FRAGMASSERR $FRAGMASSUNIT for fragment-ions.
The identified peptides were processed and analyzed through the Trans-Proteomic Pipeline (%s) using PeptideProphet, iProphet and ProteinProphet scoring. Peptide identifications were reported at FDR of $FDR.
    
Yours sincerely,
The iPortal team
    
Please note that this message along with your results are stored in openbis:
https://openbis-phosphonetx.ethz.ch/openbis/#action=BROWSE&entity=EXPERIMENT&project=/$SPACE/$PROJECT""" % (tandemver,omssaver,myriver,tppver)
        except:
            Exception ("Creating mail summary failed")
        return template,info


class Copy2DropboxQuant(Copy2Dropbox):
    """
    Copy files to an Openbis-quantification-dropbox
    """
    
    def main(self,info,log):
        info['DROPBOXSTAGE'] = self._make_stagebox(log, info)

        #copy files        
        keys = ['PEPCSV','PROTCSV','FEATUREXMLS','CONSENSUSXML']
        self._keys_to_dropbox(log, info, keys, info['DROPBOXSTAGE'])

        #compress XML files        
        subprocess.check_call(('gzip -v '+ info['DROPBOXSTAGE'] + '/*XML'),shell=True)

        #protxml special naming
        filename = os.path.basename(info['DROPBOXSTAGE']) + '.prot.xml'
        filepath = os.path.join(info['DROPBOXSTAGE'],filename)
        shutil.copy(info['PROTXML'],filepath)

        #properties file
        expinfo = info.copy()
        expinfo['PARENT-DATA-SET-CODES'] = info[self.DATASET_CODE]
        expinfo['BASE_EXPERIMENT'] = info['EXPERIMENT']
        expinfo['QUANTIFICATION_TYPE'] = 'LABEL-FREE'
        expinfo['PEAKPICKER'] = 'YES'
        expinfo['MAPALIGNER'] = 'YES'
        expinfo[self.OUTPUT] = os.path.join(info['DROPBOXSTAGE'],'quantification.properties')
        BasicInformationHandler().write_info(expinfo, log)
        
        #create witolds LFQ report mail
        reportcmd = 'mailLFQ.sh ' + expinfo[self.OUTPUT] + ' ' + expinfo['PEPCSV'] + ' '+ expinfo['PROTCSV'] + ' '+ expinfo['USERNAME']
        try:
            subprocess.call(reportcmd,shell=True)
            shutil.copy('analyseLFQ.pdf',info['DROPBOXSTAGE'])
        except:
            log.warn("LFQ report command [%s] failed, skipping"%reportcmd)
        
        self._move_stage_to_dropbox(info['DROPBOXSTAGE'], info['DROPBOX'])
     
        return 0,info