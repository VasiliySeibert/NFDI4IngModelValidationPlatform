import semantic_benchmark
import utils

def main():
    benchmark_file = "/Users/mahdi/Documents/GitHub/NFDI4IngModelValidationPlatform/examples/linear-elastic-plate-with-hole/benchmark.json"
    simulation_result_path = "/Users/mahdi/Documents/GitHub/NFDI4IngModelValidationPlatform/examples/linear-elastic-plate-with-hole/fenics/results"
    benchmark_object = semantic_benchmark.BenchmarkLoader(benchmark_file).load()
    
    for step in benchmark_object.processing_steps:
        print(f"Processing Step: {step.label}")
        for config in step.configurations:
            print(f"  Configuration: {config.label}")
            for part in config.parts:
                if isinstance(part, semantic_benchmark.NumericalParameter):
                    print(f"    Numerical Parameter: {part.label} = {part.numerical_value} {part.unit}")
                elif isinstance(part, semantic_benchmark.TextParameter):
                    print(f"    Text Parameter: {part.label} = {part.string_value}")
        
        for tool in step.employed_tools:
            print(f"  Employed Tool: {tool.label}")
            
    utils.create_main_ro(simulation_result_path, benchmark_object)

if __name__ == "__main__":
    main()
