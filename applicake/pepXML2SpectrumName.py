#!/usr/bin/env python
'''
Created on Jan 23, 2012

@author: quandtan
'''

import os,sys,shutil,re,cStringIO
import xml.etree.cElementTree as xml
from applicake.app import InternalWorkflowApplication

class PepXML2SpectrumName(InternalWorkflowApplication):
    
    def main(self):
        config = self._iniFile.read_ini()
        self.fin = config['PEPXML']
        root,ext = os.path.splitext(self.fin)
        basename = os.path.splitext(os.path.split(self.fin)[1])[0]    
        self._result_filename  = os.path.join(self._wd,basename + "%s" % ext)
        config['PEPXML'] = self._result_filename
        self._iniFile.write_ini(config)
        #
        # xml-paser based parsing 
        #
#        root = None
#        for event, elem in xml.iterparse(self.fin):    
#            if root is None:
#                root=elem        
#            if elem.tag == self.get_ns_name('spectrum_query'): 
#                spectrum = elem.attrib['spectrum'].split('.')[0]
#                start_scan = elem.attrib['start_scan']
#                end_scan = elem.attrib['end_scan']
#                assumed_charge = elem.attrib['assumed_charge']
#                digets = len(start_scan)
#                if digets < 5:
#                    num_zeros = 5 - digets
#                    elem.attrib['spectrum'] = "%s.%s.%s.%s" %(spectrum,'0'*num_zeros + start_scan,'0'*num_zeros + end_scan,assumed_charge)
#                else:
#                    self.log.fatal('scan number larger that 5 digets: [%s]' % start_scan)
#                    print 'error'
#                    sys.exit(1)
#        xml.ElementTree(elem).write(self._result_filename)
        fout = open(self._result_filename,'wb')
        self.log.debug('start reading file [%s] line by line' % self.fin)
        for line in open(self.fin,'r'):            
            if '<spectrum_query spectrum="' in line:                
                spectrum = line.split('spectrum="')[1].split('" ')[0]
                (basename,start_scan,end_scan,assumed_charge) = spectrum.split('.')
                digets = len(start_scan)
                if digets <= 5:
                    num_zeros = 5 - digets
                    spectrum_mod = "%s.%s.%s.%s" %(basename,'0'*num_zeros + start_scan,'0'*num_zeros + end_scan,assumed_charge)
                    line = line.replace(spectrum,spectrum_mod)                                        
                    ''.join([line,'\n'])  
                                     
                else:
                    self.log.fatal('scan number larger that 5 digets: [%s]' % start_scan)
                    sys.exit(1)
            fout.write(line) 
        self.log.debug('finished writing output file [%s]' % self._result_filename)



    def get_ns_name(self,name):
        ns = '{http://regis-web.systemsbiology.net/pepXML}'
        return "%s%s" % (ns,name)        
        
                                                    
                       
                              
#        return elem_lst          
               
if "__main__" == __name__:
    # init the application object (__init__)
    a = PepXML2SpectrumName(use_filesystem=True,name=None)
    # call the application object as method (__call__)
    exit_code = a(sys.argv)
    #copy the log file to the working dir
    for filename in [a._log_filename,a._stderr_filename,a._stdout_filename]:
        shutil.move(filename, os.path.join(a._wd,filename))
    print(exit_code)
    sys.exit(exit_code) 