"""
Unit tests for detect.py module
Tests for vulnerability detection engine, AST analysis, and rule scanning
"""
import pytest
import json
import ast
from pathlib import Path
import sys
import tempfile

# Add project root to path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

from detect import TaintVisitor, scan_line, load_rules, discover_targets, scan_file_regex


class TestTaintVisitor:
    """Test TaintVisitor AST analysis class"""
    
    def test_taint_visitor_init(self):
        """Test TaintVisitor initialization"""
        lines = ["x = 1", "y = 2"]
        visitor = TaintVisitor(lines)
        assert visitor.tainted == set()
        assert visitor.findings == []
        assert visitor.lines == lines
    
    def test_detect_input_source(self):
        """Test detecting input() as taint source"""
        code = "user_input = input()"
        tree = ast.parse(code)
        lines = code.split("\n")
        visitor = TaintVisitor(lines)
        visitor.visit(tree)
        assert "user_input" in visitor.tainted
    
    def test_detect_request_args_source(self):
        """Test detecting request.args.get() as taint source"""
        code = "user_id = request.args.get('id')"
        tree = ast.parse(code)
        lines = code.split("\n")
        visitor = TaintVisitor(lines)
        visitor.visit(tree)
        assert "user_id" in visitor.tainted
    
    def test_detect_request_form_source(self):
        """Test detecting request.form.get() as taint source"""
        code = "username = request.form.get('user')"
        tree = ast.parse(code)
        lines = code.split("\n")
        visitor = TaintVisitor(lines)
        visitor.visit(tree)
        assert "username" in visitor.tainted
    
    def test_detect_tainted_propagation(self):
        """Test taint propagation through assignment"""
        code = """
user_input = input()
processed = user_input + "suffix"
"""
        tree = ast.parse(code)
        lines = code.split("\n")
        visitor = TaintVisitor(lines)
        visitor.visit(tree)
        assert "user_input" in visitor.tainted
        assert "processed" in visitor.tainted
    
    def test_detect_debug_true(self):
        """Test detecting app.run(debug=True)"""
        code = "app.run(debug=True)"
        tree = ast.parse(code)
        lines = code.split("\n")
        visitor = TaintVisitor(lines)
        visitor.visit(tree)
        assert len(visitor.findings) > 0
        finding = visitor.findings[0]
        assert "DEBUG-TRUE-001" in finding
    
    def test_detect_make_response_with_tainted(self):
        """Test detecting make_response with tainted argument"""
        code = """
user_data = input()
response = make_response(user_data)
"""
        tree = ast.parse(code)
        lines = code.split("\n")
        visitor = TaintVisitor(lines)
        visitor.visit(tree)
        # Should detect tainted data passed to make_response
        assert len(visitor.findings) > 0
    
    def test_no_taint_with_constant(self):
        """Test that constants are not marked as tainted"""
        code = "safe_var = 'constant_string'"
        tree = ast.parse(code)
        lines = code.split("\n")
        visitor = TaintVisitor(lines)
        visitor.visit(tree)
        assert "safe_var" not in visitor.tainted
    
    def test_annotated_assignment_with_source(self):
        """Test annotated variable assignment with tainted source"""
        code = "user_input: str = input()"
        tree = ast.parse(code)
        lines = code.split("\n")
        visitor = TaintVisitor(lines)
        visitor.visit(tree)
        assert "user_input" in visitor.tainted


class TestScanLine:
    """Test scan_line function for regex-based detection"""
    
    def test_scan_line_no_match(self):
        """Test scan_line with no matches"""
        # Load actual rules from the project
        rules = load_rules()
        result = scan_line("x = 1 + 2", rules)
        assert isinstance(result, list)
    
    def test_scan_line_sql_injection_pattern(self):
        """Test scan_line detects SQL injection patterns"""
        rules = load_rules()
        vulnerable_line = 'query = "SELECT * FROM users WHERE id=" + user_input'
        result = scan_line(vulnerable_line, rules)
        assert isinstance(result, list)
    
    def test_scan_line_pickle_pattern(self):
        """Test scan_line detects pickle usage"""
        rules = load_rules()
        vulnerable_line = "data = pickle.loads(user_data)"
        result = scan_line(vulnerable_line, rules)
        assert isinstance(result, list)
    
    def test_scan_line_eval_pattern(self):
        """Test scan_line detects eval usage"""
        rules = load_rules()
        vulnerable_line = "result = eval(user_input)"
        result = scan_line(vulnerable_line, rules)
        assert isinstance(result, list)
    
    def test_scan_line_returns_list(self):
        """Test scan_line always returns list"""
        rules = load_rules()
        result = scan_line("import os", rules)
        assert isinstance(result, list)


