from argparse import FileType, ArgumentTypeError
from sys import stderr, stdout
from base_output import OutputMethodBase, Parameter, print_check_closed_pipe
from math import ceil, log, log2

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

    def output(
        self,
        sector_number,
        sector_offset,
        sector_entropy,
        sector_pattern
    ):
        # self._image.putpixel(self._next_pos(), self.palette.get())  # TODO
        if sector_pattern == 0:
            self._image.putpixel(self._next_pos(), (0, 0, 255))
        elif sector_pattern is not None:
            self._image.putpixel(
                self._next_pos(), (0, int(255) * sector_pattern, 0))
        else:
            self._image.putpixel(self._next_pos(),
                                 (int(255 * sector_entropy), 0, int(255 * sector_entropy)))
        return True

    def _next_pos(self):
        raise NotImplementedError(
            f"Children of {self.__class__.__name__} need to implement the _get_line() method"
        )

    def _get_size(self):
        raise NotImplementedError(
            f"Children of {self.__class__.__name__} need to implement the _get_line() method"
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
        self.scan_block_size = 1
        super().__init__(input_size, **kwargs)


# hilbert-curve
class HilbertCurve(ImageOutput):
    def __init__(self, input_size, **kwargs):
        side = ceil(log(input_size, 4))
        if input_size > 3 * 4 ** (side - 1):
            self.width = self.height = 2 ** side
        else:
            self.width = 2 ** (side - 1)
            self.height = ceil(input_size / 2 ** (2 * side - 3)) * 2 ** (side - 2)

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
        x = y = 0
        s = 1
        while s < n:
            ry = 1 & (d >> 1)
            rx = 1 & (d ^ ry)

            #rotate accordingly
            if rx == 0 and ry == 1:
                x, y = s - 1 - y, s - 1 - x
            elif rx == 0:
                x, y = y, x 
            
            x += s * rx
            y += s * ry
            d >>= 2
            s <<= 1
        return x, y
