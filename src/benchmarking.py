from pathlib import Path
from typing import Optional
import shutil
import subprocess




class benchmark:
    """
    Represents a benchmark instance and manages all related operations.
    """
    def __init__(self, name: str, benchmark_dir: Path, benchmark_uri: Optional[str] = None):
        """
        Initialize a Benchmark instance.
        
        Args:
            name: The name of the benchmark
            benchmark_dir: Optional path to the benchmark directory
            benchmark_uri: Optional URI/URL for the benchmark
        """
        self.name = name
        self.benchmark_dir = benchmark_dir
        self.benchmark_uri = benchmark_uri
        self.mesh = {}
        self.tool = {}
    
        
        
        
    def add_tool(self, name: str, version: Optional[str] = None, uri: Optional[str] = None):
        """
        Register a new tool with optional metadata.
        
        Args:
            name: Name of the tool
            version: Optional version string
            uri: Optional URI/URL for tool documentation
        """
        
        #if not Path(name).exists():
        #    raise FileNotFoundError(f"Tool directory not found: {name}")        
        
        tool_info = {
            "name": name,
            "version": version,
            "uri": uri if uri is not None else "NA",
        }
        self.tool.update(tool_info)
        
        
        
         
    def add_tool_scripts(self, simulation_script: Path, environment_file: Path):
        """
        Add a command or script for the tool.
        
        Args:
            tool_name: Name of the tool to add script to
            script_cmd: Command or script path
            environment_file: Path to conda environment file
        """

        #if not (Path(self.tool["name"]) / simulation_script).exists():
        if not simulation_script.exists():
            raise FileNotFoundError(f"Simulation script not found: {simulation_script}")
        
        #if not (Path(self.tool["name"]) / environment_file).exists():
        if not environment_file.exists():
            raise FileNotFoundError(f"Environment file not found: {environment_file}")

        self.tool.update({"simulation_script": simulation_script, "environment_file": environment_file})
        
        
        
        
    def add_tool_workflow(self, workflow_file: Path):
        """
        Add a Snakemake workflow file for the tool.
        
        Args:
            workflow_file: Path to the Snakemake workflow file
        """
        
        if workflow_file.exists():
            raise FileNotFoundError(f"Workflow file not found: {workflow_file}")

        self.tool.update({"workflow_file": workflow_file})  
     
        
        
        
    def generate_workflow(self, parameter_file: str, configuration: str):
        """
        Generate the Snakemake workflow for the benchmark with the associated tool.
        parameter_file: The name of the parameter file to be used in the workflow.
        configuration: The name of the configuration to be used for naming the output directory and files.
        """
        
        ###############################################################################
        #Read the simulation tool workflow template
        ###############################################################################

        if "simulation_script" in self.tool and "workflow_file" not in self.tool:
            # Load template from external file
            tool_template_path = self.benchmark_dir / "tool_workflow_template.txt"

            with open(tool_template_path, 'r') as f:
                tool_template = f.read()

            # Replace placeholders with actual values
            tool_workflow_content = tool_template.replace("$SIMULATION_SCRIPT$", self.tool["simulation_script"].name) \
                                                  .replace("$TOOL_ENVIRONMENT_FILE$", self.tool["environment_file"].name)
                                                  
        ###############################################################################
        #Read the simulation tool user-defined workflow 
        ###############################################################################
                                                                             
        elif "workflow_file" in self.tool and "simulation_script" not in self.tool:
            #tool_workflow_path = Path(self.tool["name"]) / self.tool["workflow_file"]
            with open(self.tool["workflow_file"], 'r') as f:
                tool_workflow_content = f.read() 
            
        else:
            raise ValueError("Either tool scripts (the simulation script and the environment file) or tool workflow must be provided.")

        ###############################################################################
        # Append the simulation tool workflow to the main workflow template
        ###############################################################################
        
        main_template_path = self.benchmark_dir / "main_workflow_template.txt"
        with open(main_template_path, 'r') as f:
            main_template = f.read()     
            
        main_workflow_content = main_template.replace("$TOOL_WORKFLOW$", tool_workflow_content) \
                                            .replace("$BENCHMARK_NAME$", self.name) \
                                            .replace("$BENCHMARK_URI$", "https://portal.mardi4nfdi.de/wiki/Model:6775296")
                                            
        
        self.output_dir = self.benchmark_dir / "results" / configuration
        self.output_dir.mkdir(parents=True, exist_ok=True)           
            
        # Copy files from benchmark_dir to self.output_dir, excluding non-matching parameter files and workflow template files
        for item in self.benchmark_dir.iterdir():
            if item.is_file():
                if item.name.startswith("parameters_"):
                    # Only copy the matching parameter file
                    if item.name == parameter_file:
                        item_copy = self.output_dir / "parameters.json"
                        shutil.copy(item, item_copy)
                elif item.name not in [tool_template_path.name, main_template_path.name]:  # Exclude template files
                    # Copy all non-parameter files
                    shutil.copy(item, self.output_dir / item.name)
                
        
        with open(self.output_dir / "Snakefile", 'w') as f:
            f.write(main_workflow_content)

        print(f"Snakefile generated successfully")  
        
        
        
     
    def run_workflow(self):
        """
        Run the generated Snakemake workflow.
        """
        if not (self.output_dir / "Snakefile").exists():
            raise ValueError("Snakemake workflow file not found. Please generate the workflow first.")
        
        #Creates a directory to store the conda environments. The environments are shared across different parameter configurations.
        #To avoid redundant creation of environments, this path will be passed to all snakemake files during execution.
        
        shared_env_dir = self.benchmark_dir / "conda_envs"
        shared_env_dir.mkdir(parents=True, exist_ok=True)
        
        # Run the Snakemake workflow using subprocess
        try:
            subprocess.run(["snakemake", "--use-conda", "--force", "--cores", "all", "--conda-prefix", str(self.benchmark_dir / "conda_envs")], check=True, cwd=self.output_dir)
            print("Workflow executed successfully.")
            
            #Running the reporter plugin.
            subprocess.run(["snakemake", "--use-conda", "--force", "--cores", "all", 
                           "--reporter", "metadata4ing", 
                           "--report-metadata4ing-filename", "SubCrate"], check=True, cwd=self.output_dir)

        except subprocess.CalledProcessError as e:
            print(f"Error occurred while running the workflow: {e}")
