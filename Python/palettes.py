class SamplePalette:
    NEEDS_ALPHA = False
    LEGEND = [
        ((0, 0, 255), 'Byte pattern (x00)'),
        ((0, 255, 0), 'Byte pattern (xff)'),
        ((0, 64, 0), 'Byte pattern (x40)'),
        ((255, 0, 255), 'High entropy'),
        ((64, 0, 64), 'Low entropy')
    ]

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
