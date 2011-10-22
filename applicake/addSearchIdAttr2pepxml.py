'''
Created on Oct 22, 2011

@author: quandtan
'''
import os,sys,shutil,re
import xml.etree.cElementTree as xml
from applicake.app import InternalWorkflowApplication

class AddSearchIdAttr2Pepxml(InternalWorkflowApplication):
    
    def main(self):
        config = self._iniFile.read_ini()
        inpath = config['PEPXML']
        root,ext = os.path.splitext(inpath)
        self._result_filename = re.sub('%s$'% ext, '', inpath) + '_corrected.%s' % ext 
        config['PEPXML'] = self._result_filename
        ns = '{http://regis-web.systemsbiology.net/protXML}'
        self.log.debug('output file [%s]' % self._result_filename)
        for event, elem in xml.iterparse(file):
            if elem.tag == "%ssearch_summary" % ns: 
                self.log.debug("found <search_summary>")
                elem.set("search_id", "1")
                break
        xml.ElementTree.write(self._result_filename)
        self._iniFile.write_ini(config)  
               
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