import os
import ast
import json

class CodeAnalyzer:
    def __init__(self, repo_path, repo_name):
        self.repo_path = repo_path
        self.repo_name = repo_name
        self.dataset = []  # List to hold function data

    def analyze_repo(self):
        """Walks through the repository and analyzes Python files."""
        for root, _, files in os.walk(self.repo_path):
            for file in files:
                if file.endswith(".py"):
                    filepath = os.path.join(root, file)
                    self.analyze_file(filepath)
        self.save_dataset()

    def analyze_file(self, filepath):
        """Analyzes a single Python file."""
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            tree = ast.parse(content)  # Parse code into AST
            for node in ast.walk(tree): # Walk through AST nodes
                if isinstance(node, ast.FunctionDef):
                    self.analyze_function(node, filepath, content)
        except Exception as e: # Basic error handling - improve this!
            print(f"Error analyzing file {filepath}: {e}")

    def analyze_function(self, function_node, filepath, file_content):
        """Analyzes a single function node from the AST, extracting code and variables."""
        function_name = function_node.name

        function_text = ast.get_source_segment(file_content, function_node)
        if function_text is None:
            print(f"Warning: Could not retrieve source for function {function_name} in {filepath}")
            return  # Skip this function

        function_text = function_text.strip()

        variables = set()
        # Extract function arguments
        for arg in function_node.args.args:
            variables.add(arg.arg)
        for arg in function_node.args.kwonlyargs:
            variables.add(arg.arg)
        if function_node.args.vararg:
            variables.add(function_node.args.vararg.arg)
        if function_node.args.kwarg:
            variables.add(function_node.args.kwarg.arg)

        # Extract assigned variables, comprehension variables, and exception handler variables (as in your code)
        for sub_node in ast.walk(function_node):
            if isinstance(sub_node, ast.Name) and isinstance(sub_node.ctx, ast.Store):
                variables.add(sub_node.id)
            elif isinstance(sub_node, (ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)):
                for generator in sub_node.generators:
                    if isinstance(generator.target, ast.Name):
                        variables.add(generator.target.id)
                    elif isinstance(generator.target, ast.Tuple):
                        for elt in generator.target.elts:
                            if isinstance(elt, ast.Name):
                                variables.add(elt.id)
            elif isinstance(sub_node, ast.Try):
                for handler in sub_node.handlers:
                    if handler.name is not None and isinstance(handler.name, str): # Check for handler.name not being None
                        variables.add(handler.name)


        # Extract docstring (if present)
        docstring = ast.get_docstring(function_node)

        function_data = {
            "repo_name": self.repo_name,
            "filepath": filepath,
            "function_name": function_name,
            "code_chunk": function_text,
            "variables": list(variables), # Convert set to list for JSON serialization
            "docstring": docstring if docstring else None, # Handle cases with no docstring
            # Add more fields as needed (parameters, return type inference later)
        }
        self.dataset.append(function_data)

    def get_function_code_chunk(self, function_node, file_content):
        """Extracts the code chunk for a function, handling splitting if needed.
           **This is where your code splitting logic will go.**
        """
        start_lineno = function_node.lineno
        end_lineno = function_node.end_lineno # Python 3.8+ for end_lineno

        if end_lineno is None: # Fallback for older Python versions if end_lineno is not available
            # Rough approximation, can be improved by parsing the code lines more carefully
            lines = file_content.splitlines()
            function_lines = lines[start_lineno-1:] # Start line is 1-indexed
            function_code = "\n".join(function_lines) # Reconstruct code
        else:
            lines = file_content.splitlines()
            function_lines = lines[start_lineno-1:end_lineno] # line numbers are 1-indexed
            function_code = "\n".join(function_lines) # Reconstruct code


        # **Token counting and splitting logic goes HERE**
        # For now, just return the whole function code

        return function_code

    def generate_prompts_for_chunk(self, code_chunk):
        """Generates boilerplate prompts for a given code chunk."""
        prompts = [
            "What does this function do?",
            "What are the input parameters for this function?",
            "What is the output of this function?",
            # Add more prompts here, potentially using templates and function data
        ]
        return prompts

    def save_dataset(self):
        """Saves the dataset to a JSON file."""
        output_filename = f"{self.repo_name}_code_dataset.json" # Or .sqlite if using SQLite
        with open(output_filename, "w") as f:
            json.dump(self.dataset, f, indent=4) # Pretty printing for readability
        print(f"Dataset saved to {output_filename}")

def main():
    #repo_path = "/home/jonny/python/ONS/rdsa-utils" 
    repo_path = "D:/coding_repos/rdsa-utils"
     # **CHANGE THIS TO YOUR REPO PATH**
    repo_name = "rdsa-utils" # **CHANGE THIS TO YOUR REPO NAME**

    analyzer = CodeAnalyzer(repo_path, repo_name)
    analyzer.analyze_repo()
    print("Analysis complete.")

if __name__ == "__main__":
    main()