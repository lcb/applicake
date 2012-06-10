
'''
Created on May 24, 2012

@author: quandtan
'''
import os
from applicake.applications.proteomics.modifications import ModificationDb
from applicake.applications.proteomics.base import MsMsIdentification
from applicake.framework.templatehandler import BasicTemplateHandler
from applicake.utils.fileutils import FileUtils
from applicake.utils.xmlutils import XmlValidator




class Xtandem(MsMsIdentification):
    '''
    Wrapper for the search engine X!Tandem.
    '''
    
    def __init__(self):
        base = self.__class__.__name__
        self._template_file = '%s.input' % base # application specific config file
        self._result_file = '%s.result' % base # result produced by the application
        self._taxonomy_file = '%s.taxonomy' % base      


    def _define_score(self, info, log):
        if not info.has_key('XTANDEM_SCORE'):
            info['XTANDEM_SCORE'] = 'default'
            log.debug('did not find value for key [%s]. set it to [%s]' % ('XTANDEM_SCORE', info['XTANDEM_SCORE']))
        if info['XTANDEM_SCORE'] == 'default': # for default score, no entry is allowed in template
            info['XTANDEM_SCORE'] = ''
        else:
            info['XTANDEM_SCORE'] = '<note label="scoring, algorithm" type="input">%s</note>' % info['XTANDEM_SCORE']
        return info
    
    def _define_mods(self,info,log):
        """
        Convert generic static/variable modifications into the program-specific format 
        """
        mod_keys = [self.STATIC_MODS,self.VARIABLE_MODS]
        for key in mod_keys:
            if not info.has_key(key):
                info[key] = ''
            else:
                mods = []
                for mod in info[key].split(';'):
                    log.debug('modification [%s]' % key)
                    log.debug('name [%s]')
                    
                    converted_mod = ModificationDb(log).get(mod, self.__class__.__name__)
                    mods.append(converted_mod)
                info[key] = ','.join(mods)                
        return info
                 
    def get_prefix(self,info,log):
        if not info.has_key(self.PREFIX):
            info[self.PREFIX] = 'tandem'
            log.debug('set [%s] to [%s] because it was not set before.' % (self.PREFIX,info[self.PREFIX]))
        return info[self.PREFIX],info         

    def _write_input_files(self,info,log):       
        db_file = os.path.join(info[self.WORKDIR],info['DBASE'])
        with open(self._taxonomy_file, "w") as sink:
            sink.write('<?xml version="1.0"?>\n')
            sink.write('<bioml>\n<taxon label="database">')
            sink.write('<file format="peptide" URL="%s"/>' % db_file)
            sink.write("</taxon>\n</bioml>")
        log.debug('Created [%s]' % self._taxonomy_file)          
        with open(self._template_file, "w") as sink:
            sink.write('<?xml version="1.0"?>\n')
            sink.write("<bioml>\n<note type='input' label='list path, default parameters'>"+info[self.TEMPLATE]+"</note>\n")
            sink.write("<note type='input' label='output, xsl path' />\n<note type='input' label='output, path'>"+self._result_file+"</note>\n")
            sink.write("<note type='input' label='list path, taxonomy information'>"+self._taxonomy_file+"</note>\n")
            sink.write("<note type='input' label='spectrum, path'>"+info['MZXML']+"</note>\n")
            sink.write("<note type='input' label='protein, taxon'>database</note>\n</bioml>\n")
        log.debug('Created [%s]' % self._template_file)    
        return info

    def get_template_handler(self):
        """
        See interface
        """
        return XtandemTemplate()
    
    def prepare_run(self,info,log):
        """
        See interface.
        
        - Read the template from the handler
        - Convert scoring and modifications into the specific format
        - modifies the template from the handler
        - writes the files needed to execute the program 
        
        @precondition: info object need the key [%s]
        """ % self.TEMPLATE
        wd = info[self.WORKDIR]
        log.debug('reset path of application files from current dir to work dir [%s]' % wd)
        self._template_file = os.path.join(wd,self._template_file)  
        self._result_file = os.path.join(wd,self._result_file) 
        self._taxonomy_file = os.path.join(wd,self._taxonomy_file)
        log.debug('add key [XTANDEM_RESULT] to info') 
        info['XTANDEM_RESULT'] = self._result_file    
