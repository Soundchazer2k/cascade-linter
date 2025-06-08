# cascade_linter/gui/tools/simple_analytics.py
"""
Simple Analytics Backend - Core functionality without Qt widgets
This is a fallback that provides the essential dependency analysis
"""

import ast
import os
import json
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple, Any
from dataclasses import dataclass, field


@dataclass
class ModuleInfo:
    name: str
    file_path: str
    size_lines: int
    imports: List[str] = field(default_factory=list)
    from_imports: List[str] = field(default_factory=list)
    functions: List[str] = field(default_factory=list)
    classes: List[str] = field(default_factory=list)
    dependencies: Set[str] = field(default_factory=set)
    dependents: Set[str] = field(default_factory=set)
    complexity_score: float = 0.0


@dataclass
class RiskAssessment:
    module_name: str
    risk_level: str  # 'LOW', 'MEDIUM', 'CRITICAL'
    risk_score: float
    impact_score: float
    complexity_score: float
    risk_factors: List[str] = field(default_factory=list)


class SimpleDependencyAnalyzer:
    """Core dependency analysis without Qt dependencies"""

    def __init__(self):
        self.modules: Dict[str, ModuleInfo] = {}
        self.risk_assessments: Dict[str, RiskAssessment] = {}

    def analyze_project(self, project_paths: List[str]) -> Dict[str, Any]:
        """Analyze Python projects and return results"""

        # Reset state
        self.modules.clear()
        self.risk_assessments.clear()

        # Step 1: Discover and analyze all Python files
        for project_path in project_paths:
            self._discover_modules(project_path)

        # Step 2: Calculate risk assessments
        self._calculate_risk_assessments()

        # Step 3: Generate project health metrics
        project_health = self._calculate_project_health()

        # Build results
        results = {
            "total_modules": len(self.modules),
            "modules": {
                name: self._module_to_dict(module)
                for name, module in self.modules.items()
            },
            "risk_assessments": {
                name: self._assessment_to_dict(assessment)
                for name, assessment in self.risk_assessments.items()
            },
            "project_health": project_health,
            "risk_distribution": self._get_risk_distribution(),
        }

        return results

    def _discover_modules(self, project_path: str):
        """Discover and analyze all Python modules in a project"""
        project_root = Path(project_path)

        if not project_root.exists():
            return

        # Find all Python files
        python_files = list(project_root.rglob("*.py"))

        for file_path in python_files:
            try:
                # Skip __pycache__ and other non-source directories
                if "__pycache__" in str(file_path) or ".git" in str(file_path):
                    continue

                # Generate module name from file path
                relative_path = file_path.relative_to(project_root)
                module_name = str(relative_path.with_suffix("")).replace(os.sep, ".")

                # Analyze the module
                module_info = self._analyze_module(file_path, module_name)
                if module_info:
                    self.modules[module_name] = module_info

            except Exception:
                continue

    def _analyze_module(
        self, file_path: Path, module_name: str
    ) -> Optional[ModuleInfo]:
        """Analyze a single Python module using AST"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Parse the AST
            tree = ast.parse(content, filename=str(file_path))

            # Count lines (excluding empty lines and comments)
            lines = content.split("\n")
            size_lines = len(
                [
                    line
                    for line in lines
                    if line.strip() and not line.strip().startswith("#")
                ]
            )

            # Extract information from AST
            imports = []
            from_imports = []
            functions = []
            classes = []
            complexity_score = 0

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        from_imports.append(node.module)
                elif isinstance(node, ast.FunctionDef):
                    functions.append(node.name)
                    complexity_score += self._calculate_complexity(node)
                elif isinstance(node, ast.ClassDef):
                    classes.append(node.name)
                    complexity_score += 2  # Classes add base complexity

            return ModuleInfo(
                name=module_name,
                file_path=str(file_path),
                size_lines=size_lines,
                imports=imports,
                from_imports=from_imports,
                functions=functions,
                classes=classes,
                complexity_score=complexity_score,
            )

        except Exception:
            return None

    def _calculate_complexity(self, node: ast.FunctionDef) -> int:
        """Calculate cyclomatic complexity for a function"""
        complexity = 1  # Base complexity

        for child in ast.walk(node):
            # Count decision points
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1

        return complexity

    def _calculate_risk_assessments(self):
        """Calculate risk assessments for all modules"""
        for module_name, module_info in self.modules.items():
            assessment = self._assess_module_risk(module_info)
            self.risk_assessments[module_name] = assessment

    def _assess_module_risk(self, module_info: ModuleInfo) -> RiskAssessment:
        """Assess risk level for a single module"""
        risk_factors = []
        risk_score = 0.0

        # Factor 1: File size
        if module_info.size_lines > 500:
            risk_factors.append("Large file (>500 lines)")
            risk_score += 0.3
        elif module_info.size_lines > 200:
            risk_factors.append("Medium-sized file (>200 lines)")
            risk_score += 0.1

        # Factor 2: Complexity
        avg_complexity = module_info.complexity_score / max(
            len(module_info.functions), 1
        )
        if avg_complexity > 10:
            risk_factors.append("High average complexity")
            risk_score += 0.4
        elif avg_complexity > 5:
            risk_factors.append("Medium complexity")
            risk_score += 0.2

        # Factor 3: Module name patterns
        module_lower = module_info.name.lower()
        if any(keyword in module_lower for keyword in ["core", "main", "base"]):
            risk_factors.append("Core module")
            risk_score += 0.2

        # Determine risk level
        if risk_score > 0.6:
            risk_level = "CRITICAL"
        elif risk_score > 0.3:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"

        return RiskAssessment(
            module_name=module_info.name,
            risk_level=risk_level,
            risk_score=risk_score,
            impact_score=0.5,  # Simplified
            complexity_score=module_info.complexity_score,
            risk_factors=risk_factors,
        )

    def _calculate_project_health(self) -> Dict[str, Any]:
        """Calculate overall project health metrics"""
        if not self.modules:
            return {}

        # Calculate averages
        total_complexity = sum(m.complexity_score for m in self.modules.values())
        avg_complexity = total_complexity / len(self.modules)

        total_risk = sum(r.risk_score for r in self.risk_assessments.values())
        avg_risk_score = (
            total_risk / len(self.risk_assessments) if self.risk_assessments else 0
        )

        # Calculate health grade
        if avg_risk_score < 0.2:
            health_grade = "A"
        elif avg_risk_score < 0.4:
            health_grade = "B"
        elif avg_risk_score < 0.6:
            health_grade = "C"
        else:
            health_grade = "F"

        return {
            "health_grade": health_grade,
            "average_complexity": avg_complexity,
            "average_risk_score": avg_risk_score,
        }

    def _get_risk_distribution(self) -> Dict[str, int]:
        """Get distribution of risk levels"""
        distribution = {"CRITICAL": 0, "MEDIUM": 0, "LOW": 0}
        for assessment in self.risk_assessments.values():
            distribution[assessment.risk_level] += 1
        return distribution

    def _module_to_dict(self, module: ModuleInfo) -> Dict[str, Any]:
        return {
            "name": module.name,
            "file_path": module.file_path,
            "size_lines": module.size_lines,
            "functions": module.functions,
            "classes": module.classes,
            "complexity_score": module.complexity_score,
        }

    def _assessment_to_dict(self, assessment: RiskAssessment) -> Dict[str, Any]:
        return {
            "module_name": assessment.module_name,
            "risk_level": assessment.risk_level,
            "risk_score": assessment.risk_score,
            "impact_score": assessment.impact_score,
            "complexity_score": assessment.complexity_score,
            "risk_factors": assessment.risk_factors,
        }


# For easy importing
DependencyAnalyzer = SimpleDependencyAnalyzer
