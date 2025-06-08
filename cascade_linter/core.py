#!/usr/bin/env python3
"""
Cascade Linter Core Module - COMPLETELY REFACTORED
Modern architecture with proper timezone handling, accurate issue counting, and working auto-fix
"""

import os
import shutil
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional, Callable
from enum import Enum
from dataclasses import dataclass, field
import logging
import re
import threading

# Rich imports with fallback
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.progress import (
        Progress,
        SpinnerColumn,
        TextColumn,
        BarColumn,
        TimeElapsedColumn,
    )
    from rich.table import Table
    from rich.tree import Tree
    from rich.syntax import Syntax

    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

# Structlog imports with fallback
try:
    import structlog
    from structlog.dev import ConsoleRenderer

    STRUCTLOG_AVAILABLE = True
except ImportError:
    STRUCTLOG_AVAILABLE = False

# Pathspec for gitignore support
try:
    import pathspec

    PATHSPEC_AVAILABLE = True
except ImportError:
    PATHSPEC_AVAILABLE = False


# ============================================================================
# EXCLUSION PATTERNS AND CONFIGURATION
# ============================================================================

# Standard exclusion patterns for all linters - dramatically reduces file count
DEFAULT_EXCLUDE_PATTERNS = [
    "venv",
    ".venv",
    "env",
    ".env",  # Virtual environments
    "__pycache__",
    "*.pyc",
    "*.pyo",
    "*.pyd",  # Python cache
    ".git",
    ".svn",
    ".hg",  # Version control
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",  # Tool caches
    ".tox",
    ".coverage",  # Testing tools
    "build",
    "dist",
    "*.egg-info",  # Build artifacts
    "node_modules",  # JS dependencies (mixed projects)
    ".vscode",
    ".idea",  # IDE files
    "*.log",
    "logs",  # Log files
    "backup",  # Backup directories
    "*.bak",  # Backup files
    "*_backup*",  # Backup files/folders
    "*.broken",  # Broken files
    "archive",  # Archive directories
]


class GitIgnoreHandler:
    """Handle gitignore file parsing and path filtering"""

    def __init__(self, project_path: str, respect_gitignore: bool = True):
        self.project_path = Path(project_path).resolve()
        self.respect_gitignore = respect_gitignore
        self.gitignore_spec = None

        if self.respect_gitignore and PATHSPEC_AVAILABLE:
            self._load_gitignore()

    def _load_gitignore(self) -> None:
        """Load and parse .gitignore file"""
        gitignore_path = self.project_path / ".gitignore"

        if gitignore_path.exists():
            try:
                with open(gitignore_path, "r", encoding="utf-8") as f:
                    gitignore_content = f.read()

                # Create pathspec from gitignore content
                self.gitignore_spec = pathspec.PathSpec.from_lines(
                    "gitwildmatch", gitignore_content.splitlines()
                )
            except Exception:
                # Fall back to default exclusions if gitignore parsing fails
                self.gitignore_spec = None

    def should_exclude_path(self, path: str) -> bool:
        """Check if a path should be excluded based on gitignore rules"""
        if not self.respect_gitignore or not self.gitignore_spec:
            return False

        # Convert to relative path from project root
        try:
            abs_path = Path(path).resolve()
            rel_path = abs_path.relative_to(self.project_path)
            return self.gitignore_spec.match_file(str(rel_path))
        except (ValueError, OSError):
            return False

    def get_exclude_patterns_for_command(self) -> List[str]:
        """Get exclusion patterns for command line tools"""
        patterns = DEFAULT_EXCLUDE_PATTERNS.copy()

        # If gitignore is respected and available, add common gitignore patterns
        if self.respect_gitignore and self.gitignore_spec:
            # Don't add DEFAULT_EXCLUDE_PATTERNS when using gitignore
            # Let gitignore handle all exclusions
            return []

        return patterns


# ============================================================================
# ENUMS AND CONFIGURATION
# ============================================================================


class LinterStage(Enum):
    """Available linting stages with comprehensive metadata"""

    RUFF = ("ruff", "R", "Fast Python linter and formatter", True)  # Removed emoji
    FLAKE8 = ("flake8", "F", "Style guide enforcement", False)  # Removed emoji
    PYLINT = ("pylint", "P", "Deep code analysis", False)  # Removed emoji
    BANDIT = ("bandit", "B", "Security vulnerability scanner", False)  # Removed emoji
    MYPY = ("mypy", "M", "Static type checker", False)  # Removed emoji

    def __init__(self, command: str, icon: str, description: str, has_autofix: bool):
        self.command = command
        self.icon = icon
        self.description = description
        self.has_autofix = has_autofix


class IssueSeverity(Enum):
    """Issue severity levels with display properties"""

    ERROR = ("error", "E", 3, "#FF5252")  # Removed emoji
    WARNING = ("warning", "W", 2, "#FF9800")  # Removed emoji
    INFO = ("info", "I", 1, "#2196F3")  # Removed emoji

    def __init__(self, name: str, icon: str, weight: int, color: str):
        self.severity_name = name
        self.icon = icon
        self.weight = weight
        self.color = color


# ============================================================================
# DATA CLASSES
# ============================================================================


@dataclass(frozen=True)
class IssueItem:
    """Immutable issue representation with enhanced metadata"""

    file_path: str
    line: int
    column: int
    code: str
    message: str
    linter: str
    severity: IssueSeverity = IssueSeverity.ERROR
    raw_line: str = ""  # Original output line for debugging

    def __post_init__(self):
        # Determine severity based on linter and code
        severity = self._determine_severity()
        object.__setattr__(self, "severity", severity)

    def _determine_severity(self) -> IssueSeverity:
        """Determine severity based on linter and code"""
        if self.linter == "bandit":
            return IssueSeverity.WARNING
        elif self.linter == "mypy":
            return IssueSeverity.ERROR
        elif self.code.startswith(("E", "F")):
            return IssueSeverity.ERROR
        elif self.code.startswith("W"):
            return IssueSeverity.WARNING
        else:
            return IssueSeverity.INFO

    @property
    def fixable(self) -> bool:
        """Determine if issue is auto-fixable"""
        if self.linter == "ruff":
            return self._is_ruff_fixable()
        return False

    def _is_ruff_fixable(self) -> bool:
        """Check if Ruff can auto-fix this issue"""
        auto_fixable_prefixes = {
            "F401",
            "F403",
            "F405",
            "F811",
            "F841",  # Import issues
            "E501",
            "E502",
            "E701",
            "E702",
            "E703",  # Line length/formatting
            "W291",
            "W292",
            "W293",
            "W391",  # Whitespace
            "E225",
            "E231",
            "E261",
            "E262",
            "E265",  # Spacing
            "I001",
            "I002",  # Import sorting
        }
        return any(self.code.startswith(prefix) for prefix in auto_fixable_prefixes)

    @property
    def display_name(self) -> str:
        """Clean display name for UI"""
        return f"{Path(self.file_path).name}:{self.line}:{self.column}"

    def __str__(self) -> str:
        return f"{self.display_name} {self.code}: {self.message}"

    def __hash__(self) -> int:
        return hash((self.file_path, self.line, self.column, self.code))


