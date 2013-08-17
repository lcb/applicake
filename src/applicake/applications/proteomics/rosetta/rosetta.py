"""
Created on May 10, 2012

@author: loblum
"""

import os,subprocess
from configobj import ConfigObj 
from applicake.framework.interfaces import IWrapper
from applicake.framework.templatehandler import BasicTemplateHandler
from applicake.framework.keys import Keys


class Rosetta(IWrapper):
    """
    Wrapper for minirosetta.default.linuxgcc
    """

    def prepare_run(self, info, log):
        for f in info[Keys.DSSOUTPUT]:
            if "dataset.properties" in f:
                dsprop = ConfigObj(f)
        wd = info[Keys.WORKDIR]
        
        info["SEQ"] = dsprop["SEQ"]
        info["IN__FILE__ALIGNMENT"] = os.path.join(info["ROSETTA_EXTRACTDIR"],dsprop["ALIGNMENT_FILE"])
        info["IN__FILE__FASTA"] = os.path.join(info["ROSETTA_EXTRACTDIR"],dsprop["FILE_STEM"]+".fasta")
        info["FRAG3"] = os.path.join(info["ROSETTA_EXTRACTDIR"],dsprop["3MERS"]) 
        info["FRAG9"] = os.path.join(info["ROSETTA_EXTRACTDIR"],dsprop["9MERS"])
        info["LOOPS__FRAG_SIZES"] = "9 3 1"
        info["LOOPS__FRAG_FILES"] = info["FRAG9"] + " " + info["FRAG3"] + " none"
        info["IN__FILE__PSIPRED_SS2"] = os.path.join(info["ROSETTA_EXTRACTDIR"],dsprop["FILE_STEM"]+".psipred_ss2")
        info['ROSETTA_OUT'] = os.path.join(wd, 'default.out')
        #needed because of rosetta && gzip
        info['ROSETTA_COMPRESSEDOUT'] = info['ROSETTA_OUT'] + '.gz'        
        
        info["IN__FILE__TEMPLATE_PDB"] = ""               
        for pdb in dsprop["TEMPLATES"].split():
            info["IN__FILE__TEMPLATE_PDB"] += os.path.join(info["ROSETTA_EXTRACTDIR"],pdb) + " "        
        info["IN__FILE__TEMPLATE_PDB"] = info["IN__FILE__TEMPLATE_PDB"].strip()
        
        info["DATABASE"] = os.environ["ROSETTA3_DB"]
        info["ROSETTA_VERSION"] = subprocess.check_output("which %s | cut -d/ -f5"%info["PREFIX"],shell=True).strip()
        info["INFRASTRUCTURE"] = "BRUTUS"
        
        #change the on/off flags only in the template, not the info  
        app_info = info.copy()
        app_info['RUN__SHUFFLE'] = "-run:shuffle" if info['RUN__SHUFFLE'] == "TRUE" else ""
        app_info['IN__FILE__FULLATOM'] = "-in:file:fullatom" if info['IN__FILE__FULLATOM'] == "TRUE" else ""
        app_info['IDEALIZE_AFTER_LOOP_CLOSE'] = "-idealize_after_loop_close" if info['IDEALIZE_AFTER_LOOP_CLOSE'] == "TRUE" else ""
        app_info['LOOPS__EXTENDED'] = "-loops:extended" if info['LOOPS__EXTENDED'] == "TRUE" else ""
        app_info['LOOPS__BUILD_INITIAL'] = "-loops:build_initial" if info['LOOPS__BUILD_INITIAL'] == "TRUE" else ""
        app_info['RELAX__FAST'] = "-relax:fast" if info['RELAX__FAST'] == "TRUE" else ""
        app_info['SILENT_DECOYTIME'] = "-silent_decoytime" if info['SILENT_DECOYTIME'] == "TRUE" else ""
        app_info['BGDT'] = "-bGDT" if info['BGDT'] == "TRUE" else ""
        app_info['EVALUATION__GDTMM'] = "-evaluation:gdtmm" if info['EVALUATION__GDTMM'] == "TRUE" else ""
        
        app_info['TEMPLATE'] = os.path.join(wd, 'flags')
        RosettaTemplate().modify_template(app_info, log)
        
        command = "%s @%s && gzip %s" % (app_info["PREFIX"], app_info['TEMPLATE'], app_info['ROSETTA_OUT'])
        print command
        return command, info

    def set_args(self, log, args_handler):
        args_handler.add_app_args(log, Keys.PREFIX, 'command to execute',default="minirosetta.default.linuxgccrelease")
        args_handler.add_app_args(log, Keys.DSSOUTPUT, 'file list downloaded by dss')
        args_handler.add_app_args(log, Keys.WORKDIR, 'Directory to store files')
        args_handler.add_app_args(log, 'ROSETTA_EXTRACTDIR', 'dir where rosetta dataset was extracted to')
        args_handler.add_app_args(log, 'N_MODELS', 'Number of models created')       
        
        args_handler.add_app_args(log, 'RUN__PROTOCOL', '',default="threading")
        args_handler.add_app_args(log, 'RUN__SHUFFLE', '',default="TRUE")
        args_handler.add_app_args(log, 'CM__ALN_FORMAT', '',default="grishin")
        args_handler.add_app_args(log, 'IN__FILE__FULLATOM', '',default="TRUE")
        args_handler.add_app_args(log, 'IDEALIZE_AFTER_LOOP_CLOSE', '',default="TRUE")
        args_handler.add_app_args(log, 'OUT__FILE__SILENT_STRUCT_TYPE', '',default="binary")
        args_handler.add_app_args(log, 'LOOPS__EXTENDED', '',default="TRUE")
        args_handler.add_app_args(log, 'LOOPS__BUILD_INITIAL', '',default="TRUE")
        args_handler.add_app_args(log, 'LOOPS__REMODEL', '',default="quick_ccd")
        args_handler.add_app_args(log, 'LOOPS__RELAX', '',default="relax")
        args_handler.add_app_args(log, 'RELAX__FAST', '',default="TRUE")
        args_handler.add_app_args(log, 'RELAX__DEFAULT_REPEATS', '',default="16")
        args_handler.add_app_args(log, 'SILENT_DECOYTIME', '',default="TRUE")
        args_handler.add_app_args(log, 'RANDOM_GROW_LOOPS_BY', '',default="4")        
        args_handler.add_app_args(log, 'SELECT_BEST_LOOP_FROM', '',default="1")
        args_handler.add_app_args(log, 'IN__DETECT_DISULF', '',default="false")        
        args_handler.add_app_args(log, 'FAIL_ON_BAD_HBOND', '',default="false")                 
        args_handler.add_app_args(log, 'BGDT', '',default="TRUE")
        args_handler.add_app_args(log, 'EVALUATION__GDTMM', '',default="TRUE")
        

        return args_handler

    def validate_run(self, info, log, run_code, out_stream, err_stream):
        return run_code, info


class RosettaTemplate(BasicTemplateHandler):
    def read_template(self, info, log):
        template = """
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
        """
        return template, info
    
