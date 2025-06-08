# cascade_linter/gui/__init__.py

"""
Cascade Linter GUI Package

Professional PySide6-based graphical user interface for the Cascade Linter.

Features:
- Modern flat design with multiple themes
- Real-time progress tracking with animated widgets
- Batch processing capabilities
- Rich HTML logging with filtering
- Responsive layouts following Nielsen's heuristics
- Cross-platform compatibility (Windows, macOS, Linux)

Main Components:
- main_window.py: Primary application window with dashboard
- widgets/: Custom PySide6 widgets (MetricCard, ProgressDonut, LogViewer)
- dialogs/: Settings and batch processing dialogs
- tools/: Utility modules (ThemeLoader, ConfigManager, etc.)
"""

__version__ = "1.0.0"
__author__ = "Cascade Linter Project"

# Don't import MainWindow by default to avoid circular imports during development
__all__ = []
