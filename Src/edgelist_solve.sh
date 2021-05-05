#!/bin/bash

# Bash script to generate ILP file from generate_ilp.py, then feed ILP file into glpk.
run_py() {

	if [ -z $3 ]
	then
		echo 'Invalid number of arguments. Please see usage requirements.'
		python3 generate_ilp.py -h

	elif [ -z $4 ]  # memory usage not specified
	then
		python3 generate_ilp.py -i $1 -o $2 -l $3 

	else
		python3 generate_ilp.py -i $1 -m $2 -o $3 -l $4 

	fi
}

run_glpk() {

	glpsol --cpxlp ilp_output.lp -o $1 > error.txt
}

while getopts hi:m:o:l:f: flag
do
	case "${flag}" in
		i) file=${OPTARG};;
		m) memory=${OPTARG};;
		o) objective=${OPTARG};;
		l) latency=${OPTARG};;
		h) python3 run.py -h; exit;;
		f) file_name=${OPTARG};;
	esac
done

if [ -z $file_name ]
then
	file_name='glpk_solved.txt'
fi

run_py $file $memory $objective $latency 

if [ $? -eq 0 ]
then
	echo 'Created "ilp_output.lp". Running glpk...'
	run_glpk $file_name

	if [ $? -gt 0 ]
	then
		echo 'ERROR! glpk ran into issue! Check "error.txt" file.'
	else
		rm error.txt
		echo "GLP Solution in $file_name"
	fi

elif [ $? -eq 1 ]
then
	exit
fi

