<?xml version="1.0"?>
<?xml-stylesheet type="text/xsl" href="tandem-input-style.xsl"?>
<bioml>

    <note label="scoring, algorithm" type="input">k-score</note>
    <note label="spectrum, use conditioning" type="input">no</note>
    <note label="scoring, minimum ion count" type="input">1</note>
    <note type="input" label="list path, default parameters">default_input.xml</note>
    <note type="input" label="list path, taxonomy information">taxonomy_pro.xml</note>
    <note type="input" label="spectrum, fragment monoisotopic mass error">$FRAGMASSERR</note>
    <note type="input" label="spectrum, fragment monoisotopic mass error units">$FRAGMASSUNIT</note>
    <note>Alex Schmidt 25 ppm for the FT and down to 15ppm for orbitrab. as both data are concatenated :decision to use 25 ppm</note>
    <note type="input" label="spectrum, parent monoisotopic mass isotope error">yes</note>
	<note type="input" label="spectrum, parent monoisotopic mass error plus">$PRECMASSERR</note>
	<note type="input" label="spectrum, parent monoisotopic mass error minus">$PRECMASSERR</note>
    <note type="input" label="spectrum, parent monoisotopic mass error units">$PRECMASSUNIT</note>
    <note type="input" label="spectrum, fragment mass type">monoisotopic</note>
    <note type="input" label="spectrum, dynamic range">1000.0</note>
    <note>
        This parameter is used to normalize the intensity values of fragment ions, from spectrum to spectrum.
        For example, if Drange = 100.0, then the intensity of the most intense peak in a spectrum is set to 100, and all
        of the other intensities are linearly scaled to that intensity. Any peak with a scaled intensity of less than 1 is rejected
        as being outside of the dynamic range. Therefore, in addition to normalizing the spectra, it sets an effective relative threshold for peaks.
    </note>
    <note type="input" label="spectrum, total peaks">50</note>
    <note type="input" label="spectrum, maximum parent charge">5</note>
    <note type="input" label="spectrum, use noise suppression">yes</note>
    <note type="input" label="spectrum, minimum parent m+h">400.0</note>
    <note type="input" label="spectrum, maximum parent m+h">6000</note>
    <note type="input" label="spectrum, minimum fragment mz">150.0</note>
    <note type="input" label="spectrum, minimum peaks">6</note>
    <note type="input" label="spectrum, threads">8</note>
    <note type="input" label="residue, modification mass">57.021464@C</note>
    <!--<note type="input" label="residue, potential modification mass">79.966331@S,79.966331@T</note>-->
    <note type="input" label="residue, potential modification mass"></note>
    <note type="input" label="residue, potential modification motif"></note>
    <note type="input" label="protein, taxon">no default</note>
    <note type="input" label="protein, cleavage site">[RK]|{P}</note>
    <!--<note type="input" label="protein, cleavage semi">no</note>-->
    <note type="input" label="protein, cleavage semi">no</note>
    <note type="input" label="protein, N-terminal residue modification mass">0.0</note>
    <note type="input" label="protein, C-terminal residue modification mass">0.0</note>
    <note type="input" label="protein, homolog management">no</note>


    <!--<note type="input" label="refine">yes</note>-->
    <note type="input" label="refine">no</note>
    <note type="input" label="refine, spectrum synthesis">yes</note>
    <note type="input" label="refine, maximum valid expectation value">0.1</note>
    <!--<note type="input" label="refine, potential N-terminus modifications">42.01056</note>-->
    <note type="input" label="refine, potential C-terminus modifications"></note>
    <note type="input" label="refine, unanticipated cleavage">no</note>
    <note type="input" label="refine, cleavage semi">no</note>
    <note type="input" label="refine, modification mass">57.021464@C</note>
    <!--<note type="input" label="refine, potential modification mass">79.966331@S,79.966331@T,79.966331@Y</note>-->
    <note type="input" label="refine, point mutations">no</note>
    <note type="input" label="refine, use potential modifications for full refinement">yes</note>
    <note type="input" label="refine, potential modification motif"></note>
    <!--<note type="input" label="scoring, minimum ion count">4</note>-->


    <note type="input" label="scoring, maximum missed cleavage sites">$MISSEDCLEAVAGE</note>
    <note type="input" label="scoring, x ions">no</note>
    <note type="input" label="scoring, y ions">yes</note>
    <note type="input" label="scoring, z ions">no</note>
    <note type="input" label="scoring, a ions">no</note>
    <note type="input" label="scoring, b ions">yes</note>
    <note type="input" label="scoring, c ions">no</note>
    <note type="input" label="scoring, cyclic permutation">no</note>
    <note type="input" label="scoring, include reverse">no</note>
    <note type="input" label="output, message">testing 1 2 3</note>
    <note type="input" label="output, path">output.xml</note>
    <note type="input" label="output, sort results by">spectrum</note>
    <note type="input" label="output, path hashing">no</note>
    <note type="input" label="output, xsl path">tandem-style.xsl</note>
    <note type="input" label="output, parameters">yes</note>
    <note type="input" label="output, performance">yes</note>
    <note type="input" label="output, spectra">yes</note>
    <note type="input" label="output, histograms">no</note>
    <note type="input" label="output, proteins">yes</note>
    <note type="input" label="output, sequences">no</note>
    <note type="input" label="output, one sequence copy">yes</note>
    <note type="input" label="output, results">all</note>
    <note type="input" label="output, maximum valid expectation value">0.1</note>
    <note type="input" label="output, histogram column width">30</note>

</bioml>
