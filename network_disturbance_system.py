#!/usr/bin/python3
"""
Created by: Arthur Zachow Coelho (azcoelho@inf.ufrgs.br)
Date: 08/10/2017
"""

#Modules
#Python's modules
import argparse as ArgP
import random as rnd

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
    ##separated into 2 edges if it is not directed.
    graph = iG.Graph(directed=True)
    #Adds the vertices
    #Note that if the name is not converted to string you may have problems with the function
    ##adding a number of vertices because the name is a number.
    graph.add_vertices([str(n.name) for n in node_list])
    #Checks if necessary to use weights
    if with_cost:
        for edge in edge_list:
            graph.add_edge(edge.start, edge.end, weight=edge.cost)
    else:
        graph.add_edges([(edge.start, edge.end) for edge in edge_list])

    return graph

def assignment(net_file=None, episodes=400, edge_list=None, node_list=None):
    """
    Calls the MSA and Cplex to compute UE (User Equilibrium) and SO (System Optimal) and PoA (Price
    of Anarchy), respectively.
    In:
        net_file:String = The absolute path to the network file.
        episodes:Integer = Number of episodes for the MSA run.

    ##Needs to be run in the program a 2nd time where it receives directly the edges and nodes.
    ###Maybe one way to address this is to generate a network file from it.
    """
    if edge_list and node_list:
        pass
    else:
        #Calls MSA for network and UE
        nodes, edges, od_matrix, UE = MSA.run(net_file, episodes)

        #Calls Cplex (SO and PoA)

    return nodes, edges, od_matrix, UE, SO, PoA

def change_edges(node_list, edge_list, od_matrix):
    """
    Makes random changes in a graph's edges (defined as traffic network).
    In:
        node_list:List = List of Node objects from the MSA module.
        edge_list:List = List of Edge objects from the MSA module.
    Out:
        edge_ln:List = New list of Edge objects representing the new graph.
        changed_edge:String = String representing the edge that was changed.
    #Maybe it does't need the new list.
    #Probably a function that can get stuck in a loop, because it can have possibly 0 connected
    ##graph that can be generated from it
    """
    found = False
    edge_ln = edge_list
    while not found:
        #Chooses an edge randomly
        rnd_edge = rnd.choice(edge_ln)
        #Chooses 2 random nodes
        node1 = rnd.choice(node_list)
        node2 = rnd.choice(node_list)
        #Checks if the 2 nodes are equal or they are an OD pair
        if node1 == node2 or str(node1.name + '|' + node2.name) in od_matrix:
            break
        else:
            #Changes the edge start and end
            """
            Needs to the for actually two edges, because an undirected graph is represented as
                having two directed edges, let's call it complementary edge. The graph isn't
                necessarily an undirected graph.
            """
            #Gets this complementary edge
            has_comp_edge = False
            for edge in edge_ln:
                if edge.end == rnd_edge.start and edge.start == rnd_edge.end:
                    comp_edge = edge
                    has_comp_edge = True
                    break
            #Changes the random edge
            rnd_edge.start = node1.name
            rnd_edge.end = node2.name
            #Changes the complementary edges, if it has one
            if has_comp_edge:
                comp_edge.start = node2.name
                comp_edge.end = node1.name
            #Checks if the graph is connected, if it is, then the function is over and a new graph
            ##has been found
            if not export_to_igraph(node_list, edge_ln).is_connected():
                break
            else:
                found = True
                changed_edge = node1.name + '-' + node2.name

    return edge_ln, changed_edge

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
    #List of the changed edges
    changed_edges = []
    #Gets the original nodes and edges
    nodes, edge_or, od_matrix, UE, SO, PoA = assignment(args.file, args.episodes)
    #Gets the original graph
    graph_o = export_to_igraph(nodes, edge_or, with_cost=True)
    #Gets betweenness
    ## Needs to adjust the weights
    graph_o.edge_betweenness()

    #Modified edges of the graph
    edge_modf, changed_edge = change_edges(nodes, edge_or)
    changed_edges.append(changed_edge)
    #Number of changes made in the edges
    changes = 1
    #While loop for changing the edges of the graph
    while changes < args.changes:
        edge_modf, changed_edge = change_edges(nodes, edge_modf)
        changed_edges.append(changed_edge)
        changes += 1

    #Calls the assignment function on the resulting graph
    _, _, _, UE_modf, SO_modf, PoA_modf = assignment()

    graph_modf = export_to_igraph(nodes, edge_modf, with_cost=True)
    #Gets betweenness
    ## Needs to adjust the weights
    graph_modf.edge_betweenness()

if __name__ == '__main__':
    main()
