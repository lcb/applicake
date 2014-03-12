"""
Created on Jun 14, 2012

@author: quandtan
"""

import os
from applicake.applications.proteomics.tpp.searchengines.enzymes import enzymestr_to_engine
from applicake.applications.proteomics.tpp.searchengines.modifications import modstr_to_engine
from applicake.applications.proteomics.tpp.searchengines.omssa import Omssa
from applicake.framework.interfaces import IWrapper
from applicake.framework.keys import Keys
from applicake.framework.templatehandler import BasicTemplateHandler
from applicake.utils.fileutils import FileUtils
from applicake.utils.xmlutils import XmlValidator


class Comet(IWrapper):
    """
    Wrapper for the search engine OMSSA.
    """
    def prepare_run(self, info, log):
        wd = info[Keys.WORKDIR]

        basename = os.path.join(wd,os.path.splitext(os.path.split(info['MZXML'])[1])[0])
        info['PEPXMLS'] = [basename+'.pep.xml']

        #mk copy of info before destroying it
        app_info = info.copy()

        if info['PRECMASSUNIT'] == 'Da':
            app_info['PRECMASSUNIT'] = '0'
        elif info['PRECMASSUNIT'] == 'ppm':
            app_info['PRECMASSUNIT'] = '2'
        else:
            log.error("Precmassunit %s unknown"%info['PRECMASSUNIT'])

        if info['FRAGMASSUNIT'] == 'ppm':
            log.fatal("Comet does not support frag mass error unit PPM")
            return "false", info

        if float(app_info['FRAGMASSERR']) < 0.01 or float(app_info['FRAGMASSERR']) > 1.0:
            log.warn('Very high or low ')


        app_info["STATIC_MODS"], app_info["VARIABLE_MODS"], _ = modstr_to_engine(info["STATIC_MODS"], info["VARIABLE_MODS"], 'Comet')
        app_info['ENZYME'], app_info['NUM_TERM_CLEAVAGES'] = enzymestr_to_engine(info[Keys.ENZYME], 'Comet')
        app_info['TEMPLATE'] = os.path.join(wd,'comet.params')
        CometTemplate().modify_template(app_info, log)
        prefix = app_info.get('PREFIX','comet')

        command = "%s -N%s -P%s %s" % (prefix,basename,app_info['TEMPLATE'],info['MZXML'])
        return command, info

    def set_args(self, log, args_handler):
        args_handler.add_app_args(log, Keys.PREFIX, 'Path to the executable')
        args_handler.add_app_args(log, 'FRAGMASSERR', 'Fragment mass error')
        args_handler.add_app_args(log, 'FRAGMASSUNIT', 'Unit of the fragment mass error')
        args_handler.add_app_args(log, 'PRECMASSERR', 'Precursor mass error')
        args_handler.add_app_args(log, 'PRECMASSUNIT', 'Unit of the precursor mass error')
        args_handler.add_app_args(log, 'MISSEDCLEAVAGE', 'Number of maximal allowed missed cleavages')
        args_handler.add_app_args(log, 'DBASE', 'Sequence database file with target/decoy entries')
        args_handler.add_app_args(log, Keys.ENZYME, 'Enzyme used to digest the proteins')
        args_handler.add_app_args(log, Keys.STATIC_MODS, 'List of static modifications')
        args_handler.add_app_args(log, Keys.VARIABLE_MODS, 'List of variable modifications')
        args_handler.add_app_args(log, Keys.THREADS, 'Number of threads used in the process.')
        args_handler.add_app_args(log, Keys.WORKDIR, 'Directory to store files')
        args_handler.add_app_args(log, 'MZXML', 'Peak list file in mzXML format')
        return args_handler

    def validate_run(self, info, log, run_code, out_stream, err_stream):
        if 0 != run_code:
            return run_code, info
        result_file = info[Keys.PEPXMLS][0]
        if not FileUtils.is_valid_file(log, result_file):
            log.critical('[%s] is not valid' % result_file)
            return 1, info
        if not XmlValidator.is_wellformed(result_file):
            log.critical('[%s] is not well formed.' % result_file)
            return 1, info
        return 0, info


