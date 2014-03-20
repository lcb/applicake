"""
Created on Jul 5, 2012

@author: quandtan, lorenz
"""

import os
import re
from applicake.framework.keys import Keys
from applicake.framework.interfaces import IApplication


class PepXMLCorrector(IApplication):
    def main(self, info, log):
        """
        http://www.systemsx.ch:8080/browse/TPP-12

        1) <spectrum_query spectrum=...>: different padding in scan numbers leads to mismatches in iProphet (CHLUDWIG_M1107_001.00650.00650.2 wont match CHLUDWIG_M1107_001.650.650.2)
        Tandem: Tandem2XML makes tags with 00000-Padding (00650, 123456)
        Omssa: MzXML2Search makes tags with 00000-Padding (00650, 123456) 
        Myrimatch: No padding (650, 123456)
        Fix: Add Padding for myrimatch

        2) <msms_run_summary base_name=...>: .pep.xml in this tag leads to error in LFQ (IDFileConverter: found no experiment with name NNN)
        Tandem2xml: /dspath/DSID OK
        Omssa: /temppath/DSID.pep.xml ERROR
        Myrimatch: DSID OK
        Fix: Remove .pep.xml for Omssa        
        """
        pepxmlin = info[Keys.PEPXMLS][0]
        pepxmlout = os.path.join(info[Keys.WORKDIR], 'corrected.pep.xml')
        mzxml = info[Keys.MZXML]
        mzxmlbase = os.path.splitext(os.path.basename(mzxml))[0]

        log.info("correcting pepxml")
        fout = open(pepxmlout, 'w')
        sq = 0
        sn = 0
        for line in open(pepxmlin).readlines():
            #fix 1)
            if '<spectrum_query spectrum="' in line:
                spectrum = self._getValue(line, 'spectrum')
                (basename, start_scan, end_scan, assumed_charge) = spectrum.split('.')
                if len(start_scan) < 5:
                    spectrum_mod = "%s.%05d.%05d.%s" % (basename, int(start_scan), int(end_scan), assumed_charge)
                    line = line.replace(spectrum, spectrum_mod)
                    sq+=1
                if 'spectrumNativeID' in line:
                    line = re.sub('spectrumNativeID="[^"]*"','',line)
                    sn+=1
            #fix 2)            
            elif '<msms_run_summary base_name' in line and ".pep.xml" in line:
                spaces = line[:line.find('<')]
                line = spaces + '<msms_run_summary base_name="%s" raw_data_type="" raw_data=".mzXML">\n' % mzxmlbase
                log.debug('modified msms_run_summary (fixes omssa for IDFileConverter)')

            fout.write(line)

        fout.close()
        if sq != 0: log.debug('modified spectrum_query %s times (fixes myrimatch for iprophet)'%sq)
        if sn != 0: log.debug('modified spectrumNativeID %s times (fixes myrimatch for xinteract 4.7.0)'%sn)
        info['PEPXMLS'] = [pepxmlout]
        return 0, info

    def set_args(self, log, args_handler):
        args_handler.add_app_args(log, 'MZXML', 'Path to the original MZXML inputfile')
        args_handler.add_app_args(log, 'PEPXMLS', 'Base name for collecting output files (e.g. from a parameter sweep)')
        args_handler.add_app_args(log, Keys.WORKDIR, 'Workdir')
        return args_handler

    def _getValue(self, line, attribute):
        """Get the value of an attribute from the XML element contained in 'line'"""
        pos0 = line.index(attribute + '="')
        pos1 = line.index('"', pos0) + 1
        pos2 = line.index('"', pos1)
        return line[pos1:pos2]
