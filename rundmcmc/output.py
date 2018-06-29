import json
import math
from collections import Counter


def p_value_report(score_name, ensemble_scores, initial_plan_score):
    """
    p_value_report takes an iterable :ensemble_scores: (scores computed on the
    ensemble seen in the random walk) and the :initial_plan_score: and returns
    a report like page 5 of Moon's PA analysis, including the fraction of plans
    in the ensemble that scored higher than the initial score and the p-value
    that the plan is chosen randomly as determined by the 'square root of
    2*epsilon' theorem.
    """
    count_higher = Counter(score > initial_plan_score for score in ensemble_scores)
    total_scores = sum(count_higher.values())
    fraction_higher = count_higher[True] / total_scores
    fraction_lower = count_higher[False] / total_scores

    # By Chikina-Frieze-Pegden, if a plan scores in the highest fraction_higher of all
    # plans seen in a random walk, then it has less than sqrt(2 * fraction_higher)
    # probability of being chosen randomly from the sample space. (Paraphrasing Moon's
    # PA report).

    p_value = math.sqrt(2 * fraction_higher)
    opposite_p_value = math.sqrt(2 * fraction_lower)

    report = {'name': score_name,
              'initial_plan_score': initial_plan_score,
              'fraction_higher': fraction_higher,
              'p_value': p_value,
              'opposite_p_value': opposite_p_value}
    return report


def pipe_to_handlers(iterable, handlers):
    for element in iterable:
        yield (handlers[key](element) for key in handlers for element in iterable)


class Histogram:
    """
    A histogram with fixed bins, determined by the number of bins and the
    bounds for values.

    Anthony is working on the super smart histogram that does the binning for you.
    """

    def __init__(self, bounds, number_of_bins):
        self.bounds = bounds
        self.number_of_bins = number_of_bins

        left, right = bounds
        self.bin_size = (right - left) / number_of_bins

        self.bins = self.generate_bins()

    def count(self, values):
        """
        :values: iterable
        :returns: a Counter counting how many values appeared in each bin.
        """
        return Counter(self.find_bin(value) for value in values)

    def find_bin_index(self, value):
        """
        find_bin conducts a binary search to find the right bin for the given value.
        """
        left, right = self.bounds
        return math.floor((value - left) / self.bin_size)

    def find_bin(self, value):
        return self.bins[self.find_bin_index(value)]

    def generate_bins(self):
        left, right = self.bounds
        for n in range(self.number_of_bins):
            yield (left + n * self.bin_size, left + (n + 1) * self.bin_size)


class ChainOutputTable:
    def __init__(self, data=None):
        if not data:
            data = list()
        self.data = data

    def append(self, row):
        self.data.append(row)

    def json(self, row):
        return json.dumps(self.data)

    def __iter__(self):
        return self

    def __next__(self):
        return self.data

    def __getitem__(self, key):
        if isinstance(key, int):
            return self.data[key]
        else:
            return [row[key] for row in self.data]

    def district(self, district_id):
        return get_from_each(self.data, district_id)


def get_from_each(table, key):
    return [{header: row[header][key] for header in row if key in row[header]}
            for row in table]
