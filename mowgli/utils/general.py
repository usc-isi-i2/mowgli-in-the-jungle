import random

from sklearn.metrics import accuracy_score
from typing import List, Iterable, Any
import os
import pkgutil


def divide_chunks(l, n):
    # looping till length l
    for i in range(0, len(l), n):
        yield l[i:i + n]


def load_predictions(input_file: str) -> List[str]:
    lines = []
    input_data = pkgutil.get_data('mowgli', input_file).decode()
    rows = input_data.split('\n')
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


import importlib


class LazyLoader:
    def __init__(self, lib_name):
        self.lib_name = lib_name
        self._mod = None

    def __getattrib__(self, name):
        if self._mod is None:
            self._mod = importlib.import_module(self.lib_name)
        return getattr(self._mod, name)


_missing = object()


class CachedProperty(object):
    """A decorator that converts a function into a lazy property.  The
    function wrapped is called the first time to retrieve the result
    and then that calculated result is used the next time you access
    the value::

        class Foo(object):

            @CachedProperty
            def foo(self):
                # calculate something important here
                return 42

    The class has to have a `__dict__` in order for this property to
    work.
    """

    # implementation detail: this property is implemented as non-data
    # descriptor.  non-data descriptors are only invoked if there is
    # no entry with the same name in the instance's __dict__.
    # this allows us to completely get rid of the access function call
    # overhead.  If one choses to invoke __get__ by hand the property
    # will still work as expected because the lookup logic is replicated
    # in __get__ for manual invocation.

    def __init__(self, func, name=None, doc=None):
        self.__name__ = name or func.__name__
        self.__module__ = func.__module__
        self.__doc__ = doc or func.__doc__
        self.func = func

    def __get__(self, obj, type=None):
        if obj is None:
            return self
        value = obj.__dict__.get(self.__name__, _missing)
        if value is _missing:
            value = self.func(obj)
            obj.__dict__[self.__name__] = value
        return value


def reservoir_sampling(iterable: Iterable, samplesize: int) -> List[Any]:
    """
    The method samples a set of `samplesize` elements from the given `iterable` object.
    Args:
        iterable: Iterable[Any]
        samplesize: int

    Returns:
        List[Any]

    """
    results: List[Any] = []
    iterator = iter(iterable)
    # Fill in the first samplesize elements:
    for _ in range(samplesize):
        results.append(next(iterator))
    random.shuffle(results)  # Randomize their positions
    for i, v in enumerate(iterator, samplesize):
        r = random.randint(0, i)
        if r < samplesize:
            results[r] = v  # at a decreasing rate, replace random items

    if len(results) < samplesize:
        raise ValueError("Sample larger than population.")
    return results
