class Choice(object):
    """A single answer for a given question."""

    def __init__(self, text, label):
        """Constructs an Answer.
        Args:
            text: string. Text of the answer, e.g., 'wants to go home'.
            label: string. A label/identifier of this answer, e.g., 'B'.
        """
        self.text = text
        self.label = label


class Entry(object):
    """A single training/dev/test entry for simple sequence classification."""

    def __init__(self, split, id, context, question, answers, correct_answer=None, qc=None, ac=None, metadata={}):
        """Constructs an Entry.
        Args:
          split: string. Which data partition (tune-dev-test) is the entry from.
          id: string. Unique id for the entry.
          context: string. Context preceding the question.
          question: string. A list of several components, including the question context, the actual question, or pre-post situations (see the README for concrete details).
          answers: list. A list of all possible answers/hypotheses associated with the question. Each answer is a member of the Choice class.
          labels: list. Which labels does this entry have.
          correct_answer: (Optional) string. Order number of the correct answer, zero-padded. Applicable to tune and dev splits only.
          qc: (Optional) string. Concepts grounded from the question.
          ac: (Optional) string. Concepts grounded from the answer.
          metadata: (Optional) dict. Any other relevant metadata per entry, such as domain or image information.
        """
        self.split = split
        self.id = id
        self.context = context
        self.question = question
        self.answers = answers
        self.labels = self.get_labels()
        self.correct_answer = correct_answer
        self.qc = qc
        self.ac = ac
        self.metadata = metadata

    def get_labels(self):
        return [x.label for x in self.answers]


class Dataset(object):
    """Dataset object containing a list of entries."""

    def __init__(self, name, train=[], dev=[], test=[], trial=[]):
        """Constructs a dataset.
        Args:
            name: string. The official name of this dataset.
            train: list. A list of entries in this dataset.
            dev: list. A list of entries in this dataset.
            test: list. A list of entries in this dataset.
            trial: list. A list of entries in this dataset.
        """
        self.name = name
        self.train = train
        self.dev = dev
        self.test = test
        self.trial = trial