@dataclass
class StageResult:
    """Enhanced stage result with detailed metrics"""

    stage: LinterStage
    success: bool
    execution_time: float
    issues: Set[IssueItem] = field(default_factory=set)
    stdout: str = ""
    stderr: str = ""
    command_used: List[str] = field(default_factory=list)
    files_processed: int = 0
    auto_fixes_applied: int = 0
    initial_issue_count: int = 0  # Before fixes

    @property
    def issue_count(self) -> int:
        return len(self.issues)

    @property
    def fixes_count(self) -> int:
        """Number of issues actually fixed"""
        return max(0, self.initial_issue_count - self.issue_count)

    @property
    def status_icon(self) -> str:
        return "PASS" if self.success else "FAIL"  # Removed emoji

    @property
    def status_color(self) -> str:
        return "#4CAF50" if self.success else "#F44336"


@dataclass
class LintingSession:
    """Complete session tracking with accurate metrics"""

    target_path: str
    stages_requested: List[LinterStage]
    check_only: bool = False
    unsafe_fixes: bool = False
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    stage_results: Dict[LinterStage, StageResult] = field(default_factory=dict)
    session_id: str = field(default_factory=lambda: f"session_{int(time.time())}")

    # Internal tracking
    _issues_cache: Optional[Set[IssueItem]] = field(default=None, init=False)
    _files_cache: Optional[Dict[str, Set[IssueItem]]] = field(default=None, init=False)
    _log_entries: List[str] = field(default_factory=list, init=False)

    def add_stage_result(self, result: StageResult):
        """Add stage result and invalidate caches"""
        self.stage_results[result.stage] = result
        self._invalidate_caches()

    def add_log_entry(self, message: str):
        """Add timestamped log entry with local timezone"""
        timestamp = datetime.now().strftime("%H:%M:%S")  # Local time
        entry = f"[{timestamp}] {message}"
        self._log_entries.append(entry)

    def _invalidate_caches(self):
        """Clear cached data when session changes"""
        self._issues_cache = None
        self._files_cache = None

    @property
    def all_issues(self) -> Set[IssueItem]:
        """All unique issues across stages (cached)"""
        if self._issues_cache is None:
            self._issues_cache = set()
            for result in self.stage_results.values():
                self._issues_cache.update(result.issues)
        return self._issues_cache

    @property
    def issues_by_file(self) -> Dict[str, Set[IssueItem]]:
        """Issues grouped by file (cached)"""
        if self._files_cache is None:
            self._files_cache = {}
            for issue in self.all_issues:
                file_path = issue.file_path
                if file_path not in self._files_cache:
                    self._files_cache[file_path] = set()
                self._files_cache[file_path].add(issue)
        return self._files_cache

    @property
    def total_issues(self) -> int:
        """Accurate total issue count"""
        return len(self.all_issues)

    @property
    def total_files_with_issues(self) -> int:
        return len(self.issues_by_file)

    @property
    def total_fixes_applied(self) -> int:
        """Total fixes applied across all stages"""
        return sum(result.fixes_count for result in self.stage_results.values())

    @property
    def execution_time(self) -> float:
        """Total execution time in seconds"""
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return (datetime.now() - self.start_time).total_seconds()

    @property
    def success(self) -> bool:
        """True if all stages completed successfully"""
        return len(self.all_issues) == 0 and all(
            result.success for result in self.stage_results.values()
        )

    @property
    def raw_log(self) -> str:
        """Complete session log as string"""
        return "\n".join(self._log_entries)

    def finish(self):
        """Mark session complete"""
        self.end_time = datetime.now()
        self.add_log_entry(
            f"Session completed in {self.execution_time:.2f}s"
        )  # Removed emoji
        self.add_log_entry(
            f"Final summary: {self.total_issues} issues, {self.total_fixes_applied} fixes applied"
        )


# ============================================================================
# PROGRESS CALLBACK SYSTEM
# ============================================================================


class LinterProgressCallback:
    """Progress callback for GUI integration"""

    def __init__(
        self,
        progress_func: Optional[Callable[[str], None]] = None,
        stage_start_func: Optional[Callable[[str], None]] = None,
        stage_finish_func: Optional[Callable[[str, bool, float], None]] = None,
    ):
        self.progress_func = progress_func or self._default_progress
        self.stage_start_func = stage_start_func or self._default_stage_start
        self.stage_finish_func = stage_finish_func or self._default_stage_finish

    def _default_progress(self, message: str):
        print(f"Progress: {message}")

    def _default_stage_start(self, stage_name: str):
        print(f"Starting: {stage_name}")

    def _default_stage_finish(self, stage_name: str, success: bool, duration: float):
        status = "PASS" if success else "FAIL"  # Removed emoji
        print(f"{status} {stage_name} completed in {duration:.2f}s")

    def on_progress(self, message: str):
        """Report progress update"""
        self.progress_func(message)

    def on_stage_start(self, stage_name: str):
        """Report stage start"""
        self.stage_start_func(stage_name)

    def on_stage_finish(self, stage_name: str, success: bool, duration: float):
        """Report stage completion"""
        self.stage_finish_func(stage_name, success, duration)


# ============================================================================
# ENHANCED COMMAND RUNNER
# ============================================================================


