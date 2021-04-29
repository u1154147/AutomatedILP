#!/bin/bash

while getopts hi:m:o:l: flag
do
	case "${flag}" in
		i) file=${OPTARG};;
		m) memory=${OPTARG};;
		o) objective=${OPTARG};;
		l) latency=${OPTARG};;
		h) help_flag=${OPTARG};;
	esac
done

python3 run.py -i $file -m $memory -o $objective -l $latency

echo 'Created "ilp_output.lp".'
./glpk-4.35/examples/glpsol --cpxlp ilp_output.lp -o output.txt
echo 'GLP Solution in "output.txt"'