#        info[self.COPY_TO_WD] = info[self.COPY_TO_WD].extend([self._taxonomy_file,self._input_file,self._result_file])        
        log.debug('get template handler')
        th = self.get_template_handler()
        log.debug('define score value')
        info = self._define_score(info, log)
        log.debug('define modifications')
        info = self._define_mods(info, log)
        log.debug('modify template')                
        mod_template,info = th.modify_template(info, log)
        log.debug('write input files')
        info = self._write_input_files(info, log)        
        prefix,info = self.get_prefix(info,log)
        command = '%s %s' % (prefix,self._template_file)
        return command,info    

    def set_args(self,log,args_handler):
        """
        See interface
        """        
        args_handler = super(Xtandem, self).set_args(log,args_handler)
        args_handler.add_app_args(log, 'MZXML', 'Peak list file in mzXML format')   
        args_handler.add_app_args(log, 'XTANDEM_SCORE', 'Scoring algorithm used in the search.',choices=['default','k-score','c-score','hrk-score'])        
        return args_handler
    
    def validate_run(self,info,log, run_code,out_stream, err_stream):
        """
        See super class.
        
        Check the following:
        - more than 0 valid models found
        - result file is valid
        - result file is a well-formed xml
        """  
        exit_code,info = super(Xtandem,self).validate_run(info,log, run_code,out_stream, err_stream)
        if 0 != run_code:
            return exit_code,info   
        out_stream.seek(0)        
        if 'Valid models = 0' in out_stream.read():
            log.critical('No valid model found')
            return 1,info
        if not FileUtils.is_valid_file(log, self._result_file):
            log.critical('[%s] is not valid' %self._result_file)
            return 1,info
        if not XmlValidator.is_wellformed(self._result_file):
            log.critical('[%s] is not well formed.' % self._result_file)
            return 1,info
        return 0,info  
            

