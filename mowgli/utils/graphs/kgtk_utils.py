import lazy_import
# import kgtk.utils.gt.io_utils as gtio
gtio = lazy_import.lazy_module('kgtk.utils.gt.io_utils')

# import graph_tool.topology as gtt
gtt = lazy_import.lazy_module('graph_tool.topology')

#import graph_tool.all as gtall
gtall = lazy_import.lazy_module('graph_tool.all')

from graph_tool import GraphView, Graph
from graph_tool.topology import similarity

def make_filter(g, concepts, fltr):
    fltr.a=False
    for n in concepts:
        #v=gtall.find_vertex(g, prop=g.properties[('v', '_graphml_vertex_id')], match=str(n))[0]
        v=qtqu.get_nodes_by_node_prop(g, '_graphml_vertex_id', n)[0]
        fltr[v]=True
        for vn in v.out_neighbors():
            fltr[vn]=True
    return fltr

def reason_over_paths(g1, g2):
    return similarity(g1, g2)

def produce_answer(entry, g, prune):
    qc_fltr = g.new_vertex_property("bool")
    qc_fltr=make_filter(g, entry.qc, qc_fltr)
    qg = GraphView(g, qc_fltr)
    qg=Graph(qg, prune=prune)

    best_score=0.0
    answer=-1
    for i, ac in enumerate(entry.ac):
        ac_fltr = g.new_vertex_property("bool")
        ac_fltr=None #make_filter(g, ac, ac_fltr)
        ag=GraphView(g, ac_fltr)
        ag=Graph(ag, prune=prune)
        score=reason_over_paths(qg, ag)
        if score>best_score:
            best_score=score
            answer=i
        del ac_fltr 
    del qc_fltr
    return answer

def load_graph(graph_name):
    return gtio.load_gt_graph(graph_name)

