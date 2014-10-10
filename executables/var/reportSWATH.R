#! /usr/bin/env Rscript
Sweave("/cluster/apps/guse/stable/bin/analyseSWATH.Rnw")
tools::texi2dvi("analyseSWATH.tex",pdf=TRUE)
