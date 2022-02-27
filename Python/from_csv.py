#!/usr/bin/env python3

import argparse

from output_methods import output_methods
from argument_parsing import add_output_method_arguments, check_invalid_output_method_args, output_method_type
from entropy_calculation import ResultFlag
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

def main(args, output_args):
    with args.file as f:
        lines = f.readlines()
        header = not lines[0][0].isdigit()
        with args.method(len(lines) - header, **vars(output_args)) as output:
            for row in csv.reader(lines, delimiter=args.delimiter):
                if header:
                    header = False
                    continue
                ret = output.output(
                    int(row[0]),
                    int(row[1]),
                    float(row[2]),
                    ResultFlag(int(row[3])),
                    None if row[4] == '' else int(row[4])
                )
                if not ret: # the pipe was closed
                    exit(0)


if __name__ == '__main__':
    args, output_args = parse_arguments()
    main(args, output_args)
    exit(0)