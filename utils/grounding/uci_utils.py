import sys
sys.path.append('../../mowgli-uci')
sys.path.append('../mowgli-uci')

import graphify
import link

def ground_dataset(sentences):
    graphs=graphify.graphify_dataset(sentences)
    linked_graphs=link.link_dataset(graphs)

    return linked_graphs
