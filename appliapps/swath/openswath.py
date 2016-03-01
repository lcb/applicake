#!/usr/bin/env python
import os

from applicake.app import WrappedApp
from applicake.apputils import validation
from applicake.coreutils.arguments import Argument
from applicake.coreutils.keys import Keys, KeyHelp


class OpenSwathWorkflow(WrappedApp):
    """
    Created on Jul 11, 2013
    CPU: 1 or 2 too long runtime, >10 CPU queue too long => 8CPU. 4CPU to give less load to filesystem2
    MEM: can be controlled with -batchSize. 4000-5000 batchSize ~ 1G RAM per thread
    """

    # Note: Only put static opts here
    opts = {
        'IRTTRAML': "tr_irt",
        'THREADS': 'threads',
        'MIN_RSQ': 'min_rsq',
        'MIN_COVERAGE': 'min_coverage',
        'MIN_UPPER_EDGE_DIST': 'min_upper_edge_dist',
        'EXTRACTION_WINDOW': 'mz_extraction_window',
        'RT_EXTRACTION_WINDOW': 'rt_extraction_window',
        'EXTRA_RT_EXTRACTION_WINDOW': 'extra_rt_extraction_window',
        'USE_DIA_SCORES': 'Scoring:Scores:use_dia_scores',
        'USE_BG_SUBTRACT': 'Scoring:TransitionGroupPicker:background_subtraction',
        'UIS_SN_THRESHOLD': 'Scoring:uis_threshold_sn',
        'UIS_PEAKAREA_THRESHOLD': 'Scoring:uis_threshold_peak_area',
        'STOP_AFTER_FEATURE': 'Scoring:stop_report_after_feature',
    }

    def add_args(self):
        ret = [
            Argument(Keys.WORKDIR, KeyHelp.WORKDIR),
            Argument('DSSOUT', "if key MZXML not set, get from DSSOUT file (after getdataset)"),
            Argument('TRAML_CSV', "Path to the traml2csv library"),

            Argument('WINDOW_UNIT', 'extraction window unit thompson/ppm'),
            Argument('USE_MS1_TRACES', ""),
            Argument('USE_UIS_SCORES', ''),
            Argument('DO_CHROMML_REQUANT', 'to skip set to false'),
        ]
        for k, v in self.opts.iteritems():
            ret.append(Argument(k, v))

        return ret

    def _getmzxml_from_dssout(self, info, log):
        # in case getdataset instead of getmsdata was used key MZXML is not set but mzXML.gz is in DSSOUT list
        if not Keys.MZXML in info:
            if not isinstance(info['DSSOUT'], list):
                info['DSSOUT'] = [info['DSSOUT']]
            for key in info['DSSOUT']:
                if '.mzXML' in key:
                    info[Keys.MZXML] = key
                    log.info("MZXML is " + os.path.basename(key))
        return info

    def prepare_run(self, log, info):
        info = self._getmzxml_from_dssout(info, log)

        flags = ''
        for k, v in self.opts.iteritems():
            if info.get(k, "") != "":
                flags += " -%s %s" % (v, info[k])

        #These two cannot be 'flags' because they are options without argument
        if info['WINDOW_UNIT'] == 'ppm':
            flags += ' -ppm'

        if info.get("USE_MS1_TRACES", "") == "true":
            flags += " -use_ms1_traces"

        if info.get("USE_UIS_SCORES", "") == "true":
            flags += " -enable_uis_scoring"

        # We need to decrease netI/O here, so we move everything to local scratch and calc here, then move back
        tmpdir = os.environ.get('TMPDIR', info[Keys.WORKDIR]) + '/'
        tmpmzxml = os.path.join(tmpdir, os.path.basename(info['MZXML']))
        samplename = os.path.basename(info['MZXML']).split(".")[0]
        tmptsv = os.path.join(tmpdir, samplename + '.tsv.tmp')
        info['FEATURETSV'] = os.path.join(info[Keys.WORKDIR], samplename + '.tsv')

        if info.get('DO_CHROMML_REQUANT', "") == "false":
            log.info("Skipping creation of chromMZML")
            chrommlmv = "/bin/true"
        else:
            tmpchrom = os.path.join(tmpdir, samplename + '.chrom.mzML.tmp')
            flags += " -out_chrom " + tmpchrom
            info['CHROM_MZML'] = os.path.join(info[Keys.WORKDIR], samplename + '.chrom.mzML.gz')
            chrommlmv = " gzip -c %s > %s " % (tmpchrom, info['CHROM_MZML'])

        #command: 1) copy mzXML to local, 2) OpenSwathWorkflow, 3) copy result tsv (& ev. chrom.mzml) to global
        command = """cp -v %s %s &&
        OpenSwathWorkflow -in %s -tr %s -out_tsv %s -tempDirectory %s -readOptions cacheWorkingInMemory -batchSize 1000 %s &&
        cp -v %s %s &&
        %s""" % (
            info["MZXML"], tmpmzxml,
            tmpmzxml, info['TRAML_CSV'], tmptsv, tmpdir, flags,
            tmptsv, info['FEATURETSV'],
            chrommlmv
        )

        return info, command


    def validate_run(self, log, info, exit_code, stdout):
        for line in stdout.splitlines():
            # Determined there to be 35792 SWATH windows and in total 6306 MS1 spectra
            if 'Determined there to be' in line:
                no_swathes = float(line.split()[4])
                if no_swathes > 128:
                    raise RuntimeError('This is a DDA sample, not SWATH!')
            if 'is below limit of ' in line:
                raise RuntimeError("iRT calibration failed: " + line)

        # validation.check_stdout(log,stdout)
        validation.check_exitcode(log, exit_code)
        validation.check_file(log, info['FEATURETSV'])
        if os.path.getsize(info['FEATURETSV']) < 1000:
            raise RuntimeError("No peak found, output is empty!")
        if 'CHROM_MZML' in info:
            #don't use check_xml() because of .gz
            validation.check_file(log, info['CHROM_MZML'])

        return info


if __name__ == "__main__":
    OpenSwathWorkflow.main()
