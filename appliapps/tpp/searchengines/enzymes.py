"""
Created on Jun 15, 2012

[COMET_ENZYME_INFO]
0.  No_enzyme              0      -           -
1.  Trypsin                1      KR          P
2.  Trypsin/P              1      KR          -
3.  Lys_C                  1      K           P
4.  Lys_N                  0      K           -
5.  Arg_C                  1      R           P
6.  Asp_N                  0      D           -
7.  CNBr                   1      M           -
8.  Glu_C                  1      DE          P
9.  PepsinA                1      FL          P
10. Chymotrypsin           1      FWYL        P
num_enz_termini: This parameter is unused if a no-enzyme search is specified.

OMSSA.xsd
              <xs:enumeration value="trypsin" ncbi:intvalue="0"/>
              <xs:enumeration value="argc" ncbi:intvalue="1"/>
              <xs:enumeration value="cnbr" ncbi:intvalue="2"/>
              <xs:enumeration value="chymotrypsin" ncbi:intvalue="3"/>
              <xs:enumeration value="formicacid" ncbi:intvalue="4"/>
              <xs:enumeration value="lysc" ncbi:intvalue="5"/>
              <xs:enumeration value="lysc-p" ncbi:intvalue="6"/>
              <xs:enumeration value="pepsin-a" ncbi:intvalue="7"/>
              <xs:enumeration value="tryp-cnbr" ncbi:intvalue="8"/>
              <xs:enumeration value="tryp-chymo" ncbi:intvalue="9"/>
              <xs:enumeration value="trypsin-p" ncbi:intvalue="10"/>
              <xs:enumeration value="whole-protein" ncbi:intvalue="11"/>
              <xs:enumeration value="aspn" ncbi:intvalue="12"/>
              <xs:enumeration value="gluc" ncbi:intvalue="13"/>
              <xs:enumeration value="aspngluc" ncbi:intvalue="14"/>
              <xs:enumeration value="top-down" ncbi:intvalue="15"/>
              <xs:enumeration value="semi-tryptic" ncbi:intvalue="16"/>
              <xs:enumeration value="no-enzyme" ncbi:intvalue="17"/>
              <xs:enumeration value="chymotrypsin-p" ncbi:intvalue="18"/>
              <xs:enumeration value="aspn-de" ncbi:intvalue="19"/>
              <xs:enumeration value="gluc-de" ncbi:intvalue="20"/>
              <xs:enumeration value="lysn" ncbi:intvalue="21"/>
              <xs:enumeration value="thermolysin-p" ncbi:intvalue="22"/>
              <xs:enumeration value="semi-chymotrypsin" ncbi:intvalue="23"/>
              <xs:enumeration value="semi-gluc" ncbi:intvalue="24"/>
              <xs:enumeration value="max" ncbi:intvalue="25"/>
              <xs:enumeration value="none" ncbi:intvalue="255"/>

XTandem & Myrimatch use rules

"""

_enzymes = {
    #'Enzyme': {
    # 'XTandem':   [ cut_rule  , semi_yesno ],
    # 'Myrimatch': [ myri_name , num_enzymatic_termini_012 ],
    # 'Comet':     [ comet_num , num_enz_termini_nothing12 ],
    # 'Omssa':     [ ommsa_num , None],
    # 'InteractParser': [ interact_name , None],
    #},
    'Trypsin': {
        'XTandem': ['[RK]|{P}', 'no'],
        'Myrimatch': ['Trypsin/P', '2'],
        'Comet': ['1', '2'],
        'Omssa': ['0', None],
        'InteractParser': ['trypsin', None],
    },
    'Semi-Tryptic': {
        'XTandem': ['[RK]|{P}', 'yes'],
        'Myrimatch': ['Trypsin/P', '1'],
        'Comet': ['1', '1'],
        'Omssa': ['16', None],
        'InteractParser': ['semitrypsin', None],
    },
    'Nonspecific': {
        'XTandem': ['[X]|[X]', 'no'],
        'Myrimatch': ['Trypsin/P', '0'],
        'Comet': ['0', ''],
        'Omssa': ['17', None],
        'InteractParser': ['nonspecific', None],
    },
    'Asp-N': {
        'XTandem': ['[X]|[D]', 'no'],
        'Myrimatch': ['Asp-N', '2'],
        'Comet': ['6', '2'],
        'Omssa': ['12', None],
        'InteractParser': ['AspN', None],
    },
    'Lys-C': {
        'XTandem': ['[K]|[X]', 'no'],
        'Myrimatch': ['Lys-C', '2'],
        'Comet': ['3', '2'],
        'Omssa': ['5', None],
        'InteractParser': ['LysC', None],
    },
      'Arg-C' : {
        'XTandem': [ '[R]|{P}' , 'no' ],
        'Myrimatch': ['Arg-C' , '2'],
        'Comet': [ '5' , '2' ],
        'Omssa': [ '1', None ],
        'InteractParser': [ 'argc', None ],
    }
}


def enzymestr_to_engine(enzyme, search_engine):
    """
    engine_specific_enzyme_name, engine_specific_semicleavage = get[enzyme_string][search_engine]
    """
    try:
        enz_name, enz_semi = _enzymes[enzyme][search_engine]
        return enz_name, enz_semi
    except Exception, e:
        raise RuntimeError("Enzyme " + enzyme + " for engine " + search_engine + " not found. message : " + e.message)