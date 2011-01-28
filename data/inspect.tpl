spectra,mergedSpectra.mgf
spectra,mergedSpectra.mgf
DB,./fromAC.trie
DB,./fromAC.trie

protease,trypsin
mods,0
ParentPPM,25
IonTolerance,0.25
Instrument,QTOF

# spectra,[FILENAME] - Specifies a spectrum file to search.
# You can specify the name of a directory to search every file in that directory
# (non-recursively).
# Accepted file formats: .mgf, .mzXML, .mzData, .ms2 .dta.
# Note that multiple spectra in a single .dta file are not supported.

# DB,[FILENAME] - Specifies the name of a database (.trie file) to search.
# The .trie file contains one or more protein sequences delimited by asterisks,
# with no whitespace or other data. You should specify at least one database.
# You may specify several databases; if so, each database will be searched in turn.


# SequenceFile,[FILENAME] - Specifies the name of a FASTA-format protein database
# to search. You can specify at most one SequenceFile.

# protease,[NAME] - Specifies the name of a protease. "Trypsin", "None", and
# "Chymotrypsin" are the available values.
# If tryptic digest is specified, then matches with non-tryptic termini are
# penalized.


# mod,[MASS],[RESIDUES],[TYPE],[NAME] - Specifies an amino acid modification.
# The delta mass (in daltons) and affected amino acids are required.
# The first four characters of the name should be unique. Valid values for "type"
# are "fix", "cterminal", "nterminal", and "opt" (the default).
# For a guide to various known modification types, consult the following databases:
# ABRF mass delta reference
# UNIMOD database
# RESID database of modifications Examples:
# Important note: When searching for phosphorylation sites, use a modification
# with the name "phosphorylation". This lets Inspect know that it should
# use its model of phosphopeptide fragmentation when generating tags and scoring
# matches. (Phosphorylation of serine dramatically affects fragmentation,
# so modeling it as simply an 80Da offset is typically not sufficient to detect
# sites with high sensitivity)
# mod,+57,C,fix
# mod,80,STY,opt,phosphorylation
# mod,16,M
# mod,43,*,nterminal


# Mods,[COUNT] - Number of PTMs permitted in a single peptide. Set this to 1
# (or higher) if you specify PTMs to search for.

# Unrestrictive,[FLAG] - If FLAG is 1, use the MS-Alignment algorithm to perform
# an unrestrictive search (allowing arbitrary modification masses).
# Running an unrestrictive search with one mod per peptide is slower than
# the normal (tag-based) search; running time is approximately 1 second per
# spectrum per megabyte of database. Running an unrestrictive search with two
# mods is significantly slower.
# We recommend performing unrestrictive searches against a small database,
# containing proteins output by an earlier search.
#Unrestrictive,1

# MaxPTMSize,[SIZE] - For blind search, specifies the maximum modification size
# (in Da) to consider. Defaults to 250.


# PMTolerance,[MASS] - Specifies the parent mass tolerance, in Daltons.
# A candidate's flanking mass can differ from the tag's flanking mass by no more
# than ths amount. Default value is 2.5. Note that secondary ions are often
# selected for fragmentation, so parent mass errors near 1.0Da or -1.0Da are
# not uncommon in typical datasets, even on FT machines.
PMTolerance,1.5

# ParentPPM,[MASS] - Specifies a parent mass tolerance, in parts per million. Alternative to PMTolerance.

# IonTolerance,[MASS] - Error tolerance for how far ion fragments (b and y peaks) can be shifted from their expected masses.
# Default is 0.5. Higher values produce a more sensitive but much slower search.


# RequiredMod,[NAME] - The specified modification MUST be found somewhere on the peptide.

# TagCount,[COUNT] - Number of tags to generate

# TagLength,[LENGTH] - Length of peptide sequence tags. Defaults to 3. Accepted values are 1 through 6.

# RequireTermini,[COUNT] - If set to 1 or 2, require 1 or 2 valid proteolytic termini. Deprecated, because the scoring model already incorporates the number of valid (tryptic) termini.

# Non-standard options:
# TagsOnly - Tags are generated and written to the specified output file. No search is performed.

# Instrument type (QTOF or ESI-ION-TRAP)


# end of parameter file