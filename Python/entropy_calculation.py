from math import log2
from collections import Counter
from random import sample


class ShannonsEntropy:
    def __init__(self, sector_size):
        self.sector_size = sector_size
    
    def calc_ent(self, buf):
        """ Calculates and returns sample entropy on byte level for
        the argument and single byte pattern if present or None.

        This code has been adapted from 
        https://gitlab.com/cryptsetup/cryptsetup/-/blob/master/misc/keyslot_checker/chk_luks_keyslots.c#L81
        """
        if len(buf) != self.sector_size:
            raise ValueError("Invalid buf size")

        freq = Counter(buf)
        if len(freq) == 1:
            return 0.0, freq.popitem()[0]
        
        entropy = 0.0
        for f in freq.values():
            if f > 0:
                f /= self.sector_size
                entropy += f * log2(f)

        normalized_entropy = abs(entropy) / 8

        return normalized_entropy, None
        

class ChiSquare:
    BYTES_TO_CHECK = 64
    EXPECTED_BITS = BYTES_TO_CHECK * 4

    def __init__(self, sector_size):
        self.sector_size = sector_size
        
        # randomly generated positions of checked bytes
        self._positions = sample(range(sector_size), self.BYTES_TO_CHECK)
        
        # Table to look up the bit counts of byte values
        self._bit_table = [0] * 256
        
        # Initialize the _bit_table
        for i in range(256):
            self._bit_table[i] = self._bit_table[i // 2] + (i & 1)


    def calc_ent(self, buf):
        set_bits = sum(self._bit_table[buf[position]] for position in self._positions)
        if set_bits == 0:
            return 0.0, 0
        if set_bits == 8 * self.BYTES_TO_CHECK:
            return 0.0, 255
        
        chis = (set_bits - self.EXPECTED_BITS) ** 2 / self.EXPECTED_BITS
        # if chis <= 1:
        #     return 1.0, None
        # if chis >= 200:
        #     return 0.0, None
        # return 0.5
        return 1 - chis / self.EXPECTED_BITS, None