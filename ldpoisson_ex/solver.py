"""
Solver for 1D Poisson simulations with parameter sweeps.

This module provides the main solver class and parameter management
for running 1D Poisson simulations across multiple parameter combinations.
"""

from functools import cached_property
import itertools
import logging
import os
from pathlib import Path
import shutil
import subprocess as sp
import typing as t

from jinja2 import (
    Environment,
    FileSystemLoader,
    select_autoescape,
)
import numpy as np

from .data import OutputData
from .models import (
    SimulationConfig,
    Variable,
    Constant,
)


class ParamsManager:
    """
    Manager for simulation parameters and variable combinations.

    Handles the generation of all parameter combinations from
    constants and variable specifications.
    """

    def __init__(
        self,
        constants: list[Constant],
        variables: list[Variable],
    ) -> None:
        """
        Initialize the parameter manager.

        Args:
            constants: List of constant parameters.
            variables: List of variable parameters for sweeps.
        """
        self._constants: dict[str, float] = {}
        for const in constants:
            self._constants[const.name] = const.value

        self._variables: dict[str, list[float]] = {}
        for var in variables:
            if isinstance(var.value, list):
                self._variables[var.name] = var.value
            else:
                self._variables[var.name] = list(np.arange(
                    var.value.start,
                    var.value.end,
                    var.value.step,
                ))

        self._variable_formats: dict[str, str] = {
            var.name: var.format for var in variables
        }

    @property
    def constants(self) -> dict[str, float]:
        """Dictionary of constant parameters."""
        return self._constants

    @property
    def variables(self) -> dict[str, list[float]]:
        """Dictionary of variable parameters and their value lists."""
        return self._variables

    @property
    def variable_formats(self) -> dict[str, str]:
        """Dictionary of variable names and their format strings."""
        return self._variable_formats

    def generate_variables(self) -> t.Generator[dict[str, float], None, None]:
        """
        Generate all combinations of variable parameters.

        Yields:
            Dictionary containing one combination of all variables.
            If no variables are defined, yields only constants.
        """
        if not self._variables:
            yield self._constants
            return

        var_names = list(self._variables.keys())
        var_values = [self._variables[name] for name in var_names]
        for combination in itertools.product(*var_values):
            yield dict(zip(var_names, combination))

    @cached_property
    def shape_variables(self) -> tuple[int, ...]:
        """Shape tuple representing the dimensions of the variable space."""
        return tuple(len(values) for values in self._variables.values())


class lDPoissonExSolver:
    """
    Main solver for 1D Poisson simulations with parameter sweeps.

    This class manages the execution of 1D Poisson simulations across
    multiple parameter combinations, handles template rendering, and
    processes output data.
    """

    def __init__(self, config: SimulationConfig) -> None:
        """
        Initialize the solver with simulation configuration.

        Args:
            config: SimulationConfig object containing all necessary
                   paths, parameters, and settings.
        """
        self._config = config
        self._params_manager = ParamsManager(
            config.constants,
            config.variables,
        )

        # Set up Jinja2 environment
        self._env = Environment(
            loader=FileSystemLoader(Path(config.file_template).parent),
            autoescape=select_autoescape(),
        )
        self._template = self._env.get_template(config.file_template.name)

        # Set up logging
        if self._config.log_file is None:
            logging_handler = logging.StreamHandler()
        else:
            logging_handler = logging.FileHandler(config.log_file)
        logging_handler.setLevel(logging.INFO)
        self._logger = logging.getLogger(__name__)
        self._logger.setLevel(logging.INFO)
        self._logger.addHandler(logging_handler)

    def _get_dir_name(self, variables: dict[str, float]) -> str:
        results = []
        for k, v in variables.items():
            format_str = self._params_manager.variable_formats[k]
            results.append(f"{k}({format_str.format(v)})")
        return "_".join(results)

    def _run_single(
        self,
        constants: dict[str, float],
        variables: dict[str, float],
    ) -> OutputData:
        # Create input file
        path_app = self._config.path_1d_poisson
        input_file_name = self._get_dir_name(variables)
        input_file = path_app.parent / f"{input_file_name}.txt"

        self._logger.info(f"Creating input file: {input_file}")
        with open(input_file, "w") as f:
            f.write(self._template.render(constants | variables))

        # Run 1D Poisson
        self._logger.info(f"Running 1D Poisson simulation for: {variables}")
        cwd = os.getcwd()
        os.chdir(path_app.parent)
        sp.run(f"\"{path_app}\" {input_file_name}")
        os.chdir(cwd)

        # Create output directory
        dir_out_single = (self._config.dir_output / input_file_name)
        self._logger.info(f"Creating output directory: {dir_out_single}")
        os.makedirs(dir_out_single)

        # Move output files
        path_out = path_app.parent / f"{input_file_name}_Out.txt"
        path_status = path_app.parent / f"{input_file_name}_Status.txt"
        path_wave = path_app.parent / f"{input_file_name}_Wave.txt"

        self._logger.info(f"Moving output files to: {dir_out_single}")
        shutil.move(input_file, dir_out_single)
        shutil.move(path_out, dir_out_single)
        shutil.move(path_status, dir_out_single)
        shutil.move(path_wave, dir_out_single)

        return OutputData(dir_out_single / f"{input_file_name}_Out.txt")

    def run(self) -> None:
        total_combinations = np.prod(self._params_manager.shape_variables)
        self._logger.info(
            f"Starting parameter sweep with {total_combinations} combinations"
        )
        self._logger.info(f"Variables: {self._params_manager.variables}")
        self._logger.info(f"Constants: {self._params_manager.constants}")

        # Run simulations
        energies_ground_states = []
        positions_ground_states = []
        for i, variables in enumerate(
            self._params_manager.generate_variables(), 1
        ):
            self._logger.info(
                f"Processing combination {i}/{total_combinations}"
            )
            output = self._run_single(
                self._params_manager.constants,
                variables,
            )
            energies_ground_states.append(output.energy_ground_state)
            positions_ground_states.append(output.position_ground_state)

        self._logger.info("All simulations completed. Saving results...")

        # Save individual variable states
        for var_name, var_values in self._params_manager._variables.items():
            var_values = np.array(var_values)
            output_path = self._config.dir_output / f"{var_name}.npy"
            np.save(output_path, var_values)
            self._logger.info(f"Saved variable '{var_name}' to {output_path}")

        # Save ground state energies and positions
        energies_ground_states = np.array(energies_ground_states).reshape(
            self._params_manager.shape_variables
        )
        positions_ground_states = np.array(positions_ground_states).reshape(
            self._params_manager.shape_variables
        )

        energy_path = self._config.dir_output / "energies_ground_states.npy"
        position_path = self._config.dir_output / "positions_ground_states.npy"

        np.save(energy_path, energies_ground_states)
        np.save(position_path, positions_ground_states)

        self._logger.info(f"Saved ground state energies to {energy_path}")
        self._logger.info(f"Saved ground state positions to {position_path}")
        self._logger.info("Parameter sweep completed successfully!")
