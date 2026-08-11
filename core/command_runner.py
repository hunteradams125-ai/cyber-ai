"""Safe command execution for optional Termux tools."""

from __future__ import annotations

import logging
import shutil
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence


@dataclass(frozen=True)
class CommandResult:
    args: tuple[str, ...]
    returncode: int
    stdout: str
    stderr: str
    duration_seconds: float
    unavailable: bool = False
    timed_out: bool = False

    @property
    def ok(self) -> bool:
        return self.returncode == 0 and not self.unavailable and not self.timed_out


class CommandRunner:
    """Runs a fixed argument vector without invoking a shell."""

    def __init__(self, logger: logging.Logger) -> None:
        self._logger = logger

    def run(
        self,
        args: Sequence[str],
        *,
        timeout_seconds: float = 30,
        cwd: Path | None = None,
        allowed_exit_codes: Sequence[int] = (0,),
    ) -> CommandResult:
        command = tuple(str(value) for value in args)
        if not command or not command[0]:
            raise ValueError("A non-empty command argument array is required")
        executable = shutil.which(command[0])
        if executable is None:
            self._logger.warning("Optional command unavailable: %s", command[0])
            return CommandResult(command, 127, "", f"{command[0]} is not installed", 0.0, True)

        # Log only the executable and argument count. Arguments can contain secrets.
        self._logger.info("Running command %s with %d arguments", command[0], len(command) - 1)
        started = time.monotonic()
        try:
            completed = subprocess.run(
                list(command),
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
                check=False,
                shell=False,
            )
        except subprocess.TimeoutExpired as error:
            duration = time.monotonic() - started
            self._logger.warning("Command timed out: %s", command[0])
            return CommandResult(
                command,
                124,
                error.stdout or "",
                error.stderr or "",
                duration,
                timed_out=True,
            )
        duration = time.monotonic() - started
        if completed.returncode not in allowed_exit_codes:
            self._logger.warning("Command failed: %s (%s)", command[0], completed.returncode)
        return CommandResult(
            command,
            completed.returncode,
            completed.stdout,
            completed.stderr,
            duration,
        )