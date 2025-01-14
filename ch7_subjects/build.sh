#!/bin/sh

#pandoc --smart --normalize --bibliography=references/refs.bib --csl=references/sage-harvard.csl --latex-engine=xelatex ejors.rmd -o ejors.pdf
#pandoc --smart --normalize --bibliography=references/refs.bib --csl=references/sage-harvard.csl --latex-engine=xelatex mcmc.md -o mcmc.pdf

## knit the R code
./knitall.sh

##format bibliography and  display
./pandoc.sh

evince ch_learning_subjects.pdf

