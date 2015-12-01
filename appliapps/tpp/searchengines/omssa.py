#!/usr/bin/env python
import os

from appliapps.tpp.searchengines.enzymes import enzymestr_to_engine
from appliapps.tpp.searchengines.modifications import genmodstr_to_engine
from appliapps.tpp.searchengines.searchenginebase import SearchEnginesBase
from applicake.app import WrappedApp
from applicake.apputils import validation
from applicake.apputils import templates
from applicake.coreutils.arguments import Argument
from applicake.coreutils.keys import Keys, KeyHelp


class Omssa(SearchEnginesBase):
    """
    Wrapper for the search engine OMSSA.

    About the template:
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

    def prepare_run(self, log, info):
        wd = info[Keys.WORKDIR]

        #add in blast and mzxml2mgf conversion
        omssadbase = os.path.join(wd, os.path.basename(info['DBASE']))
        os.symlink(info['DBASE'], omssadbase)
        mzxmlbase = os.path.basename(info[Keys.MZXML])
        mzxmllink = os.path.join(wd, mzxmlbase)
        mgffile = os.path.join(wd, os.path.splitext(mzxmlbase)[0] + '.mgf')
        os.symlink(info[Keys.MZXML], mzxmllink)

        basename = os.path.splitext(os.path.split(info[Keys.MZXML])[1])[0]
        result = os.path.join(wd, basename+'.pep.xml')
        iresult = os.path.join(wd, basename+'.withRT.pep.xml')
        info[Keys.PEPXML] = iresult

        # need to create a working copy to prevent replacement or generic definitions
        # with app specific definitions
        app_info = info.copy()
        app_info['DBASE'] = omssadbase

        if info['FRAGMASSUNIT'] == 'ppm':
            raise RuntimeError("OMSSA does not support frag mass error unit PPM")

        app_info['USERMODXML'] = os.path.join(wd, 'usermod.xml')
        app_info["STATIC_MODS"], app_info["VARIABLE_MODS"], tpl = genmodstr_to_engine(info["STATIC_MODS"],
                                                                                   info["VARIABLE_MODS"], 'Omssa')
        if app_info['STATIC_MODS']:
            app_info['STATIC_MODS'] = "-mf " + app_info['STATIC_MODS']
        if app_info['VARIABLE_MODS']:
            app_info['VARIABLE_MODS'] = "-mv " + app_info['VARIABLE_MODS']

        open(app_info['USERMODXML'], 'w').write(tpl)
        app_info['ENZYME'], _ = enzymestr_to_engine(info['ENZYME'], 'Omssa')
        mod_template = templates.modify_template(app_info, templates.read_template(templates.get_tpl_of_class(self)))
        # necessary check for the precursor mass unig
        if app_info['PRECMASSUNIT'].lower() == "ppm":
            mod_template += ' -teppm'
            log.debug('added [ -teppm] to modified template because the precursor mass is defined in ppm')

        exe = app_info.get(Keys.EXECUTABLE, 'omssacl')

        #grep to prevent log overflow, InteractParser to add RT to pepXML
        command = "makeblastdb -dbtype prot -in %s && " \
                  "MzXML2Search -mgf %s | grep -v scan && " \
                  "%s %s -fm %s -op %s && " \
                  "InteractParser %s %s -S" % (
                      omssadbase,
                      mzxmllink,
                      exe, mod_template, mgffile, result,
                      iresult, result)
        return info, command


    def validate_run(self, log, info, exit_code, stdout):
        validation.check_exitcode(log, exit_code)
        validation.check_stdout(log,stdout)
        validation.check_xml(log, info[Keys.PEPXML])
        return info

if __name__ == "__main__":
    Omssa.main()