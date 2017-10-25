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
import route_coupling.coupling as Coup

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

def assignment(net_file='', iterations=400, edge_list=None, node_list=None, od_matrix=None):
    """
    Calls the MSA and System Optimal Solver to compute UE (User Equilibrium) and SO (System Optimal)
    and PoA (Price of Anarchy), respectively.

    **Needs either a network file path or (edge_list and node_list and od_matrix) to work.
    In:
        net_file:String = The absolute path to the network file.
        iterations:Integer = Number of iterations for the MSA run.
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
        nodes, edges, od_matrix, ue = MSA.run(iterations, edge_list=edge_list, node_list=node_list,
                                              od_matrix=od_matrix, output=False)
    else:
        #Calls MSA for network and UE
        nodes, edges, od_matrix, ue, od_routes_flow = MSA.run(iterations, net_file=net_file, output=False)

    #Calls System Optimal Solver for SO
    so = SO.SOSolver(nodes, edges, od_matrix)
    so.solve()
    sop = so.get_system_optimal()

    #Price of anarchy value
    PoA = ue/sop

    return nodes, edges, od_matrix, ue, sop, PoA, od_routes_flow

def change_edges(node_list, edge_list, od_matrix, complementary_edges, just_remove=False,
                 edge_to_remove='', ranked_edges=[]):
    """
    Makes random changes in a graph's edges (defined as traffic network).
    In:
        node_list:List = List of Node objects from the MSA module.
        edge_list:List = List of Edge objects from the MSA module.
        od_matrix:Dictionary = Dictionary of the OD pairs with the associated demand.
        complementary_edges:Boolean = If it needs to change the complementary edge too.
        just_remove:Boolean = If it doesn't need to add an edge.
        edge_to_remove:String = Specific edge to be removed from the network.
    Out:
        edge_ln:List = New list of Edge objects representing the new graph.
        changed_edge:String = String representing the edge that was changed.
    #Probably a function that can get stuck in a loop, because it can have possibly 0 connected
    ##graph that can be generated from it
    ##I think that it cannot be stuck on an infinite loop because if it is randomly trying to add a
    ##new edge, sometime it will be the old edge, so you get stuck with the old graph and cannot
    ##generate any new from that, which is not the case if it is just removing.
    """
    found = False
    edge_ln = edge_list
    changed_edge = None
    #Redundant but it's easier for now
    if just_remove:
        #If it is needed to remove one specific edge in the network
        if edge_to_remove:
            edge_ln.remove(next(edge for edge in edge_ln if edge.name == edge_to_remove))
            changed_edge = edge_to_remove
            if not export_to_igraph(node_list, edge_ln).is_connected():
                raise Exception("The new graph with that edge removed became disconnected!")
        else:
            while not found:
                #Chooses one random edge
                edge_rmv = rnd.choice(edge_ln)
                if edge_rmv.flow not in ranked_edges:
                    #Removes it from the network
                    edge_ln.remove(edge_rmv)
                    #Network (graph) still needs to be connected (strongly)
                    if export_to_igraph(node_list, edge_ln).is_connected():
                        found = True
                        changed_edge = "{0}-{1}".format(edge_rmv.start, edge_rmv.end)
    else:
        while not found:
            #Searches the list for the edge requested
            ##Warning: It will raise a StopIteration exception if no matching edge is found
            if edge_to_remove:
                rnd_edge = next(edge for edge in edge_ln if edge.name == edge_to_remove)
            else:
                #Chooses an edge randomly
                rnd_edge = rnd.choice(edge_ln)
                edge_old_name = rnd_edge.name
            #Not one of the top edges
            if rnd_edge.flow not in ranked_edges:
                #Chooses 2 random nodes
                node1 = rnd.choice(node_list)
                node2 = rnd.choice(node_list)
                #Checks if the 2 nodes are equal or they are an OD pair
                if not (node1 == node2 or (str(node1.name + '|' + node2.name) in od_matrix)):
                    #Changes the edge start and end
                    if complementary_edges:
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

                    if complementary_edges:
                        #Changes the complementary edges, if it has one
                        if has_comp_edge:
                            comp_edge.start = node2.name
                            comp_edge.end = node1.name

                    #Checks if the graph is connected, if it is, then the function is over and a new graph
                    ##has been found
                    if export_to_igraph(node_list, edge_ln).is_connected():
                        found = True
                        changed_edge = "{0}_{1}-{2}".format(edge_old_name, node1.name, node2.name)

    return edge_ln, changed_edge

def print_results(net_name, changed_edges_list, iterations, UE, SO, PoA, edge_list):
    """
    Prints the results in a table.
    In:
        net_name:String = Name of the network.
        changed_edges_list:List = List of the changes made in the edges.
        iterations:Integer = Number of iterations in the MSA.
        UE:Float = User equilibrium.
        SO:Float = System optimal.
        PoA:Float = Price of Anarchy.
        edge_list:List = List of edges.
    """
    #Creates the name of the network correctly in the form: network_name_original + _change1_change2
    net_name = get_network_name(net_name, changed_edges_list)

    #Prints some kind of table
    print('#Network name = {0}\t# of iterations (MSA) = {1}'.format(net_name, iterations))
    print('#UE\tSO\tPoA\tEach edge flow (MSA)')
    print('{0}\t{1}\t{2}\t{3}'.format(UE, SO, PoA, [(e.start + '-' + e.end + ', ', e.flow) for e in
                                      sorted(edge_list, key=lambda x:x.start)]))

def get_network_name(net_name, changed_edges_list):
    """
    Given the network's base name and a list of changed edges, it creates a new name for the
    network.
    In:
        net_name:String = Network's base name.
        changed_edges_list:List = List of changed edges.
    Out:
        net_name:String = New network's name.
    """
    for change in changed_edges_list:
        net_name += '_' + change

    return net_name

def rank_edges(edge_list, n):
    """
    Returns a list with the n edge with most flow.
    In:
        edge_list:List = Edge list of the network.
        n:Integer = Number of top elements to choose.
    Out:
        ranked_edges:List = List with the top n edges on flow.
    """
    return [edge.flow for edge in sorted(edge_list, key=lambda x:x.flow, reverse=True)[:n+1]]

def main():
    """
    Upper level function. It calls the other functions in an orderly way.
    Parser inputs:
        file:String = The absolute path to the network file.
        iterations:Integer = Number of iterations in the MSA run.
        changes:Integer = Number of edges to change in the algorithm.
        k:Integer = Number of routes for the KSP algorithm.
        complementary_edges:Boolean = If it is to change only one direction of the edge.
    """
    #Parser things for the parameters
    prs = ArgP.ArgumentParser(formatter_class=ArgP.ArgumentDefaultsHelpFormatter,
                                  description="""
                                              Network Disturbance System is a software that disturbs
                                              a traffic network (graph) by removing 1 random edge
                                              and inserting another with the same attributes but
                                              with different start and end nodes.\n
                                              V2.0
                                              """)
    prs.add_argument("-f", dest="file", required=True, help="The network file.\n")
    prs.add_argument("-i", "--iterations", type=int, default=1000, help="Number of iterations (MSA).\n")
    prs.add_argument("-c", "--changes", type=int, default=1, help="Number of changes in the network.\n")
    prs.add_argument("-k", type=int, default=8, help="Number of routes for KSP algorithm.\n")
    prs.add_argument("-ce", "--complementary_edges", action="store_true", default=False,
                     help="If it is to change both directions of the edge.\n")
    prs.add_argument("-jr", "--just_remove", action="store_true", default=False,
                     help="If it is only to remove edges and not add any afterwards.\n")
    prs.add_argument("-e", "--edge", type=str, default='',
                     help="Specific edge to change (CASE SENSITIVE).\n")
    prs.add_argument("-re", "--ranked_edges", type=int, default=0,
                     help="Number of top edges to not remove (random removing/changing).\n")
    prs.add_argument("-fod", "--flow_per_route_per_od", action="store_true", default=False,
                     help="If it is only to print the flow per route per OD pair (MSA).\n")
    args = prs.parse_args()

    #Network name
    net_name = os.path.basename(args.file).split('.')[0]

    #List of the changed edges
    changed_edges = []

    #Number of changes made in the edges
    changes = 0

    #Specific edge to change
    edge_to_remove = args.edge

    #Start of the algorithm
    #Gets the original nodes and edges
    nodes, edges, od_matrix, ue, so, PoA, od_routes_flow = assignment(net_file=args.file, iterations=args.iterations)
    #List of edges to safeguard
    ranked_edgs = rank_edges(edges, args.ranked_edges)
    #Gets the original graph
    graph = export_to_igraph(nodes, edges, with_cost=True)

    #Prints the results on-screen
    print_results(net_name, changed_edges, args.iterations, ue, so, PoA, edges)

    #Prints the flow per route per OD pair
    if args.flow_per_route_per_od:
        print("#Flow per route per OD pair:")
        for od in od_matrix:
            print("{}".format(od))
            for route in od_routes_flow[od]:
                print("\t{0} = {1} vehicles".format(route, od_routes_flow[od][route][1]))


    #Coupling call
    print("#Routes:")
    Coup.calculate_coupling(args.file, None, None, args.k, output=True)
    #While loop for changing the edges of the graph
    while changes < args.changes:
        #Resets the flow and the cost in each edge
        for edge in edges:
            edge.flow = 0
            edge.update_cost()

        #Modified edges of the graph
        edges, changed_edge = change_edges(nodes, edges, od_matrix, args.complementary_edges,
                                           just_remove=args.just_remove,
                                           edge_to_remove=edge_to_remove, ranked_edges=ranked_edgs)
        #Append to the list of changes if it's not None
        changed_edges.append(changed_edge)
        #Number of changes made in the edges
        changes += 1

        #Can ignore the output of edges, nodes and od_matrix as they don't change
        _, _, _, ue, so, PoA, od_routes_flow = assignment(iterations=args.iterations, edge_list=edges,
                                          node_list=nodes, od_matrix=od_matrix)

        #Prints the results on-screen
        print_results(net_name, changed_edges, args.iterations, ue, so, PoA, edges)

        #Resets the flow and the cost in each edge
        for edge in edges:
            edge.flow = 0
            edge.update_cost()

        #Coupling call
        print("#Routes:")
        Coup.calculate_coupling(get_network_name(net_name, changed_edges), None, None, args.k,
                                edge_list=edges, node_list=nodes, od_matrix=od_matrix, output=True)
        #Resets edge
        edge_to_remove = ''


if __name__ == '__main__':
    main()
