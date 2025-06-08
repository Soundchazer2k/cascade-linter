#!/usr/bin/env python3
"""
Enhanced Dependency Analysis Formatter
Provides actionable, developer-friendly insights instead of abstract metrics
"""

from typing import List
from dataclasses import dataclass

from .logging_utils import symbols


@dataclass
class ActionableInsight:
    """A concrete, actionable insight for developers"""

    title: str
    problem: str
    impact: str
    recommendation: str
    affected_files: List[str]
    priority: str  # 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'


class ActionableReportFormatter:
    """Generates developer-friendly, actionable dependency analysis reports"""

    def format_actionable_console_report(
        self, result, show_details: bool = False
    ) -> str:
        """Format results as actionable developer insights"""
        lines = []

        # Header with context
        lines.append(f"\n{symbols.GRAPH} DEPENDENCY ANALYSIS - ACTIONABLE INSIGHTS")
        lines.append("=" * 60)
        lines.append(f"Project: {result.project_path}")
        lines.append(f"Analyzed in {result.analysis_time:.2f}s")
        lines.append("")

        # Generate actionable insights
        insights = self._generate_actionable_insights(result)

        if not insights:
            lines.append(
                f"{symbols.SUCCESS} GREAT NEWS! No critical dependency issues found."
            )
            lines.append("")
            lines.append("Your project has a healthy dependency structure:")
            lines.append(
                f"  {symbols.ARROW} {result.total_files} files with clean import relationships"
            )
            lines.append(f"  {symbols.ARROW} No circular dependencies detected")
            lines.append(f"  {symbols.ARROW} Well-modularized codebase")
            lines.append("")
            lines.append(
                f"{symbols.INFO} Consider running with MyPy analysis for error prioritization:"
            )
            lines.append(
                "  python -m cascade_linter.cli_enhanced --dependency-analysis ."
            )
            return "\n".join(lines)

        # Show actionable insights
        lines.append(f"{symbols.HIGH} ACTIONABLE INSIGHTS ({len(insights)} found):")
        lines.append("")

        for i, insight in enumerate(insights, 1):
            priority_symbol = self._get_priority_symbol(insight.priority)
            lines.append(f"{i}. {priority_symbol} {insight.title}")
            lines.append(f"   Problem: {insight.problem}")
            lines.append(f"   Impact: {insight.impact}")
            lines.append(f"   Action: {insight.recommendation}")

            if insight.affected_files and show_details:
                lines.append(
                    f"   Files affected: {', '.join(insight.affected_files[:3])}"
                )
                if len(insight.affected_files) > 3:
                    lines.append(
                        f"   ... and {len(insight.affected_files) - 3} more files"
                    )

            lines.append("")

        # Quick wins section
        quick_wins = self._identify_quick_wins(result)
        if quick_wins:
            lines.append(f"{symbols.SUCCESS} QUICK WINS (Low effort, high impact):")
            lines.append("")
            for win in quick_wins:
                lines.append(f"  {symbols.ARROW} {win}")
            lines.append("")

        # Project health summary
        health_score = self._calculate_health_score(result)
        lines.append(f"{symbols.INFO} PROJECT HEALTH SCORE: {health_score}/100")
        lines.append("")
        lines.append(self._generate_health_explanation(health_score))
        lines.append("")

        # Next steps
        lines.append(f"{symbols.ARROW} RECOMMENDED NEXT STEPS:")
        next_steps = self._generate_next_steps(insights, result)
        for step in next_steps:
            lines.append(f"  {step}")

        return "\n".join(lines)

    def _generate_actionable_insights(self, result) -> List[ActionableInsight]:
        """Generate concrete, actionable insights from analysis results"""
        insights = []

        # High-impact modules that are hard to change
        high_impact_modules = self._find_high_impact_modules(result)
        for module, data in high_impact_modules:
            if data["imported_by_count"] >= 5:  # Used by 5+ modules
                insights.append(
                    ActionableInsight(
                        title=f"High-risk central module: {module}",
                        problem=f"This module is used by {data['imported_by_count']} other modules, making it risky to change",
                        impact=f"Any breaking changes here will affect {data['imported_by_count']} files",
                        recommendation="Add comprehensive tests before modifying. Consider breaking into smaller, focused modules.",
                        affected_files=self._get_modules_that_import(module, result),
                        priority=(
                            "HIGH" if data["imported_by_count"] >= 10 else "MEDIUM"
                        ),
                    )
                )

        # Circular dependencies
        if result.graph.cycles:
            for cycle in result.graph.cycles[:3]:  # Show top 3
                insights.append(
                    ActionableInsight(
                        title="Circular dependency detected",
                        problem=f"Modules {' → '.join(cycle[:3])} import each other in a circle",
                        impact="Makes code harder to understand, test, and refactor. Can cause import errors.",
                        recommendation="Break the cycle by extracting shared code into a new module or using dependency injection",
                        affected_files=cycle,
                        priority="CRITICAL",
                    )
                )

        # Complex modules (imports too many things)
        complex_modules = self._find_overly_complex_modules(result)
        for module, imports_count in complex_modules:
            insights.append(
                ActionableInsight(
                    title=f"Overly complex module: {module}",
                    problem=f"Imports {imports_count} different modules - doing too many things",
                    impact="Hard to understand, test, and maintain. Violates single responsibility principle.",
                    recommendation="Split into smaller, focused modules. Extract related functionality into separate files.",
                    affected_files=[module],
                    priority="MEDIUM" if imports_count >= 15 else "LOW",
                )
            )

        # God modules (both high imports AND high usage)
        god_modules = self._find_god_modules(result)
        for module, data in god_modules:
            insights.append(
                ActionableInsight(
                    title=f'"God module" detected: {module}',
                    problem=f"Used by {data['imported_by_count']} modules AND imports {data['imports_count']} modules",
                    impact="Central bottleneck - changes are risky but module is already too complex",
                    recommendation="Priority refactoring target. Split responsibilities and reduce coupling.",
                    affected_files=self._get_modules_that_import(module, result),
                    priority="CRITICAL",
                )
            )

        # Modules with errors (if available)
        if result.priority_errors:
            for error in result.priority_errors[:3]:
                if error["error_count"] > 0:
                    insights.append(
                        ActionableInsight(
                            title=f"Error hotspot: {error['module']}",
                            problem=f"Contains {error['error_count']} type errors and affects {error['impact_score']} modules",
                            impact="Errors here cascade to dependent modules, making debugging harder",
                            recommendation="Fix type errors here first - will improve code quality across multiple files",
                            affected_files=[error["module"]],
                            priority="HIGH",
                        )
                    )

        # Sort by priority
        priority_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
        insights.sort(
            key=lambda x: (priority_order[x.priority], -len(x.affected_files))
        )

        return insights[:8]  # Limit to most important insights

    def _find_high_impact_modules(self, result) -> List[tuple]:
        """Find modules that many other modules depend on"""
        high_impact = []
        for module, data in result.metrics.items():
            if isinstance(data, dict) and data.get("imported_by_count", 0) >= 3:
                high_impact.append((module, data))

        # Sort by impact
        high_impact.sort(key=lambda x: x[1].get("imported_by_count", 0), reverse=True)
        return high_impact[:5]

    def _find_overly_complex_modules(self, result) -> List[tuple]:
        """Find modules that import too many other modules"""
        complex_modules = []
        for module, data in result.metrics.items():
            if isinstance(data, dict):
                imports_count = data.get("imports_count", 0)
                if imports_count >= 8:  # Threshold for "too many imports"
                    complex_modules.append((module, imports_count))

        # Sort by complexity
        complex_modules.sort(key=lambda x: x[1], reverse=True)
        return complex_modules[:3]

    def _find_god_modules(self, result) -> List[tuple]:
        """Find modules that are both heavily used AND complex"""
        god_modules = []
        for module, data in result.metrics.items():
            if isinstance(data, dict):
                imported_by = data.get("imported_by_count", 0)
                imports = data.get("imports_count", 0)

                # God module: used by many AND imports many
                if imported_by >= 4 and imports >= 6:
                    god_modules.append((module, data))

        return god_modules

    def _get_modules_that_import(self, target_module: str, result) -> List[str]:
        """Get list of modules that import the target module"""
        importers = []

        # Search through import graph (simplified approach)
        for module, data in result.metrics.items():
            # This is a simplified version - in reality we'd traverse the import graph
            pass

        return importers[:5]  # Limit to 5 examples

    def _identify_quick_wins(self, result) -> List[str]:
        """Identify low-effort, high-impact improvements"""
        wins = []

        if result.total_files > 20:
            wins.append(
                "Add a project README with architecture overview to help new developers"
            )

        if len(result.graph.cycles) > 0:
            wins.append(
                "Document known circular dependencies to help future refactoring"
            )

        # Check for potential improvements
        complex_count = len(
            [
                m
                for m, d in result.metrics.items()
                if isinstance(d, dict) and d.get("imports_count", 0) > 10
            ]
        )
        if complex_count > 5:
            wins.append("Consider adding __init__.py files to group related modules")

        if result.total_imports > 200:
            wins.append(
                "Review import statements - some might be unused or could be more specific"
            )

        return wins[:3]  # Limit to top 3

    def _calculate_health_score(self, result) -> int:
        """Calculate overall project health score (0-100)"""
        score = 100

        # Deduct for issues
        score -= len(result.graph.cycles) * 15  # Circular dependencies are bad
        score -= min(result.total_errors * 2, 30)  # Type errors

        # Deduct for complexity
        complex_modules = len(
            [
                m
                for m, d in result.metrics.items()
                if isinstance(d, dict) and d.get("imports_count", 0) > 15
            ]
        )
        score -= min(complex_modules * 5, 25)

        # Deduct for high coupling
        high_coupling = len(
            [
                m
                for m, d in result.metrics.items()
                if isinstance(d, dict) and d.get("imported_by_count", 0) > 8
            ]
        )
        score -= min(high_coupling * 8, 20)

        return max(0, min(100, score))

    def _generate_health_explanation(self, score: int) -> str:
        """Generate explanation of health score"""
        if score >= 85:
            return f"{symbols.SUCCESS} Excellent! Your codebase has clean architecture and low technical debt."
        elif score >= 70:
            return f"{symbols.INFO} Good structure with some areas for improvement."
        elif score >= 50:
            return f"{symbols.HIGH} Moderate issues - consider prioritizing refactoring efforts."
        else:
            return f"{symbols.CRITICAL} Significant architecture issues detected - refactoring recommended."

    def _generate_next_steps(
        self, insights: List[ActionableInsight], result
    ) -> List[str]:
        """Generate concrete next steps based on insights"""
        steps = []

        if not insights:
            steps.append(
                "1. Great job! Run with MyPy integration to find type-related improvements"
            )
            steps.append("2. Consider adding more documentation for complex modules")
            return steps

        # Prioritize steps based on insights
        critical_insights = [i for i in insights if i.priority == "CRITICAL"]
        high_insights = [i for i in insights if i.priority == "HIGH"]

        if critical_insights:
            steps.append(
                f"1. URGENT: Address {len(critical_insights)} critical issue(s) first"
            )
            steps.append(f"   Start with: {critical_insights[0].title}")

        if high_insights:
            steps.append(f"2. Address {len(high_insights)} high-priority issue(s)")

        if len(insights) > 3:
            steps.append("3. Consider architectural review meeting with team")

        steps.append("4. Run analysis again after changes to measure improvement")

        if result.total_errors == 0:
            steps.append(
                "5. Add dependency analysis to CI/CD pipeline to prevent regressions"
            )

        return steps[:5]  # Limit to 5 steps

    def _get_priority_symbol(self, priority: str) -> str:
        """Get appropriate symbol for priority level"""
        priority_symbols = {
            "CRITICAL": symbols.CRITICAL,
            "HIGH": symbols.HIGH,
            "MEDIUM": symbols.INFO,
            "LOW": symbols.SUCCESS,
        }
        return priority_symbols.get(priority, symbols.INFO)


# Update the existing DependencyAnalysisFormatter to use the new actionable formatter
def enhance_existing_formatter():
    """Monkey patch to enhance existing formatter with actionable reports"""

    # Import the existing formatter
    try:
        from .dependency_analysis_cli import DependencyAnalysisFormatter

        # Add the new method
        def format_actionable_console_report(self, result, show_details=False):
            formatter = ActionableReportFormatter()
            return formatter.format_actionable_console_report(result, show_details)

        # Patch the existing class
        DependencyAnalysisFormatter.format_actionable_console_report = (
            format_actionable_console_report
        )

    except ImportError:
        pass  # If not available, that's fine


# Auto-enhance on import
enhance_existing_formatter()
