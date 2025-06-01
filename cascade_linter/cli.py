#!/usr/bin/env python3
"""
Command Line Interface for Cascade Linter
Provides the same functionality as the original cascade_linter.py but using the modular core.
Enhanced with Tier 1 features: Interactive mode, rule explanations, config scaffolding, CI helpers.
"""

import argparse
import os
import sys
from pathlib import Path
from typing import List, Optional, Dict

from .core import CodeQualityRunner, LinterStage, LinterProgressCallback


class CLIProgressCallback(LinterProgressCallback):
    """Progress callback for CLI output - FIXED interface compatibility"""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        # Initialize parent class with proper function references
        super().__init__(
            progress_func=self._progress_func,
            stage_start_func=self._stage_start_func, 
            stage_finish_func=self._stage_finish_func
        )

    def _progress_func(self, message: str):
        """Internal progress function"""
        if self.verbose:
            print(f"Progress: {message}", file=sys.stderr)

    def _stage_start_func(self, stage_name: str):
        """Internal stage start function"""
        if self.verbose:
            print(f"Starting {stage_name}...", file=sys.stderr)

    def _stage_finish_func(self, stage_name: str, success: bool, duration: float):
        """Internal stage finish function"""
        if self.verbose:
            status = "PASS" if success else "FAIL"
            print(f"{status} {stage_name} completed in {duration:.2f}s", file=sys.stderr)


