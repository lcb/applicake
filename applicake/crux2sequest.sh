#!/bin/bash

## needed to test processing crux results with TPP before r5366

# parse the *.ini file to grep for the value stored for the PEPXML key
#PEPXML=`find . -maxdepth 1 -name '*search.target.pep.xml'`
PEPXML=`find . -maxdepth 1 -name '*.ini' | xargs grep 'PEPXML' | perl -nle 'split(/=/);print $_[1]'`
echo "process ${PEPXML} ..."

TMP="${PEPXML}.tmp"
cp $PEPXML $TMP

# rename the search engine entry and the scores to map it to sequest
sed -i 's/search_engine="Crux"/search_engine="SEQUEST"/' $TMP
sed -i 's/name="xcorr_score"/name="xcorr"/' $TMP
sed -i 's/name="delta_cn"/name="deltacn"/' $TMP

# flip deltacn and xcorr positions and add missing score attributes (with default values)
cat $TMP | perl -ne '$a;while(<>){if(/.*name="deltacn"/){$a = $_}elsif(/.*name="xcorr"/){print $_.$a."        <search_score name=\"deltacnstar\" value=\"0.000\"/>\n        <search_score name=\"spscore\" value=\"0.0000\"/>\n        <search_score name=\"sprank\" value=\"1\"/>\\n"}else{print}}' > $PEPXML

