from sys import stdout, stderr

output_methods: dict = {}


def output_method_class(argument_name):
    def decorator(c):
        if argument_name in output_methods:
            raise ValueError(
                f"Output method argument name {argument_name} already exists")
        output_methods[argument_name] = c
        return c
    return decorator


@output_method_class('sample-output')
class SampleOutput:
    default_parameters = {
        "output_file": stdout,
        "err_file": stderr,
        "entropy_threshold": 1.0
    }

    def __init__(self, **kwargs):
        # in python 3.9+: (SampleOutput.default_parameters | kwargs).items()
        for key, value in dict(SampleOutput.default_parameters, **kwargs).items():
            if key in SampleOutput.default_parameters:
                setattr(self, key, value)

    def output(
        self,
        sector_number,
        sector_offset,
        sector_entropy,
        sector_pattern
    ):
        if self.entropy_threshold > sector_entropy:
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
        "output_file": stdout,
        "err_file": stderr,
        "entropy_threshold": 1.0,
        "no_header": False,
        "separator": ","
    }

    def __init__(self, **kwargs):
        for key, value in dict(CSVOutput.default_parameters, **kwargs).items():
            if key in CSVOutput.default_parameters:
                setattr(self, key, value)
        if not self.no_header:
            print("SECTOR_NUM,SECTOR_OFFSET,SECTOR_ENTROPY,PATTERN")

    def output(self, *args):
        if self.entropy_threshold > args[2]:
            print(
                self.separator.join('' if x is None else str(x) for x in args),
                file=self.output_file
            )

    def error(self, message):
        print(message, file=self.err_file)
