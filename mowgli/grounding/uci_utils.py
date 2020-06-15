import lazy_import
# from graphify import graphify, link
graphify = lazy_import.lazy_module('graphify.graphify')
link = lazy_import.lazy_module('graphify.link')

##### Helper functions #####

def get_concepts(nodes, normalize_nodes):
    concepts = []
    for node_id, node_data in nodes.items():
        if len(node_data['candidates']):
            best_candidate = node_data['candidates'][0]["uri"]
            if normalize_nodes:
                best_candidate = best_candidate.replace('/c/en/', '')
            concepts.append(best_candidate)
    return concepts


def generate_instances(l):
    for graph in l:
        yield graph


##### API #####

def graphify_sentences(sentences):
    return graphify.graphify_dataset(sentences)


def link_concepts(graphs, embedding_file):
    return link.link(generate_instances(graphs), embedding_file=embedding_file)


def ground_dataset(sentences, embedding_file):
    graphs = graphify_sentences(sentences)
    print('GRAPHIFY', graphs)
    linked_graphs = link_concepts(graphs, embedding_file)
    print('LINKIFY', linked_graphs)
    return linked_graphs
