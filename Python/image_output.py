from argparse import FileType
from sys import stderr, stdout
from base_output import OutputMethodBase, Parameter, print_check_closed_pipe
from math import ceil

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


class Scanning(ScanBlocks):
    default_parameters = {
        **ImageOutput.default_parameters,
        "width": Parameter(int, 1024, "the width of the resulting image in pixels")
    }

    def __init__(self, input_size, **kwargs):
        self.scan_block_size = 1
        super().__init__(input_size, **kwargs)
