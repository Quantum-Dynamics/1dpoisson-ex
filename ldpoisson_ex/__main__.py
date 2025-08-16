"""
Entry point for running the package as a module.

This allows the package to be executed with:
    python -m ldpoisson_ex config.yaml
"""

from .cli import main
main()
