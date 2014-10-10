#!/bin/bash

#$1 properties 
#$2 peptides.csv
#$3 proteins.csv
#$4 username

#execute main reportLFQ.R R script
#set -x

#min: 1quant per sample. thus 4lines header + 2proteins for min 2 samples = 6 lines
if [ $(cat $2 | wc -l) -ge "6" ]
then
   echo reportLFQ.R "$1" "$2" "$3" $4
   reportLFQ.R "$1" "$2" "$3" $4
   exitcode=$?

   if [ "$exitcode" == "0" -a -e "analyseLFQ.pdf" ]
   then
		echo OK
		echo "Your LFQ analysis and report finished and will show up in openBIS soon!" | mail -s "LFQ finished - Report" -a analyseLFQ.pdf $4@ethz.ch 
	else
		echo SOME ERROR
		echo "Your LFQ analysis finished and will show up in openBIS soon! Unfortunately the LFQ report failed, so there is no PDF report" | mail -s "LFQ finished - no Report" $4@ethz.ch,loblum@ethz.ch
   fi
else
	echo NOT ENOUGH FEATURES
	echo "Your LFQ analysis finished and will show up in openBIS soon! Unfortunately not enough features could be assigned to peptides, so there is no PDF report" | mail -s "LFQ finished - no Report" $4@ethz.ch
fi
