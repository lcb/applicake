#!/usr/bin/env python
import os

from appliapps.tpp.searchengines.enzymes import enzymestr_to_engine
from appliapps.tpp.searchengines.modifications import genmodstr_to_engine
from applicake.app import WrappedApp
from applicake.apputils.templates import read_mod_write, get_tpl_of_class
from applicake.apputils.validation import check_exitcode, check_xml, check_stdout
from applicake.coreutils.arguments import Argument
from applicake.coreutils.keys import Keys, KeyHelp


class Comet(WrappedApp):
    """
    Wrapper for the search engine comet.
    """

    def add_args(self):
        return [
            Argument(Keys.EXECUTABLE, KeyHelp.EXECUTABLE),
            Argument(Keys.WORKDIR, KeyHelp.WORKDIR),
            Argument(Keys.THREADS, KeyHelp.THREADS),
            Argument(Keys.MZXML, KeyHelp.MZXML),

            Argument('FRAGMASSERR', 'Fragment mass error'),
            Argument('FRAGMASSUNIT', 'Unit of the fragment mass error'),
            Argument('PRECMASSERR', 'Precursor mass error'),
            Argument('PRECMASSUNIT', 'Unit of the precursor mass error'),
            Argument('MISSEDCLEAVAGE', 'Number of maximal allowed missed cleavages'),
            Argument('DBASE', 'Sequence database file with target/decoy entries'),
            Argument('ENZYME', 'Enzyme used to digest the proteins'),
            Argument('STATIC_MODS', 'List of static modifications'),
            Argument('VARIABLE_MODS', 'List of variable modifications'),
        ]

    def prepare_run(self, log, info):
        wd = info[Keys.WORKDIR]
        basename = os.path.join(wd, os.path.splitext(os.path.split(info[Keys.MZXML])[1])[0])
        info[Keys.PEPXML] = basename + '.pep.xml'

        # need to create a working copy to prevent replacement or generic definitions
        # with app specific definitions
        app_info = info.copy()

        if info['PRECMASSUNIT'] == 'Da':
            app_info['PRECMASSUNIT'] = '0'
        elif info['PRECMASSUNIT'] == 'ppm':
            app_info['PRECMASSUNIT'] = '2'
        else:
            raise RuntimeError("Precmassunit %s unknown" % info['PRECMASSUNIT'])

        if info['FRAGMASSUNIT'] == 'ppm':
            raise RuntimeError("Comet does not support frag mass error unit PPM")

        if not 0.01 < float(app_info['FRAGMASSERR']) < 1.1:
            log.warn('Very high or low fragmasserror ' + app_info['FRAGMASSERR'])

        app_info["STATIC_MODS"], app_info["VARIABLE_MODS"], _ = genmodstr_to_engine(info["STATIC_MODS"],
                                                                                 info["VARIABLE_MODS"], 'Comet')
        app_info['ENZYME'], app_info['NUM_TERM_CLEAVAGES'] = enzymestr_to_engine(info['ENZYME'], 'Comet')

        tplfile = os.path.join(wd, "comet.params")
        read_mod_write(app_info, get_tpl_of_class(self), tplfile)
        exe = app_info.get(Keys.EXECUTABLE, 'comet')

        command = "%s -N%s -P%s %s" % (exe, basename, tplfile, info[Keys.MZXML])
        return info, command

    def validate_run(self, log, info, exit_code, stdout):
        if "Warning - no spectra searched" in stdout:
            raise RuntimeError("No spectra in mzXML!")
        check_stdout(log,stdout)
        check_exitcode(log, exit_code)
        check_xml(log, info[Keys.PEPXML])
        return info


if __name__ == "__main__":
    Comet.main()