class CommandRunner:
    """Enhanced command execution with proper timezone logging"""

    def __init__(self, debug: bool = False, timeout: int = 300):
        self.debug = debug
        self.timeout = timeout
        self.logger = self._setup_logging()
        self._lock = threading.Lock()

    def _setup_logging(self) -> Optional[logging.Logger]:
        """Setup logging with LOCAL timezone (fixes UTC issue)"""
        if not STRUCTLOG_AVAILABLE:
            return None

        def local_timestamper(logger, method_name, event_dict):
            """Custom timestamper that uses LOCAL time, not UTC"""
            # Use local time instead of UTC
            local_time = datetime.now()  # This gives local time
            event_dict["timestamp"] = local_time.strftime("%H:%M:%S")
            return event_dict

        structlog.configure(
            processors=[
                structlog.processors.add_log_level,
                local_timestamper,  # Use our local timestamper
                ConsoleRenderer(colors=True),
            ],
            logger_factory=structlog.PrintLoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )

        return structlog.get_logger()

    def find_executable(self, command: str) -> str:
        """Find executable with comprehensive path search"""
        # First try system PATH
        full_path = shutil.which(command)
        if full_path:
            return full_path

        # Try virtual environment locations
        possible_locations = [
            # Current directory venv
            Path.cwd() / "venv" / "Scripts" / f"{command}.exe",
            Path.cwd() / "venv" / "bin" / command,
            Path.cwd() / ".venv" / "Scripts" / f"{command}.exe",
            Path.cwd() / ".venv" / "bin" / command,
            # User local
            Path.home() / ".local" / "bin" / command,
            # Poetry venv (common location)
            Path.home() / ".cache" / "pypoetry" / "virtualenvs" / "*" / "bin" / command,
        ]

        for location in possible_locations:
            if location.exists():
                return str(location)

        # Return original command - let subprocess handle the error
        return command

    def run_command(
        self,
        command: List[str],
        description: str = "",
        cwd: Optional[str] = None,
        env_vars: Optional[Dict[str, str]] = None,
    ) -> Tuple[bool, str, str]:
        """Execute command with enhanced error handling and logging"""

        with self._lock:
            if self.logger:
                self.logger.info(
                    "command_start",
                    command=" ".join(command),
                    description=description,
                    cwd=cwd,
                )

            try:
                # Resolve executable path
                resolved_command = command.copy()
                resolved_command[0] = self.find_executable(command[0])

                if self.debug:
                    print(
                        f"Running command: {description or 'Running command'}"
                    )  # Removed emoji
                    print(f"DEBUG: Original: {' '.join(command)}")
                    print(f"DEBUG: Resolved: {' '.join(resolved_command)}")
                    print(f"DEBUG: Working dir: {cwd or os.getcwd()}")

                # Setup environment
                env = os.environ.copy()
                env.update(
                    {
                        "PYTHONIOENCODING": "utf-8",
                        "PYTHONUNBUFFERED": "1",
                        "NO_COLOR": "1" if not RICH_AVAILABLE else "0",
                        "FORCE_COLOR": "0" if not RICH_AVAILABLE else "1",
                    }
                )

                # Add custom environment variables
                if env_vars:
                    env.update(env_vars)

                # Execute command
                result = subprocess.run(
                    resolved_command,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    env=env,
                    timeout=self.timeout,
                    cwd=cwd or os.getcwd(),
                    shell=False,
                )

                success = result.returncode == 0

                if self.logger:
                    self.logger.info(
                        "command_complete",
                        success=success,
                        return_code=result.returncode,
                        stdout_lines=len(result.stdout.splitlines()),
                        stderr_lines=len(result.stderr.splitlines()),
                    )

                if self.debug:
                    print(f"DEBUG: Return code: {result.returncode}")
                    print(f"DEBUG: Stdout lines: {len(result.stdout.splitlines())}")
                    print(f"DEBUG: Stderr lines: {len(result.stderr.splitlines())}")
                    if result.stderr:
                        print(f"DEBUG: Stderr preview: {result.stderr[:200]}...")

                return success, result.stdout, result.stderr

            except subprocess.TimeoutExpired:
                error_msg = (
                    f"Command timed out after {self.timeout}s: {' '.join(command)}"
                )
                if self.logger:
                    self.logger.error(
                        "command_timeout",
                        command=" ".join(command),
                        timeout=self.timeout,
                    )
                return False, "", error_msg

            except FileNotFoundError as e:
                error_msg = (
                    f"Command not found: {resolved_command[0]} (original: {command[0]})"
                )
                if self.logger:
                    self.logger.error(
                        "command_not_found", command=command[0], error=str(e)
                    )
                return False, "", error_msg

            except Exception as e:
                error_msg = f"Unexpected error running {' '.join(command)}: {e}"
                if self.logger:
                    self.logger.error(
                        "command_error", command=" ".join(command), error=str(e)
                    )
                return False, "", error_msg


# ============================================================================
# ENHANCED ISSUE PARSER
# ============================================================================


