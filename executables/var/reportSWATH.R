#! /usr/bin/env Rscript
Sweave("/cluster/apps/guse/stable/applicake/master/executables/var/analyseSWATH.Rnw")
tools::texi2dvi("analyseSWATH.tex",pdf=TRUE)
