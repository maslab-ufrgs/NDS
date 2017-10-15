#!/usr/bin/python3
"""
Created by: Arthur Zachow Coelho (azcoelho@inf.ufrgs.br)
Date: 08/10/2017
"""

#Modules
#Python's modules
import argparse as ArgP
import random as rnd
import os

#3rd party modules
import igraph as iG

#Home-made modules
import MSA.successive_averages as MSA
import system_optimal_solver.so_solver as SO

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

def assignment(net_file='', episodes=400, edge_list=None, node_list=None, od_matrix=None):
    """
    Calls the MSA and System Optimal Solver to compute UE (User Equilibrium) and SO (System Optimal)
    and PoA (Price of Anarchy), respectively.

    **Needs either a network file path or (edge_list and node_list and od_matrix) to work.
    In:
        net_file:String = The absolute path to the network file.
        episodes:Integer = Number of episodes for the MSA run.
        edge_list:List = Node objects from the MSA module.
        node_list:List = Edge objects from the MSA module.
        od_matrix:Dictionary = Represents the OD pairs and their demands.
    Out:
        nodes:List = Node objects from the MSA module.
        edges:List = Edge objects from the MSA module.
        od_matrix:Dictionary = Represents the OD pairs and their demands.
        ue:Float = User equilibrium solution.
        so:Float = System optimal solution.
        PoA:Float = Price of Anarchy.
    """
    if edge_list and node_list and od_matrix:
        nodes, edges, od_matrix, ue = MSA.run(episodes, edge_list=edge_list, node_list=node_list,
                                              od_matrix=od_matrix, output=False)
    else:
        #Calls MSA for network and UE
        nodes, edges, od_matrix, ue = MSA.run(episodes, net_file=net_file, output=False)

    #Calls System Optimal Solver for SO
    so = SO.SOSolver(nodes, edges, od_matrix)
    so.solve()
    sop = so.get_system_optimal()

    #Price of anarchy value
    PoA = ue/sop

    return nodes, edges, od_matrix, ue, sop, PoA

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
        edge_old_name = rnd_edge.name
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
            #If we change the name of the edge, we`ll receive warnings from Docplex because of
            ##duplicate names sometimes
            #rnd_edge.name = "{0}-{1}".format(node1.name, node2.name)
            #Changes the complementary edges, if it has one
            if has_comp_edge:
                comp_edge.start = node2.name
                comp_edge.end = node1.name
                #comp_edge.name = "{0}-{1}".format(node2.name, node1.name)
            #Checks if the graph is connected, if it is, then the function is over and a new graph
            ##has been found
            if not export_to_igraph(node_list, edge_ln).is_connected():
                break
            else:
                found = True
                changed_edge = "{0}_{1}-{2}".format(edge_old_name, node1.name, node2.name)

    return edge_ln, changed_edge

def print_results(net_name, changed_edges_list, episodes, UE, SO, PoA, avg_betweenness):
    """
    Prints the results in a table.
    In:
        net_name:String = Name of the network.
        changed_edges_list:List = List of the changes made in the edges.
        UE:Float = User equilibrium.
        SO:Float = System optimal.
        PoA:Float = Price of Anarchy.
        avg_betweenness:Float = Average value of the edge betweenness of the graph.
    """
    #Creates the name of the network correctly in the form: network_name_original + _change1_change2
    for change in changed_edges_list:
        net_name += '_' + change
    #Prints some kind of table
    print('#Network name = {0}\t# of episodes = {1}'.format(net_name, episodes))
    print('#User Equilibrium\tSystem Optimal\tPrice of Anarchy\tEdge Betweenness')
    print('{0}\t{1}\t{2}\t{3}'.format(UE, SO, PoA, avg_betweenness))

def main():
    """
    Upper level function. It calls the other functions in an orderly way.
    Parser inputs:
        file:String = The absolute path to the network file.
        episodes:Integer = Number of episodes in the MSA run.
        changes:Integer = Number of edges to change in the algorithm.
    """
    #Parser things for the parameters
    prs = ArgP.ArgumentParser(formatter_class=ArgP.ArgumentDefaultsHelpFormatter,
                                  description="""
                                              Network Disturbance System is a software that disturbs
                                              a traffic network (graph) by removing 1 random edge
                                              and inserting another with the same attributes but
                                              with different start and end nodes.\n
                                              V0.9
                                              """)
    prs.add_argument("-f", dest="file", required=True, help="The network file.\n")
    prs.add_argument("-e", "--episodes", type=int, default=1000, help="Number of episodes.\n")
    prs.add_argument("-c", "--changes", type=int, default=1, help="Number of changes in the network.\n")
    args = prs.parse_args()

    #Network name
    net_name = os.path.basename(args.file).split('.')[0]

    #List of the changed edges
    changed_edges = []

    #Number of changes made in the edges
    changes = 0

    #Start of the algorithm
    #Gets the original nodes and edges
    nodes, edge_or, od_matrix, ue, so, PoA = assignment(net_file=args.file, episodes=args.episodes)
    #Gets the original graph
    graph_o = export_to_igraph(nodes, edge_or, with_cost=True)

    #Needs to adjust the weights in the betweenness
    print_results(net_name, changed_edges, args.episodes, ue, so, PoA,
                  sum(graph_o.edge_betweenness(weights='weight'))/len(graph_o.es))

    #While loop for changing the edges of the graph
    while changes < args.changes:
        #Modified edges of the graph
        edge_modf, c_edge = change_edges(nodes, edge_or, od_matrix)
        changed_edges.append(c_edge)
        #Number of changes made in the edges
        changes += 1

        #Can ignore the output of edges, nodes and od_matrix as they don't change
        _, _, _, ue, so, PoA = assignment(episodes=args.episodes, edge_list=edge_modf,
                                          node_list=nodes, od_matrix=od_matrix)
        #Gets the modified graph
        graph_m = export_to_igraph(nodes, edge_modf, with_cost=True)
        print_results(net_name, changed_edges, args.episodes, ue, so, PoA,
                      sum(graph_m.edge_betweenness(weights='weight'))/len(graph_m.es))


if __name__ == '__main__':
    main()
