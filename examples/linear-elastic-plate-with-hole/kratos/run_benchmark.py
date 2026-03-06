from pathlib import Path
import zipfile
import json
from benchmarking import benchmark

"""
The script performs the following steps:

1. Extracts the benchmark files from a zip archive (currently assuming that it is an RO-Crate of the benchmark).
2. Creates a benchmark object and registers the simulation tool (FEniCS) along with its version and URI.
3. Adds the simulation script and environment file to the benchmark object.
4. Iterates through the parameter configuration files, checks the "element-size" value, and if it meets the specified condition (>= 0.025), it generates and executes the Snakemake workflow for that configuration.

The results of each run (and the files used by it) are stored in the directory with the configuration name.
"""


####################################################################################################
####################################################################################################
# Benchmark Extraction
####################################################################################################
####################################################################################################

zipped_benchmark_dir = Path(__file__).resolve().parent.parent
unzipped_benchmark_dir = Path(__file__).resolve().parent

with zipfile.ZipFile(zipped_benchmark_dir / "linear-elastic-plate-with-hole.zip", 'r') as zip_ref:
    # Extract all files
    zip_ref.extractall(unzipped_benchmark_dir)
    
    
####################################################################################################
####################################################################################################
# Creation of benchmark object and the addition of simulation tool scripts
####################################################################################################
####################################################################################################

linear_elastic_problem = benchmark("linear-elastic-plate-with-hole", \
                                    benchmark_dir=unzipped_benchmark_dir, \
                                    benchmark_uri="https://portal.mardi4nfdi.de/wiki/Model:6775296") 

linear_elastic_problem.add_tool("kratos", \
                                version="10.3.1", \
                                uri="https://github.com/KratosMultiphysics/Kratos")

""" linear_elastic_problem.add_tool_scripts(
    simulation_script = unzipped_benchmark_dir / "run_fenics_simulation.py",
    environment_file = unzipped_benchmark_dir / "environment_simulation.yml"
)

####################################################################################################
####################################################################################################
# Conditional creation and execution of snakemake workflows based on parameter configurations
####################################################################################################
####################################################################################################

for file in unzipped_benchmark_dir.glob("parameters_*.json"):
    with open(file, "r") as f:
        data = json.load(f)
        if data.get("element-size").get("value") >= 0.025:
            linear_elastic_problem.generate_workflow(file.name, data.get("configuration"))
            linear_elastic_problem.run_workflow()
            """