"""Stub: the backlog merge driver is not implemented yet (T004, tests first)."""

ATTRIBUTES_BEGIN = "# >>> taskrail >>>"
ATTRIBUTES_END = "# <<< taskrail <<<"
DRIVER_NAME = "taskrail backlog tables"
DRIVER_COMMAND = ""


def merge_text(*args, **kwargs):
    raise NotImplementedError


def merge_tables(*args, **kwargs):
    raise NotImplementedError


def reopen_sides(*args, **kwargs):
    raise NotImplementedError


def attribute_line(*args, **kwargs):
    raise NotImplementedError
