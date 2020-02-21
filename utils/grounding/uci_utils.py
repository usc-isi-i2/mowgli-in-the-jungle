import sys
sys.path.append('../../mowgli-uci')
sys.path.append('../mowgli-uci')
sys.path.append('mowgli-uci')

import graphify
import link

def get_concepts(nodes, normalize_nodes):
	concepts=[]
	for node_id, node_data in nodes.items():
		best_candidate=node_data['candidates'][-1]["uri"]
		if normalize_nodes:
			best_candidate=best_candidate.lstrip('/c/en/')
		concepts.append(best_candidate)
	return concepts

def generate_instances(l):
	for graph in l:
		yield graph

def ground_dataset(sentences, embedding_file):
    graphs=graphify.graphify_dataset(sentences)
    print('GRAPHIFY', graphs)
    linked_graphs=link.link(generate_instances(graphs), embedding_file=embedding_file)
    print('LINKIFY', linked_graphs)
    return linked_graphs
