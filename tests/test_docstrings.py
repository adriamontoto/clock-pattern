"""
Collect and execute Python code blocks from package docstrings and Markdown files.
"""

from ast import PyCF_ALLOW_TOP_LEVEL_AWAIT
from asyncio import run
from inspect import isawaitable
from pathlib import Path
from textwrap import dedent

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


pytest_collect_file = Sybil(
    path=str(Path(__file__).resolve().parents[1]),
    parsers=[
        CodeBlockParser(
            language='python',
            evaluator=evaluate_python,
        ),
    ],
    patterns=['*.py', '*.md'],
).pytest()
