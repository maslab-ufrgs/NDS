Network Disturbance System (NDS)
=============================
Network Disturbance System is a software that disturbs a traffic network
(graph) by removing 1 random edge and inserting another with the same
attributes but with different start and end nodes.

## Requirements
 * [Python 3](https://www.python.org/downloads/)
 * [Python Mathematical Expression Evaluator](https://pypi.python.org/pypi/py_expression_eval)
 
 There is the need to initialize the submodules, to do so use the following command:
```sh
git submodule init && git submodule update
```

## Networks
 Available at:  [Networks](https://github.com/maslab-ufrgs/network-files)
 
## Usage
Download, extract and from the program folder:
```sh
python3 network_disturbance_system.py [OPTIONS]
```
Or:
```sh
./network_disturbance_system.py [OPTIONS]
```

All the options have usable defaults so check them before running an experiment.

Use:

```sh
python3 network_disturbance_system.py -h
```

## Results
The results of each experiment are printed on the screen after you run the experiment.

## Options
```
arguments:
  -h, --help            shows help message and exit
  -f FILE               The network file. (default: None)
  -e EPISODES, --episodes EPISODES  Number of episodes. (default: 1000)
  -c CHANGES, --changes CHANGES  Number of changes in the network. (default: 1)
```
