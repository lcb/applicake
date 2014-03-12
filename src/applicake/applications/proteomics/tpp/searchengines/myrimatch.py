"""
Created on Jun 24, 2012

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


class Myrimatch(IWrapper):
    """
    Wrapper for the search engine Myrimatch.
    """

    def prepare_run(self, info, log):
        wd = info[Keys.WORKDIR]

        info['TEMPLATE'] = os.path.join(wd, 'myrimatch.cfg')
        basename = os.path.splitext(os.path.split(info['MZXML'])[1])[0]
        info[Keys.PEPXMLS] = [os.path.join(wd, basename + ".pepXML")]  #myrimatch default is pepXML NOT pep.xml

        # need to create a working copy to prevent replacement or generic definitions
        # with app specific definitions
        app_info = info.copy()
        app_info['ENZYME'], app_info['MYRIMATCH_MINTERMINICLEAVAGES'] = enzymestr_to_engine(info[Keys.ENZYME], 'Myrimatch')
        app_info["STATIC_MODS"], app_info["VARIABLE_MODS"], _ = modstr_to_engine(info["STATIC_MODS"],
                                                                                 info["VARIABLE_MODS"], 'Myrimatch')
        if app_info['FRAGMASSUNIT'] == 'Da':
            log.debug("replace 'FRAGMASSUNIT' with value [Da] to [daltons]")
            app_info['FRAGMASSUNIT'] = 'daltons'
        mod_template, _ = MyrimatchTemplate().modify_template(app_info, log)

        prefix = app_info.get('PREFIX', 'myrimatch')
        command = "%s -cpus %s -cfg %s -workdir %s -ProteinDatabase %s %s" % (
            prefix, app_info['THREADS'], app_info['TEMPLATE'],
            app_info[Keys.WORKDIR], app_info['DBASE'],
            app_info['MZXML'])
        # update original info object with new keys from working copy
        #info = DictUtils.merge(log, info, app_info, priority='left')        
        return command, info

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
        return args_handler

    def validate_run(self, info, log, run_code, out_stream, err_stream):
        if 0 != run_code:
            return run_code, info
        result_file = info[Keys.PEPXMLS][0]
        if not FileUtils.is_valid_file(log, result_file):
            log.critical('[%s] is not valid' % result_file)
            return 1, info
        if not XmlValidator.is_wellformed(result_file):
            log.critical('[%s] is not well formed.' % result_file)
            return 1, info
        return 0, info


class MyrimatchTemplate(BasicTemplateHandler):
    """
    Template handler for Myrimatch.
    """

    def read_template(self, info, log):

        template = """MonoPrecursorMzTolerance = $PRECMASSERR $PRECMASSUNIT
FragmentMzTolerance = $FRAGMASSERR $FRAGMASSUNIT
CleavageRules = "$ENZYME"
MaxMissedCleavages = $MISSEDCLEAVAGE
MinTerminiCleavages = $MYRIMATCH_MINTERMINICLEAVAGES
DynamicMods = "$VARIABLE_MODS"
StaticMods = "$STATIC_MODS"

DecoyPrefix = ""
TicCutoffPercentage = 0.95
PrecursorMzToleranceRule = "mono"
FragmentationAutoRule = false
FragmentationRule= "cid"
NumChargeStates = 5
MaxPeptideMass = 6500
MinPeptideMass = 400
MaxDynamicMods = 4
MaxResultRank = 1
"""
        return template, info
