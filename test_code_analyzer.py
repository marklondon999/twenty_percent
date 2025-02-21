import unittest
import ast
from code_analyzer import CodeAnalyzer  # Assuming your class is in code_analyzer.py

class TestCodeAnalyzer(unittest.TestCase):

    def setUp(self):
        """Set up for test methods."""
        self.repo_path = "/dummy/repo/path"  # Dummy path, not actually used in these tests
        self.repo_name = "test_repo"
        self.analyzer = CodeAnalyzer(self.repo_path, self.repo_name)

    def _get_function_node_and_source(self, code_string, function_name="test_function"):
        """Helper function to parse code and get a FunctionDef node."""
        tree = ast.parse(code_string)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == function_name:
                return node, code_string  # Return node and original source
        self.fail(f"Function '{function_name}' not found in code string.") # Fail if function not found

    def test_analyze_function_basic(self):
        """Test analyze_function with a basic function."""
        code = """
def test_function(arg1, arg2):
    \"\"\"Basic function docstring.\"\"\"
    variable1 = arg1 + arg2
    return variable1
"""
        function_node, source = self._get_function_node_and_source(code)
        self.analyzer.analyze_function(function_node, "test_file.py", source)
        self.assertEqual(len(self.analyzer.dataset), 1)
        function_data = self.analyzer.dataset[0]

        self.assertEqual(function_data['function_name'], 'test_function')
        self.assertEqual(function_data['docstring'], "Basic function docstring.")
        self.assertEqual(function_data['variables'], ['arg1', 'arg2', 'variable1'])
        expected_code_chunk = """def test_function(arg1, arg2):
    \"\"\"Basic function docstring.\"\"\"
    variable1 = arg1 + arg2
    return variable1"""
        self.assertEqual(function_data['code_chunk'].strip(), expected_code_chunk.strip())


    def test_analyze_function_no_docstring(self):
        """Test analyze_function with a function that has no docstring."""
        code = """
def test_function(arg1):
    variable2 = arg1 * 2
    return variable2
"""
        function_node, source = self._get_function_node_and_source(code)
        self.analyzer.analyze_function(function_node, "another_file.py", source)
        self.assertEqual(self.analyzer.dataset[1]['function_name'], 'test_function') #dataset index 1 now
        self.assertIsNone(self.analyzer.dataset[1]['docstring'])
        self.assertEqual(self.analyzer.dataset[1]['variables'], ['arg1', 'variable2'])


    def test_analyze_function_complex_vars(self):
        """Test analyze_function with complex variable extraction (comprehensions, try)."""
        code = """
def test_function(data):
    results = [x*2 for x in data if x > 5]
    try:
        value = results[0]
    except IndexError as e:
        value = None
    return value
"""
        function_node, source = self._get_function_node_and_source(code)
        self.analyzer.analyze_function(function_node, "complex_file.py", source)
        self.assertEqual(self.analyzer.dataset[2]['function_name'], 'test_function') #dataset index 2 now
        self.assertEqual(self.analyzer.dataset[2]['variables'], ['data', 'results', 'x', 'value', 'e']) # 'e' for exception handler


    def test_analyze_function_kwargs_varargs(self):
        """Test analyze_function with *args, **kwargs, keyword-only args."""
        code = """
def test_function(arg1, *args, kw_only, **kwargs):
    z = arg1 + sum(args) + sum(kwargs.values()) + kw_only
    return z
"""
        function_node, source = self._get_function_node_and_source(code)
        self.analyzer.analyze_function(function_node, "args_file.py", source)
        self.assertEqual(self.analyzer.dataset[3]['function_name'], 'test_function') #dataset index 3 now
        self.assertEqual(self.analyzer.dataset[3]['variables'], ['arg1', 'args', 'kw_only', 'kwargs', 'z'])


    def test_analyze_function_code_extraction_indentation(self):
        """Test analyze_function correctly extracts code with indentation and comments."""
        code = """
def test_function(value):
    # A comment line before
    if value > 10:
        # Indented comment
        result = value * 2
    else:
        result = value / 2
    # Comment after the if/else
    return result # Inline comment
"""
        function_node, source = self._get_function_node_and_source(code)
        self.analyzer.analyze_function(function_node, "indent_file.py", source)
        expected_code_chunk = """def test_function(value):
    # A comment line before
    if value > 10:
        # Indented comment
        result = value * 2
    else:
        result = value / 2
    # Comment after the if/else
    return result # Inline comment"""
        self.assertEqual(self.analyzer.dataset[4]['code_chunk'].strip(), expected_code_chunk.strip()) #dataset index 4 now


    def tearDown(self):
        """Clean up after test methods - reset dataset."""
        self.analyzer.dataset = [] # Important to reset dataset for each test run


if __name__ == '__main__':
    unittest.main()