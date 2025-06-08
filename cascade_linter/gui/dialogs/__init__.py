# cascade_linter/gui/dialogs/__init__.py

"""
GUI Dialogs Package for Cascade Linter

This package contains all dialog windows used in the Cascade Linter GUI:
- SettingsDialog: Comprehensive settings with animated help popups
- HelpPopup: Animated help dialog with smooth zoom transitions
"""

from .SettingsDialog import SettingsDialog, show_settings_dialog
from .HelpPopup import HelpPopup, HelpContent

__all__ = [
    "SettingsDialog",
    "show_settings_dialog",
    "HelpPopup",
    "HelpContent",
]
