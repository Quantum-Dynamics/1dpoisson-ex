"""
Data handling for 1D Poisson simulation output.

This module provides classes for parsing and accessing 1D Poisson
simulation output data, including energy levels, electric fields,
and carrier densities.
"""

import csv
from pathlib import Path

import numpy as np


class OutputData:
    """
    Parser and container for 1D Poisson simulation output data.

    This class reads the output file from a 1D Poisson simulation and
    provides access to various physical quantities through properties.

    Attributes:
        _FIELD_NAMES: Expected column names in the output file.
    """

    _FIELD_NAMES = (
        "Y (ang)",
        "Ec (eV)",
        "Ev (eV)",
        "E (V/cm)",
        "Ef (eV)",
        "n (cm-3)",
        "p (cm-3)",
        "Nd - Na (cm-3)",
        "el eval 1 (eV)",
    )

    def __init__(self, output_file: str | Path) -> None:
        """
        Initialize OutputData by parsing a 1D Poisson output file.

        Args:
            output_file: Path to the output file from 1D Poisson simulation.
                        Expected to be a CSV-like file with specific columns.

        Raises:
            FileNotFoundError: If the output file does not exist.
            ValueError: If the file format is invalid or required columns
                       are missing.
        """
        z: list[float] = []
        energy_conduction: list[float] = []
        energy_valence: list[float] = []
        electric_field: list[float] = []
        energy_fermi: list[float] = []
        density_electron: list[float] = []
        density_hole: list[float] = []
        self._energy_ground_state: float | None = None
        self._position_ground_state: float | None = None

        with open(output_file, "rt") as f:
            reader = csv.DictReader(
                f,
                fieldnames=self._FIELD_NAMES,
                delimiter="\t",
            )

            for i, row in enumerate(reader):
                if i == 0:
                    continue

                z.append(float(row["Y (ang)"]) / 1e1)
                energy_conduction.append(float(row["Ec (eV)"]))
                energy_valence.append(float(row["Ev (eV)"]))
                electric_field.append(float(row["E (V/cm)"]))
                energy_fermi.append(float(row["Ef (eV)"]))
                density_electron.append(float(row["n (cm-3)"]))
                density_hole.append(float(row["p (cm-3)"]))

                if (
                    row["el eval 1 (eV)"] is not None and
                    self._energy_ground_state is None
                ):
                    self._energy_ground_state = float(row["el eval 1 (eV)"])
                    self._position_ground_state = float(row["Y (ang)"]) / 1e1

        self._z = np.array(z)
        self._energy_conduction = np.array(energy_conduction)
        self._energy_valence = np.array(energy_valence)
        self._electric_field = np.array(electric_field)
        self._energy_fermi = np.array(energy_fermi)
        self._density_electron = np.array(density_electron)
        self._density_hole = np.array(density_hole)

    @property
    def z(self) -> np.ndarray:
        """Position coordinates in nanometers."""
        return self._z

    @property
    def energy_conduction(self) -> np.ndarray:
        """Conduction band energy in eV."""
        return self._energy_conduction

    @property
    def energy_valence(self) -> np.ndarray:
        """Valence band energy in eV."""
        return self._energy_valence

    @property
    def electric_field(self) -> np.ndarray:
        """Electric field in V/cm."""
        return self._electric_field

    @property
    def energy_fermi(self) -> np.ndarray:
        """Fermi energy in eV."""
        return self._energy_fermi

    @property
    def density_electron(self) -> np.ndarray:
        """Electron density in cm^-3."""
        return self._density_electron

    @property
    def density_hole(self) -> np.ndarray:
        """Hole density in cm^-3."""
        return self._density_hole

    @property
    def energy_ground_state(self) -> float:
        """Ground state energy in eV."""
        return self._energy_ground_state

    @property
    def position_ground_state(self) -> float:
        """Ground state position in nanometers."""
        return self._position_ground_state
