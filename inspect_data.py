import classes

import glob
import pickle
from collections import Counter

parts=['train', 'dev']
for f in glob.glob('data/*.bin'):
    with open(f, 'rb') as afile:
        data=pickle.load(afile)

    print()
    print('#' * 30 + f + '#' * 30)

    for part in parts:
        answers=[]
        len_q=[]
        len_i=[]
        entries=getattr(data, part)
        for entry in entries:
            answers.append(entry.correct_answer)
            len_q.append(len(' '.join(entry.question)))

        print()
        print(part.upper())
        print('Number of entries: %d' % len(answers))
        print('Number of possible answers per entry: %d' % len([a for a in entry.answers if a]))
        print('Answer distribution:')
        print(Counter(answers))
        print('Average length of a question (in characters): %.2f' % (sum(len_q)/len(len_q)))
