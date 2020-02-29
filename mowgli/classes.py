class Entry(object):
    """A single training/dev/test entry for simple sequence classification."""

    def __init__(self, split, id, question, answers, intro='', correct_answer=None, qc=None, ac=None, metadata={}):
        """Constructs an Entry.
        Args:
          split: string. Which data partition (train-dev-test) is the entry from.
          id: string. Unique id for the entry.
          question: list. A list of several components, including the question context, the actual question, or pre-post situations (see the README for concrete details).
          answers: list. A list of all possible answers/hypotheses associated with the question.
          correct_answer: (Optional) string. Order number of the correct answer, zero-padded. Applicable to train and dev splits only.
          metadata: (Optional) dict. Any other relevant metadata per entry, such as domain or image information.
        """
        self.split=split
        self.id=id
        self.question=question
        self.answers=answers
        self.correct_answer=correct_answer
        self.qc=qc
        self.ac=ac
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
