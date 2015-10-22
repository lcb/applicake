#!/usr/bin/env python
import os

from appliapps.tpp.searchengines.enzymes import enzymestr_to_engine
from applicake.app import WrappedApp
from applicake.apputils import validation
from applicake.coreutils.arguments import Argument
from applicake.coreutils.keys import Keys, KeyHelp

class PeptideProphetSequence(WrappedApp):
    """
    Corrects pepxml output to make compatible with TPP and openms, then executes xinteract
    (step by step because of semiTrypsin option)
    """

    def add_args(self):
        return [
            Argument(Keys.WORKDIR, KeyHelp.WORKDIR),
            Argument(Keys.PEPXML, KeyHelp.PEPXML),
            Argument('ENZYME', 'Enzyme used for digest'),
            Argument('DBASE', 'FASTA dbase'),
            Argument('MZXML', 'Path to the original MZXML inputfile'),
            Argument('TPPDIR', 'Path to the tpp',  default=''),
            Argument('DECOY', 'Decoy pattern', default='DECOY_')
        ]

    def prepare_run(self, log, info):
        """
        -OI PI
        -Ow INSTRWARN
        -dDECOY_ -OAPdlIw (dummy)
        """

        # XTINERACT
        # TODO check if this is needed
        info['XINTERACT'] = '-dDECOY_ -OAPdlIw'
        result = os.path.join(info[Keys.WORKDIR], 'interact.pep.xml')
        enz, _ = enzymestr_to_engine(info['ENZYME'], 'InteractParser')

        command=[]
        command.append(
            "{tppdir}InteractParser {result} {pepxml} -E{enzyme}".format(tppdir=info['TPPDIR'],result=result,pepxml=info[Keys.PEPXML],enzyme=enz)
        )
        command.append(
            "{tppdir}RefreshParser {result} {database}".format(
                tppdir=info['TPPDIR'], result=result, pepxml=info[Keys.PEPXML],enzyme=enz,database=info['DBASE'])
        )
        command.append(
            "{tppdir}PeptideProphetParser {result} DECOY={decoy} ACCMASS NONPARAM DECOYPROBS LEAVE PI INSTRWARN".format(
            tppdir =info['TPPDIR'] ,result=result, )
        )

        info[Keys.PEPXML] = result
        return info, command

    def validate_run(self, log, info, run_code, out):
        if "No decoys with label DECOY_ were found" in out:
            raise RuntimeError("No DECOY_s found in fasta. Please use other fasta!")
        validation.check_stdout(log, out)
        validation.check_exitcode(log, run_code)
        validation.check_xml(log, info[Keys.PEPXML])
        return info


if __name__ == "__main__":
    PeptideProphetSequence.main()
