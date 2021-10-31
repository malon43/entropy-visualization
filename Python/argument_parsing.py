import argparse
from output_methods import output_methods

DEFAULT_SECTOR_SIZE = 512
DEFAULT_OUTPUT_METHOD = 'sample-output'


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


def parse_arguments():
    main_parser = argparse.ArgumentParser(
        usage='%(prog)s [-h] [-s SIZE] [-m OUTPUT_METHOD] [output method arguments] file'
    )
    main_parser.add_argument(
        "-s", "--size",
        help=f"Set the sector size (default: {DEFAULT_SECTOR_SIZE})",
        type=sector_size_type,
        default=DEFAULT_SECTOR_SIZE
    )
    main_parser.add_argument(
        "-m", "--method",
        help=f"Set the output method (available: {', '.join(output_methods.keys())}) (default: {DEFAULT_OUTPUT_METHOD})",
        type=output_method_type,
        default=DEFAULT_OUTPUT_METHOD,
        dest="output_method"
    )

    main_args, rest = main_parser.parse_known_args()
    second_parser = argparse.ArgumentParser()
    second_parser.add_argument(
        "file",
        type=argparse.FileType("rb"),
        help="Disk iamge to analyze"
    )

    for argument, value in main_args.output_method.default_parameters.items():
        if value.type == bool:
            second_parser.add_argument(
                f"--{argument.replace('_', '-')}",
                help=value.help_,
                action="store_false" if value.default_value else "store_true",
                dest=argument
            )
            continue
        second_parser.add_argument(
            f"--{argument.replace('_', '-')}",
            help=f"{value.help_} (default: {value.default_value})",
            type=value.type,
            default=value.default_value,
            dest=argument,
            required=value.default_value is None
        )
    output_args = second_parser.parse_args(rest)
    main_args.file = output_args.file
    delattr(output_args, 'file')
    return main_args, output_args
