# SPDX-License-Identifier: MIT

from typing import Dict, Any, List, Optional
from dataclasses import dataclass


@dataclass
class Parameter:
    type: Any
    default_value: Any
    help_: str
    def_val_descr: Optional[str] = None
    available: Optional[List[str]] = None


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
            f'Class {self.__class__.__name__} needs to implement the output() method'
        )

    @staticmethod
    def check_args(**kwargs):
        """Return None if args are correct otherwise return error message"""
        return None

    def error(self, message):
        raise NotImplementedError(
            f'Class {self.__class__.__name__} needs to implement the error() method'
        )

    def exit(self):
        raise NotImplementedError(
            f'Class {self.__class__.__name__} needs to implement the exit() method'
        )


def print_check_closed_pipe(*args, **kwargs):
    """Returns False on BrokenPipeError,
       otherwise lets error through or returns True"""
    try:
        print(*args, **kwargs)
        return True
    except BrokenPipeError:
        return False
