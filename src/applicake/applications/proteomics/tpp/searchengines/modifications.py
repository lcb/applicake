"""
Created on Jun 5, 2012

@author: quandtan

"""

import sys
from applicake.framework.logger import Logger


class ModificationDb(object):
    """
    Access to post-translational modifications (PTMs).
    """

    _applications = ['Xtandem', 'Omssa', 'Myrimatch', 'Openms']

    _mods = {
        'Carbamidomethyl (C)': {
            _applications[0]: '57.021464@C',
            _applications[1]: '3',
            _applications[2]: 'C 57.021464',
            _applications[3]: '<LISTITEM value="Carbamidomethyl (C)"/>'

        },
        'Oxidation (M)': {
            _applications[0]: '15.994915@M',
            _applications[1]: '1',
            _applications[2]: 'M 15.995',
            _applications[3]: '<LISTITEM value="Oxidation (M)"/>'
        },
        'Phospho (STY)': {
            _applications[0]: '79.966331@S,79.966331@T,79.966331@Y',
            _applications[1]: '6,7,8,132,133',
            _applications[2]: '[STY] 79.966',
            _applications[3]: '<LISTITEM value="Phospho (STY)"/>'
        },
        '13C(6)15(N)(2) (K)': {
            _applications[0]: '8.014199@K',
            _applications[1]: '181',
            _applications[2]: 'K 8.014199',
            _applications[3]: '<LISTITEM value="13C(6)15(N)(2) (K)"/>'
        },
        '13C(6)15(N)(4) (R)': {
            _applications[0]: '10.008269@R',
            _applications[1]: '137',
            _applications[2]: 'R 10.008269',
            _applications[3]: '<LISTITEM value="13C(6)15(N)(4) (R)"/>'
        },
        'Biotin (K)': {
            _applications[0]: '226.077598@K',
            _applications[1]: '119',
            _applications[2]: 'K 226.077598',
            _applications[3]: '<LISTITEM value="Biotin (K)"/>'
        },

        'Oxidation (HW)': {
            _applications[0]: '15.994915@H,15.994915@W',
            _applications[1]: '89,90',
            _applications[2]: '[HW] 15.995',
            _applications[3]: '<LISTITEM value="Oxidation (HW)"/>'
        },
             
        'Deamidation (NQ)': {
            _applications[0]: '0.984016@N,0.984016@Q',
            _applications[1]: '4',
            _applications[2]: '[NQ] 0.984016',
            _applications[3]: '<LISTITEM value="Deamidation (NQ)"/>'
        },
    }
    
    def write_omssa_usermodxml(self,path):
        """
        Writes a usermods.xml file for OMSSA. This file contains all user defined modifications not
        defined in OMSSAS default "mods.xml". Included here to be independent of the current omssa
        installation.
        """
        open(path,"w").write("""<?xml version="1.0"?>
<MSModSpecSet
    xmlns="http://www.ncbi.nlm.nih.gov"
    xmlns:xs="http://www.w3.org/2001/XMLSchema-instance"
    xs:schemaLocation="http://www.ncbi.nlm.nih.gov OMSSA.xsd"
>
  <MSModSpec>
    <MSModSpec_mod>
      <MSMod value="usermod1">119</MSMod>
    </MSModSpec_mod>
    <MSModSpec_type>
      <MSModType value="modaa">0</MSModType>
    </MSModSpec_type>
    <MSModSpec_name>Biotin</MSModSpec_name>
    <MSModSpec_monomass>226.077598</MSModSpec_monomass>
    <MSModSpec_averagemass>226.2954</MSModSpec_averagemass>
    <MSModSpec_n15mass>0</MSModSpec_n15mass>
    <MSModSpec_residues>
      <MSModSpec_residues_E>K</MSModSpec_residues_E>
    </MSModSpec_residues>
    <MSModSpec_unimod>21</MSModSpec_unimod>
    <MSModSpec_psi-ms>Biotin</MSModSpec_psi-ms>
  </MSModSpec>
</MSModSpecSet>
""")

    def __init__(self, log=None):
        """
        Constructor

        """
        if log is None:
            self.log = Logger.create(level='DEBUG', name='memory_logger', stream=sys.stderr)
        else:
            self.log = log


    def get(self, name, search_engine):
        """
        Return the program specific modification.
        """
        if name is None or name == "":
            #self.log.info("No modification used")
            return ''
        try:
            name = name.strip()
            assert self._mods.has_key(name)
            assert search_engine in self._applications
            return self._mods[name][search_engine]
        except:
            self.log.fatal('either name [%s] not found [%s] or search engine [%s] is not supported [%s]' % (
            name, self._mods.keys(), search_engine, self._applications))
            sys.exit(1)

    def get_keys(self):
        """
        Return all available modifications.
        """
        return self._mods.keys()
        