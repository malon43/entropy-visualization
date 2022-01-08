from typing import Dict, NamedTuple, Any

class Parameter(NamedTuple):
    type: Any
    default_value: Any
    help_: str


class OutputMethodBase:
    default_parameters: Dict[str, Parameter] = dict()

    def __init__(self, input_size, **kwargs):
        self._input_size = input_size
        for key, value in {**{k: v.default_value for k, v in self.default_parameters.items()},
                           **kwargs}.items():
            if key in self.default_parameters:
                setattr(self, key, value)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.exit()

    def output(self, *args):
        raise NotImplementedError(
            f"Children of {self.__class__.__name__} need to implement the output() method"
        )

    def error(self, message):
        raise NotImplementedError(
            f"Children of {self.__class__.__name__} need to implement the error() method"
        )

    def exit(self):
        raise NotImplementedError(
            f"Children of {self.__class__.__name__} need to implement the exit() method"
        )


def print_check_closed_pipe(*args, **kwargs):
    """Returns False on BrokenPipeError,
       otherwise lets error through or returns True"""
    try:
        print(*args, **kwargs)
        return True
    except BrokenPipeError:
        return False

