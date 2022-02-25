from entropy_calculation import ResultFlag

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
            return (0, result_arg, 0) if result_arg else (0, 0, 255)
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
    NEEDS_ALPHA = False
    LEGEND = [
        ((0, 255, 0), 'zeroed/discarded'),
        ((255, 0, 0), 'data (not random)'),
        ((0, 0, 0), 'data (random)'),
    ]

    @staticmethod
    def get(sector_number, 
            sector_offset, 
            sector_randomness, 
            result_flag, 
            result_arg):
        if result_flag == ResultFlag.SINGLE_BYTE_PATTERN:
            return (255, 0, 0) if result_arg else (0, 255, 0)
        if result_flag in (ResultFlag.RANDOM, ResultFlag.RANDOMNESS_SUSPICIOUSLY_HIGH):
            return (0, 0, 0)
        if result_flag == ResultFlag.NOT_RANDOM:
            return (255, 0, 0)
        if result_flag == ResultFlag.NONE:
            return (int((1 - sector_randomness) * 255), 0, 0)
        raise ValueError(f'invalid result_flag value: \'{result_flag}\'')


palettes = {
    'sample': SamplePalette,
    'asalor': AsalorPalette
}