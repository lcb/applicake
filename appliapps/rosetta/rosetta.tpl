# module load rosetta (no need to specify the Rosetta database)
-run:protocol $RUN__PROTOCOL
$RUN__SHUFFLE

# alignment.filt is an input file
-in:file:alignment $IN__FILE__ALIGNMENT
-cm:aln_format $CM__ALN_FORMAT


# fasta file is a file: t000_.fasta (always same name)
-in:file:fasta $IN__FILE__FASTA
$IN__FILE__FULLATOM

# files that start with aat000 are fragment files, 03 and 09 refers to length of fragments (always same name)
-frag3 $FRAG3
-frag9 $FRAG9

-loops:frag_sizes $LOOPS__FRAG_SIZES
# these are the same as above (always same name)
-loops:frag_files $LOOPS__FRAG_FILES

# file is also a file: t000_.psipred_ss2 (always same name)
-in:file:psipred_ss2 $IN__FILE__PSIPRED_SS2
$IN__FILE__FULLATOM

$IDEALIZE_AFTER_LOOP_CLOSE
-out:file:silent_struct_type $OUT__FILE__SILENT_STRUCT_TYPE
-out:file:silent $ROSETTA_OUT
-out:nstruct $N_MODELS

$LOOPS__EXTENDED
$LOOPS__BUILD_INITIAL
-loops:remodel $LOOPS__REMODEL
-loops:relax $LOOPS__RELAX
$RELAX__FAST
-relax:default_repeats $RELAX__DEFAULT_REPEATS

$SILENT_DECOYTIME

-random_grow_loops_by $RANDOM_GROW_LOOPS_BY
-select_best_loop_from $SELECT_BEST_LOOP_FROM

-in:detect_disulf $IN__DETECT_DISULF
-fail_on_bad_hbond $FAIL_ON_BAD_HBOND
-in:file:template_pdb $IN__FILE__TEMPLATE_PDB
$BGDT
$EVALUATION__GDTMM