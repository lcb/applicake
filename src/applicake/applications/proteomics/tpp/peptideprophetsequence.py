#!/usr/bin/env python

'''
Created on Jan 22, 2013

@author: lorenz
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
        self._correctPepxml(log, info[self.PEPXMLS][0], info[self.MZXML], corrected_pepxml)        
        
        self._result_file  = os.path.join(info[self.WORKDIR], 'interact.pep.xml')
        
        omssafix = ''
        if info.has_key('OMSSAFIX'):
            omssafix = "-C -P"
            
        info['TEMPLATE'] = os.path.join(info[self.WORKDIR], 'interact.tpl')
        template,info = PeptideProphetSequenceTemplate().modify_template(info, log)
        paramarr = template.splitlines()
        
        cmds = []                
        # InteractParser <outfile> <file1.pep.xml> <file2.pep.xml>... <options>            
        cmds.append('InteractParser %s %s %s %s' % (self._result_file,corrected_pepxml,paramarr[0],omssafix))
        #RefreshParser <xmlfile> <database>
        cmds.append('RefreshParser %s %s %s' % (self._result_file,db_filename,paramarr[1]))    
        #PeptideProphetParser output.pep.xml DECOY=DECOY_ MINPROB=0 NONPARAM MINPROB required for myrimatch otherwise 'no results found'
        cmds.append('PeptideProphetParser %s %s' % (self._result_file,paramarr[2]))           
        return ' && '.join(cmds),info
    
    def set_args(self,log,args_handler):
        args_handler.add_app_args(log, self.WORKDIR, 'Directory to store files')
        args_handler.add_app_args(log, self.PEPXMLS, 'List of pepXML files',action='append')
        args_handler.add_app_args(log, 'ENZYME', 'Enzyme used for digest')
        args_handler.add_app_args(log, 'DBASE', 'FASTA dbase')
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
        log.info("Correcting pepxml")
        mzxmlbase = os.path.splitext(mzxml)[0]
        
        fout = open(pepxmlout, 'w')
        for line in open(pepxmlin).readlines():
            if '<msms_run_summary base_name' in line:
                line = '<msms_run_summary base_name="%s" raw_data_type="" raw_data=".mzXML">\n' % mzxmlbase
                log.debug('changed msms_run_summary tag')
            if '<search_summary base_name' in line:
                if line.find('search_id') == -1:
                    line = line.replace('>', ' search_id="1">')
                    log.debug("added search_id")
                basename = self._getValue(line, 'base_name')
                line = line.replace(basename,mzxmlbase) + '\n'
                log.debug('changed search_summary')

            if '<spectrum_query spectrum="' in line:
                spectrum = self._getValue(line, 'spectrum')
                (basename,start_scan,end_scan,assumed_charge) = spectrum.split('.')  
                if len(end_scan) > 5:
                    log.fatal("Scan number > 5, this will kill the Prophets, aborting!")
                    raise Exception('Scan number > 5')                              
                spectrum_mod = "%s.%05d.%05d.%s" %(basename,int(start_scan),int(end_scan),assumed_charge)
                line = line.replace(spectrum,spectrum_mod) + '\n'                                    
                                    
            fout.write(line) 
        fout.close()

class PeptideProphetSequenceTemplate(BasicTemplateHandler):
    """
    Template handler for xinteract.
    """
    def read_template(self, info, log):
        """
        See super class.
        """
        # Threads is not set by a variable as this does not make sense here
        template = """-L7 -E$ENZYME

DECOY=DECOY_ ACCMASS NONPARAM DECOYPROBS LEAVE PI INSTRWARN MINPROB=0"""        
        log.debug('read template from [%s]' % self.__class__.__name__)
        return template,info
        
