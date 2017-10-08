#!/usr/bin/python3

#Python's modules
import argparse as ArgP

#3rd party modules
import igraph as iG

#Home-made modules
import MSA.successive_averages as MSA

def assignment(net_file, episodes=400):
    """
    Calls the MSA and Cplex to compute UE (User Equilibrium) and SO (System Optimal) and PoA (Price
    of Anarchy), respectively.
    In:
        net_file:String = The absolute path to the network file.
        episodes:Integer = Number of episodes for the MSA run.
    """
    #Call MSA
    MSA.run(net_file, episodes)

    #Call Cplex (SO and PoA)


def main():
    """
    Upper level function. It calls the other functions in an orderly way.
    Parser inputs:
        net_file:String = The absolute path to the network file.
        changes:Integer = Number of edges to change in the algorithm.
    """
    #Parser things for the parameters
    prs = ArgP.ArgumentParser(formatter_class=ArgP.ArgumentDefaultsHelpFormatter,
                                  description="""
                                              Network Disturbance System is a software that randomly
                                              generates a new network. (needs work yet)
                                              V0.1
                                              """)
    prs.add_argument("-f", dest="file", required=True, help="The network file.\n")
    prs.add_argument("-e", "--episodes", type=int, default=1000, help="Number of episodes.\n")
    prs.add_argument("-c", "--changes", type=int, default=1, help="Number of changes in the network.\n")
    args = prs.parse_args()

    #Start of the algorithm
    assignment(args.file, args.episodes)

if __name__ == '__main__':
    main()
