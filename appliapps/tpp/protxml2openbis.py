#!/usr/bin/env python
import os

from applicake.app import WrappedApp
from applicake.apputils import validation
from applicake.coreutils.arguments import Argument
from applicake.coreutils.keys import Keys, KeyHelp


class ProtXml2OpenbisSequence(WrappedApp):
    """
    Wrapper for SyBIT-tools protxml2openbis made by lucia.
    """

    def add_args(self):
        return [
            Argument(Keys.WORKDIR, KeyHelp.WORKDIR),
            Argument(Keys.EXECUTABLE, KeyHelp.EXECUTABLE),
            Argument(Keys.PEPXML, KeyHelp.PEPXML),
            Argument('PROTXML', 'Path to a file in protXML format'),
            Argument('DBASE', 'Sequence database file with target/decoy entries'),
            Argument('IPROB','Use same iprob cutoff as used in ProteinProphet (before).'),
            Argument('SPECTRALCOUNT_TYPE','type of spectralcount {all, unique}')
        ]

    def prepare_run(self, log, info):
        wd = info[Keys.WORKDIR]

        info['PEPCSV'] = os.path.join(wd, 'peptides.tsv')
        countprotxml = os.path.join(wd, 'spectralcount.prot.xml')
        modprotxml = os.path.join(wd, 'modifications.prot.xml')
        bisprotxml = os.path.join(wd, 'protxml2openbis.prot.xml')

        command = """pepxml2csv -IPROPHET -header -cP=%s -OUT=%s %s &&
        protxml2modifications -CSV=%s -OUT=%s %s &&
        protxml2openbis -DB=%s -OUT=%s %s &&
        protxml2spectralcount.py -CSV=%s -TYP %s -OUT=%s %s
        """ % (
            info['IPROB'], info['PEPCSV'], info[Keys.PEPXML],
            info['PEPCSV'], modprotxml, info['PROTXML'],
            info['DBASE'], bisprotxml, modprotxml,
            info['PEPCSV'], info['SPECTRALCOUNT_TYPE'], countprotxml, bisprotxml,
        )

        info['PROTXML'] = countprotxml

        return info, command


    def validate_run(self, log, info, exit_code, stdout):
        validation.check_exitcode(log, exit_code)
        validation.check_xml(log, info['PROTXML'])
        return info


if __name__ == "__main__":
    ProtXml2OpenbisSequence.main()