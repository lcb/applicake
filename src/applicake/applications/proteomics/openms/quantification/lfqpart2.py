'''
Created on Jun 18, 2012

@author: loblum
'''

import os
from applicake.framework.interfaces import IWrapper
from applicake.framework.templatehandler import BasicTemplateHandler
from applicake.utils.fileutils import FileUtils

class LFQpart2(IWrapper):

    def prepare_run(self,info,log):

        wd = info[self.WORKDIR]
        
        #required because openbis requires prot.xml and openms protXML
        protlink = os.path.join(wd,'protein.protXML')
        os.symlink(info['PROTXML'], protlink)
        info['PROTXML'] = protlink
        
        info['FEATUREXMLLIST'] = ''
        for i in info['FEATUREXMLS']:
            info['FEATUREXMLLIST'] += '<LISTITEM value="' + i + '"/>'
            
        info[self.TEMPLATE] = os.path.join(wd,'LFQpart2.toppas')
        _,info = LFQpart2WorkflowTemplate().modify_template(info, log)
        
        del info['FEATUREXMLLIST']
         
        rawprot = os.path.join(wd,'TOPPAS_out/009-ProteinQuantifier/*.csv')
        rawpep = os.path.join(wd,'TOPPAS_out/010-ProteinQuantifier/*.csv')
        rawconsensusxml = os.path.join(wd,'TOPPAS_out/011-FeatureLinker*/*.consensusXML')
        
        info['PROTCSV'] = os.path.join(wd,'proteins.csv')
        info['PEPCSV'] = os.path.join(wd,'peptides.csv')
        info['CONSENSUSXML'] = os.path.join(wd,'FeatureLinker.consensusXML')
        
        self._result_files = []
        self._result_files.append(info['PROTCSV'])
        self._result_files.append(info['PEPCSV'])
        self._result_files.append(info['CONSENSUSXML'])
        
        
        command = 'ExecutePipeline -in %s -out_dir %s && mv -v %s %s && mv -v %s %s && mv -v %s %s' % \
            (info[self.TEMPLATE], wd,rawprot,info['PROTCSV'],rawpep,info['PEPCSV'],rawconsensusxml,info['CONSENSUSXML'])
        return command,info

    def set_args(self,log,args_handler):
        """
        See interface
        """
        args_handler.add_app_args(log, self.WORKDIR, 'wd')
        args_handler.add_app_args(log, 'FEATUREXMLS', 'Path to the featureXML fileS.')
        args_handler.add_app_args(log, 'PROTXML', 'Path to the protXML file (one).')
        
        args_handler.add_app_args(log, "MAPALIGNER_ALGORITHM__MAX_RT_SHIFT", "")
        #requested as option by olgas
        args_handler.add_app_args(log, "MAPALIGNER_ALGORITHM__MIN_RUN_OCCUR", "")
        args_handler.add_app_args(log, "MAPALIGNER_MODEL__TYPE", "")
        args_handler.add_app_args(log, "PROTEINQUANTIFIER_INCLUDE_ALL", "")
        args_handler.add_app_args(log, "PROTEINQUANTIFIER_TOP", "")
        args_handler.add_app_args(log, "FEATURELINKER_DISTANCE_MZ__MAX_DIFFERENCE", "")
        args_handler.add_app_args(log, "FEATURELINKER_DISTANCE_MZ__UNIT", "")
        args_handler.add_app_args(log, "FEATURELINKER_DISTANCE_RT__MAX_DIFFERENCE", "")
        args_handler.add_app_args(log, "FEATURELINKER_USE_IDENTIFICATIONS", "")
        args_handler.add_app_args(log, "MAPALIGNER_EXECUTABLE", "which mapaligner to use")
        args_handler.add_app_args(log, "FEATURELINKER_EXECUTABLE", "which featurelinker to use")
        return args_handler
        
    def validate_run(self,info,log, run_code,out_stream, err_stream):
        if 0 != run_code:
            return run_code,info 
        for i in  self._result_files:
            if not FileUtils.is_valid_file(log, i):
                log.critical('[%s] is not valid' % i)
                return 1,info
        return run_code,info

             
