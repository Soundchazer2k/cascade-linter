#!/usr/bin/env python3
"""
Cascade Linter CLI - TIER 3 ENHANCED EDITION
Advanced features: JSON output, Parallel execution, Dependency analysis

Tier 1 Features: ✅ Interactive mode, Rule explanation, Config scaffolding, CI helpers  
Tier 2 Features: ✅ JSON output, Parallel execution, Advanced options
Tier 3 Features: 🎯 Dependency analysis, Import graph analysis, Error prioritization
"""

import argparse
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime

from .core import CodeQualityRunner, LinterStage, LinterProgressCallback
from .cli import CLIInterface, CLIProgressCallback  # Import existing CLI for compatibility
from .dependency_analysis_cli import (
    DependencyAnalyzer, 
    DependencyAnalysisFormatter, 
    add_dependency_analysis_args
)
# Import enhanced dependency analyzer
from .enhanced_dependency_analyzer import (
    EnhancedDependencyAnalyzer,
    EnhancedDependencyFormatter,
    ConfigurableThresholds
)
from .logging_utils import symbols, setup_logging_environment


class EnhancedCLIProgressCallback(CLIProgressCallback):
    """Enhanced progress callback with JSON support"""

    def __init__(self, verbose: bool = False, json_output: bool = False):
        super().__init__(verbose)
        self.json_output = json_output
        self.events = []  # Store events for JSON output
        self.start_time = time.time()
    
    def _log_event(self, event_type: str, **kwargs):
        """Log event for JSON output"""
        if self.json_output:
            event = {
                'timestamp': datetime.now().isoformat(),
                'elapsed': time.time() - self.start_time,
                'type': event_type,
                **kwargs
            }
            self.events.append(event)
    
    def _progress_func(self, message: str):
        """Enhanced progress with JSON logging"""
        self._log_event('progress', message=message)
        if self.verbose and not self.json_output:
            print(f"Progress: {message}", file=sys.stderr)

    def _stage_start_func(self, stage_name: str):
        """Enhanced stage start with JSON logging"""
        self._log_event('stage_start', stage=stage_name)
        if self.verbose and not self.json_output:
            print(f"Starting {stage_name}...", file=sys.stderr)

    def _stage_finish_func(self, stage_name: str, success: bool, duration: float):
        """Enhanced stage finish with JSON logging"""
        self._log_event('stage_finish', stage=stage_name, success=success, duration=duration)
        if self.verbose and not self.json_output:
            status = "PASS" if success else "FAIL"
            print(f"{status} {stage_name} completed in {duration:.2f}s", file=sys.stderr)

    def get_events(self) -> List[Dict[str, Any]]:
        """Get all logged events for JSON output"""
        return self.events


