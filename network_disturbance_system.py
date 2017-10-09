#!/usr/bin/python3
"""
Created by: Arthur Zachow Coelho (azcoelho@inf.ufrgs.br)
Date: 08/10/2017
"""

#Modules

#Python's modules
import argparse as ArgP

#3rd party modules
import igraph as iG

#Home-made modules
import MSA.successive_averages as MSA

def export_to_igraph_file(edge_list, with_cost=False): #Don't think we'll use this one.
    '''
    This function exports a network to an edge list file to be read by the igraph module.
    In:
        edge_list:List = List of Edge class objects.
        with_cost:Boolean = If it is necessary to print into the file the cost of the edges.
    '''
    #Define folder to store the graphs generated
    path = './network_graphs/'

    #Creates the folder if it doesn`t exist
    if os.path.isdir(path) is False:
        os.makedirs(path)

    fh = open(path+NETWORK_NAME, 'w')

    #Iterates through the list of edges printing the start and end in the file.
    #It uses the format of edge list for the file input in igraph.
    for edge in edge_list:
        print('{} {}'.format(edge.start, edge.end), end='', file=fh)
        if with_cost: # If want to print the weight of the edges in the graph too.
            print(' {}'.format(edge.cost), file=fh)
        else:
            print('', file=fh)

    fh.close()

def export_to_igraph(node_list, edge_list, with_cost=False):
    """
    Exports the network that's described by node_list and edge_list to an iGraph graph.
    In:
        node_list:List = List of Node objects from the MSA module.
        edge_list:List = List of Edge objects from the MSA module.
        with_cost:Boolean = If it is needed to use weights on the edges of the graph.
    Out:
        graph:Graph = Graph corresponding to the network.
    """
    #Creates the graph, it is directed because when it is read from the graph file it is already
    #separated into 2 edges if it is not directed.
    graph = iG.Graph(directed=True)
    #Adds the vertices
    graph.add_vertices([str(n.name) for n in node_list])
    #Checks if necessary to use weights
    if with_cost:
        for edge in edge_list:
            graph.add_edge(edge.start, edge.end, weight=edge.cost)
    else:
        graph.add_edges([(edge.start, edge.end) for edge in edge_list])

    return graph

def assignment(net_file, episodes=400):
    """
    Calls the MSA and Cplex to compute UE (User Equilibrium) and SO (System Optimal) and PoA (Price
    of Anarchy), respectively.
    In:
        net_file:String = The absolute path to the network file.
        episodes:Integer = Number of episodes for the MSA run.
    """
    #Call MSA
    nodes, edges = MSA.run(net_file, episodes)

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
