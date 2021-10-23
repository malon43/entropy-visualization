#!/usr/bin/env python3

from entropy_calculation import ent_samp
from output_methods import output_methods
import argparse
from sys import exit

DEFAULT_SECTOR_SIZE = 512
DEFAULT_OUTPUT_METHOD = 'sample-output'


def main(args):
    with args.file as f:
        # TODO parse this as parameter
        iterate(f, args.size, args.output_method(entropy_threshold=1))


def pattern_recognition(buf):
    """If every byte is the same,
    returns pattern, otherwise returns None
    """
    if all(byte == buf[0] for byte in buf):
        return buf[0]
    return None


def iterate(file, sector_size, output):
    sector_number = 0
    buf = file.read(sector_size)
    while len(buf) == sector_size:
        output.output(
            sector_number,
            sector_number * sector_size,
            ent_samp(buf),
            pattern_recognition(buf)
        )

        sector_number += 1
        buf = file.read(sector_size)
    if len(buf) != 0:
        output.error(
            f"The size of provided image was not a multiple of {sector_size}"
        )
        exit(1)


def sector_size_type(x):
    val = int(x)
    if val == 0 or val & (val - 1) != 0:
        raise argparse.ArgumentTypeError(
            f"{val} is not a power of two"
        )
    return val


def output_method_type(x):
    if x not in output_methods:
        raise argparse.ArgumentTypeError(
            f"{x} is not a valid output_method"
        )
    return output_methods[x]


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "file",
        type=argparse.FileType('rb'),
        help="Disk iamge to analyze"
    )
    parser.add_argument(
        "-s", "--size",
        help=f"Set the sector size (default: {DEFAULT_SECTOR_SIZE})",
        type=sector_size_type,
        default=DEFAULT_SECTOR_SIZE
    )
    parser.add_argument(
        "-m", "--method",
        help=f"Set the output method (available: {', '.join(output_methods.keys())}) (default: {DEFAULT_OUTPUT_METHOD})",
        type=output_method_type,
        default=DEFAULT_OUTPUT_METHOD,
        dest='output_method'
    )

    args = parser.parse_args()
    main(args)
