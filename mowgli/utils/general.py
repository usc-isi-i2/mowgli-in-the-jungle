from sklearn.metrics import accuracy_score
from typing import List
import os
import pkgutil

def divide_chunks(l, n):
	# looping till length l 
	for i in range(0, len(l), n):
		yield l[i:i + n]

def load_predictions(input_file: str) -> List[str]:
    lines = []
    input_data=pkgutil.get_data('mowgli', input_file).decode()
    rows=input_data.split('\n')
    for l in rows:
        lines.append(str(l).strip())
    return lines

def save_predictions(filename, answers, probs):
    if os.path.isfile(filename):
        os.remove(filename)

    with open(filename, "a") as myfile:
        for answer, prob in zip(answers, probs):
            myfile.write(str(answer) + '\t' + ','.join(prob) + '\n')

def compute_accuracy(gold_answers, pred_answers):
    if len(gold_answers) != len(pred_answers):
        raise Exception("The prediction file does not contain the same number of lines as the "
                        "number of test instances.")

    accuracy = accuracy_score(gold_answers, pred_answers)
    return accuracy