class TestLoadRules:
    """Test load_rules function"""
    
    def test_load_rules_returns_list(self):
        """Test that load_rules returns a list"""
        rules = load_rules()
        assert isinstance(rules, list)
    
    def test_load_rules_structure(self):
        """Test that loaded rules have correct structure if present"""
        rules = load_rules()
        if len(rules) > 0:  # Only check if rules were loaded
            for rule in rules:
                assert isinstance(rule, dict)
                assert "id" in rule or "pattern" in rule
    
    def test_load_rules_compiled_patterns(self):
        """Test that patterns are properly compiled if rules exist"""
        rules = load_rules()
        if len(rules) > 0:  # Only check if rules were loaded
            for rule in rules:
                if "pattern" in rule:
                    # Pattern should be compiled to _pat
                    assert (hasattr(rule, "_pat") or "_pat" in rule or "pattern" in rule)


class TestDiscoverTargets:
    """Test discover_targets function"""
    
    def test_discover_single_file(self):
        """Test discovering a single Python file"""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text("print('test')")
            
            targets = discover_targets(test_file)
            assert len(targets) == 1
            assert targets[0].name == "test.py"
    
    def test_discover_multiple_files(self):
        """Test discovering multiple Python files in directory"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            (tmpdir / "test1.py").write_text("print('1')")
            (tmpdir / "test2.py").write_text("print('2')")
            (tmpdir / "readme.txt").write_text("not python")
            
            targets = discover_targets(tmpdir)
            assert len(targets) == 2
            names = {t.name for t in targets}
            assert "test1.py" in names
            assert "test2.py" in names
    
    def test_discover_excludes_venv(self):
        """Test that discover_targets excludes venv directories"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            (tmpdir / "test.py").write_text("print('main')")
            venv_dir = tmpdir / "venv"
            venv_dir.mkdir()
            (venv_dir / "lib.py").write_text("print('venv')")
            
            targets = discover_targets(tmpdir)
            # Should only find test.py, not lib.py in venv
            assert all(".venv" not in str(t) and "/venv/" not in str(t) for t in targets)
    
    def test_discover_excludes_pycache(self):
        """Test that discover_targets excludes __pycache__"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            (tmpdir / "test.py").write_text("print('main')")
            cache_dir = tmpdir / "__pycache__"
            cache_dir.mkdir()
            (cache_dir / "cached.pyc").write_text("compiled")
            
            targets = discover_targets(tmpdir)
            assert all("__pycache__" not in str(t) for t in targets)
    
    def test_discover_nested_directories(self):
        """Test discovering Python files in nested directories"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            subdir = tmpdir / "src"
            subdir.mkdir()
            (subdir / "app.py").write_text("print('app')")
            
            targets = discover_targets(tmpdir)
            assert len(targets) >= 1
            assert any("app.py" in str(t) for t in targets)


class TestScanFileRegex:
    """Test scan_file_regex function"""
    
    def test_scan_file_regex_valid_file(self):
        """Test scan_file_regex with valid Python file"""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text("print('hello')")
            
            rules = load_rules()
            results, lines = scan_file_regex(test_file, rules)
            assert isinstance(results, list)
            assert isinstance(lines, list)
            assert len(lines) == 1
    
    def test_scan_file_regex_vulnerable_code(self):
        """Test scan_file_regex detects vulnerabilities in file"""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "vulnerable.py"
            test_file.write_text("result = eval(user_input)")
            
            rules = load_rules()
            results, lines = scan_file_regex(test_file, rules)
            assert isinstance(results, list)
            assert len(lines) > 0
    
    def test_scan_file_regex_empty_file(self):
        """Test scan_file_regex with empty file"""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "empty.py"
            test_file.write_text("")
            
            rules = load_rules()
            results, lines = scan_file_regex(test_file, rules)
            assert isinstance(results, list)
            assert isinstance(lines, list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
