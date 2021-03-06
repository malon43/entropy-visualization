#!/usr/bin/env python3
# SPDX-License-Identifier: MIT

from sys import exit
from argument_parsing import parse_arguments
from mmap import mmap, ACCESS_READ
from math import ceil


def main(args, output_args):
    with args.disk_image as f, \
            mmap(f.fileno(), length=0, access=ACCESS_READ) as file, \
            args.output_method(ceil(file.size() / args.size), **vars(output_args)) as output:
        iterate(
            file,
            args.size,
            args.analysis_method(args.size, args.rand_lim, args.sus_rand_lim),
            output
        )


def iterate(file, sector_size, analysis_method, output):
    sector_number = 0
    buf = file.read(sector_size)
    while len(buf) == sector_size:
        ret = output.output(
            sector_number,
            sector_number * sector_size,
            *analysis_method.calc(buf)
        )
        if not ret:  # the pipe was closed
            exit(0)

        sector_number += 1
        buf = file.read(sector_size)
    if len(buf) != 0:
        output.error(
            f'The size of provided image was not a multiple of {sector_size}'
        )
        exit(1)


if __name__ == '__main__':
    arguments, output_arguments = parse_arguments()
    main(arguments, output_arguments)
    exit(0)
