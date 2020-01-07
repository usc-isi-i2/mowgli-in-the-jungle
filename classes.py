class Entry(object):
    """A single training/test entry for simple sequence classification."""

    def __init__(self, split, id, question, answers, intro='', corect_answer=None, metadata={}):
        """Constructs an Entry.
        Args:
          split: string. Which data partition (train-dev-test) is the entry from.
          id: string. Unique id for the entry.
          intro: (Optional) string. Possible introduction to the question, giving a context or an overarching label.
          question: list. If we have a sentence tokenization output, then we use that one (one list element per sentence). If not then we have a single-element array.
          answers: list. A list of all possible answers/hypotheses associated with the question.
          correct_answer: (Optional) int. Order number of the correct answer, zero-padded. Applicable to train and dev splits only.
          metadata: (Optional) dict. Any other relevant metadata per entry, such as domain or image information.
        """
        self.split=split
	self.id=id
	self.question=question
	self.answers=answers
	self.intro=intro
	self.correct_answer=correct_answer
	self.metadata=metadata


class Dataset(object):
    """Dataset object containing a list of entries."""

    def __init__(self, name, entries=[]):
        """Constructs a dataset.
        Args:
            name: string. The official name of this dataset.
            entries: (Optional) list. A list of entries in this dataset.
        """
        self.name=name
        self.entries=entries
