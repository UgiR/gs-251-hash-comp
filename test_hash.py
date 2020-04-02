import glob
import unittest
import ctypes
import logging
from scipy.stats import chisquare
import numpy as np
from gradescope_utils.autograder_utils.decorators import leaderboard, partial_credit


class TestHash(unittest.TestCase):

    def setUp(self):
        '''
        The submitted hash function is in C++. We load the previously compiled shared object.

        :return: None
        '''
        self.lib = ctypes.cdll.LoadLibrary('/autograder/source/hash.so')
        self.upper_bound = 2 ** 16 - 1  # max hash value, ret type of hash function will be unisgned short
        self.n_bins = 257  # number of bins. this divides nicely, leaving each bin responsible for 15 values
        self.bin_size = self.upper_bound / self.n_bins  # 65535 / 257 = 255
        self.bins = [i for i in range(0, self.upper_bound + 1, int(self.bin_size))]  # to be used for numpy

    def hash_(self, string):
        '''
        This function is the interface to the submitted hash function. This is what we will be testing.

        :param string: The string to hash.
        :return: Hash value.
        '''
        return self.lib.hash(bytes(string, 'utf-8'))

    def get_data_dirs(self):
        '''
        Returns a list of file paths, as strings, for each data set in /data
        '''
        return [file for file in glob.glob('/autograder/source/data/*')]

    def idempotent(self, lst):
        '''
        The idea is to hash every value in the provided list twice, then check that the resulting hash for each value
        was the same in both instances.

        :param lst: The list of values to hash.
        :return: True/false: whether the hash_ function is idempotent (in reality, we cannot reliably test this, but
        for our purposes, this will suffice.)
        '''

        # dictionary to keep track of hashes
        hash_values = dict()

        # we will be mutating the list, so make a copy
        lst = lst.copy()

        # shuffle values, hash and store into dictionary
        np.random.shuffle(lst)
        for s in lst:
            val = self.hash_(s)
            hash_values[s] = val

        # shuffle again, hash again, and check that resulting hashes for each value are the same
        np.random.shuffle(lst)
        for s in lst:
            val = self.hash_(s)
            if val != hash_values[s]:
                return False

        return True

    def is_uniform(self, distribution):
        '''
        Performs the Chi-Square test on the given distribution.

        :param distribution: Frequencies of values. In other words, this is the list containing the sizes of all
        bins/buckets.
        :return: p-value [0,1]: probability of uniform distribution
        '''
        result = chisquare(distribution)
        return result[1]

    @leaderboard('points')
    @partial_credit(100_000)
    def test_score_hash(self, set_leaderboard_value=None, set_score=None):
        """Evaluate hash function"""

        log = logging.getLogger('autograder')

        score = 0  # starting score, this will be adjust throughout testing

        for filename in self.get_data_dirs():
            with open(filename) as f:

                lines = f.readlines()

                # the hash function must always return the same hash for a given input
                if not self.idempotent(lines):
                    self.fail('The hash function must be idempotent')

                # we hash every single line and store the resulting hashes
                hashes = [self.hash_(s) for s in lines]

                # let's sort out all of the resulting hashes into 'bins'
                histo = np.histogram(hashes, bins=self.bins)

                #  adjust score based on chi-square p value
                p = self.is_uniform(histo[0])

                data_score = 50_000 * p
                log.info(data_score)
                score += data_score

        set_score(score)
        set_leaderboard_value(int(score))
