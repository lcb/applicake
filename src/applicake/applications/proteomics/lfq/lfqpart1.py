"""
Created on Jun 18, 2012

@author: loblum
"""

import os
from applicake.framework.keys import Keys
from applicake.framework.interfaces import IWrapper
from applicake.framework.templatehandler import BasicTemplateHandler
from applicake.utils.fileutils import FileUtils
from applicake.utils.xmlutils import XmlValidator
from applicake.applications.proteomics.tpp.proteinprophetFDR import ProteinProphetFDR


class LFQpart1(IWrapper):
    def prepare_run(self, info, log):

        wd = info[Keys.WORKDIR]
        #get iProb corresponding FDR for IDFilter
        info[Keys.IPROBABILITY] = ProteinProphetFDR().getiProbability(log, info)

        #required because openbis requires prot.xml and openms protXML
        peplink = os.path.join(wd, 'iprophet.pepXML')
        os.symlink(info['PEPXMLS'], peplink)
        info['PEPXMLS'] = peplink
        info['MZNAME'] = os.path.splitext(os.path.basename(info[Keys.MZXML]))[0]

        info["TOPPASFILES"] = info[Keys.TEMPLATE] = os.path.join(wd, 'LFQpart1.toppas')
        th = LFQpart1WorkflowTemplate()
        mod_template, info = th.modify_template(info, log)
        rawfeatxml = os.path.join(wd, 'TOPPAS_out/012-IDConflictResolver/*.featureXML')
        info['FEATUREXMLS'] = os.path.join(wd, os.path.splitext(os.path.basename(info[Keys.MZXML]))[0] + '.featureXML')
        self._result_file = info['FEATUREXMLS']
        
        command = 'ExecutePipeline -in %s -out_dir %s && mv -v %s %s' % (
        info[Keys.TEMPLATE], wd, rawfeatxml, self._result_file)
        return command, info

    def set_args(self, log, args_handler):
        """
        See interface
        """
        args_handler.add_app_args(log, Keys.WORKDIR, 'wd')
        args_handler.add_app_args(log, 'MZXML', 'Path to the mzXML file.')
        args_handler.add_app_args(log, 'PEPXMLS', 'Path to the pepXML file.')
        args_handler.add_app_args(log, Keys.PEPTIDEFDR, 'Peptide FDR cutoff to use')

        args_handler.add_app_args(log, "PEAKPICKER_SIGNAL_TO_NOISE", "")
        args_handler.add_app_args(log, "PEAKPICKER_MS1_ONLY", "")
        args_handler.add_app_args(log, "FEATUREFINDER_MASS_TRACE__MZ_TOLERANCE", "")
        args_handler.add_app_args(log, "FEATUREFINDER_MASS_TRACE__MIN_SPECTRA", "")
        args_handler.add_app_args(log, "FEATUREFINDER_MASS_TRACE__MAX_MISSING", "")
        args_handler.add_app_args(log, "FEATUREFINDER_ISOTOPIC_PATTERN__CHARGE_LOW", "")
        args_handler.add_app_args(log, "FEATUREFINDER_ISOTOPIC_PATTERN__CHARGE_HIGH", "")
        args_handler.add_app_args(log, "FEATUREFINDER_ISOTOPIC_PATTERN__MZ_TOLERANCE", "")
        args_handler.add_app_args(log, "FEATUREFINDER_FEATURE__MIN_SCORE", "")
        args_handler.add_app_args(log, "FEATUREFINDER_FEATURE__MIN_ISOTOPE_FIT", "")
        args_handler.add_app_args(log, "FEATUREFINDER_FEATURE__MIN_TRACE_SCORE", "")
        args_handler.add_app_args(log, "FEATUREFINDER_SEED__MIN_SCORE", "")
        args_handler.add_app_args(log, "FEATUREFINDER_MASS_TRACE__SLOPE_BOUND", "")
        args_handler.add_app_args(log, "IDMAPPER_RT_TOLERANCE", "")
        args_handler.add_app_args(log, "IDMAPPER_MZ_TOLERANCE", "")
        args_handler.add_app_args(log, "IDMAPPER_MZ_REFERENCE", "")
        args_handler.add_app_args(log, "IDMAPPER_USE_CENTROID_MZ", "")
        return args_handler

    def validate_run(self, info, log, run_code, out_stream, err_stream):
        if 0 != run_code:
            return run_code, info
        if not FileUtils.is_valid_file(log, self._result_file):
            log.critical('[%s] is not valid' % self._result_file)
            return 1, info
        if not XmlValidator.is_wellformed(self._result_file):
            log.critical('[%s] is not well formed.' % self._result_file)
            return 1, info
        return run_code, info


