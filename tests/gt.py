import sys
sys.path.append('../')
import utils.general as utils

import utils.gt.io_utils as gtio

#datadir='~/mowgli-in-the-jungle/kb/'
datadir='/nas/home/ilievski/mowgli-in-the-jungle/kb/'
mowgli_nodes=f'{datadir}nodes_v002.csv'
mowgli_edges=f'{datadir}edges_v002.csv'
output_gml=f'{datadir}graph.graphml'

gtio.transform_to_graphtool_format(mowgli_nodes, mowgli_edges, output_gml, True)
g=gtio.load_graph(output_gml.replace(".graphml", '.gt'))

print(g.num_edges())
