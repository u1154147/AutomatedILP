# AutomatedILP
Authors: Jake Steers - u1327208 && Ye Zhou - u1220084 && Zach Phelan u1154147
Version: May 4th, 2021
This tool is designed for automatically ILP scheduling to show ILP solving results.

# Introduction
It can take edgelist format DFG file as input, then transfer the graph file to ilp format 
as "ilp_output.lp" file to enable the GLPK solver for generating the scheduling 
result in "output.txt" file.

Latency L and memory M are 2 input arguments in our tool, which requires us to minimize 
the memory under latency L and minimize latency under memory M. 
We can use L and M for ML-RC scheduling or MR-LC scheduling.

# Command
Make sure GLPK files are in the same folder with our code before run following command.
To use this, use the command shown below:
py3 run.py -i <input edgelist file name> -m <max memory usage requirement> -o <objective> -l<latency requirement> 

Notice: We consider latency as a constraints since we don't want to make the file too large.

# Additional resource
GLPK https://www.gnu.org/software/glpk/
https://pypi.org/project/glpk/