class CLIInterface:
    """Command Line Interface for Cascade Linter with Tier 1 enhancements"""

    def __init__(self):
        self.parser = self._create_parser()
        self.rule_explanations = self._load_rule_explanations()

    def _load_rule_explanations(self) -> Dict[str, str]:
        """Load rule explanations for --explain feature"""
        return {
            # Ruff rules
            'E302': 'Expected 2 blank lines, found 1. PEP8 requires two blank lines between top-level function/class definitions.',
            'F401': 'Module imported but unused. Remove the import statement or use the imported module.',
            'F841': 'Local variable assigned but never used. Either use the variable or remove the assignment.',
            'E501': 'Line too long. Break the line into multiple lines or increase max-line-length setting.',
            'W291': 'Trailing whitespace. Remove spaces/tabs at the end of the line.',
            'I001': 'Import block is un-sorted or un-formatted. Use isort or Ruff to fix import order.',
            
            # Flake8 rules
            'E203': 'Whitespace before colon. Usually conflicts with Black formatter - consider ignoring.',
            'W503': 'Line break before binary operator. Style preference - can be ignored if using Black.',
            'E712': 'Comparison to True should be "if cond is True:" or "if cond:"',
            'E711': 'Comparison to None should be "if cond is None:"',
            
            # Pylint rules
            'C0114': 'Missing module docstring. Add a docstring at the top of the file.',
            'C0115': 'Missing class docstring. Add a docstring after the class definition.',
            'C0116': 'Missing function docstring. Add a docstring after the function definition.',
            'R0903': 'Too few public methods. Consider if this class is necessary or combine with others.',
            'W0613': 'Unused argument. Either use the argument, rename it with underscore prefix, or remove it.',
            
            # Bandit rules
            'B101': 'Use of assert detected. Assert statements are removed in optimized mode.',
            'B301': 'Pickle usage detected. Consider using safer serialization methods.',
            'B601': 'Shell injection possible. Use subprocess with shell=False and list arguments.',
            
            # MyPy rules
            'attr-defined': 'Attribute not defined on type. Check spelling or add type annotations.',
            'name-defined': 'Name not defined. Check for typos or missing imports.',
            'return-value': 'Missing return statement. Function should return a value of the declared type.',
        }

    def _create_parser(self) -> argparse.ArgumentParser:
        """Create the argument parser"""
        parser = argparse.ArgumentParser(
            description="Cascading Python linter with Rich UI: Ruff -> Flake8 -> Pylint -> Bandit -> MyPy",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  %(prog)s                           # Lint current directory
  %(prog)s src/                      # Lint specific directory
  %(prog)s --check-only              # Check without fixing
  %(prog)s --unsafe-fixes            # Apply unsafe fixes
  %(prog)s --ruff-only               # Run only Ruff
  %(prog)s --flake8-only             # Run only Flake8
  %(prog)s --pylint-only             # Run only Pylint  
  %(prog)s --bandit-only             # Run only Bandit
  %(prog)s --mypy-only               # Run only MyPy
  %(prog)s --stages ruff flake8      # Run specific stages
  %(prog)s --simple-output           # Plain text for piping to scripts
  %(prog)s --no-gitignore            # Ignore .gitignore file
  %(prog)s --debug --verbose         # Maximum debug output
  %(prog)s --save-log report.txt     # Save detailed log to file
            """,
        )

        # Positional arguments
        parser.add_argument(
            "path",
            nargs="?",
            default=".",
            help="Path to lint (default: current directory)",
        )

        # Linting options
        parser.add_argument(
            "--check-only", action="store_true", help="Only check, don't auto-fix"
        )
        parser.add_argument(
            "--unsafe-fixes", action="store_true", help="Apply Ruff's unsafe fixes"
        )

        # Stage selection
        stage_group = parser.add_mutually_exclusive_group()
        stage_group.add_argument(
            "--stages",
            nargs="+",
            choices=["ruff", "flake8", "pylint", "bandit", "mypy"],
            default=["ruff", "flake8", "pylint", "bandit", "mypy"],
            help="Which linting stages to run",
        )
        stage_group.add_argument(
            "--ruff-only",
            action="store_true",
            help="Run only Ruff (same as --stages ruff)",
        )
        stage_group.add_argument(
            "--flake8-only",
            action="store_true", 
            help="Run only Flake8 (same as --stages flake8)",
        )
        stage_group.add_argument(
            "--pylint-only",
            action="store_true",
            help="Run only Pylint (same as --stages pylint)",
        )
        stage_group.add_argument(
            "--bandit-only",
            action="store_true",
            help="Run only Bandit (same as --stages bandit)",
        )
        stage_group.add_argument(
            "--mypy-only",
            action="store_true",
            help="Run only MyPy (same as --stages mypy)",
        )

        # Output options
        parser.add_argument(
            "--simple-output",
            action="store_true",
            help="Plain text output suitable for piping into scripts (disables Rich tables and colors)",
        )
        parser.add_argument(
            "--debug",
            action="store_true",
            help="Enable debug output for troubleshooting",
        )
        parser.add_argument(
            "--verbose", "-v", action="store_true", help="Verbose progress output"
        )

        # GitIgnore options
        parser.add_argument(
            "--no-gitignore",
            action="store_true",
            help="Don't respect .gitignore file (default: respect .gitignore)",
        )

        # Configuration
        parser.add_argument("--config", type=str, help="Path to configuration file")
        parser.add_argument("--save-log", type=str, help="Save detailed log to file")

        # Tier 1 enhancements - beginner-friendly features
        parser.add_argument(
            "--interactive", "-i",
            action="store_true",
            help="Interactive guided mode - prompts for options (beginner-friendly)"
        )
        parser.add_argument(
            "--explain",
            type=str,
            metavar="CODE",
            help="Explain a specific lint rule code (e.g. --explain E302)"
        )
        parser.add_argument(
            "--init-config",
            action="store_true",
            help="Create a starter configuration file with commented defaults"
        )
        parser.add_argument(
            "--ci-snippet",
            choices=["github", "gitlab", "vscode"],
            help="Generate CI/editor integration snippet"
        )

        return parser

    def run(self, args: Optional[List[str]] = None) -> int:
        """Run the CLI interface with Tier 1 enhancements"""
        parsed_args = self.parser.parse_args(args)

        # Handle Tier 1 features first (these exit early)
        if parsed_args.explain:
            return self._handle_explain_rule(parsed_args.explain)
        
        if parsed_args.init_config:
            return self._handle_init_config()
        
        if parsed_args.ci_snippet:
            return self._handle_ci_snippet(parsed_args.ci_snippet)
        
        if parsed_args.interactive:
            return self._handle_interactive_mode()

        # Regular linting flow (existing code)
        return self._run_linting(parsed_args)

    def _handle_explain_rule(self, rule_code: str) -> int:
        """Handle --explain CODE feature"""
        rule_code = rule_code.upper()
        
        if rule_code in self.rule_explanations:
            print(f"\nRule Explanation: {rule_code}")
            print("=" * 50)
            print(f"{self.rule_explanations[rule_code]}")
            print("\nQuick Fix Tips:")
            
            # Add specific fix suggestions
            if rule_code == 'E302':
                print("   - Add one extra blank line above function/class definitions")
                print("   - Run 'cascade-linter --unsafe-fixes' to auto-fix")
            elif rule_code == 'F401':
                print("   - Remove unused import lines")
                print("   - Run 'cascade-linter' to auto-fix")
            elif rule_code.startswith('C011'):  # Pylint docstring rules
                print("   - Add triple-quoted docstring after definition")
                print("   - Example: def func(): \"\"\"Brief description.\"\"\"")
            else:
                print("   - Run 'cascade-linter --check-only' to see all occurrences")
                print("   - Check your linter's documentation for detailed fixes")
            
            print(f"\nMore info: Search '{rule_code} Python lint' for detailed guides")
            return 0
        else:
            print(f"Unknown rule code: {rule_code}")
            print("\nCommon rule codes:")
            common_rules = ['E302', 'F401', 'F841', 'E501', 'C0114', 'B101']
            for code in common_rules:
                if code in self.rule_explanations:
                    print(f"   {code}: {self.rule_explanations[code][:50]}...")
            return 1

    def _handle_init_config(self) -> int:
        """Handle --init-config feature"""
        config_path = Path("cascade-linter.toml")
        
        if config_path.exists():
            response = input(f"WARNING: {config_path} already exists. Overwrite? (y/N): ")
            if response.lower() != 'y':
                print("Configuration creation cancelled.")
                return 1

        config_template = '''# Cascade Linter Configuration
# Generated by --init-config

[tool.cascade-linter]
# Which linting stages to run by default
# Options: ["ruff", "flake8", "pylint", "bandit", "mypy"]
default_stages = ["ruff", "flake8", "pylint", "bandit", "mypy"]

# Only check without applying fixes
check_only = false

# Apply Ruff's unsafe fixes (more aggressive)
unsafe_fixes = false

# Respect .gitignore file when scanning
respect_gitignore = true

# Maximum line length (affects multiple linters)
max_line_length = 88

[tool.cascade-linter.output]
# Use simple text output (disable Rich tables/colors)
simple_output = false

# Enable verbose progress output
verbose = false

# Enable debug output for troubleshooting
debug = false

# Automatically save detailed logs
save_logs = true

# Keep logs for this many days
keep_logs_days = 30

[tool.cascade-linter.stages]
# Individual stage configuration

[tool.cascade-linter.stages.ruff]
enabled = true
# Additional Ruff-specific options can go here

[tool.cascade-linter.stages.flake8]
enabled = true
# Extend ignore codes (comma-separated)
extend_ignore = "E203,W503"  # Black compatibility

[tool.cascade-linter.stages.pylint]
enabled = true
# Disable specific pylint warnings
disable = "C0114,C0115,C0116"  # Docstring warnings

[tool.cascade-linter.stages.bandit]
enabled = true
# Bandit security level: low, medium, high
severity_level = "medium"

[tool.cascade-linter.stages.mypy]
enabled = true
# Ignore missing imports for third-party libraries
ignore_missing_imports = true

# Example usage:
# cascade-linter                     # Use config defaults
# cascade-linter --config other.toml # Use different config
# cascade-linter --ruff-only         # Override config, run only Ruff
'''

        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                f.write(config_template)
            
            print(f"SUCCESS: Created configuration file: {config_path}")
            print("\nNext steps:")
            print("   1. Edit the config file to customize your preferences")
            print("   2. Run 'cascade-linter' to use the config defaults")
            print("   3. Override config with command-line flags as needed")
            print(f"\nTip: Edit {config_path} to disable MyPy by default:")
            print('   default_stages = ["ruff", "flake8", "pylint", "bandit"]')
            return 0
            
        except Exception as e:
            print(f"ERROR: Failed to create config: {e}")
            return 1

    def _handle_ci_snippet(self, platform: str) -> int:
        """Handle --ci-snippet PLATFORM feature"""
        if platform == "github":
            snippet = '''# GitHub Actions workflow for Cascade Linter
# Save as: .github/workflows/lint.yml

name: Code Quality Check
on: [push, pull_request]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install cascade-linter
        # Add your project dependencies here
        # pip install -r requirements.txt
    
    - name: Run Cascade Linter
      run: |
        cascade-linter --check-only --verbose
        # Or customize: cascade-linter src/ --stages ruff flake8
'''
        
        elif platform == "gitlab":
            snippet = '''# GitLab CI configuration for Cascade Linter  
# Add to: .gitlab-ci.yml

lint:
  stage: test
  image: python:3.11
  before_script:
    - pip install --upgrade pip
    - pip install cascade-linter
    # Add your project dependencies here
    # - pip install -r requirements.txt
  script:
    - cascade-linter --check-only --verbose
    # Or customize: cascade-linter src/ --stages ruff flake8
  only:
    - merge_requests
    - main
    - develop
'''
        
        elif platform == "vscode":
            snippet = '''// VS Code settings for Cascade Linter integration
// Add to: .vscode/settings.json

{
  "python.linting.enabled": true,
  "python.linting.lintOnSave": true,
  
  // Configure Ruff (primary linter in Cascade Linter)
  "python.linting.ruffEnabled": true,
  "python.linting.ruffArgs": ["--line-length=88"],
  
  // Optional: Configure other linters individually
  "python.linting.flake8Enabled": false,  // Handled by Cascade Linter
  "python.linting.pylintEnabled": false,  // Handled by Cascade Linter
  "python.linting.banditEnabled": false,  // Handled by Cascade Linter
  "python.linting.mypyEnabled": false,    // Handled by Cascade Linter
  
  // Format on save with Ruff
  "python.formatting.provider": "none",
  "[python]": {
    "editor.formatOnSave": true,
    "editor.defaultFormatter": "charliermarsh.ruff"
  },
  
  // Terminal task for full Cascade Linter
  "tasks.version": "2.0.0",
  "tasks": {
    "tasks": [
      {
        "label": "Cascade Linter - Full",
        "type": "shell",
        "command": "cascade-linter",
        "args": ["--verbose"],
        "group": "build",
        "presentation": {
          "echo": true,
          "reveal": "always",
          "focus": false,
          "panel": "shared"
        }
      }
    ]
  }
}

// Usage:
// 1. Install Ruff extension: charliermarsh.ruff
// 2. Run full linter: Ctrl+Shift+P -> "Tasks: Run Task" -> "Cascade Linter - Full"
// 3. Or use terminal: cascade-linter
'''

        print(f"\n{platform.title()} Integration Snippet")
        print("=" * 60)
        print(snippet)
        print("=" * 60)
        print(f"\nCopy the above snippet to integrate Cascade Linter with {platform.title()}.")
        
        if platform == "github":
            print("Tip: Adjust the Python version and add your project's requirements.txt")
        elif platform == "gitlab":
            print("Tip: Modify the 'only' section to match your branch strategy")
        elif platform == "vscode":
            print("Tip: Install the Ruff extension for the best integration experience")
        
        return 0

    def _handle_interactive_mode(self) -> int:
        """Handle --interactive feature - guided prompts for beginners"""
        print("Welcome to Cascade Linter Interactive Mode!")
        print("=" * 50)
        print("This guided mode will help you set up your linting preferences.\n")
        
        # Step 1: Choose directory
        print("Step 1: Select directory to lint")
        current_dir = os.getcwd()
        print(f"Current directory: {current_dir}")
        
        while True:
            path_input = input("Enter path to lint (press Enter for current directory): ").strip()
            if not path_input:
                target_path = "."
                break
            elif os.path.exists(path_input):
                target_path = path_input
                break
            else:
                print(f"ERROR: Path '{path_input}' doesn't exist. Try again.")
        
        # Step 2: Choose linting mode
        print(f"\nStep 2: Choose linting mode")
        print("1. Quick Lint (Ruff only - fast, fixes most issues)")
        print("2. Standard Lint (Ruff + Flake8 - good balance)")
        print("3. Full Lint (All 5 stages - comprehensive)")
        print("4. Custom (choose specific stages)")
        
        while True:
            mode_choice = input("Choose mode (1-4): ").strip()
            if mode_choice == "1":
                stages = ["ruff"]
                break
            elif mode_choice == "2":
                stages = ["ruff", "flake8"]
                break
            elif mode_choice == "3":
                stages = ["ruff", "flake8", "pylint", "bandit", "mypy"]
                break
            elif mode_choice == "4":
                print("\nAvailable stages:")
                all_stages = ["ruff", "flake8", "pylint", "bandit", "mypy"]
                for i, stage in enumerate(all_stages, 1):
                    descriptions = {
                        "ruff": "Fast Python linter and formatter",
                        "flake8": "Style guide enforcement",
                        "pylint": "Deep code analysis",
                        "bandit": "Security vulnerability scanner", 
                        "mypy": "Static type checker"
                    }
                    print(f"   {i}. {stage}: {descriptions[stage]}")
                
                stage_input = input("Enter stage numbers (e.g. 1,2,3): ").strip()
                try:
                    indices = [int(x.strip()) - 1 for x in stage_input.split(",")]
                    stages = [all_stages[i] for i in indices if 0 <= i < len(all_stages)]
                    if stages:
                        break
                    else:
                        print("ERROR: No valid stages selected. Try again.")
                except (ValueError, IndexError):
                    print("ERROR: Invalid input. Use numbers and commas (e.g. 1,2,3)")
            else:
                print("ERROR: Please choose 1, 2, 3, or 4")
        
        # Step 3: Auto-fix options
        print(f"\nStep 3: Auto-fix settings")
        print("Should Cascade Linter automatically fix issues where possible?")
        print("1. Yes, apply safe fixes (recommended)")
        print("2. Yes, apply all fixes including unsafe ones (more aggressive)")
        print("3. No, just check and report issues")
        
        while True:
            fix_choice = input("Choose option (1-3): ").strip()
            if fix_choice == "1":
                check_only = False
                unsafe_fixes = False
                break
            elif fix_choice == "2":
                check_only = False
                unsafe_fixes = True
                break
            elif fix_choice == "3":
                check_only = True
                unsafe_fixes = False
                break
            else:
                print("ERROR: Please choose 1, 2, or 3")
        
        # Step 4: Verbose output
        print(f"\nStep 4: Output preferences")
        verbose_input = input("Show detailed progress? (Y/n): ").strip().lower()
        verbose = verbose_input != 'n'
        
        # Step 5: Summary and confirmation
        print(f"\nSummary of your choices:")
        print(f"   Path: {target_path}")
        print(f"   Stages: {', '.join(stages)}")
        print(f"   Auto-fix: {'Check only' if check_only else 'Safe fixes' if not unsafe_fixes else 'All fixes (unsafe)'}")
        print(f"   Verbose: {'Yes' if verbose else 'No'}")
        
        confirm = input("\nProceed with linting? (Y/n): ").strip().lower()
        if confirm == 'n':
            print("Linting cancelled.")
            return 0
        
        # Build args and run linting
        print(f"\nStarting linting with your preferences...")
        
        # Convert to parsed_args format
        class InteractiveArgs:
            def __init__(self):
                self.path = target_path
                self.stages = stages
                self.check_only = check_only
                self.unsafe_fixes = unsafe_fixes
                self.verbose = verbose
                self.debug = False
                self.simple_output = False
                self.no_gitignore = False
                self.config = None
                self.save_log = None
                # Stage-only flags
                self.ruff_only = False
                self.flake8_only = False
                self.pylint_only = False
                self.bandit_only = False
                self.mypy_only = False
        
        interactive_args = InteractiveArgs()
        return self._run_linting(interactive_args)

    def _run_linting(self, parsed_args) -> int:
        """Run the actual linting process (extracted from original run method)"""

        # Handle stage-only flags
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

        # Convert stage strings to enums - FIXED mapping
        stage_mapping = {
            'ruff': LinterStage.RUFF,
            'flake8': LinterStage.FLAKE8, 
            'pylint': LinterStage.PYLINT,
            'bandit': LinterStage.BANDIT,
            'mypy': LinterStage.MYPY
        }
        stages = [stage_mapping[stage] for stage in parsed_args.stages if stage in stage_mapping]

        # Create progress callback
        progress_callback = CLIProgressCallback(verbose=parsed_args.verbose)

        # Create linter runner - FIXED: Only pass supported parameters
        runner = CodeQualityRunner(
            debug=parsed_args.debug,
            simple_output=parsed_args.simple_output
        )

        try:
            # Run linting session (Note: gitignore support not yet implemented in core)
            session = runner.run_linting_session(
                path=parsed_args.path,
                stages=stages,
                check_only=parsed_args.check_only,
                unsafe_fixes=parsed_args.unsafe_fixes,
                callback=progress_callback,
            )
            
            # TODO: Implement gitignore filtering in core.py if needed
            if parsed_args.no_gitignore and parsed_args.debug:
                print("DEBUG: --no-gitignore flag set but not yet implemented in core", file=sys.stderr)

            # Display results
            self._display_results(session, runner, parsed_args)

            # Save log if requested
            if parsed_args.save_log:
                self._save_log(session, parsed_args.save_log)

            # Enhanced exit codes (Tier 1 improvement)
            return self._determine_exit_code(session, parsed_args)

        except KeyboardInterrupt:
            print("\nLinting interrupted by user", file=sys.stderr)
            return 130  # Standard SIGINT exit code
        except FileNotFoundError as e:
            print(f"File not found: {e}", file=sys.stderr)
            return 2    # File/directory not found
        except PermissionError as e:
            print(f"Permission denied: {e}", file=sys.stderr)
            return 3    # Permission error
        except Exception as e:
            print(f"Unexpected error: {e}", file=sys.stderr)
            if parsed_args.debug:
                import traceback
                traceback.print_exc()
            return 4    # Unexpected runtime error
    
    def _determine_exit_code(self, session, args) -> int:
        """Enhanced exit codes for better CI/CD integration"""
        if session.success:
            return 0    # All clean
        
        # Check if any errors (vs just warnings)
        has_errors = any(
            any(issue.severity.weight >= 3 for issue in result.issues)
            for result in session.stage_results.values()
        )
        
        if has_errors:
            return 1    # Lint errors found (fail build)
        else:
            return 1    # Lint warnings found (still fail by default)
            # Note: Future enhancement could add --exit-code-severity flag
            # to treat warnings as non-failing (return 0)

    def _display_results(self, session, runner, args):
        """Display the final results"""
        runner.print("\n" + "=" * 80)
        runner.print("FINAL REPORT")  # Removed emoji
        runner.print("=" * 80)

        # Results table
        if runner.console and not args.simple_output:
            from rich.table import Table

            table = Table(title="Cascading Linter Results")  # Removed emoji
            table.add_column("Stage", style="cyan", no_wrap=True)
            table.add_column("Status", style="bold")
            table.add_column("Issues", justify="right", style="magenta")
            table.add_column("Time", justify="right", style="dim")

            stage_icons = {
                LinterStage.RUFF: "R",  # Removed emoji
                LinterStage.FLAKE8: "F",  # Removed emoji
                LinterStage.PYLINT: "P",  # Removed emoji
                LinterStage.BANDIT: "B",  # Removed emoji
                LinterStage.MYPY: "M",  # Removed emoji
            }

            for stage, result in session.stage_results.items():
                icon = stage_icons.get(stage, "🔧")
                stage_name = f"{icon} {stage.command.upper()}"  # Use .command instead of .value

                if result.success:
                    status = "[green]PASSED[/green]"  # Removed emoji
                    issues = "0"
                else:
                    status = "[red]ISSUES FOUND[/red]"  # Removed emoji
                    issues = str(result.issue_count)  # Use .issue_count property

                time_str = f"{result.execution_time:.2f}s"
                table.add_row(stage_name, status, issues, time_str)

            runner.console.print(table)
        else:
            # Simple table for non-Rich output
            for stage, result in session.stage_results.items():
                status = "PASSED" if result.success else "ISSUES FOUND"  # Removed emoji
                runner.print(f"{stage.command.upper():12} {status}")  # Use .command instead of .value

        # Overall summary
        if session.success:  # Use .success instead of .overall_success
            if runner.console and not args.simple_output:
                from rich.panel import Panel

                runner.console.print(
                    Panel(
                        "ALL STAGES PASSED! Your code is squeaky clean!",  # Removed emoji
                        style="bold green",
                    )
                )
            else:
                runner.print("\nALL STAGES PASSED! Your code is squeaky clean!")  # Removed emoji
        else:
            failed_stages = [
                stage.command  # Use .command instead of .value
                for stage, result in session.stage_results.items()  # Use stage_results instead of results
                if not result.success
            ]
            runner.print(
                f"\nIssues found in {len(failed_stages)} stage(s): {', '.join(failed_stages)}"  # Removed emoji
            )

            # Provide guidance
            runner.print("\nNEXT STEPS:")  # Removed emoji
            if not args.check_only:
                runner.print(
                    "   You already ran fixes - review remaining issues above"  # Removed emoji
                )
            else:
                runner.print(
                    "   Run without --check-only to auto-fix what's possible"  # Removed emoji
                )
                if any(
                    stage == LinterStage.RUFF
                    for stage, result in session.stage_results.items()  # Use stage_results instead of results
                    if not result.success
                ):
                    runner.print("   Consider --unsafe-fixes for stubborn issues")  # Removed emoji

            runner.print("   Manual fixes may be needed for import/name errors")  # Removed emoji

        # Execution summary
        runner.print(f"\nTotal execution time: {session.execution_time:.2f}s")  # Removed emoji
        if session.total_issues > 0:
            runner.print(f"Total issues found: {session.total_issues}")  # Removed emoji

    def _save_log(self, session, log_path: str):
        """Save detailed log to file"""
        try:
            # Create a runner to generate the detailed report
            runner = CodeQualityRunner(debug=False, simple_output=True)
            log_content = runner.generate_detailed_report(session)
            
            with open(log_path, "w", encoding="utf-8") as f:
                f.write(log_content)
            print(f"Detailed log saved to: {log_path}")  # Removed emoji
        except Exception as e:
            print(f"Could not save log: {e}")  # Removed emoji


def main():
    """Main entry point for CLI"""
    cli = CLIInterface()
    sys.exit(cli.run())


# Backward compatibility function
def cascade_lint(
    path=".",
    check_only=False,
    unsafe_fixes=False,
    simple_output=False,
    stages=None,
    debug=False,
):
    """
    Backward compatibility function that matches the original cascade_lint signature
    """
    if stages is None:
        stages = ["ruff", "flake8", "pylint", "bandit", "mypy"]

    # Build CLI arguments
    args = [path]
    if check_only:
        args.append("--check-only")
    if unsafe_fixes:
        args.append("--unsafe-fixes")
    if simple_output:
        args.append("--simple-output")
    if debug:
        args.append("--debug")
    if stages != ["ruff", "flake8", "pylint", "bandit", "mypy"]:
        args.extend(["--stages"] + stages)

    cli = CLIInterface()
    result = cli.run(args)
    return result == 0


if __name__ == "__main__":
    main()
