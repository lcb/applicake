"""
Created on Jul 11, 2013

CPU: 1 or 2 too long runtime, >10 CPU queue too long => 8CPU
MEM: can be controlled with -batchSize. 4000-5000 batchSize ~ 1G RAM per thread

@author: loblum
"""

import os
from applicake.framework.keys import Keys
from applicake.framework.interfaces import IWrapper
from applicake.utils.fileutils import FileUtils


class OpenSwathWorkflow(IWrapper):
    def prepare_run(self, info, log):
        #in case getdataset instead of getmsdata was used key MZXML is not set but mzXML.gz is in DSSOUTPUT list
        if not Keys.MZXML in info:
            if not isinstance(info[Keys.DSSOUTPUT], list):
                info[Keys.DSSOUTPUT] = [info[Keys.DSSOUTPUT]]
            for key in info[Keys.DSSOUTPUT]:
                if '.mzXML' in key:
                    info[Keys.MZXML] = key

        library = info['TRAML_CSV']
        if info['TRAML_CSV'] == "":
            log.warn("No tsv library found, using traml library. Affects mem usage significantly!")
            library = info['TRAML']

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
        if 'EXTRA_RT_EXTRACTION_WINDOW' in info and info['EXTRA_RT_EXTRACTION_WINDOW'] != "":
            extraextract = "-extra_rt_extraction_window " + info['EXTRA_RT_EXTRACTION_WINDOW']

        if info.get('DO_CHROMML_REQUANT', "") == "false":
            log.info("Skipping creation of chromMZML")
            chrommlflag = ""
            chrommlmv = "/bin/true"
        else:
            info['CHROMML_GZ'] = os.path.join(info[Keys.WORKDIR], samplename + '.chrom.mzML.gz')
            tmpchromml = os.path.join(tmpdir, samplename + '.chrom.mzML.tmp')
            chrommlflag = "-out_chrom " + tmpchromml
            chrommlmv = " gzip -c %s > %s " % (tmpchromml, info['CHROMML_GZ'])

        command = """cp -v %s %s &&
        OpenSwathWorkflow -in %s -tr %s -tr_irt %s -out_tsv %s %s
        -min_rsq %s -min_coverage %s
        -min_upper_edge_dist %s -mz_extraction_window %s %s -rt_extraction_window %s %s
        -tempDirectory %s -readOptions %s  -threads %s -batchSize %s
        && mv -v %s %s &&
        %s""" % (info["MZXML"], tmpmzxml,
                 tmpmzxml, library, info['IRTTRAML'], tmptsv, chrommlflag,
                 info['MIN_RSQ'], info['MIN_COVERAGE'],
                 info['MIN_UPPER_EDGE_DIST'], info['EXTRACTION_WINDOW'], ppm, info['RT_EXTRACTION_WINDOW'],
                 extraextract,
                 tmpdir, info["READ_OPTS"], info['THREADS'], info['BATCH_SIZE'],
                 tmptsv, info['FEATURETSV'],
                 chrommlmv
        )

        return command, info

    def set_args(self, log, args_handler):
        """
        See super class.
        """
        args_handler.add_app_args(log, Keys.WORKDIR, 'Directory to store files')
        args_handler.add_app_args(log, Keys.PREFIX, 'Path to the executable')
        args_handler.add_app_args(log, Keys.TEMPLATE, 'Path to the template file')
        args_handler.add_app_args(log, Keys.DSSOUTPUT, "")
        args_handler.add_app_args(log, 'THREADS', 'Number of threads used in the process.')

        args_handler.add_app_args(log, 'TRAML', 'Path to the TraML file.')
        args_handler.add_app_args(log, 'TRAML_CSV', 'Path to the TraML file.')
        args_handler.add_app_args(log, 'IRTTRAML', 'Path to the iRT TraML file.')

        args_handler.add_app_args(log, 'MIN_RSQ', '')
        args_handler.add_app_args(log, 'MIN_COVERAGE', '')

        args_handler.add_app_args(log, 'MIN_UPPER_EDGE_DIST', 'minimum upper edge distance parameter')
        args_handler.add_app_args(log, 'EXTRACTION_WINDOW', 'extraction window to extract around')
        args_handler.add_app_args(log, 'EXTRA_RT_EXTRACTION_WINDOW', 'extra RT extraction window to extract around')
        args_handler.add_app_args(log, 'RT_EXTRACTION_WINDOW', 'RT extraction window to extract around')
        args_handler.add_app_args(log, 'WINDOW_UNIT', 'extraction window unit thompson/ppm')

        args_handler.add_app_args(log, 'READ_OPTS', 'reading options', default='cache')
        args_handler.add_app_args(log, 'BATCH_SIZE', 'mem batch size', default=4000)
        args_handler.add_app_args(log, 'DO_CHROMML_REQUANT', '')

        return args_handler

    def validate_run(self, info, log, run_code, out_stream, err_stream):
        out_stream.seek(0)
        for line in out_stream.readlines():
            if 'is below limit of ' in line:
                log.critical('iRT calibration failed'+os.path.basename(info['MZXML'])+"!\n"+line)
                return 1, info

        if 0 != run_code:
            return run_code, info

        if not FileUtils.is_valid_file(log, info['FEATURETSV']):
            log.critical('[%s] is not valid' % info['FEATURETSV'])
            return 1, info

        if 'CHROM_MZML' in info and not FileUtils.is_valid_file(log, info['CHROM_MZML']):
            log.critical('[%s] is not valid' % info['CHROM_MZML'])
            return 1, info
        return 0, info