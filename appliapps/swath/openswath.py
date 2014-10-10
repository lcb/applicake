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

    def add_args(self):
        """
        See super class.
        """
        return [
            Argument(Keys.WORKDIR, KeyHelp.WORKDIR),
            Argument('DSSOUT', "if getdataset was used kez MZXML is not set"),
            Argument('THREADS', 'Number of threads used in the process.'),

            Argument('TRAML', 'Path to the TraML file.'),
            Argument('TRAML_CSV', 'Path to the TraML file.'),
            Argument('IRTTRAML', 'Path to the iRT TraML file.'),

            Argument('MIN_RSQ', ''),
            Argument('MIN_COVERAGE', ''),

            Argument('MIN_UPPER_EDGE_DIST', 'minimum upper edge distance parameter'),
            Argument('EXTRACTION_WINDOW', 'extraction window to extract around'),
            Argument('EXTRA_RT_EXTRACTION_WINDOW', 'extra RT extraction window to extract around'),
            Argument('RT_EXTRACTION_WINDOW', 'RT extraction window to extract around'),
            Argument('WINDOW_UNIT', 'extraction window unit thompson/ppm'),

            Argument('DO_CHROMML_REQUANT', 'to skip set to false')
        ]

    def prepare_run(self, log, info):
        #in case getdataset instead of getmsdata was used key MZXML is not set but mzXML.gz is in DSSOUT list
        if not Keys.MZXML in info:
            if not isinstance(info['DSSOUT'], list):
                info['DSSOUT'] = [info['DSSOUT']]
            for key in info['DSSOUT']:
                if '.mzXML' in key:
                    info[Keys.MZXML] = key
                    log.info("MZXML is "+os.path.basename(key))

        if info.get('TRAML_CSV', "") == "":
            log.warn("No tsv library found, using traml library. Affects mem usage significantly!")
            library = info['TRAML']
        else:
            library = info['TRAML_CSV']

        ppm = ''
        if info['WINDOW_UNIT'] == 'ppm':
            ppm = '-ppm'

        samplename = os.path.basename(info['MZXML']).split(".")[0]
        info['FEATURETSV'] = os.path.join(info[Keys.WORKDIR], samplename + '.tsv')

        #copy mzxml, featureTSV and chormML first to local scratch, then back to global to decrease netI/O
        tmpdir = os.environ.get('TMPDIR', info[Keys.WORKDIR]) + '/'
        tmpmzxml = os.path.join(tmpdir, os.path.basename(info['MZXML']))
        tmptsv = os.path.join(tmpdir, samplename + '.tsv.tmp')

        extraextract = ''
        if info.get('EXTRA_RT_EXTRACTION_WINDOW', "") != "":
            extraextract = "-extra_rt_extraction_window " + info['EXTRA_RT_EXTRACTION_WINDOW']

        if info.get('DO_CHROMML_REQUANT', "") == "false":
            log.info("Skipping creation of chromMZML")
            chrommlflag = ""
            chrommlmv = "/bin/true"
        else:
            info['CHROM_MZML'] = os.path.join(info[Keys.WORKDIR], samplename + '.chrom.mzML.gz')
            tmpchrom = os.path.join(tmpdir, samplename + '.chrom.mzML.tmp')
            chrommlflag = "-out_chrom " + tmpchrom
            chrommlmv = " gzip -c %s > %s " % (tmpchrom, info['CHROM_MZML'])

        #command: copy mzXML to local scratch, run OpenSwathWorkflow, copy & zip result tsv (& ev. chrom.mzml)
        command = """cp -v %s %s &&
        OpenSwathWorkflow -in %s -tr %s -tr_irt %s -out_tsv %s %s
        -min_rsq %s -min_coverage %s
        -min_upper_edge_dist %s -mz_extraction_window %s %s -rt_extraction_window %s %s
        -tempDirectory %s -readOptions cache -batchSize 4000 -threads %s &&
        mv -v %s %s &&
        %s""" % (
            info["MZXML"], tmpmzxml,
            tmpmzxml, library, info['IRTTRAML'], tmptsv, chrommlflag,
            info['MIN_RSQ'], info['MIN_COVERAGE'],
            info['MIN_UPPER_EDGE_DIST'], info['EXTRACTION_WINDOW'], ppm, info['RT_EXTRACTION_WINDOW'], extraextract,
            tmpdir, info['THREADS'],
            tmptsv, info['FEATURETSV'],
            chrommlmv
        )

        return info, command


    def validate_run(self, log, info, exit_code, stdout):
        for line in stdout.splitlines():
            #Determined there to be 35792 SWATH windows and in total 6306 MS1 spectra
            if 'Determined there to be' in line:
                no_swathes = float(line.split()[4])
                if no_swathes > 64:
                    raise RuntimeError('This is a DDA sample, not SWATH!')
            if 'is below limit of ' in line:
                raise RuntimeError('iRT calibration failed for ' + os.path.basename(info['MZXML']) + "!\n" + line)

        #validation.check_stdout(log,stdout)
        validation.check_exitcode(log, exit_code)
        validation.check_file(log, info['FEATURETSV'])
        if 'CHROM_MZML' in info:
            #don't check_xml because of .gz
            validation.check_file(log, info['CHROM_MZML'])

        return info

if __name__ == "__main__":
    OpenSwathWorkflow.main()
