from benchmarking import benchmark
from pathlib import Path
import zipfile

with zipfile.ZipFile("../linear-elastic-plate-with-hole.zip", 'r') as zip_ref:
    # Extract all files
    zip_ref.extractall(Path.cwd())

linear_elastic_problem = benchmark("linear-elastic-plate-with-hole") 
linear_elastic_problem.add_tool("kratos", version="10.3.1", uri="https://github.com/KratosMultiphysics/Kratos")

linear_elastic_problem.add_tool_workflow(workflow_file="kratos/Snakefile")
linear_elastic_problem.generate_workflow_and_configuration_file()