"""
GUI Package for Cascade Linter
Cross-platform desktop application with PySide6
"""

try:
    from .main_window import CascadeLinterMainWindow, create_application, main

    GUI_AVAILABLE = True
except ImportError:
    GUI_AVAILABLE = False
    CascadeLinterMainWindow = None
    create_application = None
    main = None

__all__ = [
    "CascadeLinterMainWindow",
    "create_application",
    "main",
    "GUI_AVAILABLE",
]
