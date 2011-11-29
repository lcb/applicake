#!/usr/bin/env python
'''
Created on Nov 29, 2011

@author: quandtan
'''

import os, sys, shutil, glob
from applicake.app import WorkflowApplication

class Bowtie(WorkflowApplication):

    def _get_command(self, prefix, input_filename):
        config = self._iniFile.read_ini()
        bowtiebuild = config['BOWTIEBUILD']
        fastq = config['DSSOUTPUT']
#        dir = config['DSSOUTPUT']
#        fastqs = glob.glob('%s/*.fastq' % dir)
#        if not len(fastqs) == 1:
#            self.log.error('found less or more that 1 fastq file [%s] in the dss output dir [%s].' % (fastqs,dir))
#            sys.exit(1)
#        fastq = fastqs[0]             
        out_fname =  '%s%s' % (self.name,self._result_ext)  
        self._result_filename  = os.path.join(self._wd, out_fname)
        self._iniFile.add_to_ini({'SAM': self._result_filename})
        self._iniFile.add_to_ini({'EXPORT2OPENBIS': self._result_filename})
        return "%s -S -p %s %s -s %s -c -q %s %s" % (prefix,'2', bowtiebuild,fastq,fastq, self._result_filename)
    #bowtie -S -p 2 bowtie_out -s in.fastq -c -q in.fastq out.sam
    
    def _validate_run(self, run_code):
        # does any output exist?
#        if glob.glob(self._result_filename + "*.ebwt"): 
#            return 0
#        return 1 
        return 0             

      
if "__main__" == __name__:
    # init the application object (__init__)
    a = Bowtie(use_filesystem=True, name=None)
    # call the application object as method (__call__)
    exit_code = a(sys.argv)
    #copy the log file to the working dir
    for filename in [a._log_filename, a._stderr_filename, a._stdout_filename]:
        shutil.move(filename, os.path.join(a._wd,filename))
    print(exit_code)
    sys.exit(exit_code)        