class IssueParser:
    """Enhanced issue parsing with better accuracy"""

    # Comprehensive regex patterns for different linters
    PATTERNS = {
        "ruff": re.compile(r"^(.+?):(\d+):(\d+):\s*([A-Z]\d+)\s*(.*)$"),
        "flake8": re.compile(r"^(.+?):(\d+):(\d+):\s*([A-Z]\d+)\s*(.*)$"),
        "mypy": re.compile(
            r"^(.+?):(\d+):\s*(?:error|warning|note):\s*(.+?)(?:\s*\[([^\]]+)\])?$"
        ),
        "pylint": re.compile(r"^(.+?):(\d+):(\d+):\s*([A-Z]\d+):\s*(.*)$"),
        "bandit": re.compile(
            r">>.*?Issue:.*?Severity:.*?Test ID:.*?\n.*?Location:\s*(.+?):(\d+):(\d+)"
        ),
    }

    @classmethod
    def parse_linter_output(cls, output: str, linter: str) -> Set[IssueItem]:
        """Parse complete linter output with enhanced accuracy"""
        issues = set()

        if not output or not output.strip():
            return issues

        lines = output.strip().splitlines()

        for line_num, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue

            # Skip common non-issue lines
            if cls._should_skip_line(line):
                continue

            issue = cls.parse_single_line(line, linter)
            if issue:
                issues.add(issue)

        return issues

    @classmethod
    def _should_skip_line(cls, line: str) -> bool:
        """Check if line should be skipped during parsing"""
        skip_patterns = [
            r"^All done!",
            r"^would reformat",
            r"^reformatted",
            r"^\d+ files? (would be )?reformatted",
            r"^Found \d+ error",
            r"^Success: no issues found",
            r"^.*\d+\.\d+\.\d+.*$",  # Version numbers
            r"^.*--help.*$",  # Help text
            r"^.*\s*\^+\s*$",  # Caret indicators
            r"^.*={3,}.*$",  # Separator lines
            r"^.*-{3,}.*$",  # Separator lines
        ]

        return any(re.match(pattern, line) for pattern in skip_patterns)

    @classmethod
    def parse_single_line(cls, line: str, linter: str) -> Optional[IssueItem]:
        """Parse a single line with enhanced error handling"""
        pattern = cls.PATTERNS.get(linter)
        if not pattern:
            return None

        match = pattern.match(line)
        if not match:
            return None

        try:
            if linter in ("ruff", "flake8", "pylint"):
                file_path, line_num, col_num, code, message = match.groups()

                # Clean up the message
                message = message.strip()
                if not message:
                    message = f"{code} violation"

                return IssueItem(
                    file_path=file_path.strip(),
                    line=int(line_num),
                    column=int(col_num),
                    code=code.strip(),
                    message=message,
                    linter=linter,
                    raw_line=line,
                )

            elif linter == "mypy":
                file_path, line_num, message, code = match.groups()
                return IssueItem(
                    file_path=file_path.strip(),
                    line=int(line_num),
                    column=0,
                    code=code.strip() if code else "mypy-error",
                    message=message.strip(),
                    linter=linter,
                    raw_line=line,
                )

            elif linter == "bandit":
                # Bandit requires special handling due to multi-line format
                file_path, line_num, col_num = match.groups()
                return IssueItem(
                    file_path=file_path.strip(),
                    line=int(line_num),
                    column=int(col_num),
                    code="bandit-security",
                    message="Security vulnerability detected",
                    linter=linter,
                    severity=IssueSeverity.WARNING,
                    raw_line=line,
                )

        except (ValueError, IndexError, AttributeError) as e:
            # Log parsing errors in debug mode
            if os.environ.get("DEBUG"):
                print(f"DEBUG: Failed to parse line: {line}")
                print(f"DEBUG: Error: {e}")
            return None

        return None


# ============================================================================
# ENHANCED LINTER EXECUTORS
# ============================================================================


class RuffExecutor:
    """Enhanced Ruff executor with proper auto-fix sequence"""

    def __init__(self, runner: CommandRunner):
        self.runner = runner
        self.stage = LinterStage.RUFF

    def execute(
        self,
        path: str,
        check_only: bool = False,
        unsafe_fixes: bool = False,
        callback: Optional[LinterProgressCallback] = None,
    ) -> StageResult:
        """Execute Ruff with PROPER auto-fix sequence"""
        start_time = time.time()

        # Initialize result
        result = StageResult(
            stage=self.stage, success=True, execution_time=0.0, command_used=[]
        )

        try:
            if callback:
                callback.on_progress("Scanning initial issues...")  # Removed emoji

            # Step 1: Get initial issue count
            initial_issues = self._check_issues(path)
            result.initial_issue_count = len(initial_issues)
            result.issues.update(initial_issues)

            if callback:
                callback.on_progress(
                    f"Found {len(initial_issues)} initial issues"
                )  # Removed emoji

            # Step 2: Apply fixes if not check-only
            if not check_only and initial_issues:
                fixes_applied = 0

                if callback:
                    callback.on_progress("Applying formatting...")  # Removed emoji

                # Format first
                format_success = self._run_format(path)
                if format_success:
                    fixes_applied += 1

                if callback:
                    callback.on_progress("Applying auto-fixes...")  # Removed emoji

                # Then apply fixes
                fix_success = self._run_fix(path, unsafe_fixes)
                if fix_success:
                    fixes_applied += 1

                # Step 3: Check remaining issues
                if callback:
                    callback.on_progress(
                        "Checking remaining issues..."
                    )  # Removed emoji

                remaining_issues = self._check_issues(path)
                result.issues = remaining_issues
                result.auto_fixes_applied = len(initial_issues) - len(remaining_issues)

                if callback:
                    callback.on_progress(
                        f"Applied {result.auto_fixes_applied} fixes"
                    )  # Removed emoji

            # Determine success
            result.success = len(result.issues) == 0

        except Exception as e:
            result.success = False
            result.stderr = f"Ruff execution failed: {str(e)}"
            if callback:
                callback.on_progress(f"Ruff failed: {str(e)}")  # Removed emoji

        result.execution_time = time.time() - start_time
        return result

    def _check_issues(self, path: str) -> Set[IssueItem]:
        """Check issues without fixing"""
        # Use gitignore if available, otherwise fall back to default patterns
        if hasattr(self, "gitignore_handler") and self.gitignore_handler:
            exclude_patterns = self.gitignore_handler.get_exclude_patterns_for_command()
        else:
            exclude_patterns = DEFAULT_EXCLUDE_PATTERNS

        exclude_list = ",".join(exclude_patterns)
        success, stdout, stderr = self.runner.run_command(
            ["ruff", "check", path, "--exclude", exclude_list], "Ruff check"
        )

        # Parse output regardless of success (issues cause non-zero exit)
        issues = IssueParser.parse_linter_output(stdout, "ruff")

        # Also check stderr for any additional issues
        if stderr:
            stderr_issues = IssueParser.parse_linter_output(stderr, "ruff")
            issues.update(stderr_issues)

        return issues

    def _run_format(self, path: str) -> bool:
        """Run Ruff formatting"""
        # Use gitignore if available, otherwise fall back to default patterns
        if hasattr(self, "gitignore_handler") and self.gitignore_handler:
            exclude_patterns = self.gitignore_handler.get_exclude_patterns_for_command()
        else:
            exclude_patterns = DEFAULT_EXCLUDE_PATTERNS

        exclude_list = ",".join(exclude_patterns)
        success, stdout, stderr = self.runner.run_command(
            ["ruff", "format", path, "--exclude", exclude_list], "Ruff format"
        )
        return success

    def _run_fix(self, path: str, unsafe: bool = False) -> bool:
        """Run Ruff auto-fix"""
        # Use gitignore if available, otherwise fall back to default patterns
        if hasattr(self, "gitignore_handler") and self.gitignore_handler:
            exclude_patterns = self.gitignore_handler.get_exclude_patterns_for_command()
        else:
            exclude_patterns = DEFAULT_EXCLUDE_PATTERNS

        exclude_list = ",".join(exclude_patterns)
        cmd = ["ruff", "check", path, "--fix", "--exclude", exclude_list]
        if unsafe:
            cmd.append("--unsafe-fixes")

        success, stdout, stderr = self.runner.run_command(
            cmd, f"Ruff fix{'(unsafe)' if unsafe else ''}"
        )
        return success


