from sys import stdout, stderr
from typing import NamedTuple, Any
from argparse import FileType, ArgumentTypeError

output_methods: dict = {}


def output_method_class(argument_name):
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


class Parameter(NamedTuple):
    type: Any
    default_value: Any
    help_: str


@output_method_class('sample-output')
class SampleOutput:
    default_parameters = {
        "output_file": Parameter(FileType('w'), stdout, 'output file'),
        "err_file": Parameter(FileType('w'), stderr, 'error output file'),
        "entropy_limit": Parameter(
            entropy_limit_type, 1.0,
            'omits every sector the entropy of which is higher than the provided value'
        )
    }

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            if key in SampleOutput.default_parameters:
                setattr(self, key, value)

    def output(
        self,
        sector_number,
        sector_offset,
        sector_entropy,
        sector_pattern
    ):
        if self.entropy_limit >= sector_entropy:
            print(
                f"{sector_number} (0x{sector_offset:x}) - {sector_entropy:.4f}" +
                (f" (pattern of 0x{sector_pattern:02x})" if sector_pattern is not None else ""),
                file=self.output_file
            )

    def error(self, message):
        print(message, file=self.err_file)


@output_method_class('csv')
class CSVOutput:
    default_parameters = {
        "output_file": Parameter(FileType("w"), stdout, "output file"),
        "err_file": Parameter(FileType("w"), stderr, "error output file"),
        "entropy_limit": Parameter(
            entropy_limit_type, 1.0,
            "omits every sector the entropy of which is higher than the provided value"
        ),
        "no_header": Parameter(bool, False, "the resulting csv file will not contain a header"),
        "separator": Parameter(str, ",", "sets the provided string as a separator of the csv file")
    }

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            if key in CSVOutput.default_parameters:
                setattr(self, key, value)
        if not self.no_header:
            print("SECTOR_NUM,SECTOR_OFFSET,SECTOR_ENTROPY,PATTERN")

    def output(self, *args):
        if self.entropy_limit >= args[2]:
            print(
                self.separator.join('' if x is None else str(x) for x in args),
                file=self.output_file
            )

    def error(self, message):
        print(message, file=self.err_file)
