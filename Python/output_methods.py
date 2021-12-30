from sys import stdout, stderr
from typing import NamedTuple, Any
from argparse import FileType, ArgumentTypeError
from PIL import Image
from math import ceil

output_methods: dict = {}


def output_method_class(argument_name):
    """This decorator is used to mark output methods classes
        and makes them available to be used under
        the passed argument name as an option"""
    def decorator(c):
        if argument_name in output_methods:
            raise ValueError(
                f"Output method argument name {argument_name} already exists")
        output_methods[argument_name] = c
        return c
    return decorator


def entropy_limit_type(x):
    val = float(x)
    if val < 0 or val > 1:
        raise ArgumentTypeError(
            f"{val} is not from range (0, 1)"
        )
    return val


def print_check_closed_pipe(*args, **kwargs):
    """Returns False on BrokenPipeError,
       otherwise lets error through or returns True"""
    try:
        print(*args, **kwargs)
        return True
    except BrokenPipeError:
        return False


class Parameter(NamedTuple):
    type: Any
    default_value: Any
    help_: str


class OutputMethodBase:
    default_parameters = dict()

    def __init__(self, input_size, **kwargs):
        self._input_size = input_size
        for key, value in {**{k: v.default_value for k, v in self.default_parameters.items()},
                           **kwargs}.items():
            if key in self.default_parameters:
                setattr(self, key, value)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.exit()

    def output(self, *args):
        raise NotImplementedError(
            f"Children of {self.__class__.__name__} need to implement the output() method"
        )

    def error(self, message):
        raise NotImplementedError(
            f"Children of {self.__class__.__name__} need to implement the error() method"
        )

    def exit(self):
        raise NotImplementedError(
            f"Children of {self.__class__.__name__} need to implement the exit() method"
        )


class TextLineOutput(OutputMethodBase):
    default_parameters = {
        "output_file": Parameter(FileType('w'), stdout, 'output file'),
        "err_file": Parameter(FileType('w'), stderr, 'error output file'),
        "entropy_limit": Parameter(
            entropy_limit_type, 1.0,
            'omits every sector the entropy of which is higher than the provided value'
        )
    }

    def _get_line(self, *args):
        raise NotImplementedError(
            f"Children of {self.__class__.__name__} need to implement the _get_line() method"
        )

    def output(self, *args):
        if self.entropy_limit >= args[2]:
            return print_check_closed_pipe(self._get_line(*args), file=self.output_file)
        return True

    def error(self, message):
        return print_check_closed_pipe(message, file=self.err_file)

    def exit(self):
        self.output_file.close()
        self.err_file.close()


@output_method_class('sample-output')
class SampleOutput(TextLineOutput):
    def _get_line(
        self,
        sector_number,
        sector_offset,
        sector_entropy,
        sector_pattern
    ):
        return (f"{sector_number} (0x{sector_offset:x}) - {sector_entropy:.4f}" +
                (f" (pattern of 0x{sector_pattern:02x})" if sector_pattern is not None else ""))


@output_method_class('csv')
class CSVOutput(TextLineOutput):
    default_parameters = {
        **TextLineOutput.default_parameters,
        "no_header": Parameter(bool, False, "the resulting csv file will not contain a header"),
        "separator": Parameter(str, ",", "sets the provided string as a separator of the csv file")
    }

    def __init__(self, input_size, **kwargs):
        super().__init__(input_size, **kwargs)

        if not self.no_header:
            print_check_closed_pipe(
                "SECTOR_NUM,SECTOR_OFFSET,SECTOR_ENTROPY,PATTERN",
                file=self.output_file
            )

    def _get_line(self, *args):
        return self.separator.join('' if x is None else str(x) for x in args)


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
            self._image.putpixel(self._next_pos(), (255, 0, 0))
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


@output_method_class('scanning')
class Scanning(ImageOutput):
    default_parameters = {
        **ImageOutput.default_parameters,
        "width": Parameter(int, 1024, "the width of the resulting image in pixels")
    }

    def __init__(self, input_size, **kwargs):
        super().__init__(input_size, **kwargs)
        self._x = 0
        self._y = 0

    def _get_size(self):
        return self.width, ceil(self._input_size / self.width)

    def _next_pos(self):
        out = (self._x, self._y)
        self._x += 1

        if self._x >= self.width:
            self._x = 0
            self._y += 1

        return out
