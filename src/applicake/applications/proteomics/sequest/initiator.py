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
        args_handler.add_app_args(log, self.WORKDIR, 'Workdir') 
        return args_handler
    
    def main(self,info,log):
        ##First read the info and add the additional entries from sequest.params
        #copy params file from sorcerer
        sorcAddr = 'sorcerer@imsb-ra-sorcerer' + info['SEQUESTHOST'] + '.ethz.ch'
        sorcPath = '/home/sorcerer/output/' + info['SEQUESTRESULTPATH'] + '/original/'
        
        info = self.addParamsToInfo(sorcAddr+":"+ sorcPath, info)
        info = self.cpAndCheckDB(sorcAddr, info,log)
        dicts = self.convertSeq2Pepxml(info, log,sorcAddr,sorcPath);
        self.write_files(info, log, dicts)
        return 0,info
     
    def addParamsToInfo(self,sorcpath,info):
        paramfile = os.path.join(self.WORKDIR, 'sequest.params')
        #put in a method
        try:
            subprocess.check_call(['rsync', '-vrtz', sorcpath + 'sequest.params', paramfile])
        except:
            raise Exception("Cannot get params from sorcerer. Did you check passwordless SSH? Does file exist?")
        
        #transform sorcerer params to info.ini & write out
        for line in open(paramfile).readlines():
            if 'peptide_mass_tolerance' in line:
                info["PRECMASSERR"] = line.split()[2]
            if 'max_num_internal_cleavage_sites' in line:
                info["MISSEDCLEAVAGE"] = line.split()[2]
            if 'peptide_mass_units' in line:
                sequestunits = {"0":"amu", "1":"mmu", "2":"ppm" }
                info["PRECMASSUNIT"] = sequestunits[line.split()[2]]
            if line.startswith('database_name'):
                sorcDB = line.split()[2]
                info["DBASE"] = os.path.join(info[self.WORKDIR], os.path.basename(sorcDB))
        info["FRAGMASSUNIT"] = 'NA'
        info["FRAGMASSERR"] = 'NA'   
        return info
    
    def cpAndCheckDB(self,sorcAddr,info,log):
        dbfile = os.path.join(self.WORKDIR, os.path.basename(info['DBASE']))
        try:
            subprocess.check_call(['rsync', '-vrtz', sorcAddr + ':' + info['DBASE'], dbfile])
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
        info['DBASE'] = dbfile
        return info
    
    def convertSeq2Pepxml(self,info,log,sorcAddr,sorcPath):
        pepxmldirs = ''
        try:
            pepxmldirs = subprocess.check_output(['ssh', sorcAddr, 'find ' + sorcPath + '* -type d -maxdepth 1'])
        except:
            raise Exception('Could not get list of pepxml.')

        dicts = []
        parentcodes = []
        info[self.PARAM_IDX] = '0'
        for idx, pepxmldir in enumerate(pepxmldirs.strip().split('\n')):
            dict = info.copy()
            dict[self.FILE_IDX] = str(idx) 
            pepxmldir = os.path.basename(pepxmldir)
            try:
                subprocess.check_call(['ssh', sorcAddr, 'cd ' + sorcPath + ';/usr/local/tpp/bin/Out2XML ' + pepxmldir + ' 1 -P.'])
            except:
                raise Exception("Couldnt convert pepxml: " + pepxmldir)
            
            copyin = sorcAddr + ':' + sorcPath + pepxmldir + '.pep.xml'
            copyout = os.path.join(self.WORKDIR, info['PARAM_IDX'], info['SPECTRA_IDX'], 'copier')
            dict[self.SOURCE] = copyin+" "+copyout
            
            ###################################################
            try:
                scdc = subprocess.check_output(['searchmzxml', pepxmldir + '.mzXML' ])
            except:
                raise Exception("Failed matching mzxml to samplecode")
            
            (samplecode, datasetcode) = str(scdc).split(':')
            dict['NEWBASENAME'] = samplecode + '~' + datasetcode
            parentcodes.append(datasetcode.strip())
            dicts.append(dict)
        
        for dict in dicts:
            dict['PARENT-DATA-SET-CODES'] = parentcodes
            
        return dicts
