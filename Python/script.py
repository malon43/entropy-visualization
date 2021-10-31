#!/usr/bin/env python3

from entropy_calculation import ent_samp
from sys import exit
from argument_parsing import parse_arguments


def main(args, output_args):
    with args.file as f:
        iterate(f, args.size, args.output_method(**vars(output_args)))


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


if __name__ == '__main__':
    args, output_args = parse_arguments()
    main(args, output_args)
