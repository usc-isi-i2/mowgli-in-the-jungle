import sys
sys.path.append('../')

import utils.grounding.uci_utils as grounding

sentences=['When boiling butter, when it’s ready, you can Pour it onto a plate']
print(grounding.ground_dataset(sentences))
