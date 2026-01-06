import subprocess
from dataclasses import dataclass
from typing import List


@dataclass
class ExecutionResult:
    stdout: str
    stderr: str
    returncode: int


DEFAULT_CMD = ["python", "-c"]


def run_code(code: str, timeout: int = 10, cmd: List[str] | None = None) -> ExecutionResult:
    """Execute Python code locally with a timeout.

    Args:
        code: Python source to run.
        timeout: Maximum seconds to allow execution.
        cmd: Optional override for the interpreter command.
    """

    command = cmd or DEFAULT_CMD

    try:
        completed = subprocess.run(
            [*command, code],
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return ExecutionResult(
            stdout=completed.stdout,
            stderr=completed.stderr,
            returncode=completed.returncode,
        )
    except subprocess.TimeoutExpired:
        return ExecutionResult(stdout="", stderr="Execution timed out", returncode=1)
