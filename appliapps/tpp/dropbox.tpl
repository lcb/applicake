To: $USERNAME@ethz.ch
Subject: TPP search $EXPERIMENT_CODE finished!

Dear $USERNAME
Your TPP search workflow [ $COMMENT ] finished sucessfully!

$LINKTEXT run tpp2viewer3.py and use the links shown there:
[$USERNAME@imsb-ra-tpp~] # cd ~/html/petunia; tpp2viewer3.py $EXPERIMENT_CODE

To cite this workflow use:
The spectra were searched using the search engines
${ENGINES_VERSIONS}
against the $DBASE database using $ENZYME digestion and allowing $MISSEDCLEAVAGE missed cleavages.
Included were '$STATIC_MODS' as static and '$VARIABLE_MODS' as variable modifications. The mass tolerances were set to $PRECMASSERR $PRECMASSUNIT for precursor-ions and $FRAGMASSERR $FRAGMASSUNIT for fragment-ions.
The identified peptides were processed and analyzed through the Trans-Proteomic Pipeline ($TPPVERSION) using PeptideProphet, iProphet and ProteinProphet scoring.
Spectral counts and peptides for ProteinProphet were filtered at FDR of $FDR.

Yours sincerely,
The iPortal team

Please note that this message along with your results are stored in openbis:
https://ra-openbis.ethz.ch/openbis/#action=BROWSE&entity=EXPERIMENT&project=/$SPACE/$PROJECT