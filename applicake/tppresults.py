#!/usr/bin/env python
'''
Created on Jan 20, 2011

@author: quandtan
'''
import os,sys,shutil
from applicake.app import CollectorApplication

class TppResults(CollectorApplication):

    def _get_command(self,prefix,input_filename,dictionary):
        config = self._iniFile.read_ini()
        pepxml_filename = config['PEPXML']        
        self._iproph_filename  = os.path.join(self._wd, self.name  + '.pepxml')
        self._iniFile.update_ini({'PEPXML':self._iproph_filename})
        self.log.debug("updated key 'PEPXML' with value [%s] in ini" % self._iproph_filename)
        self._protxml_filename  = os.path.join(self._wd, self.name  + '.protxml')
        self._iniFile.add_to_ini({'PROTXML':self._protxml_filename})
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
            # InterProphetParser <OPTIONS> <file1.pep.xml> <file2.pep.xml>... <outfile>
            cmds.append('%s %s %s %s' % (prefixes[0],params[0],pepxml_filename,self._iproph_filename))
            # ProteinProphet <interact_pepxml_file1> [<interact_pepxml_file2>[....]] <output_protxml_file> (ICAT) (GLYC) (XPRESS) (ASAP_PROPHET) (ACCURACY) (ASAP) (PROTLEN) (NOPROTLEN) (NORMPROTLEN) (GROUPWTS) (INSTANCES) (REFRESH) (DELUDE) (NOOCCAM) (NOPLOT) (PROTMW)
            cmds.append('%s %s %s %s' % (prefixes[1],self._iproph_filename,self._protxml_filename,params[1]))
        return ';'.join(cmds)
    
    def _validate_run(self,run_code):                
#        output = os.path.abspath(self._output_filename)
        iproph = os.path.abspath(self._iproph_filename) 
        protxml = os.path.abspath(self._protxml_filename)       
        if 0 < run_code:
            self.log.debug('run code was [%s]' % run_code)
#            return run_code 
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
#        if not os.path.exists(output):
#            self.log.error("File [%s] does not exist" % output)
#            return 1
#        else:
#            self.log.debug("File [%s] does exist" % output)
#            self.log.debug("content:%s" % self._iniFile.read_ini())               
            
        stdout = self.stdout.read()
        stderr = self.stderr.read()
        msg = 'No xml file specified; please use the -file option'
        if msg in stdout:
                self.log.debug('ProteinProphet ignore [%s] of protxml2html' % msg)
        for msg in ['fin: error opening']:
            if msg in stderr:
                self.log.error('InterProphetParser error [%s]' % msg)
                return 1
            else:
                self.log.debug('ProteinProphet: passed check [%s]' % msg)                
        for msg in ['did not find any InterProphet results in input data!',
                    'no data - quitting',
                    'WARNING: No database referenced']:
            if msg in stdout:
                self.log.error('ProteinProphet error [%s]' % msg)
                return 1
            else:
                self.log.debug('ProteinProphet: passed check [%s]' % msg)
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