class LFQpart2WorkflowTemplate(BasicTemplateHandler):
    """
    Template handler for Mzxml2Mzml.
    """

    def read_template(self, info, log):
        """
        See super class.
        """
        template = """<?xml version="1.0" encoding="ISO-8859-1"?>
<PARAMETERS version="1.4" xsi:noNamespaceSchemaLocation="http://open-ms.sourceforge.net/schemas/Param_1_4.xsd" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <NODE name="info" description="">
    <ITEM name="version" value="1.10.0" type="string" description="" />
    <ITEM name="num_vertices" value="11" type="int" description="" />
    <ITEM name="num_edges" value="10" type="int" description="" />
    <ITEM name="description" value="&lt;![CDATA[]]&gt;" type="string" description="" />
  </NODE>
  <NODE name="vertices" description="">
    <NODE name="3" description="">
      <ITEM name="recycle_output" value="false" type="string" description="" />
      <ITEM name="toppas_type" value="tool" type="string" description="" />
      <ITEM name="tool_name" value="$MAPALIGNER_EXECUTABLE" type="string" description="" />
      <ITEM name="tool_type" value="" type="string" description="" />
      <ITEM name="x_pos" value="280" type="float" description="" />
      <ITEM name="y_pos" value="-60" type="float" description="" />
      <NODE name="parameters" description="">
        <ITEMLIST name="in" type="string" description="Input files separated by blanks (all must have the same file type)" tags="input file,required" supported_formats="*.featureXML,*.consensusXML,*.idXML">
        </ITEMLIST>
        <ITEMLIST name="out" type="string" description="Output files separated by blanks. Either &apos;out&apos; or &apos;trafo_out&apos; has to be provided. They can be used together." tags="output file" supported_formats="*.featureXML,*.consensusXML,*.idXML">
        </ITEMLIST>
        <ITEMLIST name="trafo_out" type="string" description="Transformation output files separated by blanks. Either &apos;out&apos; or &apos;trafo_out&apos; has to be provided. They can be used together." tags="output file" supported_formats="*.trafoXML">
        </ITEMLIST>
        <ITEM name="log" value="" type="string" description="Name of log file (created only when specified)" tags="advanced" />
        <ITEM name="debug" value="0" type="int" description="Sets the debug level" tags="advanced" />
        <ITEM name="threads" value="1" type="int" description="Sets the number of threads allowed to be used by the TOPP tool" />
        <ITEM name="no_progress" value="false" type="string" description="Disables progress logging to command line" tags="advanced" restrictions="true,false" />
        <ITEM name="test" value="false" type="string" description="Enables the test mode (needed for internal use only)" tags="advanced" restrictions="true,false" />
        <NODE name="reference" description="Options to define a reference file (use either &apos;file&apos; or &apos;index&apos;, not both; if neither is given &apos;index&apos; is used).">
          <ITEM name="file" value="" type="string" description="File to use as reference (same file format as input files required)" tags="input file" supported_formats="*.featureXML,*.consensusXML,*.idXML" />
          <ITEM name="index" value="0" type="int" description="Use one of the input files as reference (&apos;1&apos; for the first file, etc.).#br#If &apos;0&apos;, no explicit reference is set - the algorithm will select a reference." restrictions="0:" />
        </NODE>
        <NODE name="algorithm" description="Algorithm parameters section">
          <ITEM name="num_used_points" value="1000" type="int" description="Maximum number of elements considered in each map (selected by intensity).  Use this to reduce the running time and to disregard weak signals during alignment.  For using all points, set this to -1." restrictions="-1:" />
          <ITEM name="peptide_score_threshold" value="0" type="float" description="Score threshold for peptide hits to be used in the alignment.#br#Select a value that allows only &apos;high confidence&apos; matches." />
          <ITEM name="min_run_occur" value="$MAPALIGNER_ALGORITHM__MIN_RUN_OCCUR" type="int" description="Minimum number of runs (incl. reference, if any) a peptide must occur in to be used for the alignment.#br#Unless you have very few runs or identifications, increase this value to focus on more informative peptides." restrictions="2:" />
          <ITEM name="max_rt_shift" value="$MAPALIGNER_ALGORITHM__MAX_RT_SHIFT" type="float" description="Maximum realistic RT difference for a peptide (median per run vs. reference). Peptides with higher shifts (outliers) are not used to compute the alignment.#br#If 0, no limit (disable filter); if &gt; 1, the final value in seconds; if &lt;= 1, taken as a fraction of the range of the reference RT scale." restrictions="0:" />
          <ITEM name="use_unassigned_peptides" value="true" type="string" description="Should unassigned peptide identifications be used when computing an alignment of feature maps? If &apos;false&apos;, only peptide IDs assigned to features will be used." restrictions="true,false" />
          <ITEM name="use_feature_rt" value="false" type="string" description="When aligning feature maps, don&apos;t use the retention time of a peptide identification directly; instead, use the retention time of the centroid of the feature (apex of the elution profile) that the peptide was matched to. If different identifications are matched to one feature, only the peptide closest to the centroid in RT is used.#br#Precludes &apos;use_unassigned_peptides&apos;." restrictions="true,false" />
        </NODE>
        <NODE name="model" description="Options to control the modeling of retention time transformations from data">
          <ITEM name="type" value="b_spline" type="string" description="Type of model" restrictions="linear,b_spline,interpolated" />
          <NODE name="linear" description="Parameters for &apos;linear&apos; model">
            <ITEM name="symmetric_regression" value="false" type="string" description="Perform linear regression on &apos;y - x&apos; vs. &apos;y + x&apos;, instead of on &apos;y&apos; vs. &apos;x&apos;." restrictions="true,false" />
          </NODE>
          <NODE name="b_spline" description="Parameters for &apos;b_spline&apos; model">
            <ITEM name="num_breakpoints" value="5" type="int" description="Number of breakpoints of the cubic spline in the smoothing step. More breakpoints mean less smoothing. Reduce this number if the transformation has an unexpected shape." restrictions="2:" />
            <ITEM name="break_positions" value="uniform" type="string" description="How to distribute the breakpoints on the retention time scale. &apos;uniform&apos;: intervals of equal size; &apos;quantiles&apos;: equal number of data points per interval." restrictions="uniform,quantiles" />
          </NODE>
          <NODE name="interpolated" description="Parameters for &apos;interpolated&apos; model">
            <ITEM name="interpolation_type" value="cspline" type="string" description="Type of interpolation to apply." restrictions="linear,cspline,akima" />
          </NODE>
        </NODE>
      </NODE>
    </NODE>
    <NODE name="4" description="">
      <ITEM name="recycle_output" value="false" type="string" description="" />
      <ITEM name="toppas_type" value="output file list" type="string" description="" />
      <ITEM name="x_pos" value="280" type="float" description="" />
      <ITEM name="y_pos" value="80" type="float" description="" />
    </NODE>
    <NODE name="7" description="">
      <ITEM name="recycle_output" value="false" type="string" description="" />
      <ITEM name="toppas_type" value="tool" type="string" description="" />
      <ITEM name="tool_name" value="ProteinQuantifier" type="string" description="" />
      <ITEM name="tool_type" value="" type="string" description="" />
      <ITEM name="x_pos" value="640" type="float" description="" />
      <ITEM name="y_pos" value="-60" type="float" description="" />
      <NODE name="parameters" description="">
        <ITEM name="in" value="" type="string" description="Input file" tags="input file,required" supported_formats="*.featureXML,*.consensusXML" />
        <ITEM name="protxml" value="" type="string" description="ProteinProphet results (protXML converted to idXML) for the identification runs that were used to annotate the input.#br#Information about indistinguishable proteins will be used for protein quantification." tags="input file" supported_formats="*.idXML" />
        <ITEM name="out" value="" type="string" description="Output file for protein abundances" tags="output file" supported_formats="*.csv" />
        <ITEM name="peptide_out" value="" type="string" description="Output file for peptide abundances" tags="output file" supported_formats="*.csv" />
        <ITEM name="mzTab_out" value="" type="string" description="Export to mzTab.#br#Either &apos;out&apos;, &apos;peptide_out&apos;, or &apos;mzTab_out&apos; are required. They can be used together." tags="output file" supported_formats="*.csv" />
        <ITEM name="top" value="$PROTEINQUANTIFIER_TOP" type="int" description="Calculate protein abundance from this number of proteotypic peptides (most abundant first; &apos;0&apos; for all)" restrictions="0:" />
        <ITEM name="average" value="median" type="string" description="Averaging method used to compute protein abundances from peptide abundances" restrictions="median,mean,sum" />
        <ITEM name="include_all" value="$PROTEINQUANTIFIER_INCLUDE_ALL" type="string" description="Include results for proteins with fewer proteotypic peptides than indicated by &apos;top&apos; (no effect if &apos;top&apos; is 0 or 1)" restrictions="true,false" />
        <ITEM name="filter_charge" value="false" type="string" description="Distinguish between charge states of a peptide. For peptides, abundances will be reported separately for each charge;#br#for proteins, abundances will be computed based only on the most prevalent charge of each peptide.#br#By default, abundances are summed over all charge states." restrictions="true,false" />
        <ITEM name="ratios" value="false" type="string" description="Prints the log2 ratios of the abundance value to the output file. (log_2(x_0/x_0) &lt;sep&gt; log_2(x_1/x_0) &lt;sep&gt; log_2(x_2/x_0) ....)" restrictions="true,false" />
        <ITEM name="ratiosSILAC" value="false" type="string" description="Prints the SILAC log2 ratios for a triple SILAC experiment to the output file. Only performed if three maps are given, otherwise nothing will be seen in the output file. (log_2(heavy/light) &lt;sep&gt; log_2(heavy/middle) &lt;sep&gt; log_2(middle/light)" restrictions="true,false" />
        <ITEM name="log" value="" type="string" description="Name of log file (created only when specified)" tags="advanced" />
        <ITEM name="debug" value="0" type="int" description="Sets the debug level" tags="advanced" />
        <ITEM name="threads" value="1" type="int" description="Sets the number of threads allowed to be used by the TOPP tool" />
        <ITEM name="no_progress" value="false" type="string" description="Disables progress logging to command line" tags="advanced" restrictions="true,false" />
        <ITEM name="test" value="false" type="string" description="Enables the test mode (needed for internal use only)" tags="advanced" restrictions="true,false" />
        <NODE name="consensus" description="Additional options for consensus maps">
          <ITEM name="normalize" value="false" type="string" description="Scale peptide abundances so that medians of all samples are equal" restrictions="true,false" />
          <ITEM name="fix_peptides" value="false" type="string" description="Use the same peptides for protein quantification across all samples.#br#With &apos;top 0&apos;, all peptides that occur in every sample are considered.#br#Otherwise (&apos;top N&apos;), the N peptides that occur in the most samples (independently of each other) are selected,#br#breaking ties by total abundance (there is no guarantee that the best co-ocurring peptides are chosen!)." restrictions="true,false" />
        </NODE>
        <NODE name="format" description="Output formatting options">
          <ITEM name="separator" value="," type="string" description="Character(s) used to separate fields; by default, the &apos;tab&apos; character is used" />
          <ITEM name="quoting" value="double" type="string" description="Method for quoting of strings: &apos;none&apos; for no quoting, &apos;double&apos; for quoting with doubling of embedded quotes,#br#&apos;escape&apos; for quoting with backslash-escaping of embedded quotes" restrictions="none,double,escape" />
          <ITEM name="replacement" value="_" type="string" description="If &apos;quoting&apos; is &apos;none&apos;, used to replace occurrences of the separator in strings before writing" />
        </NODE>
      </NODE>
    </NODE>
    <NODE name="8" description="">
      <ITEM name="recycle_output" value="false" type="string" description="" />
      <ITEM name="toppas_type" value="output file list" type="string" description="" />
      <ITEM name="x_pos" value="640" type="float" description="" />
      <ITEM name="y_pos" value="80" type="float" description="" />
    </NODE>
    <NODE name="9" description="">
      <ITEM name="recycle_output" value="false" type="string" description="" />
      <ITEM name="toppas_type" value="output file list" type="string" description="" />
      <ITEM name="x_pos" value="640" type="float" description="" />
      <ITEM name="y_pos" value="200" type="float" description="" />
    </NODE>
    <NODE name="10" description="">
      <ITEM name="recycle_output" value="false" type="string" description="" />
      <ITEM name="toppas_type" value="output file list" type="string" description="" />
      <ITEM name="x_pos" value="460" type="float" description="" />
      <ITEM name="y_pos" value="80" type="float" description="" />
    </NODE>
    <NODE name="5" description="">
      <ITEM name="recycle_output" value="false" type="string" description="" />
      <ITEM name="toppas_type" value="tool" type="string" description="" />
      <ITEM name="tool_name" value="IDFileConverter" type="string" description="" />
      <ITEM name="tool_type" value="" type="string" description="" />
      <ITEM name="x_pos" value="640" type="float" description="" />
      <ITEM name="y_pos" value="-220" type="float" description="" />
      <NODE name="parameters" description="">
        <ITEM name="in" value="" type="string" description="Input file or directory containing the output of the search engine.#br#Sequest: Directory containing the .out files#br#pepXML: Single pepXML file.#br#protXML: Single protXML file.#br#mascotXML: Single Mascot xml file.#br#omssaXML: Single OMSSA xml file.#br#idXML: Single idXML file.#br#" tags="input file,required" supported_formats="*.pepXML,*.protXML,*.mascotXML,*.omssaXML,*.idXML" />
        <ITEM name="out" value="" type="string" description="Output file" tags="output file,required" supported_formats="*.idXML,*.mzid,*.pepXML,*.FASTA" />
        <ITEM name="out_type" value="idXML" type="string" description="output file type -- default: determined from file extension or content#br#" restrictions="idXML,mzid,pepXML,FASTA" />
        <ITEM name="mz_file" value="" type="string" description="[Sequest, pepXML, mascotXML only] Retention times will be looked up in this file" />
        <ITEM name="ignore_proteins_per_peptide" value="false" type="string" description="[Sequest only] Workaround to deal with .out files that contain e.g. &quot;+1&quot; in references column,#br#but do not list extra references in subsequent lines (try -debug 3 or 4)" tags="advanced" restrictions="true,false" />
        <ITEM name="mz_name" value="" type="string" description="[pepXML, mascotXML only] Experiment filename/path to match in the pepXML file (&apos;base_name&apos; attribute). Only necessary if different from &apos;mz_file&apos;." />
        <ITEM name="use_precursor_data" value="false" type="string" description="[pepXML, mascotXML only] Use precursor RTs (and m/z values) from &apos;mz_file&apos; for the generated peptide identifications, instead of the RTs of MS2 spectra." restrictions="true,false" />
        <ITEM name="log" value="" type="string" description="Name of log file (created only when specified)" tags="advanced" />
        <ITEM name="debug" value="0" type="int" description="Sets the debug level" tags="advanced" />
        <ITEM name="threads" value="1" type="int" description="Sets the number of threads allowed to be used by the TOPP tool" />
        <ITEM name="no_progress" value="false" type="string" description="Disables progress logging to command line" tags="advanced" restrictions="true,false" />
        <ITEM name="test" value="false" type="string" description="Enables the test mode (needed for internal use only)" tags="advanced" restrictions="true,false" />
      </NODE>
    </NODE>
    <NODE name="0" description="">
      <ITEM name="recycle_output" value="false" type="string" description="" />
      <ITEM name="toppas_type" value="input file list" type="string" description="" />
      <ITEMLIST name="file_names" type="string" description="">
          <LISTITEM value="$PROTXML" />
      </ITEMLIST>
      <ITEM name="x_pos" value="640" type="float" description="" />
      <ITEM name="y_pos" value="-360" type="float" description="" />
    </NODE>
    <NODE name="1" description="">
      <ITEM name="recycle_output" value="false" type="string" description="" />
      <ITEM name="toppas_type" value="input file list" type="string" description="" />
      <ITEMLIST name="file_names" type="string" description="">
        $FEATUREXMLLIST
      </ITEMLIST>
      <ITEM name="x_pos" value="20" type="float" description="" />
      <ITEM name="y_pos" value="-60" type="float" description="" />
    </NODE>
    <NODE name="2" description="">
      <ITEM name="recycle_output" value="false" type="string" description="" />
      <ITEM name="toppas_type" value="merger" type="string" description="" />
      <ITEM name="x_pos" value="140" type="float" description="" />
      <ITEM name="y_pos" value="-60" type="float" description="" />
      <ITEM name="round_based" value="false" type="string" description="" />
    </NODE>
    <NODE name="6" description="">
      <ITEM name="recycle_output" value="false" type="string" description="" />
      <ITEM name="toppas_type" value="tool" type="string" description="" />
      <ITEM name="tool_name" value="$FEATURELINKER_EXECUTABLE" type="string" description="" />
      <ITEM name="tool_type" value="" type="string" description="" />
      <ITEM name="x_pos" value="460" type="float" description="" />
      <ITEM name="y_pos" value="-60" type="float" description="" />
      <NODE name="parameters" description="">
        <ITEMLIST name="in" type="string" description="input files separated by blanks" tags="input file,required" supported_formats="*.featureXML,*.consensusXML">
        </ITEMLIST>
        <ITEM name="out" value="" type="string" description="Output file" tags="output file,required" supported_formats="*.consensusXML" />
        <ITEM name="keep_subelements" value="false" type="string" description="For consensusXML input only: If set, the sub-features of the inputs are transferred to the output." restrictions="true,false" />
        <ITEM name="log" value="" type="string" description="Name of log file (created only when specified)" tags="advanced" />
        <ITEM name="debug" value="0" type="int" description="Sets the debug level" tags="advanced" />
        <ITEM name="threads" value="1" type="int" description="Sets the number of threads allowed to be used by the TOPP tool" />
        <ITEM name="no_progress" value="false" type="string" description="Disables progress logging to command line" tags="advanced" restrictions="true,false" />
        <ITEM name="test" value="false" type="string" description="Enables the test mode (needed for internal use only)" tags="advanced" restrictions="true,false" />
        <NODE name="algorithm" description="Algorithm parameters section">
          <ITEM name="use_identifications" value="$FEATURELINKER_USE_IDENTIFICATIONS" type="string" description="Never link features that are annotated with different peptides (only the best hit per peptide identification is taken into account)." restrictions="true,false" />
          <ITEM name="ignore_charge" value="false" type="string" description="Compare features normally even if their charge states are different" restrictions="true,false" />
          <NODE name="distance_RT" description="Distance component based on RT differences">
            <ITEM name="max_difference" value="$FEATURELINKER_DISTANCE_RT__MAX_DIFFERENCE" type="float" description="Maximum allowed difference in RT in seconds" restrictions="0:" />
            <ITEM name="exponent" value="1" type="float" description="Normalized RT differences are raised to this power (using 1 or 2 will be fast, everything else is REALLY slow)" tags="advanced" restrictions="0:" />
            <ITEM name="weight" value="1" type="float" description="RT distances are weighted by this factor" tags="advanced" restrictions="0:" />
          </NODE>
          <NODE name="distance_MZ" description="Distance component based on m/z differences">
            <ITEM name="max_difference" value="$FEATURELINKER_DISTANCE_MZ__MAX_DIFFERENCE" type="float" description="Maximum allowed difference in m/z (unit defined by &apos;unit&apos;)" restrictions="0:" />
            <ITEM name="unit" value="$FEATURELINKER_DISTANCE_MZ__UNIT" type="string" description="Unit of the &apos;max_difference&apos; parameter" restrictions="Da,ppm" />
            <ITEM name="exponent" value="2" type="float" description="Normalized m/z differences are raised to this power (using 1 or 2 will be fast, everything else is REALLY slow)" tags="advanced" restrictions="0:" />
            <ITEM name="weight" value="1" type="float" description="m/z distances are weighted by this factor" tags="advanced" restrictions="0:" />
          </NODE>
          <NODE name="distance_intensity" description="Distance component based on differences in relative intensity">
            <ITEM name="exponent" value="1" type="float" description="Differences in relative intensity are raised to this power (using 1 or 2 will be fast, everything else is REALLY slow)" tags="advanced" restrictions="0:" />
            <ITEM name="weight" value="0" type="float" description="Distances based on relative intensity are weighted by this factor" tags="advanced" restrictions="0:" />
          </NODE>
        </NODE>
      </NODE>
    </NODE>
  </NODE>
  <NODE name="edges" description="">
    <NODE name="0" description="">
      <NODE name="source/target" description="">
        <ITEM name="" value="3/4" type="string" description="" />
      </NODE>
      <NODE name="source_out_param" description="">
        <ITEM name="" value="trafo_out" type="string" description="" />
      </NODE>
      <NODE name="target_in_param" description="">
        <ITEM name="" value="__no_name__" type="string" description="" />
      </NODE>
    </NODE>
    <NODE name="1" description="">
      <NODE name="source/target" description="">
        <ITEM name="" value="7/8" type="string" description="" />
      </NODE>
      <NODE name="source_out_param" description="">
        <ITEM name="" value="out" type="string" description="" />
      </NODE>
      <NODE name="target_in_param" description="">
        <ITEM name="" value="__no_name__" type="string" description="" />
      </NODE>
    </NODE>
    <NODE name="2" description="">
      <NODE name="source/target" description="">
        <ITEM name="" value="7/9" type="string" description="" />
      </NODE>
      <NODE name="source_out_param" description="">
        <ITEM name="" value="peptide_out" type="string" description="" />
      </NODE>
      <NODE name="target_in_param" description="">
        <ITEM name="" value="__no_name__" type="string" description="" />
      </NODE>
    </NODE>
    <NODE name="3" description="">
      <NODE name="source/target" description="">
        <ITEM name="" value="5/7" type="string" description="" />
      </NODE>
      <NODE name="source_out_param" description="">
        <ITEM name="" value="out" type="string" description="" />
      </NODE>
      <NODE name="target_in_param" description="">
        <ITEM name="" value="protxml" type="string" description="" />
      </NODE>
    </NODE>
    <NODE name="4" description="">
      <NODE name="source/target" description="">
        <ITEM name="" value="0/5" type="string" description="" />
      </NODE>
      <NODE name="source_out_param" description="">
        <ITEM name="" value="__no_name__" type="string" description="" />
      </NODE>
      <NODE name="target_in_param" description="">
        <ITEM name="" value="in" type="string" description="" />
      </NODE>
    </NODE>
    <NODE name="5" description="">
      <NODE name="source/target" description="">
        <ITEM name="" value="1/2" type="string" description="" />
      </NODE>
      <NODE name="source_out_param" description="">
        <ITEM name="" value="__no_name__" type="string" description="" />
      </NODE>
      <NODE name="target_in_param" description="">
        <ITEM name="" value="__no_name__" type="string" description="" />
      </NODE>
    </NODE>
    <NODE name="6" description="">
      <NODE name="source/target" description="">
        <ITEM name="" value="2/3" type="string" description="" />
      </NODE>
      <NODE name="source_out_param" description="">
        <ITEM name="" value="__no_name__" type="string" description="" />
      </NODE>
      <NODE name="target_in_param" description="">
        <ITEM name="" value="in" type="string" description="" />
      </NODE>
    </NODE>
    <NODE name="7" description="">
      <NODE name="source/target" description="">
        <ITEM name="" value="3/6" type="string" description="" />
      </NODE>
      <NODE name="source_out_param" description="">
        <ITEM name="" value="out" type="string" description="" />
      </NODE>
      <NODE name="target_in_param" description="">
        <ITEM name="" value="in" type="string" description="" />
      </NODE>
    </NODE>
    <NODE name="8" description="">
      <NODE name="source/target" description="">
        <ITEM name="" value="6/7" type="string" description="" />
      </NODE>
      <NODE name="source_out_param" description="">
        <ITEM name="" value="out" type="string" description="" />
      </NODE>
      <NODE name="target_in_param" description="">
        <ITEM name="" value="in" type="string" description="" />
      </NODE>
    </NODE>
    <NODE name="9" description="">
      <NODE name="source/target" description="">
        <ITEM name="" value="6/10" type="string" description="" />
      </NODE>
      <NODE name="source_out_param" description="">
        <ITEM name="" value="out" type="string" description="" />
      </NODE>
      <NODE name="target_in_param" description="">
        <ITEM name="" value="__no_name__" type="string" description="" />
      </NODE>
    </NODE>
  </NODE>
</PARAMETERS>
""" 
        log.debug('read template from [%s]' % self.__class__.__name__)
        return template,info
