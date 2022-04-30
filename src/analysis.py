from enum import IntEnum
from math import log2
from collections import Counter
from sys import stderr

try:
    from scipy.stats import chi2, kstest, uniform
except ImportError:
    print('the scipy library is not installed. \n'
          'Use `pip install scipy` to install it', file=stderr)
    exit(1)


class ResultFlag(IntEnum):
    NONE = 0
    SINGLE_BYTE_PATTERN = 1
    NOT_RANDOM = 2
    RANDOM = 3
    RANDOMNESS_SUSPICIOUSLY_HIGH = 4


class ShannonsEntropy:
    def __init__(self, sector_size, rand_lim=None, sus_rand_lim=None):
        self.sector_size = sector_size

    def calc(self, buf):
        """ Calculates and returns sample entropy on byte level for
        the argument and single byte pattern if present or None.

        This code has been adapted from
        https://gitlab.com/cryptsetup/cryptsetup/-/blob/master/misc/keyslot_checker/chk_luks_keyslots.c#L81
        """
        freq = Counter(buf)
        if len(freq) == 1:
            return 0.0, ResultFlag.SINGLE_BYTE_PATTERN, freq.popitem()[0]

        entropy = sum(f * log2(f) for f in freq.values()) / self.sector_size - log2(self.sector_size)

        normalized_entropy = abs(entropy) / 8

        return normalized_entropy, ResultFlag.NONE, None


class ChiSquare8:
    def __init__(self, sector_size, rand_lim=0.9999, sus_rand_lim=0.0001):
        self.expected = sector_size / 256
        if self.expected < 5:
            print('warn: the sector size seems to be too small to use with this calculation method.', file=stderr)
        self.random_limit = chi2.ppf(rand_lim, 255) * self.expected
        self.sus_random_limit = chi2.ppf(sus_rand_lim, 255) * self.expected

    def calc(self, buf):
        counts = Counter(buf)
        if len(counts) == 1:
            return 0.0, ResultFlag.SINGLE_BYTE_PATTERN, counts.popitem()[0]

        chis = sum((counts[i] - self.expected) ** 2 for i in range(256))
        if chis < self.sus_random_limit:
            return 0.0, ResultFlag.RANDOMNESS_SUSPICIOUSLY_HIGH, None
        if chis <= self.random_limit:
            return 1.0, ResultFlag.RANDOM, None
        return 0.5, ResultFlag.NOT_RANDOM, None


class ChiSquare4:
    def __init__(self, sector_size, rand_lim=0.9999, sus_rand_lim=0.0001):
        self.expected = sector_size / 8
        if self.expected < 5:
            print('warn: the sector size seems to be too small to use with this calculation method.', file=stderr)
        self.random_limit = chi2.ppf(rand_lim, 15) * self.expected
        self.sus_random_limit = chi2.ppf(sus_rand_lim, 15) * self.expected

    def calc(self, buf):
        counts = Counter(buf)
        if len(counts) == 1:
            return 0.0, ResultFlag.SINGLE_BYTE_PATTERN, counts.popitem()[0]

        vals = [0] * 16
        for byte, count in counts.items():
            vals[byte & 15] += count
            vals[byte >> 4] += count
        chis = sum((i - self.expected) ** 2 for i in vals)
        if chis < self.sus_random_limit:
            return 0.0, ResultFlag.RANDOMNESS_SUSPICIOUSLY_HIGH, None
        if chis <= self.random_limit:
            return 1.0, ResultFlag.RANDOM, None
        return 0.5, ResultFlag.NOT_RANDOM, None


class ChiSquare3:
    N = 3

    def __init__(self, sector_size, rand_lim=0.9999, sus_rand_lim=0.0001):
        self.single_byte_pattern_count = (sector_size * 8) // self.N
        self.expected = ((sector_size * 8) // self.N) / (2 ** self.N)
        if self.expected < 5:
            print('warn: the sector size seems to be too small to use with this calculation method.', file=stderr)
        self.random_limit = chi2.ppf(rand_lim, 2 ** self.N - 1) * self.expected
        self.sus_random_limit = chi2.ppf(sus_rand_lim, 2 ** self.N - 1) * self.expected

    def calc(self, buf):
        vals = [0] * (2 ** self.N)
        rem = 0
        bits = 0
        for byte in buf:
            for offset in range(8):
                rem = (rem << 1) | ((byte >> (7 - offset)) & 1)
                bits += 1
                if bits == self.N:
                    vals[rem] += 1
                    bits = 0
                    rem = 0
        if vals[0] == self.single_byte_pattern_count:
            return 0.0, ResultFlag.SINGLE_BYTE_PATTERN, 0
        if vals[-1] == self.single_byte_pattern_count:
            return 0.0, ResultFlag.SINGLE_BYTE_PATTERN, 255
        chis = sum((i - self.expected) ** 2 for i in vals)
        if chis < self.sus_random_limit:
            return 0.0, ResultFlag.RANDOMNESS_SUSPICIOUSLY_HIGH, None
        if chis <= self.random_limit:
            return 1.0, ResultFlag.RANDOM, None
        return 0.5, ResultFlag.NOT_RANDOM, None


class ChiSquare1:
    def __init__(self, sector_size, rand_lim=0.9999, sus_rand_lim=0.0001):
        self.single_byte_pattern_count = sector_size * 8
        self.expected = sector_size * 4
        if self.expected < 5:
            print('warn: the sector size seems to be too small to use with this calculation method.', file=stderr)
        self.random_limit = chi2.ppf(rand_lim, 1) * self.expected
        self.sus_random_limit = chi2.ppf(sus_rand_lim, 1) * self.expected

    def calc(self, buf):
        set_bits = sum(map(int.bit_count, buf))
        if set_bits == 0:
            return 0.0, ResultFlag.SINGLE_BYTE_PATTERN, 0
        if set_bits == self.single_byte_pattern_count:
            return 0.0, ResultFlag.SINGLE_BYTE_PATTERN, 255
        chis = 2 * (set_bits - self.expected) ** 2
        if chis < self.sus_random_limit:
            return 0.0, ResultFlag.RANDOMNESS_SUSPICIOUSLY_HIGH, None
        if chis <= self.random_limit:
            return 1.0, ResultFlag.RANDOM, None
        return 0.5, ResultFlag.NOT_RANDOM, None


class KSTest:
    def __init__(self, sector_size, rand_lim=0.9999, sus_rand_lim=0.0001):
        self.p_rand_lim = 1 - rand_lim
        self.p_sus_rand_lim = 1 - sus_rand_lim
        self.dist = uniform(0, 255).cdf

    def calc(self, buf):
        _, p = kstest(bytearray(buf), self.dist, mode='asymp')
        if p > self.p_sus_rand_lim:
            return 0.0, ResultFlag.RANDOMNESS_SUSPICIOUSLY_HIGH, None
        if p < self.p_rand_lim:
            return 0.0, ResultFlag.NOT_RANDOM, None
        return 0.5, ResultFlag.RANDOM, None


analysis_methods = {
    'shannon': ShannonsEntropy,
    'chi2-8': ChiSquare8,
    'chi2-4': ChiSquare4,
    'chi2-3': ChiSquare3,
    'chi2-1': ChiSquare1,
    'kstest': KSTest
}
