#!/usr/bin/env python3
# SPDX-License-Identifier: MIT

import argparse
from output_methods import output_methods
from argument_parsing import add_output_method_arguments, check_invalid_output_method_args, output_method_type
from analysis import ResultFlag
import csv


def parse_arguments():
    main_parser = argparse.ArgumentParser()
    main_parser.add_argument(
        '-d', '--delimiter',
        help='Delimiter of the source csv file (default: \',\')',
        default=',',
    )
    main_parser.add_argument(
        'method',
        help=f'Set the output method (available: {", ".join(output_methods.keys())})',
        type=output_method_type,
    )
    main_parser.add_argument(
        'file',
        help='csv file to visualize',
        type=argparse.FileType('r'),
    )

    main_args, rest = main_parser.parse_known_args()
    second_parser = argparse.ArgumentParser()
    add_output_method_arguments(second_parser, main_args.method)
    output_args = second_parser.parse_args(rest)
    check_invalid_output_method_args(main_args.method, output_args, second_parser)

    return main_args, output_args


def set_to_header_end_position(f):
    p = f.tell()
    line = f.readline()
    if line[0].isdigit():
        f.seek(p)


def get_number_of_lines(f):
    p = f.tell()
    line_number = 0
    for line_number, _ in enumerate(f):
        pass
    f.seek(p)
    return line_number + 1


def main(args, output_args):
    with args.file as f:
        set_to_header_end_position(f)
        with args.method(get_number_of_lines(f), **vars(output_args)) as output:
            for row in csv.reader(f, delimiter=args.delimiter):
                ret = output.output(
                    int(row[0]),
                    int(row[1]),
                    float(row[2]),
                    ResultFlag(int(row[3])),
                    None if row[4] == '' else int(row[4])
                )
                if not ret:  # the pipe was closed
                    exit(0)


if __name__ == '__main__':
    arguments, output_arguments = parse_arguments()
    main(arguments, output_arguments)
    exit(0)
