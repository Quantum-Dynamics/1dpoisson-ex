# 1D Poisson Extension (ldpoisson-ex)

A Python package for running [1D Poisson](https://www3.nd.edu/~gsnider/) simulations with parameter sweeps. This tool automates the execution of 1D Poisson calculations across multiple parameter combinations and provides structured output data handling.

## Installation

### Requirements

- Python 3.12+
- OS: Windows

### Installing 1D Poisson

1. Download the [1D Poisson executable](https://www3.nd.edu/~gsnider/1D_Poi_PC_b8k_CMD.zip), decompress it, and place it in a suitable directory.
2. Copy the path to the `1dpoisson.exe` executable (the path will be used in the configuration file).

### From GitHub (Recommended)

You can install directly from the GitHub repository:

```bash
# Install latest version from main branch
pip install git+https://github.com/your-username/ldpoisson-ex.git

# Install specific branch or tag
pip install git+https://github.com/your-username/ldpoisson-ex.git@branch-name

# Install in development mode from GitHub
pip install -e git+https://github.com/your-username/ldpoisson-ex.git#egg=ldpoisson-ex
```

### From Source

If you have cloned the repository locally:

```bash
# Clone the repository
git clone https://github.com/your-username/ldpoisson-ex.git
cd ldpoisson-ex

# Install from source
pip install .

# Install in development mode
pip install -e .
```

### Using Poetry (For Development)

```bash
# Clone and navigate to repository
git clone https://github.com/your-username/ldpoisson-ex.git
cd ldpoisson-ex

# Install dependencies
poetry install

# Activate virtual environment
poetry shell
```

## Usage

### Command Line Interface

After installation, you can run simulations using the `1dpoisson-ex` command:

```bash
# Run simulation with configuration file
1dpoisson-ex config.yaml
```

Or using Poetry:

```bash
# Run with Poetry
poetry run 1dpoisson-ex config.yaml
```

### Python Module

You can also run the package as a Python module:

```bash
# Run as module
python -m ldpoisson_ex config.yaml
```

### Programmatic Usage

```python
from ldpoisson_ex import lDPoissonExSolver, load_simulation_config

# Load configuration
config = load_simulation_config("config.yaml")

# Create and run solver
solver = lDPoissonExSolver(config)
solver.run()
```

## Configuration

Create a YAML configuration file to specify simulation parameters:

```yaml
# config.yaml
file_template: "template.txt"
dir_output: "surface_level_dep"
path_1d_poisson: "/path/to/1dpoisson.exe"
log_file: "simulation.log"

constants:
    - name: temperature
      value: 4.2

variables:
    - name: surface_level
      value:
        start: 0.5
        end: 1.0
        step: 0.1
      format: "{:.1f}"
```

### Variable Types

Variables can be specified in two ways:

1. **Array specification**: Define start, end, and step values
   ```yaml
   - name: surface_level
     value:
       start: 0.5
       end: 1.0
       step: 0.1
     format: "{:.1f}"  # Optional formatting
   ```

2. **List of values**: Explicitly list all values
   ```yaml
   - name: thickness
     value: [10.0, 20.0, 30.0]
   ```

### Configuration Parameters

- **file_template**: Path to Jinja2 template file for input generation
- **dir_output**: Output directory for simulation results
- **path_1d_poisson**: Path to the 1D Poisson executable
- **log_file**: Optional log file path
- **constants**: List of fixed parameters
- **variables**: List of parameters to sweep over
  - **format**: Optional Python format string for variable values

## Template Files

Input files are generated using Jinja2 templates. Use variable names in double braces:

```
# Example template.txt
surface	schottky={{ surface_level }}	v1
GaAs	t=100

AlGaAs	t=400	x=0.196
AlGaAs  t=17.1  x=1
2{
    GaAs    t=11.4
    sheetcharge=1.0e12
    GaAs    t=11.4
    AlGaAs  t=17.1  x=1
}

AlGaAs	t=300   x=0.196
# ... rest of template
```

## Output

The tool generates:
- Individual simulation results in separate directories
- Parsed output data accessible through the `OutputData` class
- Simulation logs (if specified)