class Flake8Executor:
    """Enhanced Flake8 executor"""

    def __init__(self, runner: CommandRunner):
        self.runner = runner
        self.stage = LinterStage.FLAKE8

    def execute(
        self, path: str, callback: Optional[LinterProgressCallback] = None
    ) -> StageResult:
        """Execute Flake8 analysis"""
        start_time = time.time()

        if callback:
            callback.on_progress("Running Flake8 analysis...")  # Removed emoji

        exclude_list = ",".join(DEFAULT_EXCLUDE_PATTERNS)
        cmd = [
            "flake8",
            path,
            "--format=%(path)s:%(row)d:%(col)d: %(code)s %(text)s",
            "--max-line-length=88",
            "--extend-ignore=E203,W503",  # Black compatibility
            "--exclude",
            exclude_list,
        ]

        success, stdout, stderr = self.runner.run_command(cmd, "Flake8 analysis")
        issues = IssueParser.parse_linter_output(stdout, "flake8")

        return StageResult(
            stage=self.stage,
            success=len(issues) == 0,
            execution_time=time.time() - start_time,
            issues=issues,
            stdout=stdout,
            stderr=stderr,
            command_used=cmd,
        )


class PylintExecutor:
    """Enhanced Pylint executor"""

    def __init__(self, runner: CommandRunner):
        self.runner = runner
        self.stage = LinterStage.PYLINT

    def execute(
        self, path: str, callback: Optional[LinterProgressCallback] = None
    ) -> StageResult:
        """Execute Pylint analysis"""
        start_time = time.time()

        if callback:
            callback.on_progress("Running Pylint deep analysis...")  # Removed emoji

        # Use simpler, more reliable exclusion patterns for Pylint
        cmd = [
            "pylint",
            path,
            "--output-format=text",
            "--score=no",
            "--max-line-length=88",
            "--disable=C0114,C0115,C0116",  # Disable docstring warnings
            "--ignore-patterns=.*venv.*,.*__pycache__.*,.*\\.git.*,.*build.*,.*dist.*,.*\\.pyc,.*\\.pyo",
            "--ignore-paths=.*/(venv|__pycache__|build|dist|\\.git|\\.pytest_cache|\\.mypy_cache|\\.ruff_cache)/.*",
        ]

        success, stdout, stderr = self.runner.run_command(cmd, "Pylint analysis")
        issues = IssueParser.parse_linter_output(stdout, "pylint")

        return StageResult(
            stage=self.stage,
            success=len(issues) == 0,
            execution_time=time.time() - start_time,
            issues=issues,
            stdout=stdout,
            stderr=stderr,
            command_used=cmd,
        )


class BanditExecutor:
    """Enhanced Bandit executor"""

    def __init__(self, runner: CommandRunner):
        self.runner = runner
        self.stage = LinterStage.BANDIT

    def execute(
        self, path: str, callback: Optional[LinterProgressCallback] = None
    ) -> StageResult:
        """Execute Bandit security analysis"""
        start_time = time.time()

        if callback:
            callback.on_progress("Running Bandit security scan...")  # Removed emoji

        exclude_list = ",".join(DEFAULT_EXCLUDE_PATTERNS)
        cmd = [
            "bandit",
            "-r",
            path,
            "-f",
            "txt",
            "--severity-level",
            "medium",
            "--exclude-dirs",
            exclude_list,
        ]

        success, stdout, stderr = self.runner.run_command(cmd, "Bandit security scan")
        issues = IssueParser.parse_linter_output(stdout, "bandit")

        return StageResult(
            stage=self.stage,
            success=len(issues) == 0,
            execution_time=time.time() - start_time,
            issues=issues,
            stdout=stdout,
            stderr=stderr,
            command_used=cmd,
        )


class MypyExecutor:
    """Enhanced MyPy executor"""

    def __init__(self, runner: CommandRunner):
        self.runner = runner
        self.stage = LinterStage.MYPY

    def execute(
        self, path: str, callback: Optional[LinterProgressCallback] = None
    ) -> StageResult:
        """Execute MyPy type checking"""
        start_time = time.time()

        if callback:
            callback.on_progress("Running MyPy type checking...")  # Removed emoji

        # MyPy uses regex patterns for exclusions
        exclude_patterns = "|".join(
            [pattern.replace("*", ".*") for pattern in DEFAULT_EXCLUDE_PATTERNS]
        )
        cmd = [
            "mypy",
            path,
            "--ignore-missing-imports",
            "--no-error-summary",
            f"--exclude=({exclude_patterns})",
        ]

        success, stdout, stderr = self.runner.run_command(cmd, "MyPy type checking")
        issues = IssueParser.parse_linter_output(stdout, "mypy")

        return StageResult(
            stage=self.stage,
            success=len(issues) == 0,
            execution_time=time.time() - start_time,
            issues=issues,
            stdout=stdout,
            stderr=stderr,
            command_used=cmd,
        )


# ============================================================================
# MAIN RUNNER CLASS
# ============================================================================


