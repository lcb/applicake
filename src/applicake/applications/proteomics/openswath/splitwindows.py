"""
Created on Oct 24, 2012

@author: lorenz
"""
import os

from applicake.framework.keys import Keys

from applicake.framework.interfaces import IWrapper
from applicake.utils.fileutils import FileUtils


class SplitWindowsConvertZip(IWrapper):

    def prepare_run(self, info, log):
        #in case getdataset instead of getmsdata was used key MZXML is not set but mzXML.gz is in DSSOUTPUT list
        if not Keys.MZXML in info:
            log.info("No key MZXML found, getting from DSSOUTPUT list")
            for key in info[Keys.DSSOUTPUT]:
                if '.mzXML' in key:
                    info[Keys.MZXML] = key
            
        command = '%s -i %s -o %s -t %s -w %s -n' % (info['PREFIX'], info[Keys.MZXML], info[Keys.WORKDIR], info[Keys.THREADS],info['NUMBER_OF_SWATHES'])
        return command, info

    def set_args(self, log, args_handler):
        args_handler.add_app_args(log, Keys.PREFIX, 'Path to the executable', default='mzXML_to_swathmzMLgz.sh')
        args_handler.add_app_args(log, Keys.MZXML, 'mzxml to split')
        args_handler.add_app_args(log, Keys.DSSOUTPUT, 'list with mzXML(.gz) to split in it (i.e. after getdataset instead of getmsdata)')
        args_handler.add_app_args(log, Keys.WORKDIR, 'working directory')
        args_handler.add_app_args(log, Keys.THREADS, 'number of threads')
        args_handler.add_app_args(log, 'NUMBER_OF_SWATHES', 'number of swathes',default=32)
        
        return args_handler

    def validate_run(self, info, log, run_code, out_stream, err_stream):
        """
        See super class.
        """
        if 0 != run_code:
            return run_code, info
        outfiles = []
        for outfile in os.listdir(info[Keys.WORKDIR]):
            outfile = os.path.join(info[Keys.WORKDIR], outfile)
            if str(outfile).endswith('.mzML.gz'):
                if not FileUtils.is_valid_file(log, outfile):
                    log.critical('[%s] is not valid' % outfile)
                    return 1, info
                outfiles.append(outfile)
        info[Keys.MZML] = outfiles

        if len(outfiles) != info["NUMBER_OF_SWATHES"]:
            log.critical("Number of mzML.gz %d does not correspond NUM_SWATHES %d" % (len(outfiles),info["NUMBER_OF_SWATHES"]) )
            return 1, info

        return 0, info

