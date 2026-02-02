from benchmarking import benchmark
from pathlib import Path
import zipfile

with zipfile.ZipFile("linear-elastic-plate-with-hole.zip", 'r') as zip_ref:
    # Extract all files
    zip_ref.extractall()

linear_elastic_problem = benchmark("linear-elastic-plate-with-hole") 
linear_elastic_problem.add_tool("fenics", version="0.9.0", uri="https://github.com/FEniCS/dolfinx")
linear_elastic_problem.add_tool_scripts(
    simulation_script="run_fenics_simulation.py",
    environment_file="environment_simulation.yml"
)
linear_elastic_problem.generate_workflow_and_configuration_file()