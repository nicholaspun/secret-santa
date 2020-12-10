import functools
import random

def createDerangment(n):
    """Returns a derangement of the list [0..n]

    Parameters
    ----------
    n : Integer
        Length of derangement
    """
    derangement = list(range(n))
    while functools.reduce(lambda init, tp: init or (tp[0] == tp[1]), enumerate(derangement), False):
        random.shuffle(derangement)
    return derangement
