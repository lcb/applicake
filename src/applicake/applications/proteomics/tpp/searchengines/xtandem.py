"""
Created on May 24, 2012

@author: quandtan
"""
import os

from applicake.applications.proteomics.tpp.searchengines.enzymes import enzymestr_to_engine
from applicake.applications.proteomics.tpp.searchengines.modifications import modstr_to_engine
from applicake.framework.interfaces import IWrapper
from applicake.framework.keys import Keys
from applicake.framework.templatehandler import BasicTemplateHandler
from applicake.utils.fileutils import FileUtils
from applicake.utils.xmlutils import XmlValidator


class Xtandem(IWrapper):
    """
    Wrapper for the search engine X!Tandem.
    """

    def set_args(self, log, args_handler):
        args_handler.add_app_args(log, Keys.PREFIX, 'Path to the executable')
        args_handler.add_app_args(log, 'FRAGMASSERR', 'Fragment mass error')
        args_handler.add_app_args(log, 'FRAGMASSUNIT', 'Unit of the fragment mass error')
        args_handler.add_app_args(log, 'PRECMASSERR', 'Precursor mass error')
        args_handler.add_app_args(log, 'PRECMASSUNIT', 'Unit of the precursor mass error')
        args_handler.add_app_args(log, 'MISSEDCLEAVAGE', 'Number of maximal allowed missed cleavages')
        args_handler.add_app_args(log, 'DBASE', 'Sequence database file with target/decoy entries')
        args_handler.add_app_args(log, Keys.ENZYME, 'Enzyme used to digest the proteins')
        args_handler.add_app_args(log, Keys.STATIC_MODS, 'List of static modifications')
        args_handler.add_app_args(log, Keys.VARIABLE_MODS, 'List of variable modifications')
        args_handler.add_app_args(log, Keys.THREADS, 'Number of threads used in the process.')
        args_handler.add_app_args(log, Keys.WORKDIR, 'Directory to store files')
        args_handler.add_app_args(log, 'MZXML', 'Peak list file in mzXML format')
        args_handler.add_app_args(log, 'XTANDEM_SCORE', 'Scoring algorithm used in the search.',
                                  choices=['default', 'k-score', 'c-score', 'hrk-score', ])
        return args_handler

    def prepare_run(self, info, log):
        wd = info[Keys.WORKDIR]
        # need to create a working copy to prevent replacement or generic definitions
        # with app specific definitions
        app_info = info.copy()
        app_info['XTANDEM_INPUT'] = os.path.join(wd, 'xtandem.input')
        app_info['TEMPLATE'] = os.path.join(wd, 'xtandem.params')
        app_info['XTANDEM_RESULT'] = os.path.join(wd, 'xtandem.result')
        app_info['XTANDEM_TAXONOMY'] = os.path.join(wd, 'xtandem.taxonomy')

        app_info = self._define_score(app_info, log)

        app_info["STATIC_MODS"], app_info["VARIABLE_MODS"], _ = modstr_to_engine(info["STATIC_MODS"],
                                                                                 info["VARIABLE_MODS"], 'XTandem')
        app_info[Keys.ENZYME], app_info['XTANDEM_SEMI_CLEAVAGE'] = enzymestr_to_engine(info[Keys.ENZYME], 'XTandem')
        _, app_info = XtandemTemplate().modify_template(app_info, log)
        self._write_input_files(app_info, log)

        prefix = info.get(Keys.PREFIX, 'tandem')

        #addin conversion
        pepxml = os.path.join(wd, 'xtandem.pep.xml')
        info[Keys.PEPXMLS] = [pepxml]
        command = '%s %s && Tandem2XML %s %s ' % (prefix, app_info['XTANDEM_INPUT'], app_info['XTANDEM_RESULT'], pepxml)
        return command, info

    @staticmethod
    def _define_score(info, log):
        if not info.has_key('XTANDEM_SCORE'):
            log.info('No score given, using default score')
            info['XTANDEM_SCORE'] = ''
        # for default score, no entry is allowed in template
        elif info['XTANDEM_SCORE'] == 'default':
            log.info('Using default score')
            info['XTANDEM_SCORE'] = ''
        # for k-score add special tags
        elif info['XTANDEM_SCORE'] == 'k-score':
            log.info('Using k-score')
            info['XTANDEM_SCORE'] = '<note label="scoring, algorithm" type="input">%s</note>' \
                                    '<note label="spectrum, use conditioning" type="input" >no</note>' \
                                    '<note label="scoring, minimum ion count" type="input">1</note>' % info[
                                        'XTANDEM_SCORE']
        else:
            log.warn('Using special score %s' % info['XTANDEM_SCORE'])
            info['XTANDEM_SCORE'] = '<note label="scoring, algorithm" type="input">%s</note>' % info['XTANDEM_SCORE']
        return info

    @staticmethod
    def _write_input_files(info, log):
        open(info['XTANDEM_TAXONOMY'], "w").write(
            '<?xml version="1.0"?>\n<bioml>\n'
            '<taxon label="database"><file format="peptide" URL="%s"/></taxon>'
            '\n</bioml>' % info['DBASE']
        )

        open(info['XTANDEM_INPUT'], "w").write(
            '<?xml version="1.0"?>\n'
            '<bioml>\n<note type="input" label="list path, default parameters">%s</note>\n'
            '<note type="input" label="output, xsl path" />\n'
            '<note type="input" label="output, path">%s</note>\n'
            '<note type="input" label="list path, taxonomy information">%s</note>\n'
            '<note type="input" label="spectrum, path">%s</note>\n'
            '<note type="input" label="protein, taxon">database</note>\n</bioml>\n' % \
            (info['TEMPLATE'], info['XTANDEM_RESULT'], info['XTANDEM_TAXONOMY'], info['MZXML'])
        )
        return info


    def validate_run(self, info, log, run_code, out_stream, err_stream):
        if 0 != run_code:
            return run_code, info
        out_stream.seek(0)
        if 'Valid models = 0' in out_stream.read():
            log.critical('No valid model found')
            return 1, info
        result_file = info[Keys.PEPXMLS][0]
        if not FileUtils.is_valid_file(log, result_file):
            log.critical('[%s] is not valid' % result_file)
            return 1, info
        if not XmlValidator.is_wellformed(result_file):
            log.critical('[%s] is not well formed.' % result_file)
            return 1, info
        return 0, info


class XtandemTemplate(BasicTemplateHandler):
    """
    Template handler for Xtandem.  
    """

    def read_template(self, info, log):
        """
        See super class.
        Template carefully checked Dec 2012 by hroest, olgas & loblum 
        """
        template = """<?xml version="1.0"?>
<?xml-stylesheet type="text/xsl" href="tandem-input-style.xsl"?>
<bioml>

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
    <note type="input" label="protein, cleavage site">$ENZYME</note>
    <note type="input" label="protein, cleavage semi">$XTANDEM_SEMI_CLEAVAGE</note>
<!--   do not add, otherwise xinteracts generates tons of confusing modification entries
    <note type="input" label="protein, cleavage C-terminal mass change">+17.00305</note>
    <note type="input" label="protein, cleavage N-terminal mass change">+1.00794</note>    
-->
    <note type="input" label="protein, N-terminal residue modification mass">0.0</note>
    <note type="input" label="protein, C-terminal residue modification mass">0.0</note>
    <note type="input" label="protein, homolog management">no</note>
    <!-- explicitly disabled -->
    <note type="input" label="protein, quick acetyl">no</note>
    <note type="input" label="protein, quick pyrolidone">no</note>

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


<note type="heading">model refinement paramters</note>
    <note type="input" label="refine">no</note>

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
        return template, info
