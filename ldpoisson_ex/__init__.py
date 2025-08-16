"""
1D Poisson Extension Package.

This package provides tools for running 1D Poisson simulations with
parameter sweeps. It includes configuration management, solver
functionality, and data handling.
"""

from .data import OutputData
from .models import (
    SimulationConfig,
    Variable,
    Constant,
    load_simulation_config,
)
from .solver import (
    lDPoissonExSolver,
    ParamsManager,
)
