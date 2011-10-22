'''
Created on Oct 22, 2011

@author: quandtan
'''
import os,sys,shutil,re,cStringIO
import xml.etree.cElementTree as xml
from applicake.app import InternalWorkflowApplication

class AddSearchIdAttr2Pepxml(InternalWorkflowApplication):
    
    def main(self):
        config = self._iniFile.read_ini()
        inpath = config['PEPXML']
        root,ext = os.path.splitext(inpath)
        basename = os.path.splitext(os.path.split(inpath)[1])[0]    
        self._result_filename  = os.path.join(self._wd,basename + '_corrected%s' % ext)
        fout = open(self._result_filename,'wb')
        config['PEPXML'] = self._result_filename
        self._iniFile.write_ini(config)
        not_found = True
        for line in cStringIO.StringIO(open(inpath).read()):
            if not_found:
                if '<search_summary' in line:
                    line = '%s search_id="1">\n' % re.sub('>$', '', line)
                    not_found = False
            fout.write(line)
        if not_found:
            self.log.error('file [%s] did not contain the line pattern [<search_summary]' % inpath)
            sys.exit(1)
            
          
               
if "__main__" == __name__:
    # init the application object (__init__)
    a = AddSearchIdAttr2Pepxml(use_filesystem=True,name=None)
    # call the application object as method (__call__)
    exit_code = a(sys.argv)
    #copy the log file to the working dir
    for filename in [a._log_filename,a._stderr_filename,a._stdout_filename]:
        shutil.move(filename, os.path.join(a._wd,filename))
    print(exit_code)
    sys.exit(exit_code)     