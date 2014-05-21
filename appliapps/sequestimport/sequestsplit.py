#!/usr/bin/env python
import os
import subprocess

from applicake.app import BasicApp
from applicake.coreutils.arguments import Argument
from applicake.coreutils.info import IniInfoHandler
from applicake.coreutils.keys import Keys, KeyHelp


class SequestSplit(BasicApp):
    """
    Based on Lucias importFromSorcerer script
    """

    def add_args(self):
        return [
            Argument('SEQUESTHOST', 'Sequest host (1 or 2)'),
            Argument('SEQUESTRESULTPATH', 'Sequest result path (/home/sorcerer/output/????)'),
            Argument(Keys.SPLIT, KeyHelp.SPLIT),
            Argument(Keys.WORKDIR, KeyHelp.WORKDIR),
            Argument(Keys.ALL_ARGS,KeyHelp.ALL_ARGS)
        ]

    def run(self, log, info):

        sorcAddr = 'sorcerer@imsb-ra-sorcerer' + info['SEQUESTHOST'] + '.ethz.ch'
        sorcPath = '/home/sorcerer/output/' + info['SEQUESTRESULTPATH'] + '/original/'

        info = self._addSequestParamsToInfo(info, log, sorcAddr + ":" + sorcPath)
        info = self._getAndCheckFastaDB(info, log, sorcAddr)
        pepxmls = self._getPepxmls(log, sorcAddr, sorcPath, info[Keys.WORKDIR])
        codes = self._getCodes(log, pepxmls)
        self._generateINIs(info, log, pepxmls, codes)

        return info


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
                if '>DECOY_' in line:
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
        total = len(codes)
        for i, code, pepxml in zip(range(total), codes, pepxmls):
            dict = info.copy()
            dict['MZXML'] = code + '.mzMXL'
            dict['DATASET_CODE'] = code.split('~')[1]
            dict[Keys.PEPXML] = pepxml
            dict[Keys.SUBJOBLIST] = "%s%s%d%s%d" % ('DATASET_CODE', Keys.SUBJOBSEP, i, Keys.SUBJOBSEP, total)
            out = info[Keys.SPLIT]+"_"+str(i)
            IniInfoHandler().write(dict,out)
            log.debug("Wrote "+out)

if __name__ == "__main__":
    SequestSplit.main()
