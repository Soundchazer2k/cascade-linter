# cascade_linter/gui/tools/__init__.py
"""
GUI Tools Package

This package contains utility modules for the Cascade Linter GUI:
- ConfigManager: QSettings wrapper for configuration management
- ThemeLoader: QSS theme loading and application
- BatchManager: Background batch processing with Qt signals
- LogExporter: Export logs to various formats
- AnimationRunner: Simple animation management
- logging_config: Structured logging with Rich HTML output
"""

__all__ = [
    "ConfigManager",
    "ThemeLoader", 
    "BatchManager",
    "LogExporter",
    "AnimationRunner",
]
