import sys
sys.path.append('../')
import utils.general as utils

import utils.gt.io_utils as gtio

mowgli_nodes='/Users/filipilievski/mowgli-dev-framework/kb/nodes_v002.csv'
mowgli_edges='/Users/filipilievski/mowgli-dev-framework/kb/edges_v002.csv'
output_gml='/Users/filipilievski/mowgli-dev-framework/kb/graph.graphml'

gtio.transform_to_graphtool_format(mowgli_nodes, mowgli_edges, output_gml, True)
g=gtio.load_graph(output_gml)
print(g.num_edges())
