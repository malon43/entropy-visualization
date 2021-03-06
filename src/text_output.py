# SPDX-License-Identifier: MIT

from argparse import ArgumentTypeError, FileType
from enum import IntEnum
from math import inf
from sys import stderr, stdout
from output_common import OutputMethodBase, Parameter, print_check_closed_pipe


def entropy_limit_type(x):
    val = float(x)
    if val < 0 or val > 1:
        raise ArgumentTypeError(
            f'{val} is not from range (0, 1)'
        )
    return val


class TextLineOutput(OutputMethodBase):
    default_parameters = {
        'output_file': Parameter(FileType('w'), stdout, 'output file', 'stdout'),
        'err_file': Parameter(FileType('w'), stderr, 'error output file', 'stderr'),
        'entropy_limit': Parameter(
            entropy_limit_type, inf,
            'omits every sector the entropy of which is higher than the provided value'
        )
    }

    def _get_line(self, *args):
        raise NotImplementedError(
            f'Class {self.__class__.__name__} needs to implement the _get_line() method'
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


# sample-output
class SampleOutput(TextLineOutput):
    def _get_line(
        self,
        sector_number,
        sector_offset,
        sector_randomness,
        result_flag,
        sector_pattern
    ):
        return (f'{sector_number} (0x{sector_offset:x}) - {sector_randomness:.4f}, {result_flag.name}' +
                (f' (pattern of 0x{sector_pattern:02x})' if sector_pattern is not None else ''))


# csv
class CSVOutput(TextLineOutput):
    default_parameters = {
        **TextLineOutput.default_parameters,
        'no_header': Parameter(bool, False, 'the resulting csv file will not contain a header'),
        'separator': Parameter(str, ',', 'sets the provided string as a separator of the csv file', '\',\'')
    }

    COLUMN_NAMES = [
        'SECTOR_NUM',
        'SECTOR_OFFSET',
        'SECTOR_RANDOMNESS',
        'RESULT_FLAG',
        'PATTERN'
    ]

    def __init__(self, input_size, **kwargs):
        super().__init__(input_size, **kwargs)

        if not self.no_header:
            print_check_closed_pipe(
                self.separator.join(self.COLUMN_NAMES),
                file=self.output_file
            )

    def _get_line(self, *args):
        return self.separator.join(map(self._string_map, args))
    
    @staticmethod
    def _string_map(x):
        if x is None:
            return ''
        if isinstance(x, IntEnum):
            return str(x.value)
        return str(x)
