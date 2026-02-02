import json
from pathlib import Path
from typing import Optional, List, Dict, Any


class benchmark:
    """
    Represents a benchmark instance and manages all related operations.
    """
    def __init__(self, name: str):
        """
        Initialize a Benchmark instance.
        
        Args:
            name: The name of the benchmark
            benchmark_dir: Optional path to the benchmark directory
        """
        self.name = name
        self.mesh = {}
        self.tool = {}
        
    #@classmethod
    #def from_name(cls, benchmark_name: str) -> "benchmark":
    #    """
    #    Load a benchmark from a local/git folder by name.
    #    Looks up in a known folder, e.g., benchmarks/{benchmark_name}/
    #    
    #    Args:
    #        benchmark_name: Name of the benchmark to load
    #        
    #    Returns:
    #        Benchmark instance
    #        
    #    Raises:
    #        FileNotFoundError: If benchmark directory doesn't exist
    #    """
    #    benchmark_dir = Path(benchmark_name) 
    #    if not benchmark_dir.exists():
    #        raise FileNotFoundError(f"Benchmark directory not found: {benchmark_dir}")
    #    
    #    benchmark = cls(benchmark_name, benchmark_dir)
    #    
    #    return benchmark
    
        
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
        
        
    def add_tool_scripts(self, simulation_script: str, environment_file: str):
        """
        Add a command or script for the tool.
        
        Args:
            tool_name: Name of the tool to add script to
            script_cmd: Command or script path
            environment_file: Path to conda environment file
        """
        
        #if not (Path(self.tool["name"]) / simulation_script).exists():
        if not Path(simulation_script).exists():
            raise FileNotFoundError(f"Simulation script not found: {simulation_script}")
        
        #if not (Path(self.tool["name"]) / environment_file).exists():
        if not Path(environment_file).exists():
            raise FileNotFoundError(f"Environment file not found: {environment_file}")

        self.tool.update({"simulation_script": simulation_script, "environment_file": environment_file})
        
    def add_tool_workflow(self, workflow_file: str):
        """
        Add a Snakemake workflow file for the tool.
        
        Args:
            workflow_file: Path to the Snakemake workflow file
        """
        
        #if not (Path(self.tool["name"]) / workflow_file).exists():
        if not Path(workflow_file).exists():
            raise FileNotFoundError(f"Workflow file not found: {workflow_file}")

        self.tool.update({"workflow_file": workflow_file})  
     
        
    def generate_workflow_and_configuration_file(self):
        """
        Generate the Snakemake workflow for the benchmark with the associated tool.
        
        """

        if "simulation_script" in self.tool and "workflow_file" not in self.tool:
            # Load template from external file
            tool_template_path = "tool_workflow_template.txt"

            with open(tool_template_path, 'r') as f:
                tool_template = f.read()

            # Replace placeholders with actual values
            tool_workflow_content = tool_template.replace("{SIMULATION_SCRIPT}", self.tool["simulation_script"]) \
                                                  .replace("{TOOL_ENVIRONMENT_FILE}", self.tool["environment_file"])
                                                  
                                                                     
        elif "workflow_file" in self.tool and "simulation_script" not in self.tool:
            #tool_workflow_path = Path(self.tool["name"]) / self.tool["workflow_file"]
            with open(self.tool["workflow_file"], 'r') as f:
                tool_workflow_content = f.read() 
            
        else:
            raise ValueError("Either tool scripts (the simulation script and the environment file) or tool workflow must be provided.")

        # Write the Snakefile
        main_template_path = "main_workflow_template.txt"
        with open(main_template_path, 'r') as f:
            main_template = f.read()     
            
        main_workflow_content = main_template.replace("{TOOL_WORKFLOW}", tool_workflow_content)   
        
        output_path = "Snakefile"
        with open(output_path, 'w') as f:
            f.write(main_workflow_content)

        print(f"Snakefile generated successfully")  
        
        with open("workflow_config_template.json", 'r') as f:    
            workflow_config_json = json.load(f)

        # 2. add / modify things
        workflow_config_json["tool"] = self.tool["name"]
        workflow_config_json["tool_version"] = self.tool["version"]
        workflow_config_json["tool_uri"] = self.tool["uri"]

        # 3. save under a different name
        with open("workflow_config.json", "w") as f:
            json.dump(workflow_config_json, f, indent=4)
            
        print(f"Configuration file generated successfully")
            
    

    

    

    



        
        
        
        