class XtandemTemplate(BasicTemplateHandler):
    """
    Template handler for Xtandem.  
    """
    
    def read_template(self, info, log):
        """
        See super class.
        """
        template = """<?xml version="1.0"?>
<?xml-stylesheet type="text/xsl" href="tandem-input-style.xsl"?>
<bioml>

<note type="heading">Paths</note>    
    <note type="input" label="list path, default parameters">default_input.xml</note>
    <note type="input" label="list path, taxonomy information">taxonomy_pro.xml</note>

<note type="heading">Spectrum general</note>    
    <note type="input" label="spectrum, fragment monoisotopic mass error">$FRAGMASSERR</note>
    <note type="input" label="spectrum, fragment monoisotopic mass error units">$FRAGMASSUNIT</note>
    <note type="input" label="spectrum, parent monoisotopic mass isotope error">yes</note>
    <note type="input" label="spectrum, parent monoisotopic mass error plus">$PRECMASSERR</note>
    <note type="input" label="spectrum, parent monoisotopic mass error minus">$PRECMASSERR</note>
    <note type="input" label="spectrum, parent monoisotopic mass error units">$PRECMASSUNIT</note>

<note type="heading">Spectrum conditioning</note>
    <note type="input" label="spectrum, fragment mass type">monoisotopic</note>
    <note type="input" label="spectrum, dynamic range">1000.0</note>
    <note>
        This parameter is used to normalize the intensity values of fragment ions, from spectrum to spectrum.
        For example, if Drange = 100.0, then the intensity of the most intense peak in a spectrum is set to 100, and all
        of the other intensities are linearly scaled to that intensity. Any peak with a scaled intensity of less than 1 is rejected
        as being outside of the dynamic range. Therefore, in addition to normalizing the spectra, it sets an effective relative threshold for peaks.
    </note>
    <note type="input" label="spectrum, total peaks">50</note>
    <note type="input" label="spectrum, maximum parent charge">5</note>
    <note type="input" label="spectrum, use noise suppression">yes</note>
    <note type="input" label="spectrum, minimum parent m+h">400.0</note>
    <note type="input" label="spectrum, maximum parent m+h">6000</note>
    <note type="input" label="spectrum, minimum fragment mz">150.0</note>
    <note type="input" label="spectrum, minimum peaks">6</note>
    <note type="input" label="spectrum, threads">$THREADS</note>

<note type="heading">Residue modification</note>
    <note type="input" label="residue, modification mass">$STATIC_MODS</note>
    <note type="input" label="residue, potential modification mass">$VARIABLE_MODS</note>
    <note type="input" label="residue, potential modification motif"></note>

<note type="heading">Protein general</note>    
    <note type="input" label="protein, taxon">no default</note>
    <note type="input" label="protein, cleavage site">[RK]|{P}</note>
    <!--<note type="input" label="protein, cleavage semi">no</note>-->
    <note type="input" label="protein, cleavage semi">no</note>
    <note type="input" label="protein, cleavage C-terminal mass change">+17.00305</note>
    <note type="input" label="protein, cleavage N-terminal mass change">+1.00794</note>    
    <note type="input" label="protein, N-terminal residue modification mass">0.0</note>
    <note type="input" label="protein, C-terminal residue modification mass">0.0</note>
    <note type="input" label="protein, homolog management">no</note>
    <note type="input" label="protein, quick acetyl">yes</note>
    <note>When this parameter is yes, these common modifications are checked for the peptides generated from the protein's N-terminus, at all stages of analysis.</note>
    <note type="input" label="protein, stP bias">yes</note>


<note type="heading">Scoring</note>
    <note type="input" label="scoring, maximum missed cleavage sites">$MISSEDCLEAVAGE</note>
    <note type="input" label="scoring, x ions">no</note>
    <note type="input" label="scoring, y ions">yes</note>
    <note type="input" label="scoring, z ions">no</note>
    <note type="input" label="scoring, a ions">no</note>
    <note type="input" label="scoring, b ions">yes</note>
    <note type="input" label="scoring, c ions">no</note>
    <note type="input" label="scoring, cyclic permutation">no</note>
    <note type="input" label="scoring, include reverse">no</note>
    $XTANDEM_SCORE
    <note type="input" label="scoring, minimum ion count">1</note>


<note type="heading">model refinement paramters</note>
    <!--<note type="input" label="refine">yes</note>-->
    <note type="input" label="refine">no</note>
    <note type="input" label="refine, spectrum synthesis">yes</note>
    <note type="input" label="refine, maximum valid expectation value">0.1</note>
    <!--<note type="input" label="refine, potential N-terminus modifications">42.01056</note>-->
    <note type="input" label="refine, potential C-terminus modifications"></note>
    <note type="input" label="refine, unanticipated cleavage">no</note>
    <note type="input" label="refine, cleavage semi">no</note>
    <note type="input" label="refine, modification mass">57.021464@C</note>
    <!--<note type="input" label="refine, potential modification mass">79.966331@S,79.966331@T,79.966331@Y</note>-->
    <note type="input" label="refine, point mutations">no</note>
    <note type="input" label="refine, use potential modifications for full refinement">yes</note>
    <note type="input" label="refine, potential modification motif"></note>
    <!--<note type="input" label="scoring, minimum ion count">4</note>-->


<note type="heading">Output</note>
    <note type="input" label="output, message">testing 1 2 3</note>
    <note type="input" label="output, path">output.xml</note>
    <note type="input" label="output, sort results by">spectrum</note>
    <note type="input" label="output, path hashing">no</note>
    <note type="input" label="output, xsl path">tandem-style.xsl</note>
    <note type="input" label="output, parameters">yes</note>
    <note type="input" label="output, performance">yes</note>
    <note type="input" label="output, spectra">yes</note>
    <note type="input" label="output, histograms">no</note>
    <note type="input" label="output, proteins">yes</note>
    <note type="input" label="output, sequences">no</note>
    <note type="input" label="output, one sequence copy">yes</note>
    <note type="input" label="output, results">all</note>
    <note type="input" label="output, maximum valid expectation value">0.1</note>
    <note type="input" label="output, histogram column width">30</note>

</bioml>
"""       
        log.debug('read template from [%s]' % self.__class__.__name__)
        return template,info