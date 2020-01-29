The purpose of this file is to keep track of utility functions that we want to have together with the team member(s) that are working on them.

Status is one of: not started, in progress, finished. Further details on the status should be placed in `Comment`.

| Function name | Input params | Output params | Function description | Contributor(s) | Status | Comment | File |
| ------------- | ------------- | ------------- | -------------------------- | ------------- | ------------- | ------------- | ------------- |
| transform_to_graphtool_format | `mowgli_nodes_path`, `mowgli_edges_path`, `graphml_path`, `do_gt` | `g` | Load nodes and edges from the MOWGLI structure into graph-ml formats. | Ehsan | implemented v1 | | `utils/graph-tool/io_utils.py` |
| load_graph | `graph_path` | `g` | Load an existing graph in GT or graphml format. | Ehsan | implemented v1 | | `utils/graph-tool/io_utils.py` |
| compute_paths | `from`, `to`, `L`, `**kwargs` | paths | Efficiently compute paths of max length `L` from one node to another. | | | | 
| syntax_parser | `text`, `**kwargs` | `result` | Parse provided text to produce a resulting SRL-like output, e.g., using HCI's parser. | | | |
| frame_parser | `text`, `**kwargs` | `result` | Parse provided text to produce a resulting output mapped to FrameNet. | | | |
| obtain_nodes_by_lexical_matching | `graph`, `labels`, `fields=['labels', 'aliases']`, `**kwargs` | `node_ids` | Obtain list of node IDs based on lexical matching of a bunch of labels over the fields "labels" and/or "aliases". | | | |
| obtain_node_labels | `graph`, `node_ids`, `fields=['labels', 'aliases']`, `**kwargs` | `labels` | Obtain node labels based on a list of node IDs. | | | |
| obtain_associated_nodes | `graph`, `node_ids`, `**kwargs` | `node_ids` | Obtain list of node IDs that are directly connected with the nodes in `node_ids` (either as subjects or objects). | | | |
| run_lm | `model`, `tokenizer`, `config_json`, `data` | `output` | Run a language model on the sentences in `data`, and produce a list of representations called `output`. | | | |
