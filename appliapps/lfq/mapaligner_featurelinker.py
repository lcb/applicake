#!/usr/bin/env python
import os

from applicake.app import WrappedApp
from applicake.apputils import validation
from applicake.coreutils.arguments import Argument
from applicake.coreutils.keys import Keys, KeyHelp
from applicake.apputils import templates


class MapalignerFeaturelinker(WrappedApp):
    def add_args(self):
        return [
            Argument(Keys.WORKDIR, KeyHelp.WORKDIR),
            Argument("TOPPASFILES", 'toppas files pathes used in lfqpart1'),
            Argument('FEATUREXML', 'Path to the featureXML file(s).'),
            Argument('PROTXML', 'Path to the protXML file (one).'),

            Argument("PROTEINQUANTIFIER_AVERAGE", ""),
            Argument("PROTEINQUANTIFIER_TOP", ""),
            Argument("PROTEINQUANTIFIER_INCLUDE_ALL", ""),
            Argument("FEATURELINKER_DISTANCE_RT__MAX_DIFFERENCE", ""),
            Argument("FEATURELINKER_DISTANCE_MZ__MAX_DIFFERENCE", ""),
            Argument("FEATURELINKER_DISTANCE_MZ__UNIT", ""),
            Argument("POSECLUSTERING_MZ_PAIR_MAX_DISTANCE", ""),
            Argument("POSECLUSTERING_DISTANCE_RT_MAX_DIFF", ""),
            Argument("POSECLUSTERING_DISTANCE_MZ_MAX_DIFF", "")
        ]

    def prepare_run(self, log, info):
        wd = info[Keys.WORKDIR]

        #required because openbis requires prot.xml and openms protXML
        protlink = os.path.join(wd, 'protein.protXML')
        os.symlink(info['PROTXML'], protlink)
        info['PROTXML'] = protlink

        #copy info to not destroy original
        app_info = info.copy()
        app_info['FEATUREXMLLIST'] = ''

        if not isinstance(app_info['FEATUREXML'],list):
            raise RuntimeError("Cannot perform LFQ with only one featurexml/sample!")

        for i in app_info['FEATUREXML']:
            app_info['FEATUREXMLLIST'] += '<LISTITEM value="' + i + '"/>'

        tpl = os.path.join(wd, 'part2_ma_fl.toppas')
        templates.read_mod_write(app_info, templates.get_tpl_of_class(self), tpl)
        #add toppas file path, will be added in dropbox
        info["TOPPASFILES"].append(tpl)

        rawprot = os.path.join(wd, 'TOPPAS_out/009-ProteinQuantifier/*.csv')
        rawpep = os.path.join(wd, 'TOPPAS_out/010-ProteinQuantifier/*.csv')
        rawconsensusxml = os.path.join(wd, 'TOPPAS_out/011-FeatureLinker*/*.consensusXML')
        info['PROTCSV'] = os.path.join(wd, 'proteins.csv')
        info['PEPCSV'] = os.path.join(wd, 'peptides.csv')
        info['CONSENSUSXML'] = os.path.join(wd, 'FeatureLinker.consensusXML')

        command = 'ExecutePipeline -in %s -out_dir %s && chmod -R g+w %s && ' \
                  'mv -v %s %s && ' \
                  'mv -v %s %s && ' \
                  'mv -v %s %s' % (
                      tpl, wd, wd,
                      rawprot, info['PROTCSV'],
                      rawpep, info['PEPCSV'],
                      rawconsensusxml, info['CONSENSUSXML'])
        return info, command

    def validate_run(self, log, info, run_code, out):
        validation.check_exitcode(log, run_code)
        validation.check_file(log, info['PROTCSV'])
        validation.check_file(log, info['PEPCSV'])
        validation.check_xml(log, info['CONSENSUSXML'])
        return info


if __name__ == "__main__":
    MapalignerFeaturelinker.main()