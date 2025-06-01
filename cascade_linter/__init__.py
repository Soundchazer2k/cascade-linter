#!/usr/bin/env python3
"""
Cascade Linter Package - COMPLETELY REFACTORED
Modern Python linting package with both CLI and GUI interfaces
"""

__version__ = "2.1.0"
__author__ = "Cascade Tools Team"
__description__ = "Modern cascading Python linter with Rich UI and PySide6 GUI"

# Import refactored core classes
from .core import (
    CodeQualityRunner,
    LintingSession,
    IssueItem,
    LinterStage,
    IssueSeverity,
    LinterProgressCallback,
    StageResult,
    run_cascade_lint
)

# Import CLI interface
try:
    from .cli import main as cli_main
except ImportError:
    # CLI not available - this is OK for GUI-only usage
    cli_main = None

# Package metadata
__all__ = [
    # Core classes
    "CodeQualityRunner",
    "LintingSession", 
    "IssueItem",
    "LinterStage",
    "IssueSeverity",
    "LinterProgressCallback",
    "StageResult",
    
    # Main functions
    "run_cascade_lint",
    "cli_main",
    
    # Metadata
    "__version__",
    "__author__",
    "__description__"
]

# Convenience function for backward compatibility
def create_linter_session(target_path: str = ".") -> LintingSession:
    """
    Create a new linting session (convenience function)
    
    Args:
        target_path: Path to lint (default: current directory)
        
    Returns:
        LintingSession: New linting session
    """
    return LintingSession(target_path=target_path)


def create_quality_runner() -> CodeQualityRunner:
    """
    Create a new code quality runner (convenience function)
    
    Returns:
        CodeQualityRunner: New runner instance
    """
    return CodeQualityRunner()


# Package configuration
PACKAGE_CONFIG = {
    "name": "cascade-linter",
    "version": __version__,
    "description": __description__,
    "supported_python": ">=3.8",
    "gui_framework": "PySide6",
    "linters": ["ruff", "flake8", "pylint", "bandit"],
    "features": [
        "Cross-platform GUI",
        "CLI interface", 
        "Real-time progress",
        "Rich terminal output",
        "Dark/Light themes",
        "Batch processing",
        "Issue filtering",
        "Export capabilities"
    ]
}