class LFQpart1WorkflowTemplate(BasicTemplateHandler):
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
    <ITEM name="num_vertices" value="12" type="int" description="" />
    <ITEM name="num_edges" value="11" type="int" description="" />
    <ITEM name="description" value="&lt;![CDATA[]]&gt;" type="string" description="" />
  </NODE>
  <NODE name="vertices" description="">
    <NODE name="0" description="">
      <ITEM name="recycle_output" value="false" type="string" description="" />
      <ITEM name="toppas_type" value="input file list" type="string" description="" />
      <ITEMLIST name="file_names" type="string" description="">
        <LISTITEM value="$MZXML"/>
      </ITEMLIST>
      <ITEM name="x_pos" value="-520" type="float" description="" />
      <ITEM name="y_pos" value="-440" type="float" description="" />
    </NODE>
    <NODE name="1" description="">
      <ITEM name="recycle_output" value="false" type="string" description="" />
      <ITEM name="toppas_type" value="input file list" type="string" description="" />
      <ITEMLIST name="file_names" type="string" description="">
        <LISTITEM value="$PEPXMLS"/>
      </ITEMLIST>
      <ITEM name="x_pos" value="0" type="float" description="" />
      <ITEM name="y_pos" value="-400" type="float" description="" />
    </NODE>
    <NODE name="5" description="">
      <ITEM name="recycle_output" value="false" type="string" description="" />
      <ITEM name="toppas_type" value="tool" type="string" description="" />
      <ITEM name="tool_name" value="IDFilter" type="string" description="" />
      <ITEM name="tool_type" value="" type="string" description="" />
      <ITEM name="x_pos" value="-180" type="float" description="" />
      <ITEM name="y_pos" value="-220" type="float" description="" />
      <NODE name="parameters" description="">
        <ITEM name="in" value="" type="string" description="input file " tags="input file,required" supported_formats="*.idXML" />
        <ITEM name="out" value="" type="string" description="output file " tags="output file,required" supported_formats="*.idXML" />
        <ITEM name="min_length" value="0" type="int" description="Keep only peptide hits with a length greater or equal this value. Value 0 will have no filter effect." restrictions="0:" />
        <ITEM name="max_length" value="0" type="int" description="Keep only peptide hits with a length less or equal this value. Value 0 will have no filter effect. Value is overridden by min_length, i.e. if max_length &lt; min_length, max_length will be ignored." restrictions=":0" />
        <ITEM name="min_charge" value="1" type="int" description="Keep only peptide hits for tandem spectra with charge greater or equal this value." restrictions="1:" />
        <ITEM name="var_mods" value="false" type="string" description="Keep only peptide hits with variable modifications (fixed modifications from SearchParameters will be ignored)." restrictions="true,false" />
        <ITEM name="unique" value="false" type="string" description="If a peptide hit occurs more than once, only one instance is kept. This will (for instance) remove redundant identifications from multiple charge states or concurrent CID+HCD spectra.If you are aiming towards quantitation, you probably do *not* want to use this flag!" restrictions="true,false" />
        <ITEM name="unique_per_protein" value="false" type="string" description="Only peptides matching exactly one protein are kept. Remember that isoforms count as different proteins!" restrictions="true,false" />
        <ITEM name="keep_unreferenced_protein_hits" value="false" type="string" description="Proteins not referenced by a peptide are retained in the idXML." restrictions="true,false" />
        <ITEM name="log" value="" type="string" description="Name of log file (created only when specified)" tags="advanced" />
        <ITEM name="debug" value="0" type="int" description="Sets the debug level" tags="advanced" />
        <ITEM name="threads" value="1" type="int" description="Sets the number of threads allowed to be used by the TOPP tool" />
        <ITEM name="no_progress" value="false" type="string" description="Disables progress logging to command line" tags="advanced" restrictions="true,false" />
        <ITEM name="test" value="false" type="string" description="Enables the test mode (needed for internal use only)" tags="advanced" restrictions="true,false" />
        <NODE name="score" description="Filtering by peptide/protein score. To enable any of the filters below, just change their default value. All active filters will be applied in order.">
          <ITEM name="pep" value="$IPROBABILITY" type="float" description="The score which should be reached by a peptide hit to be kept. The score is dependent on the most recent(!) preprocessing - it could be Mascot scores (if a MascotAdapter was applied before), or an FDR (if FalseDiscoveryRate was applied before), etc." />
          <ITEM name="prot" value="0" type="float" description="The score which should be reached by a protein hit to be kept." />
        </NODE>
        <NODE name="thresh" description="Filtering by significance threshold">
          <ITEM name="pep" value="0" type="float" description="Keep a peptide hit only if its score is above this fraction of the peptide significance threshold." />
          <ITEM name="prot" value="0" type="float" description="Keep a protein hit only if its score is above this fraction of the protein significance threshold." />
        </NODE>
        <NODE name="whitelist" description="Filtering by whitelisting (only instances also present in a whitelist file can pass)">
          <ITEM name="proteins" value="" type="string" description="filename of a FASTA file containing protein sequences.#br#All peptides that are not a substring of a sequence in this file are removed#br#All proteins whose accession is not present in this file are removed." tags="input file" supported_formats="*.fasta" />
          <ITEM name="by_seq_only" value="false" type="string" description="Match peptides with FASTA file by sequence instead of accession and disable protein filtering." restrictions="true,false" />
        </NODE>
        <NODE name="blacklist" description="Filtering by blacklisting (only instances not present in a blacklist file can pass)">
          <ITEM name="peptides" value="" type="string" description="Peptides having the same sequence as any peptide in this file will be filtered out#br#" tags="input file" supported_formats="*.idXML" />
        </NODE>
        <NODE name="rt" description="Filtering by RT predicted by &apos;RTPredict&apos;">
          <ITEM name="p_value" value="0" type="float" description="Retention time filtering by the p-value predicted by RTPredict." restrictions="0:1" />
          <ITEM name="p_value_1st_dim" value="0" type="float" description="Retention time filtering by the p-value predicted by RTPredict for first dimension." restrictions="0:1" />
        </NODE>
        <NODE name="mz" description="Filtering by mz">
          <ITEM name="error" value="-1" type="float" description="Filtering by deviation to theoretical mass (disabled for negative values)." />
          <ITEM name="unit" value="ppm" type="string" description="Absolute or relativ error." restrictions="Da,ppm" />
        </NODE>
        <NODE name="best" description="Filtering best hits per spectrum (for peptides) or from proteins">
          <ITEM name="n_peptide_hits" value="0" type="int" description="Keep only the &apos;n&apos; highest scoring peptide hits per spectrum (for n&gt;0)." restrictions="0:" />
          <ITEM name="n_protein_hits" value="0" type="int" description="Keep only the &apos;n&apos; highest scoring protein hits (for n&gt;0)." restrictions="0:" />
          <ITEM name="strict" value="true" type="string" description="Keep only the highest scoring peptide hit.#br#Similar to n_peptide_hits=1, but if there are two or more highest scoring hits, none are kept." restrictions="true,false" />
          <ITEM name="n_to_m_peptide_hits" value=":" type="string" description="peptide hit rank range to extracts" tags="advanced" />
        </NODE>
      </NODE>
    </NODE>
    <NODE name="6" description="">
      <ITEM name="recycle_output" value="false" type="string" description="" />
      <ITEM name="toppas_type" value="tool" type="string" description="" />
      <ITEM name="tool_name" value="PeakPickerHiRes" type="string" description="" />
      <ITEM name="tool_type" value="" type="string" description="" />
      <ITEM name="x_pos" value="-540" type="float" description="" />
      <ITEM name="y_pos" value="-60" type="float" description="" />
      <NODE name="parameters" description="">
        <ITEM name="in" value="" type="string" description="input profile data file " tags="input file,required" supported_formats="*.mzML" />
        <ITEM name="out" value="" type="string" description="output peak file " tags="output file,required" supported_formats="*.mzML" />
        <ITEM name="log" value="" type="string" description="Name of log file (created only when specified)" tags="advanced" />
        <ITEM name="debug" value="0" type="int" description="Sets the debug level" tags="advanced" />
        <ITEM name="threads" value="1" type="int" description="Sets the number of threads allowed to be used by the TOPP tool" />
        <ITEM name="no_progress" value="false" type="string" description="Disables progress logging to command line" tags="advanced" restrictions="true,false" />
        <ITEM name="test" value="false" type="string" description="Enables the test mode (needed for internal use only)" tags="advanced" restrictions="true,false" />
        <NODE name="algorithm" description="Algorithm parameters section">
          <ITEM name="signal_to_noise" value="$PEAKPICKER_SIGNAL_TO_NOISE" type="float" description="Minimal signal-to-noise ratio for a peak to be picked (0.0 disables SNT estimation!)" restrictions="0:" />
          <ITEM name="ms1_only" value="$PEAKPICKER_MS1_ONLY" type="string" description="If true, peak picking is only applied to MS1 scans. Other scans are copied to the output without changes." restrictions="true,false" />
        </NODE>
      </NODE>
    </NODE>
    <NODE name="2" description="">
      <ITEM name="recycle_output" value="false" type="string" description="" />
      <ITEM name="toppas_type" value="tool" type="string" description="" />
      <ITEM name="tool_name" value="FileConverter" type="string" description="" />
      <ITEM name="tool_type" value="" type="string" description="" />
      <ITEM name="x_pos" value="-520" type="float" description="" />
      <ITEM name="y_pos" value="-220" type="float" description="" />
      <NODE name="parameters" description="">
        <ITEM name="in" value="" type="string" description="input file " tags="input file,required" supported_formats="*.mzData,*.mzXML,*.mzML,*.dta,*.dta2d,*.mgf,*.featureXML,*.consensusXML,*.ms2,*.fid,*.tsv,*.peplist,*.kroenik,*.edta" />
        <ITEM name="in_type" value="" type="string" description="input file type -- default: determined from file extension or content#br#" restrictions="mzData,mzXML,mzML,dta,dta2d,mgf,featureXML,consensusXML,ms2,fid,tsv,peplist,kroenik,edta" />
        <ITEM name="out" value="" type="string" description="output file " tags="output file,required" supported_formats="*.mzData,*.mzXML,*.mzML,*.dta2d,*.mgf,*.featureXML,*.consensusXML,*.edta" />
        <ITEM name="out_type" value="mzML" type="string" description="output file type -- default: determined from file extension or content#br#" restrictions="mzData,mzXML,mzML,dta2d,mgf,featureXML,consensusXML,edta" />
        <ITEM name="TIC_DTA2D" value="false" type="string" description="Export the TIC instead of the entire experiment in mzML/mzData/mzXML -&gt; DTA2D conversions." tags="advanced" restrictions="true,false" />
        <ITEM name="log" value="" type="string" description="Name of log file (created only when specified)" tags="advanced" />
        <ITEM name="debug" value="0" type="int" description="Sets the debug level" tags="advanced" />
        <ITEM name="threads" value="1" type="int" description="Sets the number of threads allowed to be used by the TOPP tool" />
        <ITEM name="no_progress" value="false" type="string" description="Disables progress logging to command line" tags="advanced" restrictions="true,false" />
        <ITEM name="test" value="false" type="string" description="Enables the test mode (needed for internal use only)" tags="advanced" restrictions="true,false" />
      </NODE>
    </NODE>
    <NODE name="7" description="">
      <ITEM name="recycle_output" value="false" type="string" description="" />
      <ITEM name="toppas_type" value="tool" type="string" description="" />
      <ITEM name="tool_name" value="FeatureFinderCentroided" type="string" description="" />
      <ITEM name="tool_type" value="" type="string" description="" />
      <ITEM name="x_pos" value="-360" type="float" description="" />
      <ITEM name="y_pos" value="-60" type="float" description="" />
      <NODE name="parameters" description="">
        <ITEM name="in" value="" type="string" description="input file" tags="input file,required" supported_formats="*.mzML" />
        <ITEM name="out" value="" type="string" description="output file" tags="output file,required" supported_formats="*.featureXML" />
        <ITEM name="seeds" value="" type="string" description="User specified seed list" tags="input file" supported_formats="*.featureXML" />
        <ITEM name="log" value="" type="string" description="Name of log file (created only when specified)" tags="advanced" />
        <ITEM name="debug" value="0" type="int" description="Sets the debug level" tags="advanced" />
        <ITEM name="threads" value="1" type="int" description="Sets the number of threads allowed to be used by the TOPP tool" />
        <ITEM name="no_progress" value="false" type="string" description="Disables progress logging to command line" tags="advanced" restrictions="true,false" />
        <ITEM name="test" value="false" type="string" description="Enables the test mode (needed for internal use only)" tags="advanced" restrictions="true,false" />
        <NODE name="algorithm" description="Algorithm section">
          <ITEM name="debug" value="false" type="string" description="When debug mode is activated, several files with intermediate results are written to the folder &apos;debug&apos; (do not use in parallel mode)." restrictions="true,false" />
          <NODE name="intensity" description="Settings for the calculation of a score indicating if a peak&apos;s intensity is significant in the local environment (between 0 and 1)">
            <ITEM name="bins" value="10" type="int" description="Number of bins per dimension (RT and m/z). The higher this value, the more local the intensity significance score is.#br#This parameter should be decreased, if the algorithm is used on small regions of a map." restrictions="1:" />
          </NODE>
          <NODE name="mass_trace" description="Settings for the calculation of a score indicating if a peak is part of a mass trace (between 0 and 1).">
            <ITEM name="mz_tolerance" value="$FEATUREFINDER_MASS_TRACE__MZ_TOLERANCE" type="float" description="Tolerated m/z deviation of peaks belonging to the same mass trace.#br#It should be larger than the m/z resolution of the instument.#br#This value must be smaller than that 1/charge_high!" restrictions="0:" />
            <ITEM name="min_spectra" value="$FEATUREFINDER_MASS_TRACE__MIN_SPECTRA" type="int" description="Number of spectra that have to show a similar peak mass in a mass trace." restrictions="1:" />
            <ITEM name="max_missing" value="$FEATUREFINDER_MASS_TRACE__MAX_MISSING" type="int" description="Number of consecutive spectra where a high mass deviation or missing peak is acceptable.#br#This parameter should be well below &apos;min_spectra&apos;!" restrictions="0:" />
            <ITEM name="slope_bound" value="1" type="float" description="The maximum slope of mass trace intensities when extending from the highest peak.#br#This parameter is important to seperate overlapping elution peaks.#br#It should be increased if feature elution profiles fluctuate a lot." restrictions="0:" />
          </NODE>
          <NODE name="isotopic_pattern" description="Settings for the calculation of a score indicating if a peak is part of a isotopic pattern (between 0 and 1).">
            <ITEM name="charge_low" value="$FEATUREFINDER_ISOTOPIC_PATTERN__CHARGE_LOW" type="int" description="Lowest charge to search for." restrictions="1:" />
            <ITEM name="charge_high" value="$FEATUREFINDER_ISOTOPIC_PATTERN__CHARGE_HIGH" type="int" description="Highest charge to search for." restrictions="1:" />
            <ITEM name="mz_tolerance" value="$FEATUREFINDER_ISOTOPIC_PATTERN__MZ_TOLERANCE" type="float" description="Tolerated m/z deviation from the theoretical isotopic pattern.#br#It should be larger than the m/z resolution of the instument.#br#This value must be smaller than that 1/charge_high!" restrictions="0:" />
            <ITEM name="intensity_percentage" value="10" type="float" description="Isotopic peaks that contribute more than this percentage to the overall isotope pattern intensity must be present." tags="advanced" restrictions="0:100" />
            <ITEM name="intensity_percentage_optional" value="0.1" type="float" description="Isotopic peaks that contribute more than this percentage to the overall isotope pattern intensity can be missing." tags="advanced" restrictions="0:100" />
            <ITEM name="optional_fit_improvement" value="2" type="float" description="Minimal percental improvement of isotope fit to allow leaving out an optional peak." tags="advanced" restrictions="0:100" />
            <ITEM name="mass_window_width" value="25" type="float" description="Window width in Dalton for precalculation of estimated isotope distributions." tags="advanced" restrictions="1:200" />
            <ITEM name="abundance_12C" value="98.93" type="float" description="Rel. abundance of the light carbon. Modify if labeled." tags="advanced" restrictions="0:100" />
            <ITEM name="abundance_14N" value="99.632" type="float" description="Rel. abundance of the light nitrogen. Modify if labeled." tags="advanced" restrictions="0:100" />
          </NODE>
          <NODE name="seed" description="Settings that determine which peaks are considered a seed">
            <ITEM name="min_score" value="$FEATUREFINDER_SEED__MIN_SCORE" type="float" description="Minimum seed score a peak has to reach to be used as seed.#br#The seed score is the geometric mean of intensity score, mass trace score and isotope pattern score.#br#If your features show a large deviation from the averagene isotope distribution or from an gaussian elution profile, lower this score." restrictions="0:1" />
          </NODE>
          <NODE name="fit" description="Settings for the model fitting">
            <ITEM name="epsilon_abs" value="0.0001" type="float" description="Absolute epsilon used for convergence of the fit." tags="advanced" restrictions="0:" />
            <ITEM name="epsilon_rel" value="0.0001" type="float" description="Relative epsilon used for convergence of the fit." tags="advanced" restrictions="0:" />
            <ITEM name="max_iterations" value="500" type="int" description="Maximum number of iterations of the fit." tags="advanced" restrictions="1:" />
          </NODE>
          <NODE name="feature" description="Settings for the features (intensity, quality assessment, ...)">
            <ITEM name="min_score" value="$FEATUREFINDER_FEATURE__MIN_SCORE" type="float" description="Feature score threshold for a feature to be reported.#br#The feature score is the geometric mean of the average relative deviation and the correlation between the model and the observed peaks." restrictions="0:1" />
            <ITEM name="min_isotope_fit" value="$FEATUREFINDER_FEATURE__MIN_ISOTOPE_FIT" type="float" description="Minimum isotope fit of the feature before model fitting." tags="advanced" restrictions="0:1" />
            <ITEM name="min_trace_score" value="$FEATUREFINDER_FEATURE__MIN_TRACE_SCORE" type="float" description="Trace score threshold.#br#Traces below this threshold are removed after the model fitting.#br#This parameter is important for features that overlap in m/z dimension." tags="advanced" restrictions="0:1" />
            <ITEM name="min_rt_span" value="0.333" type="float" description="Minimum RT span in relation to extended area that has to remain after model fitting." tags="advanced" restrictions="0:1" />
            <ITEM name="max_rt_span" value="2.5" type="float" description="Maximum RT span in relation to extended area that the model is allowed to have." tags="advanced" restrictions="0.5:" />
            <ITEM name="rt_shape" value="symmetric" type="string" description="Choose model used for RT profile fitting. If set to symmetric a gauss shape is used, in case of asymmetric an EGH shape is used." tags="advanced" restrictions="symmetric,asymmetric" />
            <ITEM name="max_intersection" value="0.35" type="float" description="Maximum allowed intersection of features." tags="advanced" restrictions="0:1" />
            <ITEM name="reported_mz" value="monoisotopic" type="string" description="The mass type that is reported for features.#br#&apos;maximum&apos; returns the m/z value of the highest mass trace.#br#&apos;average&apos; returns the intensity-weighted average m/z value of all contained peaks.#br#&apos;monoisotopic&apos; returns the monoisotopic m/z value derived from the fitted isotope model." restrictions="maximum,average,monoisotopic" />
          </NODE>
          <NODE name="user-seed" description="Settings for user-specified seeds.">
            <ITEM name="rt_tolerance" value="30" type="float" description="Allowed RT deviation of seeds from the user-specified seed position." restrictions="0:" />
            <ITEM name="mz_tolerance" value="0.1" type="float" description="Allowed m/z deviation of seeds from the user-specified seed position." restrictions="0:" />
            <ITEM name="min_score" value="0.5" type="float" description="Overwrites &apos;seed:min_score&apos; for user-specified seeds. The cutoff is typically a bit lower in this case." restrictions="0:1" />
          </NODE>
          <NODE name="debug" description="">
            <ITEM name="pseudo_rt_shift" value="500" type="float" description="Pseudo RT shift used when ." tags="advanced" restrictions="1:" />
          </NODE>
        </NODE>
      </NODE>
    </NODE>
    <NODE name="8" description="">
      <ITEM name="recycle_output" value="false" type="string" description="" />
      <ITEM name="toppas_type" value="tool" type="string" description="" />
      <ITEM name="tool_name" value="IDMapper" type="string" description="" />
      <ITEM name="tool_type" value="" type="string" description="" />
      <ITEM name="x_pos" value="-180" type="float" description="" />
      <ITEM name="y_pos" value="-60" type="float" description="" />
      <NODE name="parameters" description="">
        <ITEM name="id" value="" type="string" description="Protein/peptide identifications file" tags="input file,required" supported_formats="*.idXML" />
        <ITEM name="in" value="" type="string" description="Feature map/consensus map file" tags="input file,required" supported_formats="*.featureXML,*.consensusXML,*.mzq" />
        <ITEM name="out" value="" type="string" description="Output file (the format depends on the input file format)." tags="output file,required" supported_formats="*.featureXML,*.consensusXML,*.mzq" />
        <ITEM name="rt_tolerance" value="$IDMAPPER_RT_TOLERANCE" type="float" description="RT tolerance (in seconds) for the matching of peptide identifications and (consensus) features.#br#Tolerance is understood as &apos;plus or minus x&apos;, so the matching range increases by twice the given value." restrictions="0:" />
        <ITEM name="mz_tolerance" value="$IDMAPPER_MZ_TOLERANCE" type="float" description="m/z tolerance (in ppm or Da) for the matching of peptide identifications and (consensus) features.#br#Tolerance is understood as &apos;plus or minus x&apos;, so the matching range increases by twice the given value." restrictions="0:" />
        <ITEM name="mz_measure" value="ppm" type="string" description="Unit of &apos;mz_tolerance&apos;." restrictions="ppm,Da" />
        <ITEM name="mz_reference" value="$IDMAPPER_MZ_REFERENCE" type="string" description="Source of m/z values for peptide identifications. If &apos;precursor&apos;, the precursor-m/z from the idXML is used. If &apos;peptide&apos;,#br#masses are computed from the sequences of peptide hits; in this case, an identification matches if any of its hits matches.#br#(&apos;peptide&apos; should be used together with &apos;feature:use_centroid_mz&apos; to avoid false-positive matches.)" restrictions="precursor,peptide" />
        <ITEM name="ignore_charge" value="false" type="string" description="For feature/consensus maps: Assign an ID independently of whether its charge state matches that of the (consensus) feature." restrictions="true,false" />
        <ITEM name="log" value="" type="string" description="Name of log file (created only when specified)" tags="advanced" />
        <ITEM name="debug" value="0" type="int" description="Sets the debug level" tags="advanced" />
        <ITEM name="threads" value="1" type="int" description="Sets the number of threads allowed to be used by the TOPP tool" />
        <ITEM name="no_progress" value="false" type="string" description="Disables progress logging to command line" tags="advanced" restrictions="true,false" />
        <ITEM name="test" value="false" type="string" description="Enables the test mode (needed for internal use only)" tags="advanced" restrictions="true,false" />
        <NODE name="feature" description="Additional options for featureXML input">
          <ITEM name="use_centroid_rt" value="false" type="string" description="Use the RT coordinates of the feature centroids for matching, instead of the RT ranges of the features/mass traces." restrictions="true,false" />
          <ITEM name="use_centroid_mz" value="$IDMAPPER_USE_CENTROID_MZ" type="string" description="Use the m/z coordinates of the feature centroids for matching, instead of the m/z ranges of the features/mass traces.#br#(If you choose &apos;peptide&apos; as &apos;mz_reference&apos;, you should usually set this flag to avoid false-positive matches.)" restrictions="true,false" />
        </NODE>
        <NODE name="consensusfeature" description="Additional options for consensusXML input">
          <ITEM name="use_subelements" value="false" type="string" description="Match using RT and m/z of sub-features instead of consensus RT and m/z. A consensus feature matches if any of its sub-features matches." restrictions="true,false" />
        </NODE>
      </NODE>
    </NODE>
    <NODE name="9" description="">
      <ITEM name="recycle_output" value="false" type="string" description="" />
      <ITEM name="toppas_type" value="output file list" type="string" description="" />
      <ITEM name="x_pos" value="-180" type="float" description="" />
      <ITEM name="y_pos" value="80" type="float" description="" />
    </NODE>
    <NODE name="10" description="">
      <ITEM name="recycle_output" value="false" type="string" description="" />
      <ITEM name="toppas_type" value="tool" type="string" description="" />
      <ITEM name="tool_name" value="IDConflictResolver" type="string" description="" />
      <ITEM name="tool_type" value="" type="string" description="" />
      <ITEM name="x_pos" value="0" type="float" description="" />
      <ITEM name="y_pos" value="-60" type="float" description="" />
      <NODE name="parameters" description="">
        <ITEM name="in" value="" type="string" description="Input file (data annotated with identifications)" tags="input file,required" supported_formats="*.featureXML,*.consensusXML" />
        <ITEM name="out" value="" type="string" description="Output file (data with one peptide identification per feature)" tags="output file,required" supported_formats="*.featureXML,*.consensusXML" />
        <ITEM name="log" value="" type="string" description="Name of log file (created only when specified)" tags="advanced" />
        <ITEM name="debug" value="0" type="int" description="Sets the debug level" tags="advanced" />
        <ITEM name="threads" value="1" type="int" description="Sets the number of threads allowed to be used by the TOPP tool" />
        <ITEM name="no_progress" value="false" type="string" description="Disables progress logging to command line" tags="advanced" restrictions="true,false" />
        <ITEM name="test" value="false" type="string" description="Enables the test mode (needed for internal use only)" tags="advanced" restrictions="true,false" />
      </NODE>
    </NODE>
    <NODE name="3" description="">
      <ITEM name="recycle_output" value="false" type="string" description="" />
      <ITEM name="toppas_type" value="tool" type="string" description="" />
      <ITEM name="tool_name" value="IDFileConverter" type="string" description="" />
      <ITEM name="tool_type" value="" type="string" description="" />
      <ITEM name="x_pos" value="0" type="float" description="" />
      <ITEM name="y_pos" value="-220" type="float" description="" />
      <NODE name="parameters" description="">
        <ITEM name="in" value="" type="string" description="Input file or directory containing the output of the search engine.#br#Sequest: Directory containing the .out files#br#pepXML: Single pepXML file.#br#protXML: Single protXML file.#br#mascotXML: Single Mascot xml file.#br#omssaXML: Single OMSSA xml file.#br#idXML: Single idXML file.#br#" tags="input file,required" supported_formats="*.pepXML,*.protXML,*.mascotXML,*.omssaXML,*.idXML" />
        <ITEM name="out" value="" type="string" description="Output file" tags="output file,required" supported_formats="*.idXML,*.mzid,*.pepXML,*.FASTA" />
        <ITEM name="out_type" value="idXML" type="string" description="output file type -- default: determined from file extension or content#br#" restrictions="idXML,mzid,pepXML,FASTA" />
        <ITEM name="mz_file" value="$MZXML" type="string" description="[Sequest, pepXML, mascotXML only] Retention times will be looked up in this file" />
        <ITEM name="ignore_proteins_per_peptide" value="false" type="string" description="[Sequest only] Workaround to deal with .out files that contain e.g. &quot;+1&quot; in references column,#br#but do not list extra references in subsequent lines (try -debug 3 or 4)" tags="advanced" restrictions="true,false" />
        <ITEM name="mz_name" value="$MZNAME" type="string" description="[pepXML, mascotXML only] Experiment filename/path to match in the pepXML file (&apos;base_name&apos; attribute). Only necessary if different from &apos;mz_file&apos;." />
        <ITEM name="use_precursor_data" value="false" type="string" description="[pepXML, mascotXML only] Use precursor RTs (and m/z values) from &apos;mz_file&apos; for the generated peptide identifications, instead of the RTs of MS2 spectra." restrictions="true,false" />
        <ITEM name="log" value="" type="string" description="Name of log file (created only when specified)" tags="advanced" />
        <ITEM name="debug" value="0" type="int" description="Sets the debug level" tags="advanced" />
        <ITEM name="threads" value="1" type="int" description="Sets the number of threads allowed to be used by the TOPP tool" />
        <ITEM name="no_progress" value="false" type="string" description="Disables progress logging to command line" tags="advanced" restrictions="true,false" />
        <ITEM name="test" value="false" type="string" description="Enables the test mode (needed for internal use only)" tags="advanced" restrictions="true,false" />
      </NODE>
    </NODE>
    <NODE name="11" description="">
      <ITEM name="recycle_output" value="false" type="string" description="" />
      <ITEM name="toppas_type" value="output file list" type="string" description="" />
      <ITEM name="x_pos" value="260" type="float" description="" />
      <ITEM name="y_pos" value="-60" type="float" description="" />
    </NODE>
    <NODE name="4" description="">
      <ITEM name="recycle_output" value="false" type="string" description="" />
      <ITEM name="toppas_type" value="tool" type="string" description="" />
      <ITEM name="tool_name" value="FileFilter" type="string" description="" />
      <ITEM name="tool_type" value="" type="string" description="" />
      <ITEM name="x_pos" value="-700" type="float" description="" />
      <ITEM name="y_pos" value="-160" type="float" description="" />
      <NODE name="parameters" description="">
        <ITEM name="in" value="" type="string" description="input file " tags="input file,required" supported_formats="*.mzML,*.featureXML,*.consensusXML" />
        <ITEM name="in_type" value="" type="string" description="input file type -- default: determined from file extension or content#br#" restrictions="mzML,featureXML,consensusXML" />
        <ITEM name="out" value="" type="string" description="output file" tags="output file,required" supported_formats="*.mzML,*.featureXML,*.consensusXML" />
        <ITEM name="out_type" value="" type="string" description="output file type -- default: determined from file extension or content#br#" restrictions="mzML,featureXML,consensusXML" />
        <ITEM name="rt" value=":" type="string" description="retention time range to extract" />
        <ITEM name="mz" value=":" type="string" description="m/z range to extract (applies to ALL ms levels!)" />
        <ITEM name="pc_mz" value=":" type="string" description="MSn (n&gt;=2) precursor filtering according to their m/z value. Do not use this flag in conjunction with &apos;mz&apos;, unless you want to actually remove peaks in spectra (see &apos;mz&apos;). RT filtering is covered by &apos;rt&apos; and compatible with this flag." />
        <ITEM name="int" value=":" type="string" description="intensity range to extract" />
        <ITEM name="sort" value="true" type="string" description="sorts the output according to RT and m/z." restrictions="true,false" />
        <ITEM name="log" value="" type="string" description="Name of log file (created only when specified)" tags="advanced" />
        <ITEM name="debug" value="0" type="int" description="Sets the debug level" tags="advanced" />
        <ITEM name="threads" value="1" type="int" description="Sets the number of threads allowed to be used by the TOPP tool" />
        <ITEM name="no_progress" value="false" type="string" description="Disables progress logging to command line" tags="advanced" restrictions="true,false" />
        <ITEM name="test" value="false" type="string" description="Enables the test mode (needed for internal use only)" tags="advanced" restrictions="true,false" />
        <NODE name="peak_options" description="Peak data options">
          <ITEM name="sn" value="0" type="float" description="write peaks with S/N &gt; &apos;sn&apos; values only" />
          <ITEMLIST name="rm_pc_charge" type="int" description="Remove MS(2) spectra with these precursor charges. All spectra without precursor are kept!">
          </ITEMLIST>
          <ITEMLIST name="level" type="int" description="MS levels to extract">
            <LISTITEM value="1"/>
            <LISTITEM value="2"/>
            <LISTITEM value="3"/>
          </ITEMLIST>
          <ITEM name="sort_peaks" value="true" type="string" description="sorts the peaks according to m/z." restrictions="true,false" />
          <ITEM name="no_chromatograms" value="false" type="string" description="No conversion to space-saving real chromatograms, e.g. from SRM scans." restrictions="true,false" />
          <ITEM name="remove_chromatograms" value="false" type="string" description="Removes chromatograms stored in a file." restrictions="true,false" />
          <ITEM name="mz_precision" value="64" type="string" description="Store base64 encoded m/z data using 32 or 64 bit precision." restrictions="32,64" />
          <ITEM name="int_precision" value="32" type="string" description="Store base64 encoded intensity data using 32 or 64 bit precision." restrictions="32,64" />
        </NODE>
        <NODE name="spectra" description="Remove spectra or select spectra (removing all others) with certain properties.">
          <ITEM name="remove_zoom" value="false" type="string" description="Remove zoom (enhanced resolution) scans" restrictions="true,false" />
          <ITEM name="remove_mode" value="" type="string" description="Remove scans by scan mode#br#" restrictions="Unknown,MassSpectrum,MS1Spectrum,MSnSpectrum,SelectedIonMonitoring,SelectedReactionMonitoring,ConsecutiveReactionMonitoring,ConstantNeutralGain,ConstantNeutralLoss,Precursor,EnhancedMultiplyCharged,TimeDelayedFragmentation,ElectromagneticRadiation,Emission,Absorbtion" />
          <ITEM name="remove_activation" value="" type="string" description="Remove MSn scans where any of its precursors features a certain activation method#br#" restrictions="Collision-induced dissociation,Post-source decay,Plasma desorption,Surface-induced dissociation,Blackbody infrared radiative dissociation,Electron capture dissociation,Infrared multiphoton dissociation,Sustained off-resonance irradiation,High-energy collision-induced dissociation,Low-energy collision-induced dissociation,Photodissociation,Electron transfer dissociation,Pulsed q dissociation" />
          <ITEM name="select_zoom" value="false" type="string" description="Select zoom (enhanced resolution) scans" restrictions="true,false" />
          <ITEM name="select_mode" value="" type="string" description="Selects scans by scan mode#br#" restrictions="Unknown,MassSpectrum,MS1Spectrum,MSnSpectrum,SelectedIonMonitoring,SelectedReactionMonitoring,ConsecutiveReactionMonitoring,ConstantNeutralGain,ConstantNeutralLoss,Precursor,EnhancedMultiplyCharged,TimeDelayedFragmentation,ElectromagneticRadiation,Emission,Absorbtion" />
          <ITEM name="select_activation" value="" type="string" description="Select MSn scans where any of its precursors features a certain activation method#br#" restrictions="Collision-induced dissociation,Post-source decay,Plasma desorption,Surface-induced dissociation,Blackbody infrared radiative dissociation,Electron capture dissociation,Infrared multiphoton dissociation,Sustained off-resonance irradiation,High-energy collision-induced dissociation,Low-energy collision-induced dissociation,Photodissociation,Electron transfer dissociation,Pulsed q dissociation" />
        </NODE>
        <NODE name="feature" description="Feature data options">
          <ITEM name="q" value=":" type="string" description="Overall quality range to extract [0:1]" />
        </NODE>
        <NODE name="consensusfeature" description="Consensus feature data options">
          <ITEMLIST name="map" type="int" description="maps to be extracted from a consensus">
          </ITEMLIST>
          <ITEM name="map_and" value="false" type="string" description="AND connective of map selection instead of OR." restrictions="true,false" />
        </NODE>
        <NODE name="f_and_cf" description="Feature &amp; Consensus data options">
          <ITEM name="charge" value=":" type="string" description="charge range to extract" />
          <ITEM name="size" value=":" type="string" description="size range to extract" />
          <ITEMLIST name="remove_meta" type="string" description="Expects a 3-tuple (=3 entries in the list), i.e. &lt;name&gt; &apos;lt|eq|gt&apos; &lt;value&gt;; the first is the name of meta value, followed by the comparison operator (equal, less or greater) and the value to compare to. All comparisons are done after converting the given value to the corresponding data value type of the meta value (for lists, this simply compares length, not content!)!">
          </ITEMLIST>
        </NODE>
        <NODE name="id" description="ID options. The Priority of the id-flags is: remove_annotated_features / remove_unannotated_features -&gt; remove_clashes -&gt; keep_best_score_id -&gt; sequences_whitelist / accessions_whitelist.">
          <ITEM name="remove_clashes" value="false" type="string" description="remove features with id clashes (different sequences mapped to one feature)" tags="advanced" restrictions="true,false" />
          <ITEM name="keep_best_score_id" value="false" type="string" description="in case of multiple peptide identifications, keep only the id with best score" restrictions="true,false" />
          <ITEMLIST name="sequences_whitelist" type="string" description="keep only features with white listed sequences, e.g. LYSNLVER or the modification (Oxidation)">
          </ITEMLIST>
          <ITEMLIST name="accessions_whitelist" type="string" description="keep only features with white listed accessions, e.g. sp|P02662|CASA1_BOVIN">
          </ITEMLIST>
          <ITEM name="remove_annotated_features" value="false" type="string" description="remove features with annotations" restrictions="true,false" />
          <ITEM name="remove_unannotated_features" value="false" type="string" description="remove features without annotations" restrictions="true,false" />
          <ITEM name="remove_unassigned_ids" value="false" type="string" description="remove unassigned peptide identifications" restrictions="true,false" />
          <ITEM name="blacklist" value="" type="string" description="Input file containing MS2 identifications whose corresponding MS2 spectra should be removed from the mzML file!#br#Matching tolerances are taken from &apos;id:rt&apos; and &apos;id:mz&apos; options.#br#This tool will require all IDs to be matched to an MS2 spectrum, and quit with error otherwise. Use &apos;id:blacklist_imperfect&apos; to allow for mismatches." tags="input file" supported_formats="*.idXML" />
          <ITEM name="rt" value="0.1" type="float" description="retention tolerance [s] for precursor to id position" restrictions="0:" />
          <ITEM name="mz" value="0.001" type="float" description="m/z tolerance [Th] for precursor to id position" restrictions="0:" />
          <ITEM name="blacklist_imperfect" value="false" type="string" description="Allow for mismatching precursor positions (see &apos;id:blacklist&apos;)" restrictions="true,false" />
        </NODE>
        <NODE name="algorithm" description="S/N algorithm section">
          <NODE name="SignalToNoise" description="">
            <ITEM name="max_intensity" value="-1" type="int" description="maximal intensity considered for histogram construction. By default, it will be calculated automatically (see auto_mode). Only provide this parameter if you know what you are doing (and change &apos;auto_mode&apos; to &apos;-1&apos;)! All intensities EQUAL/ABOVE &apos;max_intensity&apos; will be added to the LAST histogram bin. If you choose &apos;max_intensity&apos; too small, the noise estimate might be too small as well.  If chosen too big, the bins become quite large (which you could counter by increasing &apos;bin_count&apos;, which increases runtime). In general, the Median-S/N estimator is more robust to a manual max_intensity than the MeanIterative-S/N." tags="advanced" restrictions="-1:" />
            <ITEM name="auto_max_stdev_factor" value="3" type="float" description="parameter for &apos;max_intensity&apos; estimation (if &apos;auto_mode&apos; == 0): mean + &apos;auto_max_stdev_factor&apos; * stdev" tags="advanced" restrictions="0:999" />
            <ITEM name="auto_max_percentile" value="95" type="int" description="parameter for &apos;max_intensity&apos; estimation (if &apos;auto_mode&apos; == 1): auto_max_percentile th percentile" tags="advanced" restrictions="0:100" />
            <ITEM name="auto_mode" value="0" type="int" description="method to use to determine maximal intensity: -1 --&gt; use &apos;max_intensity&apos;; 0 --&gt; &apos;auto_max_stdev_factor&apos; method (default); 1 --&gt; &apos;auto_max_percentile&apos; method" tags="advanced" restrictions="-1:1" />
            <ITEM name="win_len" value="200" type="float" description="window length in Thomson" restrictions="1:" />
            <ITEM name="bin_count" value="30" type="int" description="number of bins for intensity values" restrictions="3:" />
            <ITEM name="min_required_elements" value="10" type="int" description="minimum number of elements required in a window (otherwise it is considered sparse)" restrictions="1:" />
            <ITEM name="noise_for_empty_window" value="1e+20" type="float" description="noise value used for sparse windows" tags="advanced" />
          </NODE>
        </NODE>
      </NODE>
    </NODE>
  </NODE>
  <NODE name="edges" description="">
    <NODE name="0" description="">
      <NODE name="source/target" description="">
        <ITEM name="" value="0/2" type="string" description="" />
      </NODE>
      <NODE name="source_out_param" description="">
        <ITEM name="" value="__no_name__" type="string" description="" />
      </NODE>
      <NODE name="target_in_param" description="">
        <ITEM name="" value="in" type="string" description="" />
      </NODE>
    </NODE>
    <NODE name="1" description="">
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
    <NODE name="2" description="">
      <NODE name="source/target" description="">
        <ITEM name="" value="7/8" type="string" description="" />
      </NODE>
      <NODE name="source_out_param" description="">
        <ITEM name="" value="out" type="string" description="" />
      </NODE>
      <NODE name="target_in_param" description="">
        <ITEM name="" value="in" type="string" description="" />
      </NODE>
    </NODE>
    <NODE name="3" description="">
      <NODE name="source/target" description="">
        <ITEM name="" value="5/8" type="string" description="" />
      </NODE>
      <NODE name="source_out_param" description="">
        <ITEM name="" value="out" type="string" description="" />
      </NODE>
      <NODE name="target_in_param" description="">
        <ITEM name="" value="id" type="string" description="" />
      </NODE>
    </NODE>
    <NODE name="4" description="">
      <NODE name="source/target" description="">
        <ITEM name="" value="8/9" type="string" description="" />
      </NODE>
      <NODE name="source_out_param" description="">
        <ITEM name="" value="out" type="string" description="" />
      </NODE>
      <NODE name="target_in_param" description="">
        <ITEM name="" value="__no_name__" type="string" description="" />
      </NODE>
    </NODE>
    <NODE name="5" description="">
      <NODE name="source/target" description="">
        <ITEM name="" value="8/10" type="string" description="" />
      </NODE>
      <NODE name="source_out_param" description="">
        <ITEM name="" value="out" type="string" description="" />
      </NODE>
      <NODE name="target_in_param" description="">
        <ITEM name="" value="in" type="string" description="" />
      </NODE>
    </NODE>
    <NODE name="6" description="">
      <NODE name="source/target" description="">
        <ITEM name="" value="3/5" type="string" description="" />
      </NODE>
      <NODE name="source_out_param" description="">
        <ITEM name="" value="out" type="string" description="" />
      </NODE>
      <NODE name="target_in_param" description="">
        <ITEM name="" value="in" type="string" description="" />
      </NODE>
    </NODE>
    <NODE name="7" description="">
      <NODE name="source/target" description="">
        <ITEM name="" value="10/11" type="string" description="" />
      </NODE>
      <NODE name="source_out_param" description="">
        <ITEM name="" value="out" type="string" description="" />
      </NODE>
      <NODE name="target_in_param" description="">
        <ITEM name="" value="__no_name__" type="string" description="" />
      </NODE>
    </NODE>
    <NODE name="8" description="">
      <NODE name="source/target" description="">
        <ITEM name="" value="2/4" type="string" description="" />
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
        <ITEM name="" value="4/6" type="string" description="" />
      </NODE>
      <NODE name="source_out_param" description="">
        <ITEM name="" value="out" type="string" description="" />
      </NODE>
      <NODE name="target_in_param" description="">
        <ITEM name="" value="in" type="string" description="" />
      </NODE>
    </NODE>
    <NODE name="10" description="">
      <NODE name="source/target" description="">
        <ITEM name="" value="1/3" type="string" description="" />
      </NODE>
      <NODE name="source_out_param" description="">
        <ITEM name="" value="__no_name__" type="string" description="" />
      </NODE>
      <NODE name="target_in_param" description="">
        <ITEM name="" value="in" type="string" description="" />
      </NODE>
    </NODE>
  </NODE>
</PARAMETERS>"""
        log.debug('read template from [%s]' % self.__class__.__name__)
        return template, info
