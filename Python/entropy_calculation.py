from math import log2


def ent_samp(buf):
    """ Calculates and returns sample entropy on byte level for
        the argument and single byte pattern if present or None.

        This code has been adapted from 
        https://gitlab.com/cryptsetup/cryptsetup/-/blob/master/misc/keyslot_checker/chk_luks_keyslots.c#L81
    """
    if len(buf) == 0:
        return 0.0, None

    freq = [0] * 256
    for byte in buf:
        freq[byte] += 1

    entropy = 0.0
    for byte_value, f in enumerate(freq):
        if f == len(buf):
            return 0.0, byte_value
        if f > 0:
            f /= len(buf)
            entropy += f * log2(f)

    entropy = abs(entropy) / 8

    return entropy, None


# from random import randint


# test1 = bytes([0] * 512)
# test2 = bytes([1] * 512)
# test3 = bytes([*range(256)] * 2)
# test4 = bytes([randint(0, 255) for _ in range(512)])
# test5 = bytes([0, 1] * 256)
# test6 = bytes([0, 1, 2] * 170 + [0, 1])
# test7 = bytes([0, 1, 2, 3] * 128)
