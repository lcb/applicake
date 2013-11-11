"""
Created on Jul 11, 2013

CPU: 1 or 2 too long runtime, >10 CPU queue too long => 8CPU
MEM: can be controlled with -batchSize. 4000-5000 batchSize ~ 1G RAM per thread

@author: loblum
"""

import os
from applicake.framework.keys import Keys
from applicake.framework.interfaces import IWrapper
from applicake.framework.templatehandler import BasicTemplateHandler
from applicake.utils.fileutils import FileUtils
from applicake.utils.xmlutils import XmlValidator


class OpenSwathWorkflow(IWrapper):

    def prepare_run(self, info, log):
        #in case getdataset instead of getmsdata was used key MZXML is not set but mzXML.gz is in DSSOUTPUT list
        if not Keys.MZXML in info:
            if not isinstance(info[Keys.DSSOUTPUT],list):
                info[Keys.DSSOUTPUT] = [info[Keys.DSSOUTPUT]]
            for key in info[Keys.DSSOUTPUT]:
                if '.mzXML' in key:
                    info[Keys.MZXML] = key

        tmpdir = os.environ.get('TMPDIR',info[Keys.WORKDIR]) + '/'
        samplename = os.path.basename(info['MZXML']).split(".")[0]
        info['FEATURETSV'] = os.path.join(info[Keys.WORKDIR],samplename + '.tsv')

        #check for skip
        chromml = ""
        if 'SKIP_CHROMML_REQUANT' in info and info['SKIP_CHROMML_REQUANT'] == "true":
            log.info("Skipping creation of chromMZML")
        else:
            info['CHROM_MZML'] = os.path.join(info[Keys.WORKDIR],samplename + '.chrom.mzML')
            chromml = "-out_chrom " + info['CHROM_MZML']

        ppm = ''
        if info['WINDOW_UNIT'] == 'ppm':
            ppm = '-ppm'

        library = info['TRAML_CSV']
        if info['TRAML_CSV'] == "":
            log.warn("No traml tsv found, using larger traml. affects mem usage significantly!")
            library = info['TRAML']

        command = """OpenSwathWorkflow -in %s -tr %s -tr_irt %s -out_tsv %s %s
        -min_rsq %s -min_coverage %s
        -min_upper_edge_dist %s -mz_extraction_window %s %s -rt_extraction_window %s
        -tempDirectory %s -readOptions %s  -threads %s -batchSize %s""" % \
        (info["MZXML"],library,info['IRTTRAML'], info['FEATURETSV'], chromml,
         info['MIN_RSQ'],info['MIN_COVERAGE'],
         info['MIN_UPPER_EDGE_DIST'], info['EXTRACTION_WINDOW'], ppm, info['RT_EXTRACTION_WINDOW'],
         tmpdir,info["READ_OPTS"],info['THREADS'],info['BATCH_SIZE'])

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
        args_handler.add_app_args(log, 'RT_EXTRACTION_WINDOW', 'RT extraction window to extract around')
        args_handler.add_app_args(log, 'WINDOW_UNIT', 'extraction window unit thompson/ppm')

        args_handler.add_app_args(log, 'READ_OPTS', 'reading options', default='cache')
        args_handler.add_app_args(log, 'BATCH_SIZE', 'mem batch size', default=4000)
        args_handler.add_app_args(log, 'SKIP_CHROMML_REQUANT', '')

        return args_handler

    def validate_run(self, info, log, run_code, out_stream, err_stream):
        if 0 != run_code:
            return run_code, info

        if not FileUtils.is_valid_file(log, info['FEATURETSV'] ):
            log.critical('[%s] is not valid' % info['FEATURETSV'] )
            return 1,info

        if 'CHROM_MZML' in info and not FileUtils.is_valid_file(log,info['CHROM_MZML']):
            log.critical('[%s] is not valid' % info['CHROM_MZML'] )
            return 1,info
        return 0, info