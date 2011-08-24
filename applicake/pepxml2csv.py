#!/usr/bin/env python
'''
Created on Jan 25, 2011

@author: quandtan
'''
import os,sys,shutil
from applicake.app import SequenceTemplateApplication

class PepXML2CSV(SequenceTemplateApplication):
    '''
    classdocs
    '''
    
    def _get_command(self,prefix,input_filename):
        config = self._iniFile.read_ini()
        pepxml_filename = config['PEPXML']
        self.log.debug('pepxml filename [%s]' % pepxml_filename)        
        peptide_fdr = config['PEPTIDEFDR']
        self.log.debug('peptide fdr [%s]' % peptide_fdr)
        csv_filename = os.path.join(self._wd, self.name  + '_nofdr.csv')
        self._result_filename  = os.path.join(self._wd, self.name  + '.csv')
        self._iniFile.add_to_ini({'CSV':self._result_filename})
        self.log.debug("add key 'CSV' with value [%s] in ini" % self._result_filename)

        # prefix is for this class a [] instead of a string
        prefixes = prefix
        self.log.debug('prefixes [%s]' %prefixes)
        if len(prefixes) != 2:
            self.log.fatal('number of prefixes is not correct [%s]' % len(prefixes))
            sys.exit(1)        
        params = open(input_filename,'r').readlines()
        self.log.debug('splitted params [%s]' %params)
        cmd = None
        if not len(prefixes)==len(params):
            self.log.fatal('number of prefixes [%s] does not match number of params [%s]' % (len(prefixes),len(params)))
            sys.exit(1)
        else:
            cmds = []
            # pepxml2csv  <options> <XML file> 
            cmds.append('%s -OUT=%s %s %s' % (prefixes[0],csv_filename,params[0],pepxml_filename))
            # fdr2probability -FDR="+fdr_cutoff+" -IPROPHET "+fdr_output_path            
            cmds.append('%s -OUT=%s -FDR=%s %s %s' % (prefixes[1],self._result_filename,peptide_fdr,params[1],csv_filename))
            # fdr2probability.py
            #cmds.append('%s -i %s -o %s -c %s %s' % (prefixes[1],csv_filename ,self._result_filename,peptide_fdr,params[1]))        
        return ';'.join(cmds)
    
    def _validate_run(self,run_code):                      
        stdout = self.stdout.read()
        stderr = self.stderr.read()
        self.log.debug('stdout [%s]' % stdout)        
        try:
            num = float(stdout)
            self.log.debug('probability calculated: [%s]' % num)
            # is necessary as protein prophet throughs error when e.g. 0.999999
            if num < 1:
                num = str(num)[:6]
                self.log.debug('probability cut to : [%s]' % num)
            else:
                num = 1
                self.log.debug('probability cut to : [%s]' % num)
            self._iniFile.add_to_ini({'PROBABILITY':num})            
        except Exception,e:
            self.log.exception(e)  
            self.log.error("stdout [%s] could not be parsed to float" % stdout)
            return 1
        exit_code = super(PepXML2CSV, self)._validate_run(run_code)
        if 0 != exit_code:
            return exit_code               
        return 0
                          

if "__main__" == __name__:
    # init the application object (__init__)
    a = PepXML2CSV(use_filesystem=True,name=None)
    # call the application object as method (__call__)
    exit_code = a(sys.argv)
    #copy the log file to the working dir
    for filename in [a._log_filename,a._stderr_filename,a._stdout_filename]:
        shutil.move(filename, os.path.join(a._wd,filename))
    print(exit_code)
    sys.exit(exit_code)       