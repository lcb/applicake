
'''
Created on May 24, 2012

@author: quandtan
'''
import os
from applicake.applications.proteomics.modifications import ModificationDb
from applicake.applications.proteomics.base import SearchEngine
from applicake.framework.templatehandler import BasicTemplateHandler
from applicake.utils.fileutils import FileUtils
from applicake.utils.xmlutils import XmlValidator
from applicake.utils.dictutils import DictUtils




class Xtandem(SearchEngine):
    '''
    Wrapper for the search engine X!Tandem.
    '''

    XTANDEM_SEMI_CLEAVAGE = 'XTANDEM_SEMI_CLEAVAGE'
    
    def __init__(self):
        '''
        Constructor
        '''
        super(Xtandem,self).__init__()
        self._default_prefix = 'tandem' # default prefix, usually the name of the application        
        base = self.__class__.__name__
        self._taxonomy_file = '%s.taxonomy' % base 
        self._input_file = '%s.input' % base     


    def _define_score(self, info, log):
        if not info.has_key('XTANDEM_SCORE'):
            info['XTANDEM_SCORE'] = 'default'
            log.debug('did not find value for key [%s]. set it to [%s]' % ('XTANDEM_SCORE', info['XTANDEM_SCORE']))
        if info['XTANDEM_SCORE'] == 'default': # for default score, no entry is allowed in template
            info['XTANDEM_SCORE'] = ''
        else:
            info['XTANDEM_SCORE'] = '<note label="scoring, algorithm" type="input">%s</note>' % info['XTANDEM_SCORE']
        return info   

    def _write_input_files(self,info,log):       
        db_file = os.path.join(info[self.WORKDIR],info['DBASE'])
        self._taxonomy_file = os.path.join(info[self.WORKDIR],self._taxonomy_file)
        with open(self._taxonomy_file, "w") as sink:
            sink.write('<?xml version="1.0"?>\n')
            sink.write('<bioml>\n<taxon label="database">')
            sink.write('<file format="peptide" URL="%s"/>' % db_file)
            sink.write("</taxon>\n</bioml>")
        log.debug('Created [%s]' % self._taxonomy_file) 
        self._input_file = os.path.join(info[self.WORKDIR],self._input_file)         
        with open(self._input_file, "w") as sink:
            sink.write('<?xml version="1.0"?>\n')
            sink.write("<bioml>\n<note type='input' label='list path, default parameters'>"+info[self.TEMPLATE]+"</note>\n")
            sink.write("<note type='input' label='output, xsl path' />\n<note type='input' label='output, path'>"+self._result_file+"</note>\n")
            sink.write("<note type='input' label='list path, taxonomy information'>"+self._taxonomy_file+"</note>\n")
            sink.write("<note type='input' label='spectrum, path'>"+info['MZXML']+"</note>\n")
            sink.write("<note type='input' label='protein, taxon'>database</note>\n</bioml>\n")
        log.debug('Created [%s]' % self._input_file)    
        return info

    def define_enzyme(self,info,log):
        """
        See super class.
        
        For X!Tandem, the method has to additionally check for semi cleavage
        """
        info = super(Xtandem,self).define_enzyme(info,log)
        if info[self.ENZYME].endswith(':2'):
            info[self.ENZYME] = info[self.ENZYME][:-2]
            info[self.XTANDEM_SEMI_CLEAVAGE] = 'yes'
        else:
            info[self.XTANDEM_SEMI_CLEAVAGE] = 'no'
        return info
    
    def prepare_run(self,info,log):
        """
        See interface.
        
        - Read the template from the handler
        - Convert scoring and modifications into the specific format
        - Convert enzyme into the specific format        
        - modifies the template from the handler
        - writes the files needed to execute the program 
        
        @precondition: info object need the key [%s]
        """ % self.TEMPLATE
        wd = info[self.WORKDIR]
        log.debug('reset path of application files from current dir to work dir [%s]' % wd)
        self._template_file = os.path.join(wd,self._template_file) 
        info['TEMPLATE'] = self._template_file 
        self._result_file = os.path.join(wd,self._result_file) 
        self._taxonomy_file = os.path.join(wd,self._taxonomy_file)
        log.debug('add key [XTANDEM_RESULT] to info') 
        info['XTANDEM_RESULT'] = self._result_file    