class CodeQualityRunner:
    """Enhanced code quality runner with proper timezone and issue handling"""

    def __init__(
        self,
        debug: bool = False,
        simple_output: bool = False,
        respect_gitignore: bool = True,
    ):
        self.debug = debug
        self.simple_output = simple_output
        self.respect_gitignore = respect_gitignore

        # Set proper encoding for Windows compatibility
        if os.name == "nt":  # Windows
            try:
                # Try to set UTF-8 encoding
                import locale

                locale.setlocale(locale.LC_ALL, "en_US.UTF-8")
            except:
                pass  # Ignore if not available

        # Initialize components
        self.runner = CommandRunner(debug=debug)
        self.console = Console() if RICH_AVAILABLE and not simple_output else None

        # Initialize executors - ALL STAGES NOW SUPPORTED
        self.executors = {
            LinterStage.RUFF: RuffExecutor(self.runner),
            LinterStage.FLAKE8: Flake8Executor(self.runner),
            LinterStage.PYLINT: PylintExecutor(self.runner),
            LinterStage.BANDIT: BanditExecutor(self.runner),
            LinterStage.MYPY: MypyExecutor(self.runner),
        }

        # Current session tracking
        self.current_session: Optional[LintingSession] = None

    def print(self, *args, **kwargs):
        """Unified print method"""
        if self.console:
            self.console.print(*args, **kwargs)
        else:
            print(*args, **kwargs)

    def run_linting_session(
        self,
        path: str,
        stages: List[LinterStage] = None,
        check_only: bool = False,
        unsafe_fixes: bool = False,
        callback: Optional[LinterProgressCallback] = None,
    ) -> LintingSession:
        """Run complete linting session with proper progress tracking"""

        if stages is None:
            stages = [LinterStage.RUFF, LinterStage.FLAKE8]

        # Create gitignore handler for this session
        gitignore_handler = GitIgnoreHandler(path, self.respect_gitignore)

        # Create session
        session = LintingSession(
            target_path=path,
            stages_requested=stages,
            check_only=check_only,
            unsafe_fixes=unsafe_fixes,
        )
        self.current_session = session

        # Display header
        self._display_session_header(session)
        session.add_log_entry("Starting cascade linting session")  # Removed emoji
        session.add_log_entry(f"Target: {path}")
        session.add_log_entry(f"Stages: {', '.join(s.command for s in stages)}")

        # Run each stage
        for stage in stages:
            if stage in self.executors:
                stage_start = time.time()

                session.add_log_entry(f"Starting {stage.command}...")  # Removed emoji
                if callback:
                    callback.on_stage_start(stage.command)

                try:
                    # Set gitignore handler for the executor temporarily
                    self.executors[stage].gitignore_handler = gitignore_handler

                    # Execute stage with proper parameters
                    if stage == LinterStage.RUFF:
                        result = self.executors[stage].execute(
                            path,
                            check_only=check_only,
                            unsafe_fixes=unsafe_fixes,
                            callback=callback,
                        )
                    else:
                        result = self.executors[stage].execute(path, callback=callback)

                    # Add result to session
                    session.add_stage_result(result)

                    # Log completion
                    stage_duration = time.time() - stage_start
                    status = "PASS" if result.success else "FAIL"  # Removed emoji
                    session.add_log_entry(
                        f"{status} {stage.command} completed in {stage_duration:.2f}s "
                        f"({result.issue_count} issues, {result.fixes_count} fixes)"
                    )

                    if callback:
                        callback.on_stage_finish(
                            stage.command, result.success, stage_duration
                        )

                    # Display stage result
                    self._display_stage_result(result)

                except Exception as e:
                    # Handle stage failure
                    error_result = StageResult(stage, False, time.time() - stage_start)
                    error_result.stderr = str(e)
                    session.add_stage_result(error_result)

                    session.add_log_entry(
                        f"FAIL {stage.command} failed: {str(e)}"
                    )  # Removed emoji
                    if callback:
                        callback.on_stage_finish(
                            stage.command, False, time.time() - stage_start
                        )

                    self.print(f"FAIL {stage.command} failed: {e}")  # Removed emoji

        # Finalize session
        session.finish()
        self._display_session_summary(session)

        return session

    def _display_session_header(self, session: LintingSession):
        """Display session start information with local time - Windows compatible"""
        local_time = session.start_time.strftime("%H:%M:%S")  # Local time display

        if self.console:
            try:
                header = Panel.fit(
                    f"CASCADE LINTER SESSION\n"  # Removed emoji for Windows compatibility
                    f"Target: {session.target_path}\n"
                    f"Stages: {' -> '.join(s.command for s in session.stages_requested)}\n"  # Simplified arrow
                    f"Started: {local_time}",  # Uses local time
                    style="bold blue",
                )
                self.console.print(header)
            except UnicodeEncodeError:
                # Fallback to simple text if Rich fails on Windows
                self.print("CASCADE LINTER SESSION")
                self.print(f"Target: {session.target_path}")
                self.print(
                    f"Stages: {' -> '.join(s.command for s in session.stages_requested)}"
                )
                self.print(f"Started: {local_time}")
        else:
            self.print("CASCADE LINTER SESSION")
            self.print(f"Target: {session.target_path}")
            self.print(
                f"Stages: {' -> '.join(s.command for s in session.stages_requested)}"
            )
            self.print(f"Started: {local_time}")

    def _display_stage_result(self, result: StageResult):
        """Display stage results with accurate metrics"""
        status = result.status_icon
        stage_name = f"{result.stage.icon} {result.stage.command.upper()}"

        self.print(f"{status} {stage_name} ({result.execution_time:.2f}s)")

        if result.issue_count > 0:
            self.print(f"   Found {result.issue_count} issues")  # Removed emoji

        if result.fixes_count > 0:
            self.print(f"   Fixed {result.fixes_count} issues")  # Removed emoji

        if result.stderr and self.debug:
            self.print(f"   Stderr: {result.stderr[:100]}...")  # Removed emoji

    def _display_session_summary(self, session: LintingSession):
        """Display comprehensive session summary with accurate counts"""
        if self.console:
            # Create summary table
            table = Table(
                title=f"Session Summary ({session.execution_time:.2f}s)"
            )  # Removed emoji
            table.add_column("Stage", style="cyan")
            table.add_column("Status", style="bold")
            table.add_column("Issues", justify="right", style="magenta")
            table.add_column("Fixed", justify="right", style="green")
            table.add_column("Time", justify="right", style="yellow")

            for stage in session.stages_requested:
                if stage in session.stage_results:
                    result = session.stage_results[stage]
                    status = f"{result.status_icon} {'CLEAN' if result.success else 'ISSUES'}"
                    table.add_row(
                        f"{stage.icon} {stage.command}",
                        status,
                        str(result.issue_count),
                        str(result.fixes_count),
                        f"{result.execution_time:.2f}s",
                    )

            self.console.print(table)

        # Text summary with accurate counts
        self.print("\nFINAL SUMMARY")  # Removed emoji
        self.print(f"Total time: {session.execution_time:.2f}s")  # Removed emoji
        self.print(f"Total issues remaining: {session.total_issues}")  # Removed emoji
        self.print(
            f"Total fixes applied: {session.total_fixes_applied}"
        )  # Removed emoji
        self.print(
            f"Files with issues: {session.total_files_with_issues}"
        )  # Removed emoji
        self.print(
            f"Overall success: {'YES' if session.success else 'NO'}"
        )  # Removed emoji

    def generate_detailed_report(self, session: LintingSession) -> str:
        """Generate comprehensive report with accurate issue counting"""
        lines = []
        lines.append("=" * 80)
        lines.append("📋 CASCADE LINTER DETAILED REPORT")
        lines.append("=" * 80)

        # Use local time formatting
        local_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        lines.append(f"Generated: {local_time}")
        lines.append(f"Session ID: {session.session_id}")
        lines.append(f"Target: {session.target_path}")
        lines.append("")

        # Executive Summary with ACCURATE counts
        lines.append("📊 EXECUTIVE SUMMARY")
        lines.append("-" * 40)
        lines.append(f"Total execution time: {session.execution_time:.2f}s")
        lines.append(f"Total issues remaining: {session.total_issues}")
        lines.append(f"Total fixes applied: {session.total_fixes_applied}")
        lines.append(f"Files with issues: {session.total_files_with_issues}")
        lines.append(
            f"Overall success: {'✅ PASSED' if session.success else '❌ ISSUES REMAIN'}"
        )
        lines.append("")

        # Stage Details with accurate metrics
        lines.append("🔧 STAGE DETAILS")
        lines.append("-" * 40)
        for stage in session.stages_requested:
            if stage in session.stage_results:
                result = session.stage_results[stage]
                lines.append(
                    f"{stage.icon} {stage.command.upper()}: {result.status_icon}"
                )
                lines.append(f"   Execution time: {result.execution_time:.2f}s")
                lines.append(f"   Initial issues: {result.initial_issue_count}")
                lines.append(f"   Remaining issues: {result.issue_count}")
                lines.append(f"   Issues fixed: {result.fixes_count}")

                if result.command_used:
                    lines.append(f"   Command: {' '.join(result.command_used)}")

                if result.stderr and self.debug:
                    lines.append(f"   Errors: {result.stderr[:200]}...")
                lines.append("")

        # Issues by File (accurate grouping)
        if session.issues_by_file:
            lines.append("📄 REMAINING ISSUES BY FILE")
            lines.append("-" * 40)

            for file_path, issues in sorted(session.issues_by_file.items()):
                lines.append(f"📁 {file_path} ({len(issues)} issues)")

                # Sort issues by line number
                sorted_issues = sorted(issues, key=lambda x: (x.line, x.column))

                for issue in sorted_issues:
                    severity_icon = issue.severity.icon
                    fixable_icon = "🔧" if issue.fixable else "👨‍💻"
                    lines.append(
                        f"   {severity_icon} {fixable_icon} {issue.line}:{issue.column} "
                        f"{issue.code}: {issue.message}"
                    )
                lines.append("")

        # Actionable Recommendations
        lines.append("💡 ACTIONABLE RECOMMENDATIONS")
        lines.append("-" * 40)

        fixable_issues = [issue for issue in session.all_issues if issue.fixable]
        manual_issues = [issue for issue in session.all_issues if not issue.fixable]

        if fixable_issues:
            lines.append(f"🔧 {len(fixable_issues)} issues can still be auto-fixed:")
            lines.append("   Run: cascade-linter --unsafe-fixes")
            lines.append("   Or: cascade-linter (for safe fixes only)")

        if manual_issues:
            lines.append(f"👨‍💻 {len(manual_issues)} issues require manual attention:")

            # Group by linter for specific guidance
            by_linter = {}
            for issue in manual_issues:
                if issue.linter not in by_linter:
                    by_linter[issue.linter] = []
                by_linter[issue.linter].append(issue)

            for linter, linter_issues in by_linter.items():
                lines.append(f"   {linter}: {len(linter_issues)} issues")

                # Show most common issue types
                issue_counts = {}
                for issue in linter_issues:
                    code = issue.code
                    issue_counts[code] = issue_counts.get(code, 0) + 1

                # Show top 3 issue types
                top_issues = sorted(
                    issue_counts.items(), key=lambda x: x[1], reverse=True
                )[:3]
                for code, count in top_issues:
                    lines.append(f"     - {code}: {count} occurrences")

        if not session.all_issues:
            lines.append("🎉 No issues found! Your code is clean!")

        lines.append("")
        lines.append("🤖 AI ASSISTANT READY")
        lines.append("This report provides structured data for AI-powered code fixing.")
        lines.append("=" * 80)

        return "\n".join(lines)

    def save_session_log(
        self, session: LintingSession, log_path: Optional[str] = None
    ) -> str:
        """Save comprehensive session log with local timestamps"""
        if not log_path:
            # Use local time for filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            log_path = f"linting_log_{timestamp}.log"

        try:
            log_content = []

            # Add detailed report
            log_content.append(self.generate_detailed_report(session))

            # Add session log
            log_content.append("\n" + "=" * 80)
            log_content.append("📋 SESSION LOG (LOCAL TIME)")
            log_content.append("=" * 80)
            log_content.append(session.raw_log)

            # Add raw command outputs for debugging
            log_content.append("\n" + "=" * 80)
            log_content.append("🔧 COMMAND OUTPUTS")
            log_content.append("=" * 80)

            for stage, result in session.stage_results.items():
                log_content.append(f"\n{'-' * 40}")
                log_content.append(f"{stage.icon} {stage.command.upper()} OUTPUT")
                log_content.append(f"{'-' * 40}")

                if result.command_used:
                    log_content.append(f"Command: {' '.join(result.command_used)}")

                if result.stdout:
                    log_content.append("STDOUT:")
                    log_content.append(result.stdout)

                if result.stderr:
                    log_content.append("STDERR:")
                    log_content.append(result.stderr)

            # Write to file
            with open(log_path, "w", encoding="utf-8") as f:
                f.write("\n".join(log_content))

            self.print(f"📄 Log saved: {log_path}")
            return log_path

        except Exception as e:
            self.print(f"⚠️ Failed to save log: {e}")
            return ""

    def validate_environment(self) -> Dict[str, bool]:
        """Validate linting tools availability"""
        tools_status = {}

        for stage in LinterStage:
            try:
                success, stdout, stderr = self.runner.run_command(
                    [stage.command, "--version"], f"Checking {stage.command}"
                )
                tools_status[stage.command] = success

                if self.debug:
                    version_info = (
                        stdout.strip().split("\n")[0] if stdout else "Unknown"
                    )
                    print(f"DEBUG: {stage.command} version: {version_info}")

            except Exception as e:
                tools_status[stage.command] = False
                if self.debug:
                    print(f"DEBUG: {stage.command} check failed: {e}")

        # Display results
        if self.console:
            table = Table(title="🔍 Environment Validation")
            table.add_column("Tool", style="cyan")
            table.add_column("Status", style="bold")
            table.add_column("Description", style="dim")

            for stage in LinterStage:
                status_color = "green" if tools_status[stage.command] else "red"
                status_text = (
                    "✅ Available" if tools_status[stage.command] else "❌ Missing"
                )
                table.add_row(
                    stage.command,
                    f"[{status_color}]{status_text}[/{status_color}]",
                    stage.description,
                )

            self.console.print(table)
        else:
            self.print("🔍 Environment Validation:")
            for stage in LinterStage:
                status = "✅" if tools_status[stage.command] else "❌"
                self.print(f"   {status} {stage.command}: {stage.description}")

        return tools_status


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================


