#!/usr/bin/env python
'''
Created on Jan 25, 2011

@author: quandtan
'''
import sys,os,shutil
from string import Template
from applicake.app import SequenceTemplateApplication
from applicake.utils import IniFile

class OpenbisExport(SequenceTemplateApplication):
    '''
    classdocs
    '''
    def _get_command(self,prefix,input_filename):
        config = self._iniFile.read_ini()
        protxml_filename = config['PROTXML']        
        self.log.debug('PROTXML [%s]' % protxml_filename)
        csv_filename = config['CSV']        
        self.log.debug('CSV [%s]' % csv_filename)
        db = config['DBASE']
        self.log.debug('DBASE [%s]' % db)    
        dbasename = os.path.splitext(os.path.split(db)[1])[0]
        self._iniFile.add_to_ini({'DBASENAME':dbasename})
        self.log.debug("add key 'DBASENAME' with value [%s] to ini" % dbasename)
        content = open(input_filename,'r').read()        
        params = Template(content).safe_substitute(config)
        self.log.debug('parameter [%s]' % params)   
        #protxml_split_filename  = os.path.join(self._wd,self.name + "_splitgroups.protxml")
        protxml_sc_filename  = os.path.join(self._wd,self.name + "_spectralcount.protxml")
        protxml_mod_filename  = os.path.join(self._wd,self.name + "_modifications.protxml")
        self._result_filename  = os.path.join(self._wd,self.name + ".prot.xml")
        self._iniFile.update_ini({'PROTXML':self._result_filename})        
         # prefix is for this class a [] instead of a string
        prefixes = prefix
        self.log.debug('prefixes [%s]' %prefixes)
        if len(prefixes) != 3:
            self.log.fatal('number of prefixes is not correct [%s]' % len(prefixes))
            sys.exit(1)        
        params = open(input_filename,'r').readlines()
        self.log.debug('splitted params [%s]' %params)
        cmds = None
        if not len(prefixes)==len(params):
            self.log.fatal('number of prefixes [%s] does not match number of params [%s]' % (len(prefixes),len(params)))
            sys.exit(1)
        else:
            cmds = []
#            # protxml2splitgropus
#            cmds.append('%s -OUT=%s %s %s' % (prefixes[0],protxml_split_filename,params[0],protxml_filename))   
            # protxml2spectralcount [Options] <protXML>
            cmds.append('%s -CSV=%s -OUT=%s %s %s' % (prefixes[0],csv_filename,protxml_sc_filename,params[0],protxml_filename))   
            # protxml2modifications
            cmds.append('%s -CSV=%s -OUT=%s %s %s' % (prefixes[1],csv_filename,protxml_mod_filename,params[1],protxml_sc_filename))            
            # protxml2openbis [Options] <protXML>
            cmds.append('%s -DB=%s -OUT=%s %s %s' % (prefixes[2],db,self._result_filename,params[2],protxml_mod_filename))                
        return ';'.join(cmds)       
    
    
    def _validate_run(self,run_code):               
        exit_code = super(OpenbisExport, self)._validate_run(0)
        if exit_code != 0:
            return  exit_code 
        self.log.info('Start [%s]' % self._copy_to_dropbox.__name__)
        self._copy_to_dropbox()
        self.log.info('Finish [%s]' % self._copy_to_dropbox.__name__)                        
        return 0 
    
    def _copy_to_dropbox(self):
        config=self._iniFile.read_ini()
        dropbox = config['DROPBOX']
        space = config['SPACE']
        project = config['PROJECT']
        param_idx = config['PARAM_IDX']
        jobid = config['JOBID']
        dropbox_dirname = '%s+%s+%s.%s'%(space,project,jobid,param_idx)
        dir = os.path.join(self._wd,dropbox_dirname)
        self.log.debug('generate dir [%s] to later copy it to [%s]...' % (dir,dropbox))
        os.mkdir(dir)
        self.log.debug('...successful')        
        self.log.debug('start copying data to dir...')                
        for filename in [config['PEPXML'],config['PROTXML'],config['CSV']]:
            basename = os.path.split(filename)[1]
            self.log.debug('basename [%s]' % basename)
            self.log.debug('dir [%s]' % self._wd)  
            dest = os.path.join(dir,basename)   
            self.log.debug('...move [%s] to [%s]...' % (filename,dest))                   
            shutil.move(filename,dest)
            self.log.debug('...successfully..')
        props_filename = os.path.join(dir,'search.properties')
        self.log.debug('...write current config to [%s]...' % props_filename)
        ini_file = IniFile(input_filename=props_filename,output_filename=props_filename)
        ini_file.write_ini(config)        
        self.log.debug('...successfully...')
        
        # needed for openbis export. otherwise openbis cannot delete dir's from dropbox
        self.log.debug('start changing permissions of [%s]' % dir) 
        os.chmod(dir, 0o777)
        self.log.debug('changed permissions of [%s] to [%s]' % (dir,'0o777'))
        for root, dirs, files in os.walk(dir):  
          for subdir in dirs:  
            self.log.debug('found subdir [%s]' % subdir)  
            os.chmod(subdir,0o777)
            self.log.debug('changed permissions of [%s] to [%s]' % (subdir,'0o777'))
          for file in files:
             fname = os.path.join(root, file)
             self.log.debug('found file [%s]' % fname)
             os.chmod(fname, 0o777)
             self.log.debug('changed permissions of [%s] to [%s]' % (fname,'0o777'))        
        self.log.debug('...copying [%s] to [%s]' % (dir, dropbox))
        shutil.copytree(dir,os.path.join(dropbox,dropbox_dirname))
        self.log.debug('...successfully!')
        
            
        
        
if "__main__" == __name__:
    # init the application object (__init__)
    a = OpenbisExport(use_filesystem=True,name=None)
    # call the application object as method (__call__)
    exit_code = a(sys.argv)
    #copy the log file to the working dir
    for filename in [a._log_filename,a._stderr_filename,a._stdout_filename]:
        shutil.move(filename, os.path.join(a._wd,filename))
    print(exit_code)
    sys.exit(exit_code)   
        