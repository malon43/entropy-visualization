from entropy_calculation import ResultFlag

def _linear_rgb_color_interpolation(color1, color2, val, min_val=0, max_val=1):
    return tuple(c1 + round((c1 - c2) / (min_val - max_val) * (val - min_val)) for c1, c2 in zip(color1, color2))


def _get_simple_palette(
        random,
        not_random,
        too_random,
        zero_pattern,
        pattern,
        low_pattern=None,
        absolute_not_random_at=0.0):
    abs_not_random = _linear_rgb_color_interpolation(not_random, random, absolute_not_random_at)

    if low_pattern is None:
        get_pattern_color = lambda _: pattern
    else:
        get_pattern_color = lambda p: _linear_rgb_color_interpolation(low_pattern, pattern, p, 1, 255)
    
    class SimplePalette:
        NEEDS_ALPHA = any(c is None or len(c) > 3 for c in [zero_pattern, pattern, low_pattern,
                                                            random, not_random, too_random])
        LEGEND = [
            (zero_pattern, 'Byte pattern (x00)'),
            *(
                [
                    (pattern, 'Other byte pattern')
                ] if low_pattern is None else [
                    (pattern, 'Byte pattern (xff)'),
                    (get_pattern_color(64), 'Byte pattern (x40)')
                ]
            ),
            (random, 'Random'),
            (abs_not_random, 'Not random'),
            (too_random, 'Perfect random')
        ]

        @staticmethod
        def get(sector_number,
                sector_offset,
                sector_randomness,
                result_flag,
                result_arg):
            if result_flag == ResultFlag.SINGLE_BYTE_PATTERN:
                if result_arg == 0:
                    return zero_pattern
                return get_pattern_color(result_arg)
            if result_flag == ResultFlag.RANDOMNESS_SUSPICIOUSLY_HIGH:
                return too_random
            if result_flag == ResultFlag.RANDOM:
                return random
            if result_flag == ResultFlag.NOT_RANDOM:
                return abs_not_random
            if result_flag == ResultFlag.NONE:
                return _linear_rgb_color_interpolation(not_random, random, sector_randomness)
            raise ValueError(f'invalid result_flag value: \'{result_flag}\'')

    return SimplePalette


class AsalorPalette:
    '''Color pallete used in 
    https://asalor.blogspot.com/2011/08/trim-dm-crypt-problems.html'''

    NEEDS_ALPHA = False
    LEGEND = [
        ((93, 132, 41), 'zeroed/discarded'),
        ((192, 192, 192), 'nonzero byte pattern'),
        ((186, 0, 70), 'data (not random)'),
        ((0, 0, 0), 'data (random)'),
    ]

    @staticmethod
    def get(sector_number, 
            sector_offset, 
            sector_randomness, 
            result_flag, 
            result_arg):
        if result_flag == ResultFlag.SINGLE_BYTE_PATTERN:
            return (93, 132, 41) if result_arg == 0 else (192, 192, 192)
        if result_flag in (ResultFlag.RANDOM, ResultFlag.RANDOMNESS_SUSPICIOUSLY_HIGH):
            return (0, 0, 0)
        if result_flag == ResultFlag.NOT_RANDOM:
            return (186, 0, 70)
        if result_flag == ResultFlag.NONE:
            return _linear_rgb_color_interpolation((186, 0, 70), (0, 0, 0), sector_randomness)
        raise ValueError(f'invalid result_flag value: \'{result_flag}\'')


palettes = {
    'asalor': AsalorPalette,
    'sample': _get_simple_palette(
        random =       (255,   0, 255),
        not_random =   (  0,   0,   0),
        too_random =   (255,   0,   0),
        zero_pattern = (  0,   0, 255),
        pattern =      (  0, 255,   0),
        low_pattern =  (  0,   0,   0),
        absolute_not_random_at=0.5
    ),
    'rg': _get_simple_palette(  # Used colors from colorbrewer2.org
        random =       ( 77, 175,  74),
        not_random =   (228,  26,  28), 
        too_random =   (152,  78, 163),
        zero_pattern = ( 55, 126, 184), 
        pattern =      (255, 255,  51), 
        low_pattern =  (  0,   0,   0)
    ),
    'photocopy-safe': _get_simple_palette(  # Used colors from colorbrewer2.org
        random =       ( 43, 131, 186), 
        not_random =   (215,  25,  28),
        too_random =   (253, 174,  97),
        zero_pattern = (171, 221, 164), 
        pattern =      (255, 255, 191)
    )
}