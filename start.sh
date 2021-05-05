#!/bin/bash

run_py() {

	if [ -z $3 ]
	then
		echo 'Invalid number of arguments. Please see usage requirements.'
		python3 run.py -h

	elif [ -z $4 ]  # memory usage not specified
	then
		python3 run.py -i $1 -o $2 -l $3 

	else
		python3 run.py -i $1 -m $2 -o $3 -l $4 

	fi
}

run_glpk() {

	glpsol --cpxlp ilp_output.lp -o output.txt > error.txt
}

while getopts hi:m:o:l: flag
do
	case "${flag}" in
		i) file=${OPTARG};;
		m) memory=${OPTARG};;
		o) objective=${OPTARG};;
		l) latency=${OPTARG};;
		h) run_py -h; exit;;
	esac
done

run_py $file $memory $objective $latency 

if [ $? -eq 0 ]
then
	echo 'Created "ilp_output.lp". Running glpk...'
	run_glpk

	if [ $? -gt 0 ]
	then
		echo 'ERROR! glpk ran into issue! Check "error.txt" file.'
	else
		rm error.txt
		echo 'GLP Solution in "output.txt"'
	fi

elif [ $? -eq 1 ]
then
	exit
fi

