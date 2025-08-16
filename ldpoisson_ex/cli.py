"""
Command-line interface for 1D Poisson Extension.

This module provides the CLI for running 1D Poisson simulations with
parameter sweeps using configuration files.
"""

import click

from .solver import lDPoissonExSolver
from .models import load_simulation_config


@click.command("1dpoisson-ex")
@click.argument("config_file", type=click.Path(exists=True))
def main(config_file: str) -> None:
    """
    Run 1D Poisson simulations with the specified configuration file.

    Args:
        config_file: Path to the YAML configuration file containing
                    simulation parameters and settings.
    """
    config = load_simulation_config(config_file)
    solver = lDPoissonExSolver(config)
    solver.run()
