#!/usr/bin/env python
import os

from appliapps.tpp.fdr import get_iprob_for_fdr
from applicake.app import WrappedApp
from applicake.apputils import validation
from applicake.coreutils.arguments import Argument
from applicake.coreutils.keys import Keys, KeyHelp
from applicake.apputils import templates


class PeakpickerFeaturefinder(WrappedApp):
    def add_args(self):
        return [
            Argument(Keys.WORKDIR, KeyHelp.WORKDIR),
            Argument(Keys.MZXML, KeyHelp.MZXML),

            Argument(Keys.PEPXML, KeyHelp.PEPXML),
            Argument('MAYUOUT','mayu out csv'),
            Argument('FDR_TYPE', "type of FDR: iprophet/mayu m/pep/protFDR"),
            Argument("FDR_CUTOFF", "cutoff for FDR"),

            Argument("PEAKPICKER_SIGNAL_TO_NOISE", ""),
            Argument("PEAKPICKER_MS1_ONLY", ""),
            Argument("FEATUREFINDER_MASS_TRACE__MZ_TOLERANCE", ""),
            Argument("FEATUREFINDER_MASS_TRACE__MIN_SPECTRA", ""),
            Argument("FEATUREFINDER_MASS_TRACE__MAX_MISSING", ""),
            Argument("FEATUREFINDER_ISOTOPIC_PATTERN__CHARGE_LOW", ""),
            Argument("FEATUREFINDER_ISOTOPIC_PATTERN__CHARGE_HIGH", ""),
            Argument("FEATUREFINDER_ISOTOPIC_PATTERN__MZ_TOLERANCE", ""),
            Argument("FEATUREFINDER_FEATURE__MIN_SCORE", ""),
            Argument("FEATUREFINDER_FEATURE__MIN_ISOTOPE_FIT", ""),
            Argument("FEATUREFINDER_FEATURE__MIN_TRACE_SCORE", ""),
            Argument("FEATUREFINDER_SEED__MIN_SCORE", ""),
            Argument("FEATUREFINDER_MASS_TRACE__SLOPE_BOUND", ""),
            Argument("IDMAPPER_RT_TOLERANCE", ""),
            Argument("IDMAPPER_MZ_TOLERANCE", ""),
            Argument("IDMAPPER_MZ_REFERENCE", ""),
            Argument("IDMAPPER_USE_CENTROID_MZ", "")
        ]

    def prepare_run(self, log, info):
        wd = info[Keys.WORKDIR]
        # get iProb corresponding FDR for IDFilter
        info['IPROB'], info['FDR'] = get_iprob_for_fdr(info['FDR_CUTOFF'], info['FDR_TYPE'], mayuout=info.get('MAYUOUT'),
                                                      pepxml=info[Keys.PEPXML])

        # required because openbis requires prot.xml and openms protXML
        peplink = os.path.join(wd, 'iprophet.pepXML')
        os.symlink(info[Keys.PEPXML], peplink)
        info[Keys.PEPXML] = peplink
        info['MZNAME'] = os.path.splitext(os.path.basename(info[Keys.MZXML]))[0]

        tpl = os.path.join(wd, 'part1_pp_ff.toppas')
        templates.read_mod_write(info, templates.get_tpl_of_class(self), tpl)
        #add toppas file path, will be added in dropbox
        info["TOPPASFILES"] = tpl

        rawfeatxml = os.path.join(wd, 'TOPPAS_out/012-IDConflictResolver/*.featureXML')
        info['FEATUREXML'] = os.path.join(wd, os.path.splitext(os.path.basename(info[Keys.MZXML]))[0] + '.featureXML')

        command = 'ExecutePipeline -in %s -out_dir %s  | grep -v "^WARNING" && chmod -R g+w %s && ' \
                  'mv -v %s %s' % (
                      tpl, wd, wd,
                      rawfeatxml, info['FEATUREXML'])
        return info, command

    def validate_run(self, log, info, run_code, out):
        for line in out.splitlines():
            if "OpenMS peak type estimation indicates that this is not profile data!" in line:
                raise RuntimeError("Found centroid data but LFQ must be run on profile mode data!")
        validation.check_stdout(log, out)
        validation.check_exitcode(log, run_code)
        validation.check_xml(log, info['FEATUREXML'])
        return info


if __name__ == "__main__":
    PeakpickerFeaturefinder.main()