#!/usr/bin/env python3
"""
Cascade Linter Dependency Analysis - Tier 3 Enhancement

Provides intelligent dependency relationship analysis to help developers understand
which files to fix first for maximum impact on code quality issues.

Core Features:
- Import graph analysis using Python AST
- Error impact scoring by dependency count
- Fix priority recommendations based on cascade effects
- Circular dependency detection
- Structured output for both CLI and programmatic use

Architecture: Algorithmic-first (no AI required), with optional AI enhancements.
"""

import ast
import sys
from pathlib import Path
from typing import Dict, List, Set, Optional, NamedTuple
from collections import defaultdict, deque
from dataclasses import dataclass
import json


class ImportNode(NamedTuple):
    """Represents an import relationship between modules"""

    importer: str  # Module doing the importing
    imported: str  # Module being imported
    import_type: str  # 'absolute', 'relative', 'builtin', 'third_party'
    line_number: int  # Line where import occurs


@dataclass
class DependencyMetrics:
    """Metrics for a single module's dependency relationships"""

    module_path: str
    imports_count: int  # How many modules this imports
    imported_by_count: int  # How many modules import this
    dependency_depth: int  # Maximum depth in dependency tree
    circular_dependencies: List[str]  # Modules involved in circular deps
    impact_score: float  # Calculated impact score (0-100)
    criticality_rank: int  # Rank by criticality (1 = most critical)


@dataclass
class ErrorImpactAnalysis:
    """Analysis of how MyPy errors cascade through dependencies"""

    file_path: str
    error_count: int
    affected_modules: List[str]  # Modules that depend on this file
    cascade_impact: int  # Total modules affected by errors here
    fix_priority_score: float  # Priority score for fixing (0-100)
    error_types: Dict[str, int]  # Count of each error type


class ImportGraphBuilder:
    """Builds import dependency graph from Python source code"""

    def __init__(self, project_root: str):
        self.project_root = Path(project_root).resolve()
        self.import_graph: Dict[str, Set[str]] = defaultdict(set)
        self.reverse_graph: Dict[str, Set[str]] = defaultdict(set)
        self.import_nodes: List[ImportNode] = []
        self.python_files: Set[str] = set()

    def analyze_project(self) -> None:
        """Analyze entire project to build import graph"""
        print(f"Analyzing imports in {self.project_root}")

        # Find all Python files
        self._discover_python_files()

        # Analyze imports in each file
        for file_path in self.python_files:
            try:
                self._analyze_file_imports(file_path)
            except Exception as e:
                print(f"Warning: Could not analyze {file_path}: {e}")

        print(
            f"Found {len(self.import_nodes)} import relationships across {len(self.python_files)} files"
        )

    def _discover_python_files(self) -> None:
        """Find all Python source files in the project"""
        for py_file in self.project_root.rglob("*.py"):
            # Skip common non-source directories
            if any(
                skip in py_file.parts
                for skip in [
                    "__pycache__",
                    ".pytest_cache",
                    "venv",
                    "env",
                    ".git",
                    "node_modules",
                ]
            ):
                continue

            # Convert to relative path for consistency
            rel_path = py_file.relative_to(self.project_root)
            self.python_files.add(str(rel_path))

    def _analyze_file_imports(self, file_path: str) -> None:
        """Analyze imports in a single Python file"""
        full_path = self.project_root / file_path

        try:
            with open(full_path, "r", encoding="utf-8") as f:
                content = f.read()
        except UnicodeDecodeError:
            # Try with different encoding
            with open(full_path, "r", encoding="latin-1") as f:
                content = f.read()

        try:
            tree = ast.parse(content, filename=str(full_path))
        except SyntaxError as e:
            print(f"Syntax error in {file_path}: {e}")
            return

        # Convert file path to module path
        module_path = self._file_to_module_path(file_path)

        # Extract imports using AST visitor
        visitor = ImportVisitor(module_path, str(self.project_root))
        visitor.visit(tree)

        # Add import relationships
        for import_node in visitor.imports:
            self.import_nodes.append(import_node)
            self.import_graph[import_node.importer].add(import_node.imported)
            self.reverse_graph[import_node.imported].add(import_node.importer)

    def _file_to_module_path(self, file_path: str) -> str:
        """Convert file path to Python module path"""
        # Remove .py extension and convert slashes to dots
        module_path = file_path.replace(".py", "").replace("/", ".").replace("\\", ".")

        # Handle __init__.py files
        if module_path.endswith(".__init__"):
            module_path = module_path[:-9]  # Remove .__init__

        return module_path


