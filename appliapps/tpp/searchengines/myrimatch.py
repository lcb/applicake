#!/usr/bin/env python
import os
import shutil
import re

from appliapps.tpp.searchengines.enzymes import enzymestr_to_engine
from appliapps.tpp.searchengines.modifications import genmodstr_to_engine
from applicake.app import WrappedApp
from applicake.apputils.templates import read_mod_write, get_tpl_of_class
from applicake.apputils.validation import check_exitcode, check_xml
from applicake.coreutils.keys import Keys, KeyHelp
from appliapps.tpp.searchengines.searchenginebase import SearchEnginesBase
from applicake.coreutils.arguments import Argument

class Myrimatch(SearchEnginesBase):
    """
    Wrapper for the search engine Myrimatch.
    """

    def add_args(self):
        args = super(Myrimatch, self).add_args()
        args.append(Argument('MYRIMATCH_DIR', 'executable location.', default=''))
        args.append(Argument('MYRIMATCH_EXE',KeyHelp.EXECUTABLE, default='myrimatch'))
        return args

    def prepare_run(self, log, info):
        wd = info[Keys.WORKDIR]
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

        #link DB to cwd
        app_info['DBASE'] = os.path.join(wd, os.path.basename(info['DBASE']))
        os.symlink(info['DBASE'], app_info['DBASE'])

        #tpl = os.path.join(wd, 'myrimatch.cfg')
        tpl = 'myrimatch.cfg'
        tplfile = os.path.join(wd, tpl)
        read_mod_write(app_info, get_tpl_of_class(self), tplfile)

        exe_path = app_info['MYRIMATCH_DIR']
        exe = app_info['MYRIMATCH_EXE']
        command = "{exe} -cpus {threads} -cfg {tpl} -workdir {workdir} -ProteinDatabase {dbase} {mzxml}".format(
            exe=os.path.join(exe_path, exe), threads=app_info['THREADS'], tpl=tpl,
            workdir=app_info[Keys.WORKDIR], dbase=app_info['DBASE'],
            mzxml=app_info[Keys.MZXML])
        # update original info object with new keys from working copy
        #info = DictUtils.merge(log, info, app_info, priority='left')        
        return info, command

    def validate_run(self, log, info, exit_code, stdout):
        check_exitcode(log, exit_code)
        check_xml(log, info[Keys.PEPXML])

        #https://groups.google.com/forum/#!topic/spctools-discuss/dV8LSaE60ao
        shutil.move(info[Keys.PEPXML], info[Keys.PEPXML]+'.broken')
        fout = open(info[Keys.PEPXML],'w')
        for line in open(info[Keys.PEPXML]+'.broken').readlines():
            if 'spectrumNativeID' in line:
                line = re.sub('spectrumNativeID="[^"]*"', '', line)
            fout.write(line)
        fout.close()

        return info

if __name__ == "__main__":
    Myrimatch.main()