class EnhancedCLIInterface(CLIInterface):
    """Enhanced CLI interface with Tier 2 features"""

    def __init__(self):
        super().__init__()
        self.parser = self._create_enhanced_parser()

    def _create_enhanced_parser(self) -> argparse.ArgumentParser:
        """Create enhanced argument parser with Tier 2 & 3 features"""
        parser = super()._create_parser()
        
        # JSON Output Options (Tier 2)
        json_group = parser.add_argument_group('JSON Output (Tier 2)')
        json_group.add_argument(
            "--json", 
            action="store_true",
            help="Output results in JSON format (machine-readable for CI/CD)"
        )
        json_group.add_argument(
            "--json-pretty", 
            action="store_true",
            help="Output pretty-formatted JSON (human-readable)"
        )

        # Parallel Execution Options (Tier 2)
        parallel_group = parser.add_argument_group('Parallel Execution (Tier 2)')
        parallel_group.add_argument(
            "--parallel",
            action="store_true",
            help="Run independent linting stages in parallel (faster execution)"
        )
        parallel_group.add_argument(
            "--timing",
            action="store_true",
            help="Show detailed timing information for each stage"
        )

        # Enhanced Dependency Analysis Options (Tier 3)
        dep_group = parser.add_argument_group('Enhanced Dependency Analysis (Tier 3)')
        
        dep_group.add_argument(
            "--dependency-analysis", "--deps",
            action="store_true",
            help="Run comprehensive dependency analysis with all requested features"
        )
        
        dep_group.add_argument(
            "--config-thresholds", metavar="FILE",
            help="Load configurable analysis thresholds from JSON file"
        )
        
        dep_group.add_argument(
            "--export-graph", metavar="FILE",
            help="Export dependency graph as Graphviz DOT file"
        )
        
        dep_group.add_argument(
            "--export-csv", metavar="FILE",
            help="Export module breakdown as CSV file"
        )
        
        dep_group.add_argument(
            "--no-coverage",
            action="store_true",
            help="Skip test coverage integration"
        )
        
        dep_group.add_argument(
            "--no-mypy-analysis",
            action="store_true", 
            help="Skip MyPy integration for faster dependency-only analysis"
        )
        
        dep_group.add_argument(
            "--show-details",
            action="store_true",
            help="Show detailed per-module breakdowns in console output"
        )
        
        dep_group.add_argument(
            "--list-missing-docstrings",
            action="store_true",
            help="List all Python files missing module-level docstrings"
        )
        
        # Add original dependency analysis args for backward compatibility (commented out to avoid conflicts)
        # add_dependency_analysis_args(parser)

        return parser

    def run(self, args: Optional[List[str]] = None) -> int:
        """Enhanced run method with Tier 2 & 3 features"""
        parsed_args = self.parser.parse_args(args)

        # Handle Tier 1 features first (unchanged)
        if parsed_args.explain:
            return self._handle_explain_rule(parsed_args.explain)
        
        if parsed_args.init_config:
            return self._handle_init_config()
        
        if parsed_args.ci_snippet:
            return self._handle_ci_snippet(parsed_args.ci_snippet)
        
        if parsed_args.interactive:
            return self._handle_interactive_mode()

        # Handle Tier 3 dependency analysis
        if parsed_args.dependency_analysis:
            return self._handle_dependency_analysis(parsed_args)
        
        # Handle --list-missing-docstrings flag
        if getattr(parsed_args, 'list_missing_docstrings', False):
            return self._handle_list_missing_docstrings(parsed_args)

        # Handle JSON output validation
        if (parsed_args.json or parsed_args.json_pretty) and parsed_args.simple_output:
            print("ERROR: Cannot use --json with --simple-output", file=sys.stderr)
            return 1

        # Regular linting with potential enhancements
        return self._run_enhanced_linting(parsed_args)

    def _run_enhanced_linting(self, parsed_args) -> int:
        """Enhanced linting with Tier 2 features"""
        # Handle stage-only flags (inherited from base class)
        if parsed_args.ruff_only:
            parsed_args.stages = ["ruff"]
        elif parsed_args.flake8_only:
            parsed_args.stages = ["flake8"]
        elif parsed_args.pylint_only:
            parsed_args.stages = ["pylint"] 
        elif parsed_args.bandit_only:
            parsed_args.stages = ["bandit"]
        elif parsed_args.mypy_only:
            parsed_args.stages = ["mypy"]

        # Convert stage strings to enums
        stage_mapping = {
            'ruff': LinterStage.RUFF,
            'flake8': LinterStage.FLAKE8, 
            'pylint': LinterStage.PYLINT,
            'bandit': LinterStage.BANDIT,
            'mypy': LinterStage.MYPY
        }
        stages = [stage_mapping[stage] for stage in parsed_args.stages if stage in stage_mapping]

        # Create enhanced progress callback
        is_json_output = parsed_args.json or parsed_args.json_pretty
        progress_callback = EnhancedCLIProgressCallback(
            verbose=parsed_args.verbose,
            json_output=is_json_output
        )

        # Create linter runner
        runner = CodeQualityRunner(
            debug=parsed_args.debug,
            simple_output=parsed_args.simple_output or is_json_output
        )

        try:
            # Handle parallel execution
            if parsed_args.parallel:
                session = self._run_parallel_linting(
                    runner, parsed_args, stages, progress_callback
                )
            else:
                # Standard sequential execution
                session = runner.run_linting_session(
                    path=parsed_args.path,
                    stages=stages,
                    check_only=parsed_args.check_only,
                    unsafe_fixes=parsed_args.unsafe_fixes,
                    callback=progress_callback,
                )

            # Handle JSON output
            if is_json_output:
                return self._output_json_results(session, parsed_args, progress_callback)
            
            # Enhanced display with timing
            if parsed_args.timing:
                self._display_timing_info(session)
            
            # Standard display
            self._display_results(session, runner, parsed_args)

            # Save log if requested
            if parsed_args.save_log:
                self._save_log(session, parsed_args.save_log)

            # Enhanced exit codes
            return self._determine_enhanced_exit_code(session, parsed_args)

        except KeyboardInterrupt:
            print("\nLinting interrupted by user", file=sys.stderr)
            return 130
        except FileNotFoundError as e:
            print(f"File not found: {e}", file=sys.stderr)
            return 2
        except PermissionError as e:
            print(f"Permission denied: {e}", file=sys.stderr)
            return 3
        except Exception as e:
            print(f"Unexpected error: {e}", file=sys.stderr)
            if parsed_args.debug:
                import traceback
                traceback.print_exc()
            return 4

    def _run_parallel_linting(self, runner, parsed_args, stages, progress_callback):
        """Run linting stages in parallel where safe"""
        
        # Conservative parallel groups: Ruff first, then others
        ruff_stages = [stage for stage in stages if stage == LinterStage.RUFF]
        other_stages = [stage for stage in stages if stage != LinterStage.RUFF]

        if not parsed_args.json and not parsed_args.json_pretty:
            print(f"Running {len(stages)} stages in parallel mode")

        # Create a session to collect results
        from .core import LintingSession
        session = LintingSession(
            target_path=parsed_args.path,
            stages_requested=stages,
            check_only=parsed_args.check_only,
            unsafe_fixes=parsed_args.unsafe_fixes
        )

        # Run Ruff first (must be sequential due to auto-fixes)
        for stage in ruff_stages:
            if not parsed_args.json and not parsed_args.json_pretty:
                print(f"Running {stage.command} (sequential - applies fixes)")
            result = runner.executors[stage].execute(
                parsed_args.path,
                check_only=parsed_args.check_only,
                unsafe_fixes=parsed_args.unsafe_fixes,
                callback=progress_callback
            )
            session.add_stage_result(result)

        # Run other stages in parallel
        if other_stages:
            if not parsed_args.json and not parsed_args.json_pretty:
                print(f"Running {len(other_stages)} stages in parallel: {', '.join(s.command for s in other_stages)}")
            
            with ThreadPoolExecutor(max_workers=min(4, len(other_stages))) as executor:
                # Submit all stages
                future_to_stage = {}
                for stage in other_stages:
                    future = executor.submit(
                        runner.executors[stage].execute,
                        parsed_args.path,
                        progress_callback
                    )
                    future_to_stage[future] = stage
                
                # Collect results as they complete
                for future in as_completed(future_to_stage):
                    stage = future_to_stage[future]
                    try:
                        result = future.result()
                        session.add_stage_result(result)
                        if not parsed_args.json and not parsed_args.json_pretty:
                            status = "PASS" if result.success else "FAIL"
                            print(f"   {status} {stage.command} ({result.execution_time:.2f}s)")
                    except Exception as e:
                        if not parsed_args.json and not parsed_args.json_pretty:
                            print(f"   FAIL {stage.command}: {e}")
                        # Create a failed result
                        from .core import StageResult
                        failed_result = StageResult(stage, False, 0.0)
                        failed_result.stderr = str(e)
                        session.add_stage_result(failed_result)

        # Finalize session
        session.finish()
        return session

    def _output_json_results(self, session, parsed_args, progress_callback) -> int:
        """Output results in JSON format"""
        
        # Build comprehensive JSON result
        result_data = {
            "cascade_linter": {
                "version": "3.0-tier3",
                "timestamp": datetime.now().isoformat(),
                "execution_mode": "parallel" if parsed_args.parallel else "sequential"
            },
            "session": {
                "id": session.session_id,
                "target_path": session.target_path,
                "start_time": session.start_time.isoformat(),
                "end_time": session.end_time.isoformat() if session.end_time else None,
                "execution_time": session.execution_time,
                "check_only": session.check_only,
                "unsafe_fixes": session.unsafe_fixes,
                "success": session.success
            },
            "summary": {
                "total_issues": session.total_issues,
                "total_fixes_applied": session.total_fixes_applied,
                "files_with_issues": session.total_files_with_issues,
                "stages_run": len(session.stage_results)
            },
            "stages": {},
            "issues": [],
            "files": {}
        }

        # Add stage results
        for stage, result in session.stage_results.items():
            result_data["stages"][stage.command] = {
                "name": stage.command,
                "description": stage.description,
                "success": result.success,
                "execution_time": result.execution_time,
                "issue_count": result.issue_count,
                "fixes_applied": result.fixes_count,
                "initial_issues": result.initial_issue_count,
                "has_autofix": stage.has_autofix
            }

        # Add detailed issues
        for issue in session.all_issues:
            issue_data = {
                "file": issue.file_path,
                "line": issue.line,
                "column": issue.column,
                "code": issue.code,
                "message": issue.message,
                "linter": issue.linter,
                "severity": issue.severity.severity_name,
                "severity_weight": issue.severity.weight,
                "fixable": issue.fixable,
                "display_name": issue.display_name
            }
            result_data["issues"].append(issue_data)

        # Add files summary
        for file_path, file_issues in session.issues_by_file.items():
            result_data["files"][file_path] = {
                "issue_count": len(file_issues),
                "severities": {
                    "error": len([i for i in file_issues if i.severity.severity_name == "error"]),
                    "warning": len([i for i in file_issues if i.severity.severity_name == "warning"]),
                    "info": len([i for i in file_issues if i.severity.severity_name == "info"])
                },
                "fixable_count": len([i for i in file_issues if i.fixable])
            }

        # Output JSON
        if parsed_args.json_pretty:
            print(json.dumps(result_data, indent=2, sort_keys=True))
        else:
            print(json.dumps(result_data, separators=(',', ':')))

        return self._determine_enhanced_exit_code(session, parsed_args)

    def _determine_enhanced_exit_code(self, session, parsed_args) -> int:
        """Enhanced exit codes"""
        if session.success:
            return 0  # All clean
        else:
            return 1  # Issues found

    def _display_timing_info(self, session):
        """Display detailed timing information"""
        print(f"\nDETAILED TIMING ANALYSIS")
        print("=" * 50)
        
        total_time = session.execution_time
        stage_times = [(stage.command, result.execution_time) 
                      for stage, result in session.stage_results.items()]
        
        # Sort by execution time
        stage_times.sort(key=lambda x: x[1], reverse=True)
        
        for stage_name, stage_time in stage_times:
            percentage = (stage_time / total_time * 100) if total_time > 0 else 0
            bar_length = int(percentage / 2)  # Scale to fit in 25 chars
            bar = "=" * bar_length + "-" * (25 - bar_length)
            print(f"{stage_name:8} |{bar}| {stage_time:6.2f}s ({percentage:5.1f}%)")
        
        print(f"{'TOTAL':8} |{'=' * 25}| {total_time:6.2f}s (100.0%)")

    def _handle_dependency_analysis(self, parsed_args) -> int:
        """Handle enhanced dependency analysis request (Tier 3)"""
        
        try:
            # Setup Unicode environment at the start
            unicode_support = setup_logging_environment()
            
            print(f"{symbols.GRAPH} Starting comprehensive dependency analysis...")
            if parsed_args.verbose:
                print(f"{symbols.INFO} Unicode support: {unicode_support}")
                print(f"{symbols.INFO} Symbol type: {symbols.symbol_type}")
            
            # Create enhanced analyzer with configurable thresholds
            config_file = getattr(parsed_args, 'config_thresholds', None)
            analyzer = EnhancedDependencyAnalyzer(parsed_args.path, config_file)
            
            # Run comprehensive analysis
            include_mypy = not getattr(parsed_args, 'no_mypy_analysis', False)
            include_coverage = not getattr(parsed_args, 'no_coverage', False)
            
            result = analyzer.analyze_codebase(
                include_mypy=include_mypy,
                include_coverage=include_coverage
            )
            
            # Create enhanced formatter
            formatter = EnhancedDependencyFormatter(analyzer.thresholds)
            
            # Handle different output formats
            is_json_output = parsed_args.json or parsed_args.json_pretty
            
            if getattr(parsed_args, 'export_graph', None):
                # Export dependency graph as DOT file
                dot_content = formatter.export_graphviz_dot(result)
                with open(parsed_args.export_graph, 'w') as f:
                    f.write(dot_content)
                print(f"{symbols.SUCCESS} Dependency graph exported to {parsed_args.export_graph}")
                print(f"{symbols.INFO} Render with: dot -Tpng {parsed_args.export_graph} -o graph.png")
                return 0
                
            elif getattr(parsed_args, 'export_csv', None):
                # Export module breakdown as CSV
                csv_content = formatter.format_csv_report(result)
                with open(parsed_args.export_csv, 'w') as f:
                    f.write(csv_content)
                print(f"{symbols.SUCCESS} Module breakdown exported to {parsed_args.export_csv}")
                return 0
                
            elif is_json_output:
                # Enhanced JSON output with all features
                json_data = formatter.format_json_report(result)
                if parsed_args.json_pretty:
                    print(json_data)
                else:
                    # Minified JSON
                    import json
                    data = json.loads(json_data)
                    print(json.dumps(data, separators=(',', ':')))
                    
            else:
                # Enhanced console report with all features
                show_details = getattr(parsed_args, 'show_details', False) or getattr(parsed_args, 'debug_imports', False)
                report = formatter.format_console_report(result, show_details)
                print(report)
            
            # Return exit code based on comprehensive findings
            if result.architectural_smells:
                critical_smells = [s for s in result.architectural_smells if s.severity == 'CRITICAL']
                if critical_smells:
                    return 3  # Critical architectural issues
            
            if result.mypy_summary and result.mypy_summary.total_error_count > 0:
                return 2  # MyPy errors found
                
            cycles_found = len([m for m in result.module_breakdowns.values() if m.circular_dependencies])
            if cycles_found > 0:
                return 1  # Circular dependencies found
                
            return 0  # All clean
                
        except Exception as e:
            print(f"{symbols.CRITICAL} Enhanced dependency analysis failed: {e}", file=sys.stderr)
            if parsed_args.debug:
                import traceback
                traceback.print_exc()
            return 4

    def _handle_list_missing_docstrings(self, parsed_args) -> int:
        """Handle --list-missing-docstrings flag"""
        try:
            # Setup Unicode environment
            unicode_support = setup_logging_environment()
            
            print(f"{symbols.INFO} Scanning for missing module docstrings...")
            
            # Create analyzer to detect missing docstrings
            analyzer = EnhancedDependencyAnalyzer(parsed_args.path)
            missing_docstrings = analyzer.detect_missing_docstrings()
            
            if missing_docstrings['count'] == 0:
                print(f"{symbols.SUCCESS} All Python files have module docstrings!")
                return 0
            
            print(f"\n{symbols.HIGH} Found {missing_docstrings['count']} files missing module docstrings:")
            print()
            
            for file_path in sorted(missing_docstrings['files']):
                print(f"  {symbols.CRITICAL} {file_path}")
            
            print(f"\n{symbols.INFO} Quick fix example:")
            print('  Add this at the top of each file (after imports):')
            print('  """')
            print('  Brief description of what this module does.')
            print('  """')
            print()
            print(f"{symbols.INFO} Total files needing docstrings: {missing_docstrings['count']}")
            
            return 1  # Issues found
            
        except Exception as e:
            print(f"{symbols.CRITICAL} Failed to scan for missing docstrings: {e}", file=sys.stderr)
            if parsed_args.debug:
                import traceback
                traceback.print_exc()
            return 4

    def _generate_ai_recommendations(self, result, parsed_args) -> str:
        """Generate AI-powered recommendations (optional enhancement)"""
        
        lines = []
        lines.append(f"\n{symbols.INFO} AI-Enhanced Recommendations:")
        lines.append("=" * 40)
        
        # For now, provide enhanced algorithmic recommendations
        # This could be extended with actual AI integration later
        
        if result.priority_errors:
            lines.append(f"\n{symbols.HIGH} Priority Fix Strategy:")
            
            # Group errors by priority
            critical_errors = [e for e in result.priority_errors if e['priority'] == 'CRITICAL']
            high_errors = [e for e in result.priority_errors if e['priority'] == 'HIGH']
            
            if critical_errors:
                lines.append(f"\n1. {symbols.CRITICAL} Address Critical Modules First:")
                for error in critical_errors[:3]:  # Top 3
                    module = error['module']
                    impact = error['impact_score']
                    lines.append(f"   • {module} (affects {impact} modules)")
                    lines.append(f"     Strategy: Fix type annotations and core interfaces")
                
            if high_errors:
                lines.append(f"\n2. {symbols.HIGH} High-Impact Modules:")
                for error in high_errors[:3]:  # Top 3
                    module = error['module']
                    impact = error['impact_score']
                    lines.append(f"   • {module} (affects {impact} modules)")
                    lines.append(f"     Strategy: Focus on public API consistency")
        
        if result.graph.cycles:
            lines.append(f"\n{symbols.CYCLE} Circular Dependency Resolution:")
            lines.append("   Strategy: Break cycles by introducing interfaces or dependency injection")
            for i, cycle in enumerate(result.graph.cycles[:2], 1):
                cycle_str = f" {symbols.ARROW} ".join(cycle[:4])  # Show first 4 modules
                lines.append(f"   {i}. {cycle_str}")
        
        # Estimated time impact
        total_errors = result.total_errors
        if total_errors > 0:
            estimated_hours = max(1, total_errors * 0.1)  # 6 minutes per error
            lines.append(f"\n{symbols.INFO} Estimated Fix Time: {estimated_hours:.1f} hours")
            lines.append(f"   Priority approach could reduce this by 60-80%")
        
        lines.append(f"\n{symbols.SUCCESS} Note: AI recommendations available with --ai-recommendations")
        lines.append("   (This is algorithmic analysis - upgrade to AI for enhanced insights)")
        
        return "\n".join(lines)


def main():
    """Enhanced main entry point"""
    cli = EnhancedCLIInterface()
    return cli.run()


if __name__ == "__main__":
    sys.exit(main())
