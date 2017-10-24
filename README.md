Network Disturbance System (NDS)
=============================
Network Disturbance System is a software that disturbs a traffic network
(graph) by removing 1 random edge and inserting another with the same
attributes but with different start and end nodes.

## Requirements
 * [Python 2.7](https://www.python.org/downloads/)
 * [Python Mathematical Expression Evaluator](https://pypi.python.org/pypi/py_expression_eval)
 
 There is the need to initialize the submodules, to do so use the following command:
```sh
git submodule update --init --recursive
```

## Networks
 Available at:  [Networks](https://github.com/maslab-ufrgs/network-files)
 
## Usage
Download, extract and from the program folder:
```sh
./network_disturbance_system.py [OPTIONS]
```
Or:
```sh
python2.7 network_disturbance_system.py [OPTIONS]
```

All the options have usable defaults so check them before running an experiment.

Use:

```sh
python2.7 network_disturbance_system.py -h
```

## Results
The results of each experiment are printed on the screen after you run the experiment.

The results of the coupling measure is in a csv file with the name of the according network.

## Options
```
arguments:
  -h, --help            shows help message and exit
  -f FILE               The network file. (default: None)
  -i ITERATIONS, --iterations ITERATIONS  Number of iterations (MSA). (default: 1000)
  -c CHANGES, --changes CHANGES  Number of changes in the network. (default: 1)
  -k K, Number of routes for KSP algorithm. (default: 8)
  -ce COMPLEMENTARY_EDGES, If it is to change both direction of the edge. (default: False)
  -jr, --just_remove    If it is only to remove edges and not add any afterwards. (default: False)
  -e EDGE, --edge EDGE  Specific edge to change (CASE SENSITIVE). (default: '')
  -re RANKED_EDGES, --ranked_edges RANKED_EDGES Number of top edges to not remove (random removing/changing). (default: 0)
```
