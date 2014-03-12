"""
Created on Jun 14, 2012

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


class Omssa(IWrapper):
    """
    Wrapper for the search engine OMSSA.
    """
    def prepare_run(self, info, log):
        wd = info[Keys.WORKDIR]

        #add in blast and mzxml2mgf conversion
        omssadbase = os.path.join(wd,os.path.basename(info['DBASE']))
        os.symlink(info['DBASE'],omssadbase)
        mzxmlbase = os.path.basename(info['MZXML'])
        mzxmllink = os.path.join(wd, mzxmlbase )
        mgffile = os.path.join(wd, os.path.splitext(mzxmlbase)[0] + '.mgf')
        os.symlink(info['MZXML'], mzxmllink)
        
        basename = os.path.splitext(os.path.split(info['MZXML'])[1])[0]
        result_file = os.path.join(wd, basename + ".pep.xml")
        info['PEPXMLS'] = [result_file]
        # need to create a working copy to prevent replacement or generic definitions
        # with app specific definitions
        app_info = info.copy()
        app_info['DBASE'] = omssadbase

        if info['FRAGMASSUNIT'] == 'ppm':
            log.fatal("OMSSA does not support frag mass error unit PPM")
            return "false", info

        app_info['USERMODXML'] = os.path.join(wd,'usermod.xml')
        app_info["STATIC_MODS"], app_info["VARIABLE_MODS"], tpl = modstr_to_engine(info["STATIC_MODS"], info["VARIABLE_MODS"], 'Omssa')
        if app_info['STATIC_MODS']:
            app_info['STATIC_MODS'] = "-mf " + app_info['STATIC_MODS']
        if app_info['VARIABLE_MODS']:
            app_info['VARIABLE_MODS'] = "-mv " + app_info['VARIABLE_MODS']


        open(app_info['USERMODXML'],'w').write(tpl)
        app_info['ENZYME'], _ = enzymestr_to_engine(info[Keys.ENZYME], 'Omssa')
        mod_template, _ = OmssaTemplate().modify_template(app_info, log)
        # necessary check for the precursor mass unig
        if app_info['PRECMASSUNIT'].lower() == "ppm":
            mod_template += ' -teppm'
            log.debug('added [ -teppm] to modified template because the precursor mass is defined in ppm')

        result = os.path.join(wd,'omssa.pep.xml')
        info[Keys.PEPXMLS] = [result]
        prefix = app_info.get('PREFIX','omssacl')

        command = "makeblastdb -dbtype prot -in %s && MzXML2Search -mgf %s | grep -v scan && %s %s -fm %s -op %s" % (omssadbase,mzxmllink ,prefix, mod_template, mgffile, result)
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


class OmssaTemplate(BasicTemplateHandler):
    """
    Template handler for Omssa.
 -zcc 1
   how should precursor charges be determined? (1=believe the input file,
   2=use a range)
   Default = 2
   tandem: google: tandem uses inputfile charge
   myrimatch: <override existing charge>bool(false)

 -hl 1
   maximum number of hits retained per precursor charge state per spectrum
   during the search
   Default = `30'
   myrimatch: MaxResultRank = 1

 -he 100000.0
   the maximum evalue allowed in the hit list
   Default = `1'

 -ii 0
   evalue threshold to iteratively search a spectrum again, 0 = always
   Default = `0.01'

 -h1 100
   number of peaks allowed in single charge window (0 = number of ion species)
   Default = `2'

 -h2 100
   number of peaks allowed in double charge window (0 = number of ion species)
   Default = `2'
    """

    def read_template(self, info, log):
        
        template = """-nt $THREADS -d $DBASE -e $ENZYME -v $MISSEDCLEAVAGE $STATIC_MODS $VARIABLE_MODS -mux $USERMODXML  -te $PRECMASSERR -to $FRAGMASSERR  -zcc 1 -hl 1 -he 100000.0 -ii 0 -h1 100 -h2 100
"""
        log.debug('read template from [%s]' % self.__class__.__name__)
        return template, info
