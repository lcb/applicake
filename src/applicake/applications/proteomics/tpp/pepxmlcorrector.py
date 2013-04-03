'''
Created on Jul 5, 2012

@author: quandtan, lorenz
'''

import os
from applicake.framework.interfaces import IApplication


class PepXMLCorrector(IApplication): 
    def main(self,info,log):
        '''
        http://www.systemsx.ch:8080/browse/TPP-12

        scan numbers => different padding leads to non-matching in iProphet & errors in spectrast
        Tandem: Tandem2XML = 00000-Padding
        Omssa: MzXML2Search = 00000-Padding
        Myrimatch: None
        
        base_name msms_run_summary => .pep.xml in this tag leads to error in LFQ (IDFileConverter: found no experiment with name NNN)
        Tandem2xml: /dspath/DSID
        Omssa: /temppath/DSID.pep.xml
        Myrimatch: DSID
        make DSID (dspath might change) and use IDFileConverter -mz_name
        
        search_id => missing attribute leads to error in LFQ (IDFileConverter: Required attribute 'search_id' not present!) FIXED IN v1.10
        Tandem y
        Omssa y
        Myrimatch n!
        '''
        pepxmlin = info[self.PEPXMLS][0]
        pepxmlout = os.path.join(info[self.WORKDIR], 'corrected.pep.xml')
        mzxml = info[self.MZXML]
        mzxmlbase = os.path.splitext(os.path.basename(mzxml))[0]
        
        
        log.info("correcting pepxml")
        fout = open(pepxmlout, 'w')
        for line in open(pepxmlin).readlines():
            if '<msms_run_summary base_name' in line:
                #all engines: link to real original mzXML
                spaces = line[:line.find('<')]
                line = spaces + '<msms_run_summary base_name="%s" raw_data_type="" raw_data=".mzXML">\n' % mzxmlbase
                log.info('changed msms_run_summary tag')
            elif '<search_summary base_name' in line:
                #myrimatch: no search_id
                if line.find('search_id') == -1:
                    line = line.replace('>', ' search_id="1">')
                    log.info("added search_id")
                #omssa: superfluous .pep.xml
                basename = self._getValue(line, 'base_name')
                line = line.replace(basename,mzxmlbase)
                log.info('changed search_summary')
            elif '<spectrum_query spectrum="' in line:
                spectrum = self._getValue(line, 'spectrum')
                (basename,start_scan,end_scan,assumed_charge) = spectrum.split('.')  
                if len(end_scan) > 5:
                    log.critical("Scan number > 5 digits, this will kill the Prophets, aborting!")
                    return 1,info                             
                spectrum_mod = "%s.%05d.%05d.%s" %(mzxmlbase,int(start_scan),int(end_scan),assumed_charge)
                line = line.replace(spectrum,spectrum_mod)                                    
                                    
            fout.write(line) 
        fout.close()
        
        info['PEPXMLS'] = [pepxmlout]
        return 0,info
    
    def set_args(self,log,args_handler):
        args_handler.add_app_args(log, 'MZXML', 'Path to the original MZXML inputfile')
        args_handler.add_app_args(log, 'PEPXMLS' , 'Base name for collecting output files (e.g. from a parameter sweep)')
        args_handler.add_app_args(log, self.WORKDIR, 'Workdir')
        return args_handler

    def _getValue(self,line, attribute):
        """Get the value of an attribute from the XML element contained in 'line'"""
        pos0 = line.index(attribute + '="')
        pos1 = line.index('"', pos0) + 1
        pos2 = line.index('"', pos1)
        return line[pos1:pos2]
