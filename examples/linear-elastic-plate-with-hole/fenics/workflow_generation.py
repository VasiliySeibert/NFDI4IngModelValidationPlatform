import sys
from pathlib import Path
import zipfile
import json

# Add src directory to Python path
src_path = Path(__file__).resolve().parent.parent.parent.parent / "src"
sys.path.insert(0, str(src_path))

from benchmarking import benchmark

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

linear_elastic_problem.add_tool("fenics", \
                                version="0.9.0", \
                                uri="https://github.com/FEniCS/dolfinx")

linear_elastic_problem.add_tool_scripts(
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
        print(data.get("element-size").get("value"))
        if data.get("element-size").get("value") >= 0.025:
            linear_elastic_problem.generate_workflow(file.name, data.get("configuration"))
            linear_elastic_problem.run_workflow()
           