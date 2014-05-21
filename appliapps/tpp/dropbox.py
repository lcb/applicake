#!/usr/bin/env python
import os
import subprocess
import shutil
import getpass

from applicake.app import BasicApp
from applicake.coreutils.arguments import Argument
from applicake.coreutils.info import IniInfoHandler
from applicake.coreutils.keys import Keys, KeyHelp
from applicake.apputils import templates, dropbox


class Copy2IdentDropbox(BasicApp):
    def add_args(self):
        return [
            Argument(Keys.ALL_ARGS, KeyHelp.ALL_ARGS),
            Argument(Keys.WORKDIR, KeyHelp.WORKDIR)
        ]

    def run(self, log, info):

        info['WORKFLOW'] = dropbox.extendWorkflowID(info['WORKFLOW'])
        info['DROPBOXSTAGE'] = dropbox.make_stagebox(log, info)
        info['EXPERIMENT_CODE']= dropbox.get_experiment_code(info)

        keys = [Keys.PEPXML, 'PEPCSV']
        dropbox.keys_to_dropbox(log, info, keys, info['DROPBOXSTAGE'])

        #protxml special naming
        filename = os.path.basename(info['DROPBOXSTAGE']) + '.prot.xml'
        filepath = os.path.join(info['DROPBOXSTAGE'], filename)
        shutil.copy(info['PROTXML'], filepath)

        #search.properties requires some specific fields
        sinfo = info.copy()
        sinfo['PEPTIDEFDR'] = info['PEPTIDEFDR']
        sinfo['DBASENAME'] = os.path.splitext(os.path.split(info['DBASE'])[1])[0]
        sinfo['PARENT-DATA-SET-CODES'] = info[Keys.DATASET_CODE]

        # set values to NONE if they were e.g. "" before
        for key in ['STATIC_MODS', 'VARIABLE_MODS']:
            if info.get(key, "") == "":
                sinfo[key] = 'NONE'
        #lowercase required
        sinfo['experiment-code'] = info['EXPERIMENT_CODE']

        path = os.path.join(info['DROPBOXSTAGE'], 'search.properties')
        IniInfoHandler().write(sinfo, path)

        #write mail to dropbox but do not send yet (after viewer only)
        info['MAILFILE'] = os.path.join(info['DROPBOXSTAGE'], 'mailtext.txt')
        self._writemail(info.copy())

        info['DROPBOXSTAGE'] = dropbox.move_stage_to_dropbox(log, info['DROPBOXSTAGE'], info['DROPBOX'], keepCopy=True)
        return info

    def _writemail(self, info):
        info['USERNAME'] = getpass.getuser()

        if info.get('RUNTPP2VIEWER', 'no') == 'no':
            info["LINKTEXT"] = "RUNTPP2VIEWER was 'no'. If you want to visualize the results"
        else:
            basepath = '/IMSB/ra/' + info['USERNAME'] + '/html/petunia/tpp2viewer3_' + info['EXPERIMENT_CODE']
            info["LINKTEXT"] = """To visualize the results use:
https://imsb-ra-tpp.ethz.ch/tpp/cgi-bin/PepXMLViewer.cgi?xmlFileName=%s
https://imsb-ra-tpp.ethz.ch/tpp/cgi-bin/protxml2html.pl?xmlfile=%s

In case the links do not work""" % (basepath + '.pep.xml', basepath + '.prot.xml')

        info['ENGINES_VERSIONS'] = ''
        if 'RUNTANDEM' in info and info['RUNTANDEM'] == 'True':
            info['ENGINES_VERSIONS'] += subprocess.check_output("tandem a | grep TANDEM",
                                                                shell=True)

        if 'RUNOMSSA' in info and info['RUNOMSSA'] == 'True':
            info['ENGINES_VERSIONS'] += subprocess.check_output("omssacl -version", shell=True).replace(
                "2.1.8", "2.1.9")

        if 'RUNMYRIMATCH' in info and info['RUNMYRIMATCH'] == 'True':
            info['ENGINES_VERSIONS'] += subprocess.check_output("myrimatch 2>&1 | grep MyriMatch",
                                                                shell=True)

        if 'RUNCOMET' in info and info['RUNCOMET'] == 'True':
            info['ENGINES_VERSIONS'] += subprocess.check_output("comet 2>&1 | grep version", shell=True)
        info['ENGINES_VERSIONS'] = info['ENGINES_VERSIONS'].strip()

        info['TPPVERSION'] = subprocess.check_output("InteractParser 2>&1 | grep TPP", shell=True).split("(")[1]

        templates.read_mod_write(info, templates.get_tpl_of_class(self), info['MAILFILE'])


if __name__ == "__main__":
    Copy2IdentDropbox.main()