import argparse
from output_methods import output_methods
from entropy_calculation import analysis_methods
from sys import argv, exit, stderr
from os import path

DEFAULT_SECTOR_SIZE = 512
DEFAULT_OUTPUT_METHOD = 'scanning'
DEFAULT_ANALYSIS_METHOD = 'chi2-4'


def sector_size_type(x):
    val = int(x)
    if val == 0 or val & (val - 1) != 0:
        raise argparse.ArgumentTypeError(
            f'{val} is not a power of two'
        )
    return val


def output_method_type(x):
    if x not in output_methods:
        raise argparse.ArgumentTypeError(
            f'{x} is not a valid output method'
        )
    return output_methods[x]

def analysis_method_type(x):
    if not x in analysis_methods:
        raise argparse.ArgumentTypeError(
            f'{x} is not a valid analysis method'
        )
    return analysis_methods[x]

def parse_arguments():
    main_parser = argparse.ArgumentParser(
        usage='%(prog)s [-h] [-s SIZE] [-m OUTPUT_METHOD] [output method arguments] file'
    )
    main_parser.add_argument(
        '-s', '--size',
        help=f'Set the sector size (default: {DEFAULT_SECTOR_SIZE})',
        type=sector_size_type,
        default=DEFAULT_SECTOR_SIZE
    )
    main_parser.add_argument(
        '-m', '--method',
        help=f'Set the output method (available: {", ".join(output_methods.keys())}) (default: {DEFAULT_OUTPUT_METHOD})',
        type=output_method_type,
        default=DEFAULT_OUTPUT_METHOD,
        dest='output_method'
    )
    main_parser.add_argument(
        '-a', '--analysis',
        help=f'Set the analysis method (available: {", ".join(analysis_methods.keys())}) (default: {DEFAULT_ANALYSIS_METHOD})',
        type=analysis_method_type,
        default=DEFAULT_ANALYSIS_METHOD,
        dest='analysis_method'
    )

    main_args, rest = main_parser.parse_known_args()
    second_parser = argparse.ArgumentParser()
    second_parser.add_argument(
        'file',
        type=argparse.FileType('rb'),
        help='Disk image to analyze'
    )

    for argument, value in main_args.output_method.default_parameters.items():
        if value.type == bool:
            second_parser.add_argument(
                f'--{argument.replace("_", "-")}',
                help=value.help_,
                action='store_false' if value.default_value else 'store_true',
                dest=argument
            )
            continue
        second_parser.add_argument(
            f'--{argument.replace("_", "-")}',
            help=f'{value.help_}' 
               + f' (available: {", ".join(value.available)})' if value.available else ''
               + ' (default: {value.default_value if value.def_val_descr is None else value.def_val_descr})',
            type=value.type,
            default=value.default_value,
            dest=argument,
            required=value.default_value is None
        )
    output_args = second_parser.parse_args(rest)
    main_args.file = output_args.file
    delattr(output_args, 'file')

    err = main_args.output_method.check_args(**vars(output_args))
    if err is not None:
        print(second_parser.format_usage(), file=stderr)
        print(f'{path.basename(argv[0])}: {err}', file=stderr)
        exit(1)

        
    return main_args, output_args
