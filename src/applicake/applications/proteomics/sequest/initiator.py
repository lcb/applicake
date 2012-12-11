'''
Based on the original applicake WFInit as good as possible.
It was not possible to use the original 1to1 because for sequest I need to
do several external 'ssh' calls before I have all information to start.
        
Created on Feb 20, 2012

@author: lorenz
'''

import os, sys, subprocess
 
from applicake.applications.commons.generator import Generator


class SequestInitiator(Generator):
    
    def set_args(self,log,args_handler):
        args_handler.add_app_args(log, 'SEQUESTHOST' , 'Sequest host (1 or 2)')
        args_handler.add_app_args(log, 'SEQUESTRESULTPATH' , 'Sequest result path (/home/sorcerer/output/????)')
        args_handler.add_app_args(log, 'GENERATORS' , 'Basename for output inis') 
        args_handler.add_app_args(log, self.WORKDIR, 'Workdir') 
        return args_handler
    
    def main(self,info,log):
        ##First read the info and add the additional entries from sequest.params
        #copy params file from sorcerer
        sorcAddr = 'sorcerer@imsb-ra-sorcerer' + info['SEQUESTHOST'] + '.ethz.ch'
        sorcPath = '/home/sorcerer/output/' + info['SEQUESTRESULTPATH'] + '/original/'
        
        info = self.addParamsToInfo(sorcAddr+":"+ sorcPath, info)
        info = self.getAndCheckDB(sorcAddr, info,log)
        dicts = self.getPepxmlAndCodes(info, log,sorcAddr,sorcPath);
        self.write_files(info, log, dicts)
        return 0,info
     
    def addParamsToInfo(self,sorcpath,info):
        paramfile = os.path.join(info[self.WORKDIR], 'sequest.params')
        try:
            subprocess.check_call(['rsync', '-vrtz', sorcpath + 'sequest.params', paramfile])
        except:
            raise Exception("Cannot get params from sorcerer. Did you check passwordless SSH? Does file exist?")
        
        #transform sorcerer params to info.ini & write out
        info["FRAGMASSUNIT"] = 'NA'
        info["FRAGMASSERR"] = 'NA'
        info["STATIC_MODS"] = 'NA'
        info["VARIABLE_MODS"] = 'NA'
        info['ENZYME'] = 'Trypsin'
        for line in open(paramfile).readlines():
            if 'peptide_mass_tolerance' in line:
                info["PRECMASSERR"] = line.split()[2]
            if 'max_num_internal_cleavage_sites' in line:
                info["MISSEDCLEAVAGE"] = line.split()[2]
            if 'peptide_mass_units' in line:
                sequestunits = {"0":"amu", "1":"mmu", "2":"ppm" }
                info["PRECMASSUNIT"] = sequestunits[line.split()[2]]
            if line.startswith('database_name'):
                info['SEQUESTDBASE'] = line.split()[2]
            if line.startswith('num_enzyme_termini = 2'):
                info['ENZYME'] = 'Semi-Tryptic'  
        return info
    
    def getAndCheckDB(self,sorcAddr,info,log):
        info['DBASE'] = os.path.join(info[self.WORKDIR], os.path.basename(info['SEQUESTDBASE']))
        print 
        try:
            subprocess.check_call(['rsync', '-vrtz', sorcAddr + ':' + info['SEQUESTDBASE'], info['DBASE']])
        except:
            raise Exception("Couldnt copy fasta dbase from sorcerer")
        hasDecoys = False;
        with open(info['DBASE']) as r:
            for line in r.readlines():
                if line.find('DECOY_') != -1:
                    hasDecoys = True;
        if not hasDecoys:
            log.critical("No DECOY_s in fasta found!")
            sys.exit(1)
        return info
    
    def getPepxmlAndCodes(self,info,log,sorcAddr,sorcPath):
        pepxmls = ''
        try:
            pepxmls = subprocess.check_output(['ssh', sorcAddr, 'find ' + sorcPath + '*.pep.xml'])
            pepxmls = pepxmls.replace(sorcPath + 'inputlists.pep.xml', '')
        except:
            raise Exception('Could not get list of pepxml.')

        dicts = []
        info[self.PARAM_IDX] = '0'
        for idx, pepxml in enumerate(pepxmls.strip().split('\n')):
            dict = info.copy()
            dict[self.FILE_IDX] = idx
            copyin = sorcAddr + ':' + pepxml
            copyout = os.path.join(info[self.WORKDIR])
            dict[self.SOURCE] = copyin+" "+copyout
            
            ###################################################
            try:
                mzbase = os.path.basename(pepxml)
                mzbase = mzbase.replace('.pep.xml','')
                if str(mzbase).endswith('_c'):
                    mzbase = mzbase[:-2] 
                scdc = subprocess.check_output(['searchmzxml', mzbase + '.mzXML*' ])
            except:
                raise Exception("Failed matching mzxml to samplecode")
            
            (samplecode, datasetcode) = scdc.split(':')
            samplecode = samplecode.strip()
            datasetcode = datasetcode.strip()
            #newbasename for pepxmlcorrector
            dict['NEWBASENAME'] = samplecode + '~' + datasetcode
            dict['DATASET_CODE'] = datasetcode
            dicts.append(dict)

            
        return dicts