from argparse import ArgumentTypeError, FileType
from itertools import chain
from sys import stderr, stdout
from output_common import OutputMethodBase, Parameter, print_check_closed_pipe
from math import ceil, log, sqrt
import re
from palettes import palettes

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print('the Pillow library is not installed. \n'
          'Use `pip install Pillow` to install it', file=stderr)
    exit(1)


def hex_color_type(x):
    colors = {
        'white': (255, 255, 255),
        'black': (0, 0, 0),
        'transparent': (255, 255, 255, 0)
    }
    nx = x.strip().lower()
    if nx in colors:
        return colors[nx]

    match = re.fullmatch(
        r'#?([0-9a-f]{2})([0-9a-f]{2})([0-9a-f]{2})([0-9a-f]{2})?', nx)
    if match is not None:
        return tuple(int(b, base=16) for b in match.groups() if b is not None)

    match = re.fullmatch(
        r'#?([0-9a-f]{2})([0-9a-f]{2})([0-9a-f]{2})\[(0?\.[0-9]+|1\.0*|0\.)\]', nx)
    if match is not None:
        return (
            *map(lambda b: int(b, base=16), match.group(1, 2, 3)),
            round(float(match.group(4)) * 255)
        )

    match = re.fullmatch(
        r'#?([0-9a-f]{2})([0-9a-f]{2})([0-9a-f]{2})\[(\d{1,2}|100)%?\]', nx)
    if match is not None:
        return (
            *map(lambda b: int(b, base=16), match.group(1, 2, 3)),
            round((255 * int(match.group(4))) / 100)
        )

    match = re.fullmatch(
        r'\[(0?\.[0-9]+|1\.0*|0\.)\]#?([0-9a-f]{2})([0-9a-f]{2})([0-9a-f]{2})', nx)
    if match is not None:
        return (
            *map(lambda b: int(b, base=16), match.group(2, 3, 4)),
            round(float(match.group(1)) * 255)
        )

    match = re.fullmatch(
        r'\[(\d{1,2}|100)%?\]#?([0-9a-f]{2})([0-9a-f]{2})([0-9a-f]{2})', nx)
    if match is not None:
        return (
            *map(lambda b: int(b, base=16), match.group(2, 3, 4)),
            round((255 * int(match.group(1))) / 100)
        )

    raise ArgumentTypeError(f'\'{x}\' is not a valid hex code')


def palette_type(x):
    if x not in palettes:
        raise ArgumentTypeError(f'{x} is not a valid palette')
    return palettes[x]


def font_type(x):
    try:
        ImageFont.truetype(x)
    except OSError:
        raise ArgumentTypeError(f'{x} is not a valid font')
    return x


def luminance_test_black_white(bg_color):
    '''Based on W3 guidelines: https://www.w3.org/TR/WCAG20/#relativeluminancedef'''
    srgb = [x / 255 for x in bg_color]
    rgb = [srgb[i] / 12.92 if srgb[i] <= 0.03928 else ((srgb[i] + 0.055) / 1.055) ** 2.4
           for i in range(3)]
    rl = 0.2126 * rgb[0] + 0.7152 * rgb[1] + 0.0722 * rgb[2]

    return (255, 255, 255) if 0.17913 > rl else (0, 0, 0)


