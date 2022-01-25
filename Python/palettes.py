class SamplePalette:
    def get(self,
            sector_number,
            sector_offset,
            sector_entropy,
            sector_pattern):
        if sector_pattern == 0:
            return (0, 0, 255)
        if sector_pattern is not None:
            return (0, int(255) * sector_pattern, 0)
        return (int(255 * sector_entropy), 0, int(255 * sector_entropy))
