"""
Data models for 1D Poisson simulation configuration.

This module defines Pydantic models for configuration management,
including parameters, variables, and simulation settings.
"""

from pydantic import BaseModel, field_validator
from pathlib import Path
import yaml


class Array(BaseModel):
    """
    Configuration for array-like parameter sweeps.

    Defines a range of values from start to end with a given step size.
    """

    start: float
    end: float
    step: float


class Variable(BaseModel):
    """
    Configuration for a simulation variable.

    Can be a single value, list of values, or an Array specification.
    """

    name: str
    value: list[float] | Array
    format: str | None = None


class Constant(BaseModel):
    """
    Configuration for a simulation constant.

    Represents a fixed parameter that doesn't change during sweeps.
    """

    name: str
    value: float


class SimulationConfig(BaseModel):
    """
    Main configuration for 1D Poisson simulations.

    Contains all necessary paths, parameters, and settings for running
    simulations with parameter sweeps.
    """

    file_template: Path
    dir_output: Path
    path_1d_poisson: Path
    log_file: str | None = None
    variables: list[Variable] = []
    constants: list[Constant] = []

    @field_validator('file_template', mode='before')
    @classmethod
    def validate_file_template(cls, v: str) -> Path:
        """Convert string path to Path object for file_template."""
        return Path(v)

    @field_validator('dir_output', mode='before')
    @classmethod
    def validate_dir_output(cls, v: str) -> Path:
        """Convert string path to Path object for dir_output."""
        return Path(v)

    @field_validator('path_1d_poisson', mode='before')
    @classmethod
    def validate_path_1d_poisson(cls, v: str) -> Path:
        """Convert string path to absolute Path object for path_1d_poisson."""
        return Path(v).absolute()


def load_simulation_config(file_path: str) -> SimulationConfig:
    """
    Load simulation configuration from a YAML file.

    Args:
        file_path: Path to the YAML configuration file.

    Returns:
        SimulationConfig object with validated parameters.

    Raises:
        FileNotFoundError: If the configuration file does not exist.
        yaml.YAMLError: If the YAML file is malformed.
        ValidationError: If the configuration data is invalid.
    """
    with open(file_path, "r") as f:
        data = yaml.safe_load(f)
    return SimulationConfig(**data)
