from argparse import FileType
from sys import stderr, stdout
from base_output import OutputMethodBase, Parameter, print_check_closed_pipe
from math import ceil, log, log2
from palettes import SamplePalette

try:
    from PIL import Image
except ImportError:
    print("the Pillow library is not installed. \n"
          "Use `pip install Pillow` to install it", file=stderr)
    exit(1)


class ImageOutput(OutputMethodBase):
    default_parameters = {
        "output_file": Parameter(FileType('wb'), stdout, 'output file'),
        "err_file": Parameter(FileType('w'), stderr, 'error output file')
    }

    def __init__(self, input_size, **kwargs):
        super().__init__(input_size, **kwargs)

        self._image = Image.new('RGB', self._get_size(), (255, 255, 255))
        self.palette = SamplePalette()  # TODO

    def output(self, *args):
        self._image.putpixel(self._next_pos(), self.palette.get(*args))
        return True

    def _next_pos(self):
        raise NotImplementedError(
            f"Class {self.__class__.__name__} needs to implement the _next_pos() method"
        )

    def _get_size(self):
        raise NotImplementedError(
            f"Class {self.__class__.__name__} needs to implement the _get_size() method"
        )

    def error(self, message):
        return print_check_closed_pipe(message, file=self.err_file)

    def exit(self):
        self._image.save(self.output_file, "PNG")  # TODO
        self.output_file.close()
        self.err_file.close()


# scan-blocks
class ScanBlocks(ImageOutput):
    default_parameters = {
        **ImageOutput.default_parameters,
        "width": Parameter(int, 1024, "the width of resulting image in pixels"),
        "scan_block_size": Parameter(int, 32, "the size of block groups of the resulting image")
    }

    def __init__(self, input_size, **kwargs):
        super().__init__(input_size, **kwargs)

        if self.width % self.scan_block_size != 0:
            raise ValueError("width needs to be a multiple of scan-block-size")

        self._position = 0

    def _get_size(self):
        return self.width, ceil(self._input_size / (self.scan_block_size * self.width)) * self.scan_block_size

    def _next_pos(self):
        out = ((self._position % self.scan_block_size +
               (self._position // self.scan_block_size ** 2) * self.scan_block_size) % self.width,
               (self._position // self.scan_block_size) % self.scan_block_size + self._position //
               (self.scan_block_size * self.width) * self.scan_block_size)
        self._position += 1
        return out


# scanning
class Scanning(ScanBlocks):
    default_parameters = {
        **ImageOutput.default_parameters,
        "width": Parameter(int, 1024, "the width of the resulting image in pixels")
    }

    def __init__(self, input_size, **kwargs):
        # scanning is equivalent to scan-blocks with the block size of 1
        self.scan_block_size = 1
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

        self._position = 0

    def _get_size(self):
        return self.width, self.height

    def _next_pos(self):
        p = self._d2xy(self.width, self._position % self.width ** 2)
        out = p[0], p[1] + (self._position // self.width ** 2) * self.width
        self._position += 1
        return out

    def _d2xy(self, n, d):
        """Calculates point on Hilbert curve from given distance

        code adapted from 
        https://en.wikipedia.org/wiki/Hilbert_curve#Applications_and_mapping_algorithms"""

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