class ImportVisitor(ast.NodeVisitor):
    """AST visitor to extract import statements"""

    def __init__(self, current_module: str, project_root: str):
        self.current_module = current_module
        self.project_root = project_root
        self.imports: List[ImportNode] = []

    def visit_Import(self, node: ast.Import) -> None:
        """Handle 'import module' statements"""
        for alias in node.names:
            import_type = self._classify_import(alias.name)
            self.imports.append(
                ImportNode(
                    importer=self.current_module,
                    imported=alias.name,
                    import_type=import_type,
                    line_number=node.lineno,
                )
            )

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Handle 'from module import name' statements"""
        if node.module is None:
            return  # Handle malformed imports gracefully

        module_name = node.module

        # Handle relative imports
        if node.level > 0:
            module_name = self._resolve_relative_import(module_name, node.level)
            import_type = "relative"
        else:
            import_type = self._classify_import(module_name)

        self.imports.append(
            ImportNode(
                importer=self.current_module,
                imported=module_name,
                import_type=import_type,
                line_number=node.lineno,
            )
        )

    def _classify_import(self, module_name: str) -> str:
        """Classify import as builtin, third_party, or local"""
        if module_name in sys.builtin_module_names:
            return "builtin"

        # Check if it's a local project module
        module_path = module_name.replace(".", "/")
        local_file = Path(self.project_root) / f"{module_path}.py"
        local_package = Path(self.project_root) / module_path / "__init__.py"

        if local_file.exists() or local_package.exists():
            return "absolute"

        return "third_party"

    def _resolve_relative_import(self, module_name: Optional[str], level: int) -> str:
        """Resolve relative import to absolute module path"""
        current_parts = self.current_module.split(".")

        # Go up 'level' number of directories
        if level >= len(current_parts):
            # Can't go higher than project root
            base_parts = []
        else:
            base_parts = current_parts[:-level]

        if module_name:
            return ".".join(base_parts + [module_name])
        else:
            return ".".join(base_parts)


class DependencyAnalyzer:
    """Analyzes dependency relationships and calculates impact metrics"""

    def __init__(self, import_graph_builder: ImportGraphBuilder):
        self.graph_builder = import_graph_builder
        self.metrics: Dict[str, DependencyMetrics] = {}

    def analyze_dependencies(self) -> Dict[str, DependencyMetrics]:
        """Perform comprehensive dependency analysis"""
        print("Calculating dependency metrics...")

        # Calculate basic metrics for each module
        for module in self.graph_builder.python_files:
            module_path = self.graph_builder._file_to_module_path(module)
            self.metrics[module_path] = self._calculate_module_metrics(module_path)

        # Calculate impact scores and rankings
        self._calculate_impact_scores()
        self._assign_criticality_rankings()

        return self.metrics

    def _calculate_module_metrics(self, module_path: str) -> DependencyMetrics:
        """Calculate metrics for a single module"""
        imports = self.graph_builder.import_graph.get(module_path, set())
        imported_by = self.graph_builder.reverse_graph.get(module_path, set())

        # Filter to only local project imports
        local_imports = {
            imp
            for imp in imports
            if any(
                node.imported == imp and node.import_type in ["absolute", "relative"]
                for node in self.graph_builder.import_nodes
            )
        }
        local_imported_by = {
            imp
            for imp in imported_by
            if any(
                node.importer == imp and node.import_type in ["absolute", "relative"]
                for node in self.graph_builder.import_nodes
            )
        }

        # Calculate dependency depth
        depth = self._calculate_dependency_depth(module_path)

        # Find circular dependencies
        circular_deps = self._find_circular_dependencies(module_path)

        return DependencyMetrics(
            module_path=module_path,
            imports_count=len(local_imports),
            imported_by_count=len(local_imported_by),
            dependency_depth=depth,
            circular_dependencies=circular_deps,
            impact_score=0.0,  # Calculated later
            criticality_rank=0,  # Assigned later
        )

    def _calculate_dependency_depth(self, module_path: str) -> int:
        """Calculate maximum dependency depth using BFS"""
        visited = set()
        queue = deque([(module_path, 0)])
        max_depth = 0

        while queue:
            current, depth = queue.popleft()
            if current in visited:
                continue

            visited.add(current)
            max_depth = max(max_depth, depth)

            # Add dependencies
            for dependency in self.graph_builder.import_graph.get(current, set()):
                if dependency not in visited:
                    queue.append((dependency, depth + 1))

        return max_depth

    def _find_circular_dependencies(self, module_path: str) -> List[str]:
        """Find circular dependencies involving this module"""

        def dfs(current: str, path: List[str], visited: Set[str]) -> List[str]:
            if current in path:
                # Found a cycle
                cycle_start = path.index(current)
                return path[cycle_start:]

            if current in visited:
                return []

            visited.add(current)
            path.append(current)

            for dependency in self.graph_builder.import_graph.get(current, set()):
                cycle = dfs(dependency, path.copy(), visited.copy())
                if cycle:
                    return cycle

            return []

        cycle = dfs(module_path, [], set())
        return cycle if module_path in cycle else []

    def _calculate_impact_scores(self) -> None:
        """Calculate impact scores for all modules"""
        max_imported_by = max(
            (m.imported_by_count for m in self.metrics.values()), default=1
        )
        max_imports = max((m.imports_count for m in self.metrics.values()), default=1)
        max_depth = max((m.dependency_depth for m in self.metrics.values()), default=1)

        for metrics in self.metrics.values():
            # Impact score based on:
            # - How many modules depend on this (40%)
            # - How deep in dependency tree (30%)
            # - How many imports it has (20%)
            # - Circular dependency penalty (10%)

            dependency_factor = (metrics.imported_by_count / max_imported_by) * 40
            depth_factor = (metrics.dependency_depth / max_depth) * 30
            complexity_factor = (metrics.imports_count / max_imports) * 20
            circular_penalty = len(metrics.circular_dependencies) * -10

            metrics.impact_score = max(
                0,
                dependency_factor + depth_factor + complexity_factor + circular_penalty,
            )

    def _assign_criticality_rankings(self) -> None:
        """Assign criticality rankings based on impact scores"""
        sorted_metrics = sorted(
            self.metrics.values(), key=lambda x: x.impact_score, reverse=True
        )

        for i, metrics in enumerate(sorted_metrics, 1):
            metrics.criticality_rank = i


class ErrorPrioritizer:
    """Correlates MyPy errors with dependency impact for fix prioritization"""

    def __init__(self, dependency_analyzer: DependencyAnalyzer):
        self.dependency_analyzer = dependency_analyzer
        self.error_analyses: Dict[str, ErrorImpactAnalysis] = {}

    def analyze_error_impact(
        self, mypy_results: Dict[str, any]
    ) -> Dict[str, ErrorImpactAnalysis]:
        """Analyze impact of MyPy errors using dependency information"""
        print("Prioritizing error fixes based on dependency impact...")

        for file_path, file_results in mypy_results.items():
            # Convert file path to module path
            module_path = self._file_to_module_path(file_path)

            # Get dependency metrics
            dep_metrics = self.dependency_analyzer.metrics.get(module_path)
            if not dep_metrics:
                continue

            # Count errors by type
            error_count = len(file_results.get("issues", []))
            error_types = self._categorize_errors(file_results.get("issues", []))

            # Calculate cascade impact
            affected_modules = list(
                self.dependency_analyzer.graph_builder.reverse_graph.get(
                    module_path, set()
                )
            )
            cascade_impact = len(affected_modules)

            # Calculate fix priority score
            fix_priority = self._calculate_fix_priority(
                error_count, dep_metrics.impact_score, cascade_impact
            )

            self.error_analyses[file_path] = ErrorImpactAnalysis(
                file_path=file_path,
                error_count=error_count,
                affected_modules=affected_modules,
                cascade_impact=cascade_impact,
                fix_priority_score=fix_priority,
                error_types=error_types,
            )

        return self.error_analyses

    def _file_to_module_path(self, file_path: str) -> str:
        """Convert file path to module path (same as in ImportGraphBuilder)"""
        module_path = file_path.replace(".py", "").replace("/", ".").replace("\\", ".")
        if module_path.endswith(".__init__"):
            module_path = module_path[:-9]
        return module_path

    def _categorize_errors(self, issues: List[Dict]) -> Dict[str, int]:
        """Categorize MyPy errors by type"""
        error_types = defaultdict(int)
        for issue in issues:
            error_type = issue.get("code", "unknown")
            error_types[error_type] += 1
        return dict(error_types)

    def _calculate_fix_priority(
        self, error_count: int, impact_score: float, cascade_impact: int
    ) -> float:
        """Calculate priority score for fixing errors in this file"""
        # Priority factors:
        # - Number of errors (30%)
        # - Dependency impact score (50%)
        # - Cascade impact (20%)

        # Normalize error count (assume max 50 errors per file)
        normalized_errors = min(error_count / 50.0, 1.0) * 30

        # Impact score is already 0-100
        normalized_impact = (impact_score / 100.0) * 50

        # Normalize cascade impact (assume max 20 affected modules)
        normalized_cascade = min(cascade_impact / 20.0, 1.0) * 20

        return normalized_errors + normalized_impact + normalized_cascade

    def get_top_priority_fixes(self, limit: int = 10) -> List[ErrorImpactAnalysis]:
        """Get top priority files to fix based on error impact"""
        sorted_analyses = sorted(
            self.error_analyses.values(),
            key=lambda x: x.fix_priority_score,
            reverse=True,
        )
        return sorted_analyses[:limit]


def analyze_project_dependencies(
    project_path: str, mypy_results: Optional[Dict] = None
) -> Dict[str, any]:
    """
    Main entry point for dependency analysis

    Args:
        project_path: Path to Python project root
        mypy_results: Optional MyPy results for error impact analysis

    Returns:
        Comprehensive dependency analysis results
    """
    # Build import graph
    graph_builder = ImportGraphBuilder(project_path)
    graph_builder.analyze_project()

    # Analyze dependencies
    dep_analyzer = DependencyAnalyzer(graph_builder)
    dependency_metrics = dep_analyzer.analyze_dependencies()

    # Analyze error impact if MyPy results provided
    error_analyses = {}
    priority_fixes = []
    if mypy_results:
        error_prioritizer = ErrorPrioritizer(dep_analyzer)
        error_analyses = error_prioritizer.analyze_error_impact(mypy_results)
        priority_fixes = error_prioritizer.get_top_priority_fixes()

    # Compile results
    results = {
        "project_path": project_path,
        "analysis_summary": {
            "total_files": len(graph_builder.python_files),
            "total_imports": len(graph_builder.import_nodes),
            "local_modules": len(dependency_metrics),
            "circular_dependencies": sum(
                1 for m in dependency_metrics.values() if m.circular_dependencies
            ),
        },
        "dependency_metrics": {k: v.__dict__ for k, v in dependency_metrics.items()},
        "import_graph": {k: list(v) for k, v in graph_builder.import_graph.items()},
        "error_impact_analysis": {k: v.__dict__ for k, v in error_analyses.items()},
        "priority_fixes": [fix.__dict__ for fix in priority_fixes],
        "recommendations": _generate_recommendations(
            dependency_metrics, priority_fixes
        ),
    }

    return results


def _generate_recommendations(
    dependency_metrics: Dict[str, DependencyMetrics],
    priority_fixes: List[ErrorImpactAnalysis],
) -> List[str]:
    """Generate actionable recommendations based on analysis"""
    recommendations = []

    # Top critical modules
    top_critical = sorted(
        dependency_metrics.values(), key=lambda x: x.impact_score, reverse=True
    )[:3]
    for i, module in enumerate(top_critical, 1):
        recommendations.append(
            f"Critical Module #{i}: {module.module_path} "
            f"(affects {module.imported_by_count} modules, impact score: {module.impact_score:.1f})"
        )

    # Circular dependencies
    circular_modules = [
        m for m in dependency_metrics.values() if m.circular_dependencies
    ]
    if circular_modules:
        recommendations.append(
            f"Found {len(circular_modules)} modules with circular dependencies - "
            f"consider refactoring to improve maintainability"
        )

    # Priority fixes
    if priority_fixes:
        top_fix = priority_fixes[0]
        recommendations.append(
            f"Highest priority fix: {top_fix.file_path} "
            f"({top_fix.error_count} errors affecting {top_fix.cascade_impact} modules)"
        )

    return recommendations


if __name__ == "__main__":
    """Command-line interface for standalone testing"""
    import argparse

    parser = argparse.ArgumentParser(description="Analyze Python project dependencies")
    parser.add_argument("project_path", help="Path to Python project root")
    parser.add_argument("--output", "-o", help="Output file for JSON results")
    parser.add_argument("--mypy-results", help="Path to MyPy JSON results file")

    args = parser.parse_args()

    # Load MyPy results if provided
    mypy_results = None
    if args.mypy_results:
        with open(args.mypy_results, "r") as f:
            mypy_results = json.load(f)

    # Run analysis
    results = analyze_project_dependencies(args.project_path, mypy_results)

    # Output results
    if args.output:
        with open(args.output, "w") as f:
            json.dump(results, f, indent=2)
        print(f"Results saved to {args.output}")
    else:
        print(json.dumps(results, indent=2))