class CometTemplate(BasicTemplateHandler):
    """

    """

    def read_template(self, info, log):
        template = """# comet_version 2013.02 rev. 2
# Comet MS/MS search engine parameters file.
# Everything following the '#' symbol is treated as a comment.

database_name = $DBASE
decoy_search = 0                       # 0=no (default), 1=concatenated search, 2=separate search

num_threads = $THREADS                        # 0=poll CPU to set num threads; else specify num threads directly (max 64)

#
# masses
#
peptide_mass_tolerance = $PRECMASSERR
peptide_mass_units = $PRECMASSUNIT                 # 0=amu, 1=mmu, 2=ppm
mass_type_parent = 1                   # 0=average masses, 1=monoisotopic masses
mass_type_fragment = 1                 # 0=average masses, 1=monoisotopic masses
precursor_tolerance_type = 0           # 0=MH+ (default), 1=precursor m/z
isotope_error = 0                      # 0=off, 1=on -1/0/1/2/3 (standard C13 error), 2= -8/-4/0/4/8 (for +4/+8 labeling)

#
# search enzyme
#
search_enzyme_number = $ENZYME               # choose from list at end of this params file
num_enzyme_termini = $NUM_TERM_CLEAVAGES                 # valid values are 1 (semi-digested), 2 (fully digested, default), 8 N-term, 9 C-term
allowed_missed_cleavage = $MISSEDCLEAVAGE            # maximum value is 5; for enzyme search

#
# Up to 6 variable modifications are supported
# format:  <mass> <residues> <0=variable/1=binary> <max mods per a peptide>
#     e.g. 79.966331 STY 0 3
#
$VARIABLE_MODS
max_variable_mods_in_peptide = 5

#
# fragment ions
#
# ion trap ms/ms:  1.0005 tolerance, 0.4 offset (mono masses), theoretical_fragment_ions = 1
# high res ms/ms:    0.02 tolerance, 0.0 offset (mono masses), theoretical_fragment_ions = 0
#
fragment_bin_tol = $FRAGMASSERR              # binning to use on fragment ions
fragment_bin_offset = 0.4              # offset position to start the binning (0.0 to 1.0)
theoretical_fragment_ions = 1          # 0=default peak shape, 1=M peak only
use_A_ions = 0
use_B_ions = 1
use_C_ions = 0
use_X_ions = 0
use_Y_ions = 1
use_Z_ions = 0
use_NL_ions = 1                        # 0=no, 1=yes to consider NH3/H2O neutral loss peaks
use_sparse_matrix = 0

#
# output
#
output_sqtstream = 0                   # 0=no, 1=yes  write sqt to standard output
output_sqtfile = 0                     # 0=no, 1=yes  write sqt file
output_txtfile = 0                     # 0=no, 1=yes  write tab-delimited txt file
output_pepxmlfile = 1                  # 0=no, 1=yes  write pep.xml file
output_pinxmlfile = 0                  # 0=no, 1=yes  write pin.xml file
output_outfiles = 0                    # 0=no, 1=yes  write .out files
print_expect_score = 1                 # 0=no, 1=yes to replace Sp with expect in out & sqt
num_output_lines = 5                   # num peptide results to show
show_fragment_ions = 0                 # 0=no, 1=yes for out files only

sample_enzyme_number = 1               # Sample enzyme which is possibly different than the one applied to the search.
                                       # Used to calculate NTT & NMC in pepXML output (default=1 for trypsin).

#
# mzXML parameters
#
scan_range = 0 0                       # start and scan scan range to search; 0 as 1st entry ignores parameter
precursor_charge = 0 0                 # precursor charge range to analyze; does not override mzXML charge; 0 as 1st entry ignores parameter
ms_level = 2                           # MS level to analyze, valid are levels 2 (default) or 3
activation_method = ALL                # activation method; used if activation method set; allowed ALL, CID, ECD, ETD, PQD, HCD, IRMPD

#
# misc parameters
#
digest_mass_range = 600.0 5000.0       # MH+ peptide mass range to analyze
num_results = 50                       # number of search hits to store internally
skip_researching = 1                   # for '.out' file output only, 0=search everything again (default), 1=don't search if .out exists
max_fragment_charge = 3                # set maximum fragment charge state to analyze (allowed max 5)
max_precursor_charge = 6               # set maximum precursor charge state to analyze (allowed max 9)
nucleotide_reading_frame = 0           # 0=proteinDB, 1-6, 7=forward three, 8=reverse three, 9=all six
clip_nterm_methionine = 0              # 0=leave sequences as-is; 1=also consider sequence w/o N-term methionine
spectrum_batch_size = 0                # max. # of spectra to search at a time; 0 to search the entire scan range in one loop
decoy_prefix = DECOY_                  # decoy entries are denoted by this string which is pre-pended to each protein accession

#
# spectral processing
#
minimum_peaks = 10                     # required minimum number of peaks in spectrum to search
minimum_intensity = 0                  # minimum intensity value to read in
remove_precursor_peak = 0              # 0=no, 1=yes, 2=all charge reduced precursor peaks (for ETD)
remove_precursor_tolerance = 1.5       # +- Da tolerance for precursor removal
clear_mz_range = 0.0 0.0               # for iTRAQ/TMT type data; will clear out all peaks in the specified m/z range

#
# additional modifications
#

variable_C_terminus = 0.0
variable_N_terminus = 0.0
variable_C_terminus_distance = -1      # -1=all peptides, 0=protein terminus, 1-N = maximum offset from C-terminus
variable_N_terminus_distance = -1      # -1=all peptides, 0=protein terminus, 1-N = maximum offset from N-terminus

add_Cterm_peptide = 0.0
add_Nterm_peptide = 0.0
add_Cterm_protein = 0.0
add_Nterm_protein = 0.0

$STATIC_MODS
add_B_user_amino_acid = 0.0000         # added to B - avg.   0.0000, mono.   0.00000
add_J_user_amino_acid = 0.0000         # added to J - avg.   0.0000, mono.   0.00000
add_U_user_amino_acid = 0.0000         # added to U - avg.   0.0000, mono.   0.00000
add_X_user_amino_acid = 0.0000         # added to X - avg.   0.0000, mono.   0.00000
add_Z_user_amino_acid = 0.0000         # added to Z - avg.   0.0000, mono.   0.00000

#
# COMET_ENZYME_INFO _must_ be at the end of this parameters file
#
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

        """
        return template, info