#        info[self.COPY_TO_WD] = info[self.COPY_TO_WD].extend([self._taxonomy_file,self._input_file,self._result_file])        

        # need to create a working copy to prevent replacement or generic definitions
        # with app specific definitions
        app_info = info.copy()
        app_info = self._define_score(app_info, log)
        log.debug('define modifications')
        app_info = self.define_mods(app_info, log)
        log.debug('define enzyme')
        app_info = self.define_enzyme(app_info, log)    
        log.debug('get template handler')
        th = XtandemTemplate()
        log.debug('define score value')     
        log.debug('modify template')                
        mod_template,app_info = th.modify_template(app_info, log)
        log.debug('write input files')        
        app_info = self._write_input_files(app_info, log)        
        prefix,app_info = self.get_prefix(app_info,log)
        command = '%s %s' % (prefix,self._input_file)
        # update original info object with new keys from working copy
        info = DictUtils.merge(log, info, app_info, priority='left')        
        return command,info    

    def set_args(self,log,args_handler):
        """
        See interface
        """        
        args_handler = super(Xtandem, self).set_args(log,args_handler)
        args_handler.add_app_args(log, 'MZXML', 'Peak list file in mzXML format')   
        args_handler.add_app_args(log, 'XTANDEM_SCORE', 'Scoring algorithm used in the search.',choices=['default','k-score','c-score','hrk-score'])        
        
        args_handler.add_app_args(log, "XTANDEMSPECPMMIE", " Spectrum, parent monoisotopic mass isotope")
        args_handler.add_app_args(log, "XTANDEMSPECUSECON", " Spectrum, use")
        args_handler.add_app_args(log, "XTANDEMSPECFMT", " Spectrum, fragment mass")
        args_handler.add_app_args(log, "XTANDEMSPECDR", " Spectrum, dynamic")
        args_handler.add_app_args(log, "XTANDEMSPECTP", " Spectrum, total")
        args_handler.add_app_args(log, "XTANDEMSPECMPCH", " Spectrum, maximum parent")
        args_handler.add_app_args(log, "XTANDEMSPECUNS", " Spectrum, use noise")
        args_handler.add_app_args(log, "XTANDEMSPECMPMPH", " Spectrum, minimum parent")
        args_handler.add_app_args(log, "XTANDEMSPECMAPMPH", " Spectrum, maximum parent")
        args_handler.add_app_args(log, "XTANDEMSPECMIFMZ", " Spectrum, minimum fragment")
        args_handler.add_app_args(log, "XTANDEMSPECMIP", " Spectrum, minimum")
        args_handler.add_app_args(log, "XTANDEMPROCS", " Protein, cleavage")
        args_handler.add_app_args(log, "XTANDEMPRONTRMM", " Protein, N-terminal residue modification")
        args_handler.add_app_args(log, "XTANDEMPROCTRMM", " Protein, C-terminal residue modification")
        args_handler.add_app_args(log, "XTANDEMPROHM", " Protein, homolog")
        args_handler.add_app_args(log, "XTANDEMSCOXI", " Scoring, x")
        args_handler.add_app_args(log, "XTANDEMSCOYI", " Scoring, y")
        args_handler.add_app_args(log, "XTANDEMSCOZI", " Scoring, z")
        args_handler.add_app_args(log, "XTANDEMSCOAI", " Scoring, a")
        args_handler.add_app_args(log, "XTANDEMSCOBI", " Scoring, b")
        args_handler.add_app_args(log, "XTANDEMSCOCI", " Scoring, c")
        args_handler.add_app_args(log, "XTANDEMSCOCP", " Scoring, cyclic")
        args_handler.add_app_args(log, "XTANDEMSCOIR", " Scoring, include")
        args_handler.add_app_args(log, "XTANDEMSCMINICOUNT", " Scoring, minimum ion")
        args_handler.add_app_args(log, "XTANDEMREFINE", "")
        args_handler.add_app_args(log, "XTANDEMREFSS", " Refine, spectrum")
        args_handler.add_app_args(log, "XTANDEMREFMVEV", " Refine, maximum valid expectation")
        args_handler.add_app_args(log, "XTANDEMREFUC", " Refine, unanticipated")
        args_handler.add_app_args(log, "XTANDEMREFCS", " Refine, cleavage")
        args_handler.add_app_args(log, "XTANDEMREFPM", " Refine, point")
        args_handler.add_app_args(log, "XTANDEMREFUPMFFR", " Refine, use potential modifications for full")
        args_handler.add_app_args(log, "XTANDEMREFMM", " Refine, modification")
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
    <note type="input" label="spectrum, parent monoisotopic mass isotope error">$XTANDEMSPECPMMIE</note>
    <note type="input" label="spectrum, parent monoisotopic mass error plus">$PRECMASSERR</note>
    <note type="input" label="spectrum, parent monoisotopic mass error minus">$PRECMASSERR</note>
    <note type="input" label="spectrum, parent monoisotopic mass error units">$PRECMASSUNIT</note>