def create_runner(
    debug: bool = False, simple_output: bool = False
) -> CodeQualityRunner:
    """Factory function for creating CodeQualityRunner"""
    return CodeQualityRunner(debug=debug, simple_output=simple_output)


def run_cascade_lint(
    path: str = ".",
    stages: Optional[List[str]] = None,
    check_only: bool = False,
    unsafe_fixes: bool = False,
    debug: bool = False,
    simple_output: bool = False,
    save_log: bool = True,
    callback: Optional[LinterProgressCallback] = None,
) -> LintingSession:
    """
    Convenience function to run cascade linting with all fixes

    Args:
        path: Target path to lint
        stages: List of linter names (default: ['ruff', 'flake8'])
        check_only: Only check, don't apply fixes
        unsafe_fixes: Apply unsafe Ruff fixes
        debug: Enable debug output
        simple_output: Plain text output
        save_log: Save detailed log file
        callback: Progress callback for GUI integration

    Returns:
        LintingSession with complete results and accurate issue counts
    """

    # Convert string stage names to LinterStage enums - FIXED mapping
    stage_objects = []
    if stages:
        stage_map = {
            stage.command: stage for stage in LinterStage
        }  # Use .command not .value
        for stage_name in stages:
            if stage_name in stage_map:
                stage_objects.append(stage_map[stage_name])
    else:
        # Default to all 5 stages for comprehensive analysis
        stage_objects = [
            LinterStage.RUFF,
            LinterStage.FLAKE8,
            LinterStage.PYLINT,
            LinterStage.BANDIT,
            LinterStage.MYPY,
        ]

    # Create runner
    runner = create_runner(debug=debug, simple_output=simple_output)

    # Validate environment in debug mode
    if debug:
        runner.validate_environment()

    # Run linting session
    session = runner.run_linting_session(
        path=path,
        stages=stage_objects,
        check_only=check_only,
        unsafe_fixes=unsafe_fixes,
        callback=callback,
    )

    # Save log if requested
    if save_log:
        runner.save_session_log(session)

    return session