class ImageOutput(OutputMethodBase):
    default_parameters = {
        'output_file': Parameter(FileType('wb'), stdout, 'output file', 'stdout'),
        'err_file': Parameter(FileType('w'), stderr, 'error output file', 'stderr'),
        'no_legend': Parameter(bool, False, 'resulting image will not contain a legend'),
        'background': Parameter(hex_color_type, (255, 255, 255), 'hex code of background color', 'white'),
        'text_color': Parameter(hex_color_type, ..., 'hex code of font color of the legend', 'determined automatically'),
        'palette': Parameter(palette_type, 'sample', 'color palette to use', available=list(palettes.keys())),
        'font': Parameter(font_type, 'FreeMono.otf', 'font to use for legend'),
        'font_size': Parameter(int, ..., 'font size to use for legend in pixels', 'automatic')
    }

    def __init__(self, input_size, **kwargs):
        super().__init__(input_size, **kwargs)

        vis_size = self._get_size()

        if not self.no_legend and len(self.palette.LEGEND) > 0:
            if self.font_size is Ellipsis:
                self.font_size = max(vis_size[1] // len(self.palette.LEGEND) // 4, 16)
            try:
                fnt = ImageFont.truetype(self.font, size=self.font_size)
            except OSError:
                fnt = ImageFont.load_default()
            legend_size = self._get_legend_size(fnt)
            total_size = (
                vis_size[0] + legend_size[0],
                max(vis_size[1], legend_size[1])
            )
        else:
            total_size = vis_size

        if self.text_color is Ellipsis:
            self.text_color = luminance_test_black_white(self.background)

        self._rgba = self.palette.NEEDS_ALPHA \
            or len(self.background) == 4 \
            or len(self.text_color) == 4

        self._image = Image.new(
            'RGBA' if self._rgba else 'RGB',
            total_size,
            self.background
        )
        if not self.no_legend and len(self.palette.LEGEND) > 0:
            self._draw_legend(fnt)

    def output(self, *args):
        self._image.putpixel(self._coords_from_pos(args[0]), self.palette.get(*args))
        return True

    def _coords_from_pos(self, pos):
        raise NotImplementedError(
            f'Class {self.__class__.__name__} needs to implement the _from_pos() method'
        )

    def _get_size(self):
        raise NotImplementedError(
            f'Class {self.__class__.__name__} needs to implement the _get_size() method'
        )

    def error(self, message):
        return print_check_closed_pipe(message, file=self.err_file)

    def exit(self):
        try:
            self._image.save(self.output_file)
        except ValueError:
            self._image.save(self.output_file, 'PNG')
        self._image.close()
        self.output_file.close()
        self.err_file.close()
    
    def _get_legend_size(self, fnt):
        if len(self.palette.LEGEND) < 1:
            raise ValueError('Legend needs to have at least one element')

        square_size = fnt.getsize('a')[1]
        spacing = square_size // 2
        sizes = [fnt.getsize(ll[1]) for ll in self.palette.LEGEND]
        width = spacing * 3 + square_size + max(x[0] for x in sizes)
        height = sum(x[1] for x in sizes) + (len(sizes) + 1) * spacing

        return width, height

    def _draw_legend(self, fnt):
        d = ImageDraw.Draw(self._image)
        lw, lh = self._get_legend_size(fnt)
        outline_color = luminance_test_black_white(self.background)
        square_size = fnt.getsize('a')[1]
        spacing = square_size // 2
        square_pos_w = self._image.size[0] - lw + spacing
        text_pos_w = square_pos_w + square_size + spacing
        text_pos_h = self._image.size[1] // 2 - lh // 2 + spacing

        for color, desc in self.palette.LEGEND:
            d.text((text_pos_w, text_pos_h), desc, font=fnt, fill=self.text_color)
            d.rectangle(((square_pos_w, text_pos_h),
                        (square_pos_w + square_size, text_pos_h + square_size)),
                        fill=color,
                        outline=outline_color,
                        width=1)
            text_pos_h += fnt.getsize(desc)[1] + spacing



# sweeping-blocks
class SweepingBlocks(ImageOutput):
    default_parameters = {
        **ImageOutput.default_parameters,
        'width': Parameter(int, ..., 'the width of resulting image in pixels', 'automatic square'),
        'sweeping_block_size': Parameter(int, ..., 'the size of block groups of the resulting image', 'automatic')
    }

    def __init__(self, input_size, **kwargs):
        super().__init__(input_size, **kwargs)

        sbsie = self.sweeping_block_size is Ellipsis
        self.width, self.sweeping_block_size = self._calc_widths()
        if sbsie and self.sweeping_block_size == 1:
            print_check_closed_pipe(f'warn: sensible sweeping block size for width {self.width}'
                                    ' could not be selected, defaulting to sweeping.', file=stderr)

    def _calc_widths(self):
        PREFFERED_BLOCK_SIZE = 32

        if self.width is not Ellipsis and self.sweeping_block_size is not Ellipsis:
            if self.width % self.sweeping_block_size != 0:
                raise ValueError('width needs to be a multiple of sweeping-block-size')
            return self.width, self.sweeping_block_size
        if self.width is not Ellipsis and self.sweeping_block_size is Ellipsis:
            for i in chain(range(PREFFERED_BLOCK_SIZE, ceil(sqrt(self.width)) + 1), 
                           range(PREFFERED_BLOCK_SIZE - 1, 0, -1)):
                # return the smallest divisor of width larger or equal to preffered block size
                # but smaller or equal to the square root of width
                # otherwise return the largest smaller divisor of width as sweeping block size
                if self.width % i == 0:
                    return self.width, i
        sbs = PREFFERED_BLOCK_SIZE if self.sweeping_block_size is Ellipsis else self.sweeping_block_size
        return ceil(ceil(sqrt(self._input_size)) / sbs) * sbs, sbs
        

    def _get_size(self):
        w, sbs = self._calc_widths()
        if self._input_size % (w * sbs) < sbs ** 2:  # if a single unifinshed block remains on the last row
            return w, (self._input_size // (sbs * w)) * sbs + ceil((self._input_size % (sbs * w)) / sbs)
        return w, ceil(self._input_size / (sbs * w)) * sbs

    def _coords_from_pos(self, pos):
        return ((pos % self.sweeping_block_size +
                (pos // self.sweeping_block_size ** 2) * self.sweeping_block_size) % self.width,
               (pos // self.sweeping_block_size) % self.sweeping_block_size + pos //
               (self.sweeping_block_size * self.width) * self.sweeping_block_size)
    
    @staticmethod
    def check_args(**kwargs):
        if 'width' in kwargs and 'sweeping_block_size' in kwargs \
             and kwargs['width'] is not Ellipsis \
             and kwargs['sweeping_block_size'] is not Ellipsis \
             and kwargs['width'] % kwargs['sweeping_block_size'] != 0:
            return 'width needs to be a multiple of sweeping-block-size'
        return None

# sweeping
class Sweeping(SweepingBlocks):
    default_parameters = {
        **ImageOutput.default_parameters,
        'width': Parameter(int, ..., 'the width of the resulting image in pixels', 'automatic square')
    }

    def __init__(self, input_size, **kwargs):
        # sweeping is equivalent to sweeping-blocks with the block size of 1
        self.sweeping_block_size = 1
        super().__init__(input_size, **kwargs)


# hilbert-curve
class HilbertCurve(ImageOutput):
    def __init__(self, input_size, **kwargs):
        # get the smallest number of iterations of Hilbert curve required to fit all sectors
        iterations = ceil(log(input_size, 4))

        # if the image would take up more than three curves of lower iteration,
        if input_size > 3 * 4 ** (iterations - 1):
            # use smallest single curve that fits all sectors
            self.width = self.height = 2 ** iterations
        else:
            # otherwise, use up to three curves of the lower iteration
            self.width = 2 ** (iterations - 1)
            # and set the smallest height (in half-curve-side increments) that fits all sectors
            self.height = int(ceil(
                input_size / 2 ** (2 * iterations - 3)) * 2 ** (iterations - 2))

        super().__init__(input_size, **kwargs)

    def _get_size(self):
        return self.width, self.height

    def _coords_from_pos(self, pos):
        p = self._d2xy(self.width, pos % self.width ** 2)
        return p[0], p[1] + (pos // self.width ** 2) * self.width

    def _d2xy(self, n, d):
        '''Calculates point on Hilbert curve from given distance

        code adapted from
        https://en.wikipedia.org/wiki/Hilbert_curve#Applications_and_mapping_algorithms'''

        x = y = 0
        s = 1
        while s < n:
            ry = 1 & (d >> 1)
            rx = 1 & (d ^ ry)

            # rotate accordingly
            if rx == 0 and ry == 1:
                x, y = s - 1 - y, s - 1 - x
            elif rx == 0:
                x, y = y, x

            x += s * rx
            y += s * ry
            d >>= 2
            s <<= 1
        return x, y
