class Entry(object):
    """A single training/dev/test entry for simple sequence classification."""

    def __init__(self, split, id, question, answers, intro='', correct_answer=None, metadata={}):
        """Constructs an Entry.
        Args:
          split: string. Which data partition (train-dev-test) is the entry from.
          id: string. Unique id for the entry.
          intro: (Optional) string. Possible introduction to the question, giving a context or an overarching label.
          question: string. The actual question (which might be formed in concatenation with each of the answers) 
          answers: list. A list of all possible answers/hypotheses associated with the question.
          correct_answer: (Optional) string. Order number of the correct answer, zero-padded. Applicable to train and dev splits only.
          metadata: (Optional) dict. Any other relevant metadata per entry, such as domain or image information.
        """
        self.split=split
        self.id=id
        self.intro=intro
        self.question=question
        self.answers=answers
        self.correct_answer=correct_answer
        self.metadata=metadata


class Dataset(object):
    """Dataset object containing a list of entries."""

    def __init__(self, name, train=[], dev=[], test=[]):
        """Constructs a dataset.
        Args:
            name: string. The official name of this dataset.
            entries: (Optional) list. A list of entries in this dataset.
        """
        self.name=name
        self.train=train
        self.dev=dev
        self.test=test