# ============================================================================
# EXPORTS AND COMPATIBILITY
# ============================================================================

__all__ = [
    # Main classes
    "CodeQualityRunner",
    "LintingSession",
    "IssueItem",
    "StageResult",
    # Enums
    "LinterStage",
    "IssueSeverity",
    # Progress system
    "LinterProgressCallback",
    # Convenience functions
    "create_runner",
    "run_cascade_lint",
    # Executors (for advanced usage)
    "RuffExecutor",
    "Flake8Executor",
    "PylintExecutor",
    "BanditExecutor",
    "MypyExecutor",
    # Utilities
    "CommandRunner",
    "IssueParser",
]

# ============================================================================
# BACKWARD COMPATIBILITY LAYER
# ============================================================================

# Legacy aliases for compatibility
LinterStatus = IssueSeverity  # Old name
LinterRunner = CodeQualityRunner  # Old name

# Add to exports
__all__.extend(["LinterStatus", "LinterRunner"])

# Debug print to confirm loading
if os.environ.get("DEBUG"):
    print("✅ Refactored core module loaded with local timezone support")

# ============================================================================
# CLI INTEGRATION
# ============================================================================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Cascade Linter - Enhanced Python Code Quality Tool"
    )
    parser.add_argument(
        "path", nargs="?", default=".", help="Path to lint (default: current directory)"
    )
    parser.add_argument(
        "--stages",
        nargs="+",
        choices=[stage.command for stage in LinterStage],
        default=None,
        help="Linting stages to run (default: ruff, flake8)",
    )
    parser.add_argument(
        "--check-only", action="store_true", help="Only check, don't auto-fix"
    )
    parser.add_argument(
        "--unsafe-fixes", action="store_true", help="Apply Ruff's unsafe fixes"
    )
    parser.add_argument(
        "--debug", action="store_true", help="Enable debug output with local timestamps"
    )
    parser.add_argument(
        "--simple-output", action="store_true", help="Plain text output for scripting"
    )
    parser.add_argument("--no-log", action="store_true", help="Don't save log file")

    args = parser.parse_args()

    # Run cascade linting
    session = run_cascade_lint(
        path=args.path,
        stages=args.stages,
        check_only=args.check_only,
        unsafe_fixes=args.unsafe_fixes,
        debug=args.debug,
        simple_output=args.simple_output,
        save_log=not args.no_log,
    )

    # Exit with appropriate code
    sys.exit(0 if session.success else 1)
