#!/bin/bash

# necessary to process crux results (<= 1.35) with TPP (>= r5366) 

# parse the *.ini file to grep for the value stored for the PEPXML key
#PEPXML=`find . -maxdepth 1 -name '*search.target.pep.xml'`
PEPXML=`find . -maxdepth 1 -name '*.ini' | xargs grep 'PEPXML' | perl -nle 'split(/=/);print $_[1]'`
echo "process ${PEPXML} ..."

# corrects spectrum attribute in <spectrum_query>
sed -i 's/\.mzXML\./\./g' $PEPXML
