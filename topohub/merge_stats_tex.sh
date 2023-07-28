#!/bin/bash

echo '\begin{tabular}{l' $(printf 'r%.0s' "${@}") '}'
echo '\toprule'
paste $1 <(cut -c 40- "${@:2}" | pr -T -J -$(ls -1q "${@:2}" | wc -l)) | sed 's/^[\t ]*$/\\midrule/; s/$/ \\\\/'
echo '\bottomrule'
echo '\end{tabular}'
