#!/usr/bin/env python

'''
Created on Jan 22, 2013

@author: lorenz

Corrects pepxml output to make compatible with TPP and openms, then executes xinteract (step by step because of semiTrypsin option)

'''

import os
from applicake.framework.interfaces import IWrapper
from applicake.framework.templatehandler import BasicTemplateHandler
from applicake.utils.fileutils import FileUtils
from applicake.utils.xmlutils import XmlValidator

class PeptideProphetSequence(IWrapper):
    
    def prepare_run(self,info,log):
        db_filename = info['DBASE'] 
        corrected_pepxml = os.path.join(info[self.WORKDIR], 'corrected.pep.xml')
        #CORRECT
        self._correctPepxml(log, info[self.PEPXMLS][0], info[self.MZXML], corrected_pepxml)            
        self._result_file  = os.path.join(info[self.WORKDIR], 'interact.pep.xml')
        
        omssafix = ''
        if info.has_key('OMSSAFIX'):
            omssafix = "-C -P"
            
        info['TEMPLATE'] = os.path.join(info[self.WORKDIR], 'interact.tpl')
        template,info = PeptideProphetSequenceTemplate().modify_template(info, log)
        paramarr = template.splitlines()
        
        #XTINERACT
        cmds = []                
        cmds.append('InteractParser %s %s %s %s' % (self._result_file,corrected_pepxml,paramarr[0],omssafix))
        cmds.append('RefreshParser %s %s %s' % (self._result_file,db_filename,paramarr[1]))    
        cmds.append('PeptideProphetParser %s %s' % (self._result_file,paramarr[2]))           
        return ' && '.join(cmds),info
    
    def set_args(self,log,args_handler):
        args_handler.add_app_args(log, self.WORKDIR, 'Directory to store files')
        args_handler.add_app_args(log, self.PEPXMLS, 'List of pepXML files',action='append')
        args_handler.add_app_args(log, 'ENZYME', 'Enzyme used for digest')
        args_handler.add_app_args(log, 'DBASE', 'FASTA dbase')
        args_handler.add_app_args(log, 'MZXML', 'Path to the original MZXML inputfile')
        args_handler.add_app_args(log, self.COPY_TO_WD, 'List of files to store in the work directory')  
        args_handler.add_app_args(log, 'OMSSAFIX', 'Fix omssa',action="store_true")
        return args_handler
    
    def validate_run(self,info,log, run_code,out_stream, err_stream):
        """
        See super class.
        """
        if not FileUtils.is_valid_file(log, self._result_file):
            log.critical('[%s] is not valid' %self._result_file)
            return 1,info
        if not XmlValidator.is_wellformed(self._result_file):
            log.critical('[%s] is not well formed.' % self._result_file)
            return 1,info  
        if not 'model complete after' in out_stream.read():
            log.error('PeptideProphet model did not complete.')
            return 1,info  
            
        info[self.PEPXMLS] = [self._result_file]         
        return run_code,info
          
    def _getValue(self,line, attribute):
        """Get the value of an attribute from the XML element contained in 'line'"""
        pos0 = line.index(attribute + '="')
        pos1 = line.index('"', pos0) + 1
        pos2 = line.index('"', pos1)
        return line[pos1:pos2]
    
    def _correctPepxml(self,log,pepxmlin,mzxml,pepxmlout):
        '''
        scan numbers => different padding leads to non-matching in iProphet & spectrast
        Tandem: Tandem2XML = 00000-Padding
        Omssa: MzXML2Search = 00000-Padding
        Myrimatch: None
        
        base_name ms_run_summary => .pep.xml in this tag leads to error in LFQ (IDFileConverter found no experiment with name NNN)
        Tandem: path/ID
        Omssa: path/ID.pep.xml
        Myrimatch: ID
        
        search_id => missing attribute leads to error in LFQ (IDFilter?)
        Tandem y
        Omssa y
        Myrimatch n!
        '''
        log.info("correcting pepxml")
        mzxmlbase = os.path.splitext(mzxml)[0]
        
        fout = open(pepxmlout, 'w')
        for line in open(pepxmlin).readlines():
            if '<msms_run_summary base_name' in line:
                #all engines: link to real original mzXML
                spaces = line[:line.find('<')]
                line = spaces + '<msms_run_summary base_name="%s" raw_data_type="" raw_data=".mzXML">\n' % mzxmlbase
                log.info('changed msms_run_summary tag')
            if '<search_summary base_name' in line:
                #myrimatch: no search_id
                if line.find('search_id') == -1:
                    line = line.replace('>', ' search_id="1">')
                    log.info("added search_id")
                #omssa: superfluous .pep.xml
                basename = self._getValue(line, 'base_name')
                line = line.replace(basename,mzxmlbase)
                log.info('changed search_summary')

            if '<spectrum_query spectrum="' in line:
                spectrum = self._getValue(line, 'spectrum')
                (basename,start_scan,end_scan,assumed_charge) = spectrum.split('.')  
                if len(end_scan) > 5:
                    log.fatal("Scan number > 5 digits, this will kill the Prophets, aborting!")
                    raise Exception('Scan number > 5 digits')                              
                spectrum_mod = "%s.%05d.%05d.%s" %(basename,int(start_scan),int(end_scan),assumed_charge)
                line = line.replace(spectrum,spectrum_mod)                                    
                                    
            fout.write(line) 
        fout.close()

class PeptideProphetSequenceTemplate(BasicTemplateHandler):
    """
    Template handler for xinteract. mapping of options:
    -p0 MINPROB=0
    -dDECOY_ DECOY=DECOY_ str used for decoys
    -OA ACCMASS accurate mass binning
    -OP NONPARAM
    -Od DECOYPROBS
    -Ol LEAVE
    -OI PI
    -Ow INSTRWARN
    """
    def read_template(self, info, log):
        """
        See super class.
        """
        template = """-L7 -E$ENZYME

DECOY=DECOY_ ACCMASS NONPARAM DECOYPROBS LEAVE PI INSTRWARN MINPROB=0"""        
        log.debug('read template from [%s]' % self.__class__.__name__)
        return template,info
        