<note type="heading">Spectrum conditioning</note>
    <note type="input" label="sepctrum, use conditioning">$XTANDEMSPECUSECON</note>
    <note type="input" label="spectrum, fragment mass type">$XTANDEMSPECFMT</note>
    <note type="input" label="spectrum, dynamic range">$XTANDEMSPECDR</note>
    <note>
        This parameter is used to normalize the intensity values of fragment ions, from spectrum to spectrum.
        For example, if Drange = 100.0, then the intensity of the most intense peak in a spectrum is set to 100, and all
        of the other intensities are linearly scaled to that intensity. Any peak with a scaled intensity of less than 1 is rejected
        as being outside of the dynamic range. Therefore, in addition to normalizing the spectra, it sets an effective relative threshold for peaks.
    </note>
    <note type="input" label="spectrum, total peaks">$XTANDEMSPECTP</note>
    <note type="input" label="spectrum, maximum parent charge">$XTANDEMSPECMPCH</note>
    <note type="input" label="spectrum, use noise suppression">$XTANDEMSPECUNS</note>
    <note type="input" label="spectrum, minimum parent m+h">$XTANDEMSPECMPMPH</note>
    <note type="input" label="spectrum, maximum parent m+h">$XTANDEMSPECMAPMPH</note>
    <note type="input" label="spectrum, minimum fragment mz">$XTANDEMSPECMIFMZ</note>
    <note type="input" label="spectrum, minimum peaks">$XTANDEMSPECMIP</note>
    <note type="input" label="spectrum, threads">$THREADS</note>

<note type="heading">Residue modification</note>
    <note type="input" label="residue, modification mass">$STATIC_MODS</note>
    <note type="input" label="residue, potential modification mass">$VARIABLE_MODS</note>
    <note type="input" label="residue, potential modification motif"></note>

<note type="heading">Protein general</note>    
    <note type="input" label="protein, taxon">no default</note>
    <note type="input" label="protein, cleavage site">[RK]|{P}</note>
    <note type="input" label="protein, cleavage semi">$XTANDEM_SEMI_CLEAVAGE</note>
    <note type="input" label="protein, cleavage C-terminal mass change">+17.00305</note>
    <note type="input" label="protein, cleavage N-terminal mass change">+1.00794</note>    
    <note type="input" label="protein, N-terminal residue modification mass">$XTANDEMPRONTRMM</note>
    <note type="input" label="protein, C-terminal residue modification mass">$XTANDEMPROCTRMM</note>
    <note type="input" label="protein, homolog management">$XTANDEMPROHM</note>
    <note type="input" label="protein, quick acetyl">yes</note>
    <note>When this parameter is yes, these common modifications are checked for the peptides generated from the protein's N-terminus, at all stages of analysis.</note>
    <note type="input" label="protein, stP bias">yes</note>

<note type="heading">Scoring</note>
    <note type="input" label="scoring, maximum missed cleavage sites">$MISSEDCLEAVAGE</note>
    <note type="input" label="scoring, x ions">$XTANDEMSCOXI</note>
    <note type="input" label="scoring, y ions">$XTANDEMSCOYI</note>
    <note type="input" label="scoring, z ions">$XTANDEMSCOZI</note>
    <note type="input" label="scoring, a ions">$XTANDEMSCOAI</note>
    <note type="input" label="scoring, b ions">$XTANDEMSCOBI</note>
    <note type="input" label="scoring, c ions">$XTANDEMSCOCI</note>
    <note type="input" label="scoring, cyclic permutation">$XTANDEMSCOCP</note>
    <note type="input" label="scoring, include reverse">$XTANDEMSCOIR</note>
    $XTANDEM_SCORE
    <note type="input" label="scoring, minimum ion count">$XTANDEMSCMINICOUNT</note>

                
<note type="heading">model refinement paramters</note>
    <note type="input" label="refine">$XTANDEMREFINE</note>
    <note type="input" label="refine, spectrum synthesis">$XTANDEMREFSS</note>
    <note type="input" label="refine, maximum valid expectation value">$XTANDEMREFMVEV</note>
    <note type="input" label="refine, potential C-terminus modifications"></note>
    <note type="input" label="refine, unanticipated cleavage">$XTANDEMREFUC</note>
    <note type="input" label="refine, cleavage semi">$XTANDEMREFCS</note>
    <note type="input" label="refine, modification mass">$XTANDEMREFMM</note>
    <note type="input" label="refine, point mutations">$XTANDEMREFPM</note>
    <note type="input" label="refine, use potential modifications for full refinement">$XTANDEMREFUPMFFR</note>
    <note type="input" label="refine, potential modification motif"></note>

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
