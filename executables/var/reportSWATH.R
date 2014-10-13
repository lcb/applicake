#! /usr/bin/env Rscript
initial.options <- commandArgs(trailingOnly = FALSE)
file.arg.name <- "--file="
script.name <- sub(file.arg.name, "", initial.options[grep(file.arg.name, initial.options)])
script.basename <- dirname(script.name)
other.name <- paste(sep="/", script.basename, "analyseSWATH.Rnw")
print(other.name)
Sweave(other.name)
tools::texi2dvi("analyseSWATH.tex",pdf=TRUE)
