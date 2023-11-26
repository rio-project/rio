import os
import shlex
from typing import *  # type: ignore

_ACTIVE_SHELL: Optional[Literal["bourne", "cmd.exe", "powershell"]] = None


def _guess_shell_non_cached() -> Literal["bourne", "cmd.exe", "powershell"]:
    # If the SHELL environment variable is set, use that
    try:
        shell_var = os.environ["SHELL"]
    except KeyError:
        pass
    else:
        if (
            shell_var.endswith("bash")
            or shell_var.endswith("zsh")
            or shell_var.endswith("sh")
        ):
            return "bourne"

        # TODO: Does windows actually expose the shell in an environment variable?
        if shell_var.endswith("cmd.exe"):
            return "cmd.exe"

        # TODO: Does windows actually expose the shell in an environment variable?
        if shell_var.endswith("powershell"):
            return "powershell"

    # Fall back to guessing from the operating system
    if os.name == "nt":
        return "cmd.exe"

    return "bourne"


def guess_shell() -> Literal["bourne", "cmd.exe", "powershell"]:
    """
    Attempt to determine the shell this program is running in.
    """
    global _ACTIVE_SHELL

    if _ACTIVE_SHELL is None:
        _ACTIVE_SHELL = _guess_shell_non_cached()

    return _ACTIVE_SHELL


def shell_escape(value: Any) -> str:
    """
    Given any value, return a string that represents the same value in a shell.
    If the value is not a string it will be converted to a string using `str`.

    Warning: This function is not guaranteed to be safe. It is a rather
        simplistic implementation that will _usually_ work.
    """
    value = str(value)

    # Try to determine the shell
    shell = guess_shell()

    # Escape the value, based on the shell
    if shell == "bourne":
        return shlex.quote(value)

    if shell == "cmd.exe":
        value = value.replace('"', '""')
        return f'"{value}"'

    if shell == "powershell":
        value = value.replace("'", "''")
        return f"'{value}'"

    raise NotImplementedError(f"Unknown/Invalid shell `{shell}`")
