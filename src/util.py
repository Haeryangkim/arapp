import cv2
import sys
from datetime import datetime
import numpy as np


def unique_rectangles(rectangles, tolerance=5):
    rectangles = np.array(rectangles)
    unique_rectangles = [rectangles[0]]

    for i in range(1, len(rectangles)):
        match_found = any(np.allclose(rect, rectangles[i], atol=tolerance) for rect in unique_rectangles)
        if not match_found:
            unique_rectangles.append(rectangles[i])

    return np.array(unique_rectangles)


class Log(object):
    def __init__(self):
        self.orgstdout = sys.stdout
        self.log = open("log.txt", "a")
        self.history = ""

    def write(self, msg):
        self.orgstdout.write(msg)
        self.history += msg
        self.log.write(msg.replace("\n", " [%s]\n" % str(datetime.now())))

    # self.history.append(msg)


def cust_range(*args, rtol=1e-05, atol=1e-08, include=[True, False]):
    """
    Combines numpy.arange and numpy.isclose to mimic
    open, half-open and closed intervals.
    Avoids also floating point rounding errors as with
    >>> numpy.arange(1, 1.3, 0.1)
    array([1. , 1.1, 1.2, 1.3])

    args: [start, ]stop, [step, ]
        as in numpy.arange
    rtol, atol: floats
        floating point tolerance as in numpy.isclose
    include: boolean list-like, length 2
        if start and end point are included
    """
    # process arguments
    if len(args) == 1:
        start = 0
        stop = args[0]
        step = 1
    elif len(args) == 2:
        start, stop = args
        step = 1
    else:
        assert len(args) == 3
        start, stop, step = tuple(args)

    # determine number of segments
    n = (stop - start) / step + 1

    # do rounding for n
    if np.isclose(n, np.round(n), rtol=rtol, atol=atol):
        n = np.round(n)

    # correct for start/end is exluded
    if not include[0]:
        n -= 1
        start += step
    if not include[1]:
        n -= 1
        stop -= step

    return np.linspace(start, stop, int(n))


def crange(*args, **kwargs):
    return cust_range(*args, **kwargs, include=[True, True])


def orange(*args, **kwargs):
    return cust_range(*args, **kwargs, include=[True, False])
