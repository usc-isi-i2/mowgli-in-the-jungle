import random
from typing import List, Any
import json

from classes import Dataset, Entry
from predictor.predictor import Predictor

import utils.grounding.uci_utils as grounding
import utils.general as utils

emb_filename = '/nas/home/ilievski/mowgli-in-the-jungle/numberbatch-en-19.08.txt'

class MowgliPredictor(Predictor):

	def preprocess(self, part_data:List, partition:str, normalize_nodes:bool = True) -> Any:

		if not part_data: 
			return []

		sentences=[]
		output=[]
		output_file=open('%s.jsonl' % partition, 'w')

		# Create a list of sentences from both the question and the answers
		for entry in part_data:
			sentences.append(' '.join(entry.question))
			for answer in entry.answers:
				if answer: # to skip empty answers (which are added to offset the answer id in the first place)
					sentences.append(answer)
		
		sent_per_question=int(len(sentences)/len(part_data))
		# run grounding
		grounded_data=grounding.ground_dataset(sentences, embedding_file=emb_filename)

		#customize output
		for grounded_entry in utils.divide_chunks(grounded_data, sent_per_question):
			question=grounded_entry[0]['sentence']
			q_concepts=grounding.get_concepts(grounded_entry[0]['nodes'], normalize_nodes)

			for ans_id in range(1, sent_per_question):
				entry_json={}
				entry_json['sent']=question
				entry_json['qc']=q_concepts 
				entry_json['ans'] = grounded_entry[ans_id]['sentence']
				entry_json['ac']=grounding.get_concepts(grounded_entry[ans_id]['nodes'], normalize_nodes)
				
				output.append(entry_json)
				output_file.write(json.dumps(entry_json) + '\n')
		output_file.close()
		return part_data #output
        
	def train(self, train_data:List, dev_data: List) -> Any:
		return None

	def predict(self, model: Any, entry: Entry) -> List:
		question=entry.question
		answers=entry.answers

		answer=random.randint(0,len(answers)-1)
		while answers[answer]=='':
			answer=random.randint(0,len(answers)-1)
		return str(answer)

