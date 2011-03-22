# 2001028
#spectra,[FILENAME] - Specifies a spectrum file to search. You can specify the name of a directory to search every file in that directory (non-recursively).
#Preferred file formats: .mzXML and .mgf 
#Other accepted file formats: .mzData, .ms2 .dta. Note that multiple spectra in a single .dta file are not supported. 
#db,[FILENAME] - Specifies the name of a database (.trie file) to search. The .trie file contains one or more protein sequences delimited by asterisks, with no whitespace or other data. Use PrepDB.py (see Databases to prepare a database. You should specify at least one database. You may specify several databases; if so, each database will be searched in turn.
#SequenceFile,[FILENAME] - Specifies the name of a FASTA-format protein database to search. If you plan to search a large database, it is more efficient to preprocess it using PrepDB.py and use the "db" command instead. You can specify at most one SequenceFile. 
#protease,[NAME] - Specifies the name of a protease. "Trypsin", "None", and "Chymotrypsin" are the available values. If tryptic digest is specified, then matches with non-tryptic termini are penalized. 
#mod,[MASS],[RESIDUES],[TYPE],[NAME] - Specifies an amino acid modification. The delta mass (in daltons) and affected amino acids are required. The first four characters of the name should be unique. Valid values for "type" are "fix", "cterminal", "nterminal", and "opt" (the default). For a guide to various known modification types, consult the following databases:
#ABRF mass delta reference
#UNIMOD database
#RESID database of modifications Examples: 
#mod,+57,C,fix - Most searches should include this line. It reflects the addition of CAM (carbamidomethylation, done by adding iodoacetamide) which prevents cysteines from forming disulfide bonds. 
#mod,80,STY,opt,phosphorylation 
#mod,16,M (Oxidation of methionine, seen in many samples) 
#mod,43,*,nterminal (N-terminal carbamylation, common if sample is treated with urea) 
#Important note: When searching for phosphorylation sites, use a modification with the name "phosphorylation". This lets Inspect know that it should use its model of phosphopeptide fragmentation when generating tags and scoring matches. (Phosphorylation of serine dramatically affects fragmentation, so modeling it as simply an 80Da offset is typically not sufficient to detect sites with high sensitivity)
#Mods,[COUNT] - Number of PTMs permitted in a single peptide. Set this to 1 (or higher) if you specify PTMs to search for.
#Unrestrictive,[FLAG] - If FLAG is 1, use the MS-Alignment algorithm to perform an unrestrictive search (allowing arbitrary modification masses). Running an unrestrictive search with one mod per peptide is slower than the normal (tag-based) search; running time is approximately 1 second per spectrum per megabyte of database. Running an unrestrictive search with two mods is significantly slower. We recommend performing unrestrictive searches against a small database, containing proteins output by an earlier search. (The "Summary.py" script can be used to generate a second-pass database from initial search results; see Analysis)
#MaxPTMSize,[SIZE] - For blind search, specifies the maximum modification size (in Da) to consider. Defaults to 250. Larger values require more time to search.
#PMTolerance,[MASS] - Specifies the parent mass tolerance, in Daltons. A candidate's flanking mass can differ from the tag's flanking mass by no more than ths amount. Default value is 2.5. Note that secondary ions are often selected for fragmentation, so parent mass errors near 1.0Da or -1.0Da are not uncommon in typical datasets, even on FT machines.
#ParentPPM,[MASS] - Specifies a parent mass tolerance, in parts per million. Alternative to PMTolerance.
#IonTolerance,[MASS] - Error tolerance for how far ion fragments (b and y peaks) can be shifted from their expected masses. Default is 0.5. Higher values produce a more sensitive but much slower search.
#PeakPPM,[MASS] - Specifies a fragment mass tolerance, in parts per million. Alternative to IonTolerance.
#MultiCharge,[FLAG] - If set to true, attempt to guess the precursor charge and mass, and consider multiple charge states if feasible.
#Instrument,[TYPE] - Options are ESI-ION-TRAP (default), QTOF, and FT-Hybrid. If set to ESI-ION-TRAP, Inspect attempts to correct the parent mass. If set to QTOF, Inspect uses a fragmentation model trained on QTOF data. (QTOF data typically features a stronger y ladder and weaker b ladder than other spectra).
#RequiredMod,[NAME] - The specified modification MUST be found somewhere on the peptide.
#TagCount,[COUNT] - Number of tags to generate
#TagLength,[LENGTH] - Length of peptide sequence tags. Defaults to 3. Accepted values are 1 through 6.
#RequireTermini,[COUNT] - If set to 1 or 2, require 1 or 2 valid proteolytic termini. Deprecated, because the scoring model already incorporates the number of valid (tryptic) termini.

Instrument,ESI-ION-TRAP
protease,trypsin
mod,+57,C,fix
Unrestrictive,0
spectra,$MZXML
db,$DBASE