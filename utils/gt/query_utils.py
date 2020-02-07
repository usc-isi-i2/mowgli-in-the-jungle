import graph_tool as gtmain
import graph_tool.all as gtall

def get_nodes_with_degree(g, deg_from, deg_to):
    u = gtmain.GraphView(g, vfilt=lambda v: v.in_degree()+v.out_degree() in range(deg_from,deg_to))
    return u

def get_nodes_by_node_prop(g, p, v):
    return gtall.find_vertex(g, prop=g.properties[('v', p)], match=v)

def get_edges_by_edge_prop(g, p, v):
    return gtall.find_edge(g, prop=g.properties[('e', p)], match=v)