import graph_tool as gtmain
import graph_tool.all as gtall
import numpy as np
from collections import defaultdict

import matplotlib.pyplot as plt
plt.rcParams.update({'font.size': 12})

import seaborn as sns
sns.set_style("whitegrid")

#### BASIC STATS ####

def get_num_nodes(g):
    return g.num_vertices()

def get_num_edges(g):
    return g.num_edges()

#### DEGREES ####

def compute_avg_node_degree(g, direction):
    return gtmain.stats.vertex_average(g, direction)

def compute_node_degree_hist(g, direction):
    return gtall.vertex_hist(g, direction, float_count=False)

def get_degree_maxn_counts(g, direction):
    return list(compute_node_degree_hist(g, direction)[0])[:10]

def plot_degrees(degrees, plottype='loglog', base=10, xlabel='', ylabel='', title=''):
    plt.loglog(degrees, basex=base, basey=base)
    plt.ylabel(ylabel)
    plt.xlabel(xlabel)
    plt.title(title)
    plt.show()

#### CENTRALITY ####
    
def compute_betweenness(g):
    bn, be=gtmain.centrality.betweenness(g)
    return bn, be

def compute_pagerank(g):
    return gtmain.centrality.pagerank(g)

def compute_hits(g):
    return gtmain.centrality.hits(g)
    
#### RUN ALL STATS ####
    
def compute_stats(g, direction):
    avg_degree, stdev_degree=compute_avg_node_degree(g, direction)
    nb, eb=compute_betweenness(g)
    hits_eig, hits_hubs, hits_auth=compute_hits(g)
    return {
            'num_nodes': get_num_nodes(g),
            'num_edges': get_num_edges(g),
            'avg_degree': avg_degree,
            'degree_maxn_counts': get_degree_maxn_counts(g, direction),
            'stdev_degree': stdev_degree,
            'node_betweenness': nb,
            'edge_betweenness': eb,
            'node_pagerank': compute_pagerank(g),
            'node_hubs': hits_eig
            }

def get_topN_relations(g, N=10):
    rel_freq=defaultdict(int)
    for i, e in enumerate(g.edges()):
        r=g.edge_properties['predicate'][e]
        rel_freq[r]+=1
    return sorted(rel_freq.items(), key=lambda x: x[1], reverse=True)[:N]
