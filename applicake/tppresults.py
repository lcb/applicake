'''
Created on Jan 20, 2011

@author: quandtan
'''
import os,sys,shutil
from applicake.app import CollectorApplication

class TppResults(CollectorApplication):

    def _get_command(self,prefix,input_filename):
        config = self._iniFile.read_ini()
        pepxml_filename = config['PEPXML']        
        self._iproph_filename  = os.path.join(self._wd, self.name  + '.pepxml')
        self._iniFile.update_ini({'PEPXML':self._iproph_filename})
        self.log.debug("updated key 'PEPXML' with value [%s] in ini" % self._iproph_filename)
        self._protxml_filename  = os.path.join(self._wd, self.name  + '.protxml')
        self._iniFile.add_to_ini({'PROTXML':self._result_filename})
        self.log.debug("add key 'PROTXML' with value [%s] to ini" % self._protxml_filename)   

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
            # InteractParser <outfile> <file1.pep.xml> <file2.pep.xml>... <options>
            cmds.append('%s %s %s %s' % (prefixes[0],self._result_filename,pepxml_filename,params[0]))
            #RefreshParser <xmlfile> <database> (<min ntt>) (DEGEN) (PROT_MW) (PREV_AA_LEN=<length(default=1)>) (NEXT_AA_LEN=<length(default=1)>) (RESTORE_NONEXISTENT_IF_PREFIX=str)
            cmds.append('%s %s %s %s' % (prefixes[1],self._result_filename,db_filename,params[1]))
            #PeptideProphetParser output.pep.xml DECOY=DECOY_ MINPROB=0 NONPARAM
            cmds.append('%s %s %s' % (prefixes[2],self._result_filename,params[2]))            
        
        return ';'.join(cmds)
    
    def _validate_run(self,run_code):                
        output = os.path.abspath(self._output_filename)
        iproph = os.path.abspath(self._iproph_filename) 
        protxml = os.path.abspath(self._protxml_filename)       
        if 0 < run_code:
            return run_code 
        if not os.path.exists(iproph):
            self.log.error('File [%s] does not exist' % iproph)
            return 1
        else:
            self.log.debug('File [%s] does exist' % iproph)
        if not os.path.exists(protxml):
            self.log.error('File [%s] does not exist' % protxml)
            return 1
        else:
            self.log.debug('File [%s] does exist' % protxml)            
        if not os.path.exists(output):
            self.log.error("File [%s] does not exist" % output)
            return 1
        else:
            self.log.debug("File [%s] does exist" % output)
            self.log.debug("content:%s" % self._iniFile.read_ini())               
            
#        stdout = self.stdout.read()
#        stderr = self.stderr.read()
#        if 'No decoys with label' in stderr:
#            self.log.error('found no decoy hits')
#            return 1             
#        else:
#            self.log.debug('did find decoy hits')        
#        if not 'model complete after' in stdout:
#            self.log.error('PeptideProphet model did not complete.')
#            return 1
#        else:
#            self.log.debug('PeptideProphet model did complete.')
        return 0       

if "__main__" == __name__:
    # init the application object (__init__)
    a = TppResults(use_filesystem=True,name=None)
    # call the application object as method (__call__)
    exit_code = a(sys.argv)
    #copy the log file to the working dir
    for filename in [a._log_filename,a._stderr_filename,a._stdout_filename]:
        shutil.move(filename, os.path.join(a._wd,filename))
    print(exit_code)
    sys.exit(exit_code)    
