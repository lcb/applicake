'''
Created on Jan 10, 2011

@author: quandtan
'''

import os,sys,shutil,argparse
from applicake.app import ExternalApplication

class Tandem2XML(ExternalApplication):
    
    def _get_parsed_args(self):
        parser = argparse.ArgumentParser(description='Script to wrap the Tandem2XML tool of the Trans-Proteomic Pipeline (TPP)')
        parser.add_argument('-p','--prefix', action="store", dest="prefix",type=str,help="prefix of the command to execute")
        parser.add_argument('-i','--input', action="store", dest="input",type=str,help="input file")
        parser.add_argument('-i','--output', action="store", dest="output",type=str,help="output file")
        a = parser.parse_args()
        return {'prefix':a.prefix,'input':a.input,'output':a.output}  
    
    def _validate_parsed_args(self,dict):    
        if not os.path.exists(dict['in']):
            self.log.fatal('file [%s] does not exist' % dict['in'])
            sys.exit(1)            
        self._command = '%s %s %s' % (dict['prefix'], dict['in'],dict['out'])        

    def _validate_run(self,run_code):        
#        if 0 < run_code:
#            return run_code 
#        if len(self._out_filenames) == 0: 
#            self.log.error('No output files defined.')
#            return 1
#        for filename in self._out_filenames:
#            if not os.path.exists(filename):
#                self.log.error('File [%s] does not exist' % os.path.abspath(filename))
#                return 1
#            else:
#                self.log.debug('File [%s] does exist' % os.path.abspath(filename))
#            stdout = self.stdout.read()
#            
#        if 'Valid models = 0' in stdout:
#            self.log.error('No valid model found')
#            return 1
        return 0      

if "__main__" == __name__:
    # init the application object (__init__)
    a = Tandem2XML(use_filesystem=True,name=None)
    # call the application object as method (__call__)
    exit_code = a(sys.argv)
    #copy the log file to the working dir
    for filename in [a._log_filename,a._stderr_filename,a._stdout_filename]:
        shutil.move(filename, os.path.join(a._wd,filename))
    print(exit_code)
    sys.exit(exit_code)        