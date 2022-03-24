import argparse
from output_methods import output_methods
from entropy_calculation import analysis_methods
from sys import argv, exit, stderr
from os import path
from re import sub

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

def add_output_method_arguments(parser, output_method):
    for argument, value in output_method.default_parameters.items():
        if value.type == bool:
            parser.add_argument(
                f'--{argument.replace("_", "-")}',
                help=value.help_,
                action='store_false' if value.default_value else 'store_true',
                dest=argument
            )
            continue
        parser.add_argument(
            f'--{argument.replace("_", "-")}',
            help=f'{value.help_}'
            + (f' (available: {", ".join(value.available)})' if value.available else '')
            + f' (default: {value.default_value if value.def_val_descr is None else value.def_val_descr})',
            type=value.type,
            default=value.default_value,
            dest=argument,
            required=value.default_value is None
        )

def check_invalid_output_method_args(output_method, output_args, parser):
    err = output_method.check_args(**vars(output_args))
    if err is not None:
        print(parser.format_usage(), file=stderr)
        print(f'{path.basename(argv[0])}: {err}', file=stderr)
        exit(1)


def get_methods_help():
    helps = []
    for method_name, method in output_methods.items():
        parser = argparse.ArgumentParser(usage='', add_help=False)
        add_output_method_arguments(parser, method)
        helps.append(
            f'  {method_name}:\n  ' + 
            sub(
                r'^options:\n*',
                '', 
                sub(r'^usage: \n*', 
                    '',
                    parser.format_help()
                )
            )
            .replace('\n', '\n  ')
        )
    return '\n'.join(helps)


def parse_arguments():
    main_parser = argparse.ArgumentParser(
        usage='%(prog)s [-h] [-s SIZE] [-m OUTPUT_METHOD] [-a ANALYSIS_METHOD] [output method arguments] disk_image',
        epilog=get_methods_help(),
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    main_parser.add_argument(
        '-s', '--size',
        help=f'set the sector size (default: {DEFAULT_SECTOR_SIZE})',
        type=sector_size_type,
        default=DEFAULT_SECTOR_SIZE
    )
    main_parser.add_argument(
        '-m', '--method',
        help=f'set the output method (available: {", ".join(output_methods.keys())}) (default: {DEFAULT_OUTPUT_METHOD})',
        type=output_method_type,
        default=DEFAULT_OUTPUT_METHOD,
        dest='output_method'
    )
    main_parser.add_argument(
        '-a', '--analysis',
        help=f'set the analysis method (available: {", ".join(analysis_methods.keys())}) (default: {DEFAULT_ANALYSIS_METHOD})',
        type=analysis_method_type,
        default=DEFAULT_ANALYSIS_METHOD,
        dest='analysis_method'
    )

    main_args, rest = main_parser.parse_known_args()
    second_parser = argparse.ArgumentParser()

    second_parser.format_help = main_parser.format_help  # If you are reading this, I am so so sorry.
                                                         # And yes, this does indeed cause second_parser instance to always
                                                         # call format_help() on the main_parser instance instead of on itself

    second_parser.add_argument(
        'disk_image',
        type=argparse.FileType('rb'),
        help='disk image to analyze',
    )

    add_output_method_arguments(second_parser, main_args.output_method)

    output_args = second_parser.parse_args(rest)
    main_args.disk_image = output_args.disk_image
    delattr(output_args, 'disk_image')

    check_invalid_output_method_args(main_args.output_method, output_args, second_parser)
        
    return main_args, output_args
