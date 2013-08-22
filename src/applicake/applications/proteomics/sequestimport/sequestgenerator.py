"""
Based on Lucias importFromSorcerer script

Created on Feb 20, 2012

@author: lorenz
"""

import os
import subprocess

from applicake.framework.keys import Keys
from applicake.applications.commons.generator import IniGenerator
from applicake.utils.dictutils import DictUtils
from applicake.framework.informationhandler import IniInformationHandler


class SequestGenerator(IniGenerator):
    def main(self, info, log):
        #TODO: simplify "wholeinfo" apps
        ini = IniInformationHandler().get_info(log, info)
        info = DictUtils.merge(log, info, ini)

        sorcAddr = 'sorcerer@imsb-ra-sorcerer' + info['SEQUESTHOST'] + '.ethz.ch'
        sorcPath = '/home/sorcerer/output/' + info['SEQUESTRESULTPATH'] + '/original/'

        info = self._addSequestParamsToInfo(info, log, sorcAddr + ":" + sorcPath)
        info = self._getAndCheckFastaDB(info, log, sorcAddr)
        pepxmls = self._getPepxmls(log, sorcAddr, sorcPath, info[Keys.WORKDIR])
        codes = self._getCodes(log, pepxmls)
        dicts = self._generateINIs(info, log, pepxmls, codes)
        self.write_files(info, log, dicts)

        return 0, info

    def set_args(self, log, args_handler):
        args_handler.add_app_args(log, 'SEQUESTHOST', 'Sequest host (1 or 2)')
        args_handler.add_app_args(log, 'SEQUESTRESULTPATH', 'Sequest result path (/home/sorcerer/output/????)')
        args_handler.add_app_args(log, Keys.GENERATOR, 'Basename for output inis')
        args_handler.add_app_args(log, Keys.WORKDIR, 'Workdir')

        #TODO: simplify "wholeinfo" apps
        args_handler.add_app_args(log, Keys.INPUT, 're-read input to access whole info')
        args_handler.add_app_args(log, Keys.BASEDIR, 'get basedir if set or modified by runner')
        args_handler.add_app_args(log, Keys.JOB_IDX, 'get jobidx if set or modified by runner')
        args_handler.add_app_args(log, Keys.STORAGE, 'get storage if set or modified by runner')
        args_handler.add_app_args(log, Keys.LOG_LEVEL, 'get loglevel if set or modified by runner')

        return args_handler

    def _addSequestParamsToInfo(self, info, log, sorcpath):
        paramfile = os.path.join(info[Keys.WORKDIR], 'sequest.params')
        try:
            subprocess.check_call(['rsync', '-vrtz', sorcpath + 'sequest.params', paramfile])
        except:
            raise Exception("Cannot get params from sorcerer. Did you check passwordless SSH? Does file exist?")

        #transform sorcerer params to info.ini & write out
        info["FRAGMASSUNIT"] = 'NA'
        info["FRAGMASSERR"] = 'NA'
        info["STATIC_MODS"] = 'NA'
        info["VARIABLE_MODS"] = 'NA'
        info['ENZYME'] = 'Trypsin'
        for line in open(paramfile).readlines():
            if 'peptide_mass_tolerance' in line:
                info["PRECMASSERR"] = line.split()[2]
            if 'max_num_internal_cleavage_sites' in line:
                info["MISSEDCLEAVAGE"] = line.split()[2]
            if 'peptide_mass_units' in line:
                sequestunits = {"0": "amu", "1": "mmu", "2": "ppm"}
                info["PRECMASSUNIT"] = sequestunits[line.split()[2]]
            if line.startswith('database_name'):
                info['SEQUESTDBASE'] = line.split()[2]
            if line.startswith('num_enzyme_termini = 2'):
                info['ENZYME'] = 'Semi-Tryptic'

        log.debug("Sucessfully added sequest parameters to info")
        return info

    def _getAndCheckFastaDB(self, info, log, sorcAddr):
        info['DBASE'] = os.path.join(info[Keys.WORKDIR], os.path.basename(info['SEQUESTDBASE']))
        print
        try:
            subprocess.check_call(['rsync', '-vrtz', sorcAddr + ':' + info['SEQUESTDBASE'], info['DBASE']])
        except:
            raise Exception("Couldnt copy fasta dbase from sorcerer")
        hasDecoys = False
        with open(info['DBASE']) as r:
            for line in r.readlines():
                if 'DECOY_' in line:
                    hasDecoys = True
        if not hasDecoys:
            log.critical("No DECOY_s in fasta found!")
            raise Exception("No DECOYs in fasta found")

        log.info("Got dbase %s" % info['DBASE'])
        return info


    def _getPepxmls(self, log, sorcAddr, sorcPath, wd):
        try:
            pepxmlstr = subprocess.check_output(['ssh', sorcAddr, 'find ' + sorcPath + '*.pep.xml'])
            pepxmlstr = pepxmlstr.replace(sorcPath + 'interact.pep.xml', '')
            pepxmlstr = pepxmlstr.replace(sorcPath + 'inputlists.pep.xml', '')
        except:
            raise Exception('Could not get list of pepxml.')

        pepxmls = []
        for pepxml in pepxmlstr.strip().split('\n'):
            outfile = os.path.join(wd, os.path.basename(pepxml))
            rsync = "rsync -vrtz " + sorcAddr + ':' + pepxml + " " + outfile
            log.debug("Copying pepxml from sorcerer " + pepxml)
            subprocess.check_call(rsync.split())
            pepxmls.append(outfile)

        log.info("Got pepxmls %s" % pepxmls)
        return pepxmls

    def _getCodes(self, log, pepxmls):
        codes = []
        for pepxml in pepxmls:
            mzbase = os.path.basename(pepxml).replace('.pep.xml', '')
            if str(mzbase).endswith('_c'):
                mzbase = mzbase[:-2]
            log.debug("Getting code for %s" % mzbase)
            #asterisk because could be .gz
            scdc = subprocess.check_output(['searchmzxml', mzbase + '.mzXML*']).strip()
            codes.append(scdc)

        log.info("Got codes [%s]" % codes)
        return codes

    def _generateINIs(self, info, log, pepxmls, codes):
        dicts = []
        info[Keys.PARAM_IDX] = '0'
        info[Keys.GENERATOR_CHECKSUM] = len(codes)

        for idx, code, pepxml in zip(range(len(codes)), codes, pepxmls):
            dict = info.copy()
            dict[Keys.FILE_IDX] = idx
            dict['MZXML'] = code + '.mzMXL'
            dict['DATASET_CODE'] = code.split('~')[1]
            dict['PEPXMLS'] = [pepxml]
            dicts.append(dict)

        log.info("Writing %d inis" % len(dicts))
        return dicts
