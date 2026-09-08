"""
Collect and execute Python code blocks from package docstrings and Markdown files.
"""

import signal
from ast import PyCF_ALLOW_TOP_LEVEL_AWAIT
from asyncio import run
from inspect import isawaitable
from pathlib import Path
from textwrap import dedent

from pytest import skip
from sybil import Example, Sybil
from sybil.parsers.myst import CodeBlockParser


def evaluate_python(example: Example) -> None:
    """
    Execute a code block, supporting synchronous code and top-level await.

    Args:
        example (Example): The example to evaluate.
    """
    code = compile(
        source=dedent(example.parsed),
        filename=example.path,
        mode='exec',
        flags=PyCF_ALLOW_TOP_LEVEL_AWAIT,
    )

    result = eval(code, example.namespace)  # noqa: S307
    if isawaitable(object=result):
        run(main=result)


def evaluate_unix_python(example: Example) -> None:
    """
    Execute a `python unix` block only when Unix signal timeouts are supported.

    Args:
        example (Example): The example to evaluate.
    """
    if not all(hasattr(signal, name) for name in ('SIGALRM', 'ITIMER_REAL', 'getitimer', 'setitimer')):
        skip('Unix signal timeout required')

    evaluate_python(example=example)


pytest_collect_file = Sybil(
    path=str(Path(__file__).resolve().parents[1]),
    parsers=[
        CodeBlockParser(
            language='python',
            evaluator=evaluate_python,
        ),
        CodeBlockParser(
            language='python unix',
            evaluator=evaluate_unix_python,
        ),
    ],
    patterns=['*.py', '*.md'],
).pytest()
