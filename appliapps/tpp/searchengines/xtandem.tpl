<?xml version="1.0"?>
<?xml-stylesheet type="text/xsl" href="tandem-input-style.xsl"?>
<bioml>

<note type="heading">Spectrum general</note>
    <note type="input" label="spectrum, fragment monoisotopic mass error">$FRAGMASSERR</note>
    <note type="input" label="spectrum, fragment monoisotopic mass error units">$FRAGMASSUNIT</note>
    <note type="input" label="spectrum, parent monoisotopic mass isotope error">yes</note>
    <note type="input" label="spectrum, parent monoisotopic mass error plus">$PRECMASSERR</note>
    <note type="input" label="spectrum, parent monoisotopic mass error minus">$PRECMASSERR</note>
    <note type="input" label="spectrum, parent monoisotopic mass error units">$PRECMASSUNIT</note>

<note type="heading">Spectrum conditioning</note>
    <note type="input" label="spectrum, fragment mass type">monoisotopic</note>
    <note type="input" label="spectrum, dynamic range">1000.0</note>
    <note type="input" label="spectrum, total peaks">50</note>
    <note type="input" label="spectrum, maximum parent charge">5</note>
    <note type="input" label="spectrum, use noise suppression">yes</note>
    <note type="input" label="spectrum, minimum parent m+h">400.0</note>
    <note type="input" label="spectrum, maximum parent m+h">6000</note>
    <note type="input" label="spectrum, minimum fragment mz">150.0</note>
    <note type="input" label="spectrum, minimum peaks">6</note>
    <note type="input" label="spectrum, threads">$THREADS</note>

<note type="heading">Residue modification</note>
    <note type="input" label="residue, modification mass">$STATIC_MODS</note>
    <note type="input" label="residue, potential modification mass">$VARIABLE_MODS</note>
    <note type="input" label="residue, potential modification motif"></note>

<note type="heading">Protein general</note>
    <note type="input" label="protein, taxon">no default</note>
    <note type="input" label="protein, cleavage site">$ENZYME</note>
    <note type="input" label="protein, cleavage semi">$XTANDEM_SEMI_CLEAVAGE</note>
<!--   do not add, otherwise xinteracts generates tons of confusing modification entries
    <note type="input" label="protein, cleavage C-terminal mass change">+17.00305</note>
    <note type="input" label="protein, cleavage N-terminal mass change">+1.00794</note>
-->
    <note type="input" label="protein, N-terminal residue modification mass">0.0</note>
    <note type="input" label="protein, C-terminal residue modification mass">0.0</note>
    <note type="input" label="protein, homolog management">no</note>
    <!-- explicitly disabled -->
    <note type="input" label="protein, quick acetyl">no</note>
    <note type="input" label="protein, quick pyrolidone">no</note>

<note type="heading">Scoring</note>
    <note type="input" label="scoring, maximum missed cleavage sites">$MISSEDCLEAVAGE</note>
    <note type="input" label="scoring, x ions">no</note>
    <note type="input" label="scoring, y ions">yes</note>
    <note type="input" label="scoring, z ions">no</note>
    <note type="input" label="scoring, a ions">no</note>
    <note type="input" label="scoring, b ions">yes</note>
    <note type="input" label="scoring, c ions">no</note>
    <note type="input" label="scoring, cyclic permutation">no</note>
    <note type="input" label="scoring, include reverse">no</note>
    $XTANDEM_SCORE


<note type="heading">model refinement paramters</note>
    <note type="input" label="refine">no</note>

<note type="heading">Output</note>
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