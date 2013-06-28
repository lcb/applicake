"""
Created on Jun 18, 2012

@author: quandtan
"""

import os
from applicake.framework.keys import Keys
from applicake.framework.interfaces import IWrapper
from applicake.framework.templatehandler import BasicTemplateHandler
from applicake.utils.fileutils import FileUtils
from applicake.utils.xmlutils import XmlValidator


class ProtXml2OpenbisSequence(IWrapper):
    """
    Wrapper for SyBIT-tool protxml2openbis.
    """

    def get_template_handler(self):
        """
        See interface
        """
        return ProtXml2OpenbisSequenceTemplate()

    def prepare_run(self, info, log):
        """
        See interface.

        - Define path to result file (depending on work directory)
        - If a template is used, the template is read variables from the info object are used to set concretes.
        - If there is a result file, it is added with a specific key to the info object.
        """
        wd = info[Keys.WORKDIR]


        # have to temporarily set a key in info to store the original protXML
        info['ORGPROTXML'] = info['PROTXML']
        info['ORGPEPXMLS'] = info['PEPXMLS']
        info['PEPXMLS'] = " ".join(info['PEPXMLS'])
        info['PEPCSV'] = os.path.join(wd, 'peptides.csv')
        info['COUNTPROTXML'] = os.path.join(wd, 'spectralcount.prot.xml')
        info['MODPROTXML'] = os.path.join(wd, 'modifications.prot.xml')
        info['PROTXML'] = os.path.join(wd, 'Protxml2Openbis.prot.xml')
        self._result_file = info['PROTXML']

        info['TEMPLATE'] = os.path.join(wd, "template.tpl")
        log.debug('get template handler')
        th = self.get_template_handler()
        log.debug('modify template')
        mod_template, info = th.modify_template(info, log)
        params = mod_template.splitlines()

        cmds = []
        cmds.append("pepxml2csv %s" % params[0])
        cmds.append("protxml2spectralcount %s" % params[1])
        cmds.append("protxml2modifications %s" % params[2])
        cmds.append("protxml2openbis %s" % params[3])
        command = " && ".join(cmds)

        # can delete temporary key as it is not longer needed
        info['PEPXMLS'] = info['ORGPEPXMLS']
        del info['ORGPROTXML']
        del info['ORGPEPXMLS']
        del info['COUNTPROTXML']
        del info['MODPROTXML']

        return command, info

    def set_args(self, log, args_handler):
        """
        See super class.

        Set several arguments shared by the different search engines
        """
        args_handler.add_app_args(log, Keys.WORKDIR, 'Directory to store files')
        args_handler.add_app_args(log, Keys.PREFIX, 'Path to the executable')
        args_handler.add_app_args(log, Keys.TEMPLATE, 'Path to the template file')
        args_handler.add_app_args(log, 'PEPXMLS', 'Path to a file in protXML format')
        args_handler.add_app_args(log, 'PROTXML', 'Path to a file in protXML format')
        args_handler.add_app_args(log, 'DBASE', 'Sequence database file with target/decoy entries')
        return args_handler

    def validate_run(self, info, log, run_code, out_stream, err_stream):
        """
        See super class.
        """
        if 0 != run_code:
            return run_code, info
        if not FileUtils.is_valid_file(log, self._result_file):
            log.critical('[%s] is not valid' % self._result_file)
            return 1, info
        if not XmlValidator.is_wellformed(self._result_file):
            log.critical('[%s] is not well formed.' % self._result_file)
            return 1, info
        return 0, info


class ProtXml2OpenbisSequenceTemplate(BasicTemplateHandler):
    """
    Template handler for ProtXml2Openbis.
    """

    def read_template(self, info, log):
        """
        See super class.
        """
        template = """-IPROPHET -header -cP=0.0 -OUT=$PEPCSV $PEPXMLS
-CSV=$PEPCSV -OUT=$COUNTPROTXML $ORGPROTXML
-CSV=$PEPCSV -OUT=$MODPROTXML $COUNTPROTXML
-DB=$DBASE -OUT=$PROTXML $MODPROTXML"""

        log.debug('read template from [%s]' % self.__class__.__name__)
        return template, info
