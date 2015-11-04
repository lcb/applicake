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
            Argument('DECOY', 'Decoy pattern', default='DECOY_'),
            Argument('TPPDIR', 'Path to the tpp',  default='')
        ]

    def prepare_run(self, log, info):
        """
        -OI PI
        -Ow INSTRWARN
        -dDECOY_ -OAPdlIw (dummy)
        """

        # XTINERACT
        # TODO check if this is needed
        #info['XINTERACT'] = '-dDECOY_ -OAPdlIw'
        result = os.path.join(info[Keys.WORKDIR], 'interact.pep.xml')
        enz, _ = enzymestr_to_engine(info['ENZYME'], 'InteractParser')

        command = []
        tpp_dir = info['TPPDIR']
        command.append(
            "{exe} {result} {pepxml} -E{enzyme}".format(exe=os.path.join(info['TPPDIR'],"InteractParser"),result=result,pepxml=info[Keys.PEPXML],enzyme=enz)
        )
        command.append(
            "{exe} {result} {database}".format(
            exe=os.path.join(info['TPPDIR'],"RefreshParser"), result=result, pepxml=info[Keys.PEPXML],enzyme=enz,database=info['DBASE'])
        )
        command.append(
            "{exe} {result} DECOY={decoy} ACCMASS NONPARAM DECOYPROBS LEAVE PI INSTRWARN".format(
            exe = os.path.join(info['TPPDIR'],"PeptideProphetParser"), result=result, decoy=info['DECOY'])
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
