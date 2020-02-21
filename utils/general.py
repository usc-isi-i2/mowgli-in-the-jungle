from sklearn.metrics import accuracy_score
from typing import List
import os

def divide_chunks(l, n):
	# looping till length l 
	for i in range(0, len(l), n):
		yield l[i:i + n]

def load_predictions(input_file: str) -> List[str]:
    lines = []
    with open(input_file, "rb") as f:
        for l in f:
            lines.append(l.decode().strip())
    return lines

def save_predictions(filename, answers):
    if os.path.isfile(filename):
        os.remove(filename)

    with open(filename, "a") as myfile:
        for answer in answers:
            myfile.write(str(answer) + '\n')

def compute_accuracy(gold_answers, pred_answers):
    if len(gold_answers) != len(pred_answers):
        raise Exception("The prediction file does not contain the same number of lines as the "
                        "number of test instances.")

    accuracy = accuracy_score(gold_answers, pred_answers)
    return accuracy
