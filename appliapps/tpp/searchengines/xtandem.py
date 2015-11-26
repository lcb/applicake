#!/usr/bin/env python
import os

from applicake.apputils import validation
from appliapps.tpp.searchengines.enzymes import enzymestr_to_engine
from appliapps.tpp.searchengines.modifications import genmodstr_to_engine
from applicake.apputils import templates
from applicake.coreutils.arguments import Argument
from applicake.coreutils.keys import Keys,KeyHelp
from appliapps.tpp.searchengines.searchenginebase import SearchEnginesBase

class Xtandem(SearchEnginesBase):
    """
    Wrapper for the search engine X!Tandem.
    """

    def add_args(self):
        args = super(Xtandem, self).add_args()
        args.append(Argument('XTANDEM_SCORE', 'Scoring algorithm used in the search.'))
        return args

    def prepare_run(self, log, info):
        wd = info[Keys.WORKDIR]
        exe = info.get(Keys.EXECUTABLE, 'tandem')

        # need to create a working copy to prevent replacement with app specific definitions
        app_info = info.copy()

        app_info = self._define_score(app_info, log)
        app_info["STATIC_MODS"], app_info["VARIABLE_MODS"], app_info['TERMINAL_MODS'] = genmodstr_to_engine(info["STATIC_MODS"],
                                                                                 info["VARIABLE_MODS"], 'XTandem')
        app_info['ENZYME'], app_info['XTANDEM_SEMI_CLEAVAGE'] = enzymestr_to_engine(info['ENZYME'], 'XTandem')

        #files required and written
        app_info['XTANDEM_PARAMS'] = os.path.join(wd, 'xtandem.params')
        templates.read_mod_write(app_info, templates.get_tpl_of_class(self), app_info['XTANDEM_PARAMS'])
        app_info['XTANDEM_INPUT'] = os.path.join(wd, 'xtandem.input')
        app_info['XTANDEM_TAXONOMY'] = os.path.join(wd, 'xtandem.taxonomy')
        app_info['XTANDEM_RESULT'] = os.path.join(wd, 'xtandem.result')
        self._write_input_files(app_info)

        #integrated tandem2xml XTANDEM_RESULT conversion
        info[Keys.PEPXML] = os.path.join(wd, 'xtandem.pep.xml')

        command = '%s %s && Tandem2XML %s %s ' % (
        exe, app_info['XTANDEM_INPUT'], app_info['XTANDEM_RESULT'], info[Keys.PEPXML])
        return info, command

    @staticmethod
    def _define_score(info, log):
        if not info.has_key('XTANDEM_SCORE'):
            log.info('No score given, using default score')
            info['XTANDEM_SCORE'] = ''
        # for default score, no entry is allowed in template
        elif info['XTANDEM_SCORE'] == 'default':
            log.info('Using default score')
            info['XTANDEM_SCORE'] = ''
        # for k-score add special tags
        elif info['XTANDEM_SCORE'] == 'k-score':
            log.info('Using k-score')
            info['XTANDEM_SCORE'] = '<note label="scoring, algorithm" type="input">%s</note>' \
                                    '<note label="spectrum, use conditioning" type="input" >no</note>' \
                                    '<note label="scoring, minimum ion count" type="input">1</note>' % info[
                                        'XTANDEM_SCORE']
        else:
            log.warn('Using special score %s' % info['XTANDEM_SCORE'])
            info['XTANDEM_SCORE'] = '<note label="scoring, algorithm" type="input">%s</note>' % info['XTANDEM_SCORE']
        return info

    @staticmethod
    def _write_input_files(info):
        open(info['XTANDEM_TAXONOMY'], "w").write(
            '<?xml version="1.0"?>\n<bioml>\n'
            '<taxon label="database"><file format="peptide" URL="%s"/></taxon>'
            '\n</bioml>' % info['DBASE']
        )

        open(info['XTANDEM_INPUT'], "w").write(
            '<?xml version="1.0"?>\n'
            '<bioml>\n<note type="input" label="list path, default parameters">%s</note>\n'
            '<note type="input" label="output, xsl path" />\n'
            '<note type="input" label="output, path">%s</note>\n'
            '<note type="input" label="list path, taxonomy information">%s</note>\n'
            '<note type="input" label="spectrum, path">%s</note>\n'
            '<note type="input" label="protein, taxon">database</note>\n</bioml>\n' % \
            (info['XTANDEM_PARAMS'], info['XTANDEM_RESULT'], info['XTANDEM_TAXONOMY'], info[Keys.MZXML])
        )


    def validate_run(self, log, info, exit_code, out):
        validation.check_exitcode(log, exit_code)

        if 'Valid models = 0' in out:
            raise RuntimeError('No valid model found')

        validation.check_xml(log, info[Keys.PEPXML])
        return info


if __name__ == "__main__":
    Xtandem.main()