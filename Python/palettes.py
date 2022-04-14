from entropy_calculation import ResultFlag

def _linear_rgb_color_interpolation(color1, color2, val, min_val=0, max_val=1):
    return tuple(c1 + round((c1 - c2) / (min_val - max_val) * (val - min_val)) for c1, c2 in zip(color1, color2))

class SamplePalette:
    NEEDS_ALPHA = False
    LEGEND = [
        ((0, 0, 255), 'Byte pattern (x00)'),
        ((0, 255, 0), 'Byte pattern (xff)'),
        ((0, 64, 0), 'Byte pattern (x40)'),
        ((255, 0, 255), 'Random'),
        ((127, 0, 127), 'Not random'),
        ((255, 0, 0), 'Too random')
    ]

    @staticmethod
    def get(sector_number,
            sector_offset,
            sector_randomness,
            result_flag,
            result_arg):
        if result_flag == ResultFlag.SINGLE_BYTE_PATTERN:
            return (0, result_arg, 0) if result_arg != 0 else (0, 0, 255)
        if result_flag == ResultFlag.RANDOMNESS_SUSPICIOUSLY_HIGH:
            return (255, 0, 0)
        if result_flag == ResultFlag.RANDOM:
            return (255, 0, 255)
        if result_flag == ResultFlag.NOT_RANDOM:
            return (127, 0, 127)
        if result_flag == ResultFlag.NONE:
            return (int(255 * sector_randomness), 0, int(255 * sector_randomness))
        raise ValueError(f'invalid result_flag value: \'{result_flag}\'')


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
            return (192, 192, 192) if result_arg != 0 else (93, 132, 41)
        if result_flag in (ResultFlag.RANDOM, ResultFlag.RANDOMNESS_SUSPICIOUSLY_HIGH):
            return (0, 0, 0)
        if result_flag == ResultFlag.NOT_RANDOM:
            return (186, 0, 70)
        if result_flag == ResultFlag.NONE:
            return _linear_rgb_color_interpolation((186, 0, 70), (0, 0, 0), sector_randomness)
        raise ValueError(f'invalid result_flag value: \'{result_flag}\'')


class RGPalette:
    '''Red-Green Palette
    Used colors from colorbrewer2.org'''
    
    NEEDS_ALPHA = False
    LEGEND = [
        ((55, 126, 184), 'Byte pattern (x00)'),
        ((255, 255, 51), 'Byte pattern (xff)'),
        ((63, 63, 13), 'Byte pattern (x40)'),
        ((77, 175, 74), 'Random'),
        ((228, 26, 28), 'Not random'),
        ((152, 78, 163), 'Too random')
    ]

    @staticmethod
    def get(sector_number,
            sector_offset,
            sector_randomness,
            result_flag,
            result_arg):
        if result_flag == ResultFlag.SINGLE_BYTE_PATTERN:
            if result_arg == 0:
                return (55, 126, 184)
            return _linear_rgb_color_interpolation((0, 0, 0), (255, 255, 51), result_arg, 1, 255)
        if result_flag == ResultFlag.RANDOMNESS_SUSPICIOUSLY_HIGH:
            return (152, 78, 163)
        if result_flag == ResultFlag.RANDOM:
            return (77, 175, 74)
        if result_flag == ResultFlag.NOT_RANDOM:
            return (228, 26, 28)
        if result_flag == ResultFlag.NONE:
            return _linear_rgb_color_interpolation((228, 26, 28), (77, 175, 74), sector_randomness)
        raise ValueError(f'invalid result_flag value: \'{result_flag}\'')


palettes = {
    'sample': SamplePalette,
    'asalor': AsalorPalette,
    'rg': RGPalette
}