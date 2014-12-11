#!/bin/bash

#$1 full align/requant output tsv 
#$2 comment

nrsamples=$(awk '{print $(NF-1)}' $1 | sort -u | grep -v align_origfilename | wc -l)
if [ $nrsamples -lt 2 ]; then
    echo ONLYONESAMPLE
    echo "Your SWATH analysis [$2] finished and will show up in openBIS soon! Unfortunately the report requires at least 2 samples, so there is no PDF report" | mail -s "SWATH finished - no Report" $(whoami)@ethz.ch
    exit
fi

if [[ $1 == *requant* ]]; then
    echo NOREQUANT
    echo "Your SWATH analysis [$2] finished and will show up in openBIS soon! Unfortunately the report requires requant, so there is no PDF report" | mail -s "SWATH finished - no Report" $(whoami)@ethz.ch
    exit
fi

echo reportSWATH.R "$1"
reportSWATH.R "$1"
exitcode=$?

if [ "$exitcode" == "0" -a -e "analyseSWATH.pdf" ]
then
    echo OK
    echo "Your SWATH analysis [$2] and report on $1 finished and will show up in openBIS soon!" | mail -s "SWATH finished - Report" -a analyseSWATH.pdf $(whoami)@ethz.ch
else
	echo SOME ERROR
	echo "Your SWATH analysis [$2] finished and will show up in openBIS soon! Unfortunately the report on $1 failed, so there is no PDF report" | mail -s "SWATH finished - no Report" $(whoami)@ethz.ch,loblum@ethz.ch
fi


