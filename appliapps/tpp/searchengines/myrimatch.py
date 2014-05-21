#!/usr/bin/env python
import os

from appliapps.tpp.searchengines.enzymes import enzymestr_to_engine
from appliapps.tpp.searchengines.modifications import genmodstr_to_engine
from applicake.app import WrappedApp
from applicake.apputils.templates import read_mod_write, get_tpl_of_class
from applicake.apputils.validation import check_exitcode, check_xml
from applicake.coreutils.arguments import Argument
from applicake.coreutils.keys import Keys, KeyHelp


class Myrimatch(WrappedApp):
    """
    Wrapper for the search engine Myrimatch.
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
        tpl = os.path.join(wd, 'myrimatch.cfg')
        basename = os.path.splitext(os.path.split(info[Keys.MZXML])[1])[0]
        info[Keys.PEPXML] = os.path.join(wd, basename + ".pepXML")  #myrimatch default is pepXML NOT pep.xml

        # need to create a working copy to prevent replacement or generic definitions
        # with app specific definitions
        app_info = info.copy()
        app_info['ENZYME'], app_info['MYRIMATCH_MINTERMINICLEAVAGES'] = enzymestr_to_engine(info['ENZYME'],
                                                                                            'Myrimatch')
        app_info["STATIC_MODS"], app_info["VARIABLE_MODS"], _ = genmodstr_to_engine(info["STATIC_MODS"],
                                                                                 info["VARIABLE_MODS"], 'Myrimatch')
        if app_info['FRAGMASSUNIT'] == 'Da':
            app_info['FRAGMASSUNIT'] = 'daltons'

        tplfile = os.path.join(wd, "myrimatch.cfg")
        read_mod_write(app_info, get_tpl_of_class(self), tplfile)

        exe = app_info.get(Keys.EXECUTABLE, 'myrimatch')
        command = "%s -cpus %s -cfg %s -workdir %s -ProteinDatabase %s %s" % (
            exe, app_info['THREADS'], tpl,
            app_info[Keys.WORKDIR], app_info['DBASE'],
            app_info[Keys.MZXML])
        # update original info object with new keys from working copy
        #info = DictUtils.merge(log, info, app_info, priority='left')        
        return info, command

    def validate_run(self, log, info, exit_code, stdout):
        check_exitcode(log, exit_code)
        check_xml(log, info[Keys.PEPXML])
        return info

if __name__ == "__main__":
    Myrimatch.main()