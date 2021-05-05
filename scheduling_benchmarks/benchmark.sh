#/bin/bash

# Script to generate and solve ILP files for edge=lists with 10 nodes.
# Note that GLPK takes a lot longer to solver once you go to 50 nodes.
i=1
for f in ./rand_DFG_s10_**.edgelist; do
	./edgelist_solve.sh -i $f -m 80 -l 12 -o latency -f test_$i.txt
	i=$(($i+1))
done
