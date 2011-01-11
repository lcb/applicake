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
        parser.add_argument('-i','--input', action="store", dest="input_filename",type=str,help="configuration file in ini file structure")
        parser.add_argument('-o','--output', action="store", dest="output_filename",type=str,help="output file to generate")
        a = parser.parse_args()
        return {'prefix':a.prefix,'input_filename':a.input_filename,'output_filename':a.output_filename}      
    
    def _validate_parsed_args(self,dict):    
        if dict['input_filename'] is None:
            self.log.fatal('argument [input] was not set')
            sys.exit(1)
        else:
            self._input_filename = dict['input_filename']
            self.log.debug("input file [%s]" % os.path.abspath(self._input_filename))
            if not os.path.exists(self._input_filename):
                self.log.fatal('file [%s] does not exist' % self._input_filename)           
        self._command = '%s %s %s' % (dict['prefix'], dict['input_filename'],dict['output_filename'])        

    def _validate_run(self,run_code):        
        if 0 < run_code:
            return run_code 
        if not os.path.exists(self.output_filename):
            self.log.error('File [%s] does not exist' % os.path.abspath(self._output_filename))
            return 1
        else:
            self.log.debug('File [%s] does exist' % os.path.abspath(self._output_filename))
        stdout = self.stdout.read()            
        if 'Valid models = 0' in stdout:
            self.log.error('No valid model found')
            return 1
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