# AutomatedILP
Version: May 4th, 2021

This tool is designed for automatically ILP scheduling to show ILP solving results.

# Introduction

It can take edgelist format DFG file as input, then transfer the graph file to ilp format 
as "ilp_output.lp" file to enable the GLPK solver for generating the scheduling 
result in "output.txt" file.

Latency _L_ and memory _M_ are 2 input arguments in our tool, which requires us to minimize 
the memory under latency _L_ and minimize latency under memory _M_. 
We can use _L_ and _M_ for ML-RC scheduling or MR-LC scheduling.

# Dependencies

## glpk

glpk is used to solve the ILP formulations. To install, run the following command:
### ```sudo apt install glpk-utils```

# Command
Once glpk is installed, we are ready to generate ILP files and solve them.
To generate an ILP file from the edgelist, use ```generate_ilp.py```:

```python3 run.py -i <input edgelist file name> -m <max memory usage requirement> -o <objective> -l <latency requirement> ```

OR

To generate an ILP file from the edgelist and feed to GLPK for solving, use ```edgelist_solve.sh```.

```./start.sh -i <edgelist file name> -l <latenct constraint> -o <objective to minimize> -m <memory constraint> -f <optional output filename> ```

Note:
  - Available objectives are (match case):
    - latency
    - memory
  - If latency is the objective, then ```-m``` does not have to be specified.

Notice: We consider latency as a constraints since we don't want to make the file too large.

# Example
In [this](https://github.com/u1154147/AutomatedILP/tree/main/scheduling_benchmarks) directory, we are using randomly generated edge-list files to run the program. One example could be:

``` ./edgelist_solve.sh -i rand_DFG_s10_1.edgelist -m 50 -l 20 -o latency```

This will generate an 'ilp_output.lp' file, then pipe this file to _glpk_ for solving. The solved file will be placed in 'glpk_solved.txt'. This can be changed using the ```-f``` flag, specifying an output name.

# Additional resource

GLPK https://www.gnu.org/software/glpk/

https://pypi.org/project/glpk/

# Authors 
-  Jake Steers: u1327208
-  Ye Zhou: u1220084
-  Zach Phelan: u1154147
