"""
Created on Jun 18, 2012

@author: loblum
"""

import os
from applicake.framework.keys import Keys
from applicake.framework.interfaces import IWrapper
from applicake.framework.templatehandler import BasicTemplateHandler
from applicake.utils.fileutils import FileUtils
from applicake.utils.xmlutils import XmlValidator



class ProteinProphetFDR(IWrapper):
    """
    Wrapper for TPP-tool ProteinProphet.
    """

    def getiProbability(self, log, info):
        minprob = ''

        for line in open(info['PEPXMLS']):
            if line.startswith('<error_point error="%s' % info['PEPTIDEFDR']):
                minprob = line.split(" ")[2].split("=")[1].replace('"', '')
                break

        if minprob != '':
            log.info("Found minprob/iprobability %s for PEPTIDEFDR %s" % (minprob, info['PEPTIDEFDR']))
        else:
            raise Exception("error point for PEPTIDEFDR %s not found" % info['PEPTIDEFDR'])
        return minprob


    def prepare_run(self, info, log):
        if len(info['PEPXMLS']) > 1:
            log.fatal("This ProteinProphet only takes one iProphet inputfile!")
            return 1, info

        ifocp = info.copy()
        ifocp['PEPXMLS'] = ifocp['PEPXMLS'][0]
        info[Keys.IPROBABILITY] = self.getiProbability(log, ifocp)
        info['PROTEINPROPHET'] = 'IPROPHET MINPROB%s' % info[Keys.IPROBABILITY]
        wd = info[Keys.WORKDIR]
        info['PROTXML'] = os.path.join(wd, 'ProteinProphet.prot.xml')
        prefix = info.get('PREFIX', 'ProteinProphet')
        command = '%s %s %s %s' % (prefix, info['PEPXMLS'][0], info['PROTXML'], info['PROTEINPROPHET'])
        return command, info

    def set_args(self, log, args_handler):
        """
        See super class.

        Set several arguments shared by the different search engines
        """
        args_handler.add_app_args(log, Keys.WORKDIR, 'Directory to store files')
        args_handler.add_app_args(log, Keys.PREFIX, 'Path to the executable')
        args_handler.add_app_args(log, Keys.PEPXMLS, 'Single iProphet inputfile', action='append')
        args_handler.add_app_args(log, Keys.PEPTIDEFDR, 'Peptide FDR cutoff')

        return args_handler

    def validate_run(self, info, log, run_code, out_stream, err_stream):
        """
        See super class.
        """
        #err_stream.seek(0)
        out_stream.seek(0)
        stdout = out_stream.read()
        msg = 'No xml file specified; please use the -file option'
        if msg in stdout:
            log.debug('ProteinProphet ignore [%s] of protxml2html' % msg)
        for msg in ['did not find any InterProphet results in input data!',
                    'no data - quitting',
                    'WARNING: No database referenced']:
            if msg in stdout:
                log.error('ProteinProphet error [%s]' % msg)
                return 1, info
            else:
                log.debug('ProteinProphet: passed check [%s]' % msg)

        if not FileUtils.is_valid_file(log, info['PROTXML']):
            log.critical('[%s] is not valid' % info['PROTXML'])
            return 1, info
        if not XmlValidator.is_wellformed(info['PROTXML']):
            log.critical('[%s] is not well formed.' % info['PROTXML'])
            return 1, info
        return 0, info
