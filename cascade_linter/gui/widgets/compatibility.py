#!/usr/bin/env python3
"""
Widget Compatibility Layer
Ensures existing widgets work with current core.py interface
"""

from typing import Optional, List, Dict, Any
from pathlib import Path

# Import existing sophisticated widgets
from .batch_processing import BatchProcessingDialog, BatchJobWorker
from .results_dashboard import ResultsDashboard as OriginalResultsDashboard
from .issue_browser import IssueBrowserWidget as OriginalIssueBrowser
from .settings_dialog import SettingsDialog as OriginalSettingsDialog

# Import core classes
try:
    from cascade_linter.core import CodeQualityRunner, LintingSession, LinterStage
except ImportError:
    # Fallback for when running from different locations
    import sys
    from pathlib import Path

    project_root = Path(__file__).parent.parent.parent
    sys.path.insert(0, str(project_root))
    from cascade_linter.core import CodeQualityRunner, LintingSession, LinterStage


class BatchProcessingWidget:
    """
    Simple interface widget that opens the sophisticated BatchProcessingDialog
    Provides the interface expected by ModernMainWindow
    """

    def __init__(self, parent=None):
        self.parent = parent
        self.current_directories = []
        self._dialog = None

    def add_directory(self, directory: str):
        """Add a directory to the processing queue"""
        self.current_directories.append(directory)
        if hasattr(self.parent, "statusBar"):
            self.parent.statusBar().showMessage(
                f"Added directory: {Path(directory).name}"
            )

    def start_quick_lint(self):
        """Start quick lint using the sophisticated batch processor"""
        self._open_batch_dialog()

    def start_full_lint(self):
        """Start full lint using the sophisticated batch processor"""
        self._open_batch_dialog()

    def _open_batch_dialog(self):
        """Open the sophisticated batch processing dialog"""
        if not self._dialog:
            self._dialog = BatchProcessingDialog(self.parent)

        # Add current directories to the batch processor
        for directory in self.current_directories:
            self._dialog.add_directory_to_queue(directory)

        # Show the dialog
        self._dialog.exec()


class ResultsDashboard(OriginalResultsDashboard):
    """
    Enhanced ResultsDashboard with compatibility methods
    """

    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent

    def update_session(self, session: Optional[LintingSession]):
        """Update dashboard with LintingSession data"""
        if not session:
            self.reset_dashboard()
            return

        # Convert LintingSession to the format expected by the dashboard
        session_data = {
            "total_files": getattr(session, "files_processed", 0),
            "total_issues": len(getattr(session, "all_issues", [])),
            "fixed_issues": getattr(session, "issues_fixed", 0),
            "total_time": getattr(session, "execution_time", 0.0),
            "stage_results": {},
        }

        # Map stage results if available
        if hasattr(session, "stage_results"):
            for stage, result in session.stage_results.items():
                stage_name = (
                    stage.name.lower() if hasattr(stage, "name") else str(stage).lower()
                )
                session_data["stage_results"][stage_name] = result

        self.update_dashboard(session_data)

    def clear(self):
        """Clear the dashboard"""
        self.reset_dashboard()

    def export_results(self):
        """Export current results"""
        # This could be enhanced to export from the current session
        if hasattr(self.parent, "current_session") and self.parent.current_session:
            from .settings_dialog import ExportDialog

            dialog = ExportDialog(self._convert_session_for_export(), self.parent)
            dialog.exec()
        else:
            from PySide6.QtWidgets import QMessageBox

            QMessageBox.information(
                self.parent, "No Data", "No session data available to export."
            )

    def _convert_session_for_export(self) -> Dict[str, Any]:
        """Convert current session to export format"""
        if (
            not hasattr(self.parent, "current_session")
            or not self.parent.current_session
        ):
            return {}

        session = self.parent.current_session
        return {
            "total_files": getattr(session, "files_processed", 0),
            "total_issues": len(getattr(session, "all_issues", [])),
            "total_time": getattr(session, "execution_time", 0.0),
            "stage_results": getattr(session, "stage_results", {}),
            "issues": [
                {
                    "file": issue.file_path,
                    "line": issue.line,
                    "column": issue.column,
                    "code": issue.code,
                    "message": issue.message,
                    "severity": issue.severity.name,
                    "linter": issue.linter,
                }
                for issue in getattr(session, "all_issues", [])
            ],
        }


class IssueBrowser(OriginalIssueBrowser):
    """
    Enhanced IssueBrowser with compatibility methods
    """

    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent

    def update_session(self, session: Optional[LintingSession]):
        """Update browser with LintingSession data"""
        if not session:
            self.clear()
            return

        # Get issues from session
        issues = getattr(session, "all_issues", [])
        self.load_issues(issues)

    def clear(self):
        """Clear the issue browser"""
        self.load_issues([])


class SettingsDialog(OriginalSettingsDialog):
    """
    Enhanced SettingsDialog with compatibility for main window
    """

    def __init__(self, parent=None):
        # Create a simple mock config manager since we don't have one yet
        class MockConfigManager:
            def __init__(self):
                from types import SimpleNamespace

                self.config = SimpleNamespace()
                self.config.general = SimpleNamespace()
                self.config.general.check_only_default = False
                self.config.general.unsafe_fixes_default = False
                self.config.general.respect_gitignore = True
                self.config.general.auto_save_logs = True
                self.config.general.log_retention_days = 30
                self.config.general.max_log_files = 100

                self.config.linters = {
                    "ruff": SimpleNamespace(enabled=True, max_line_length=88),
                    "flake8": SimpleNamespace(enabled=True, max_line_length=88),
                    "pylint": SimpleNamespace(enabled=True, max_line_length=88),
                    "bandit": SimpleNamespace(enabled=True, max_line_length=88),
                    "mypy": SimpleNamespace(enabled=True, max_line_length=88),
                }

                self.config.ui = SimpleNamespace()
                from types import SimpleNamespace

                ThemeMode = SimpleNamespace()
                ThemeMode.SYSTEM = "system"
                ThemeMode.LIGHT = "light"
                ThemeMode.DARK = "dark"
                self.config.ui.theme = ThemeMode()
                self.config.ui.theme.value = "system"
                self.config.ui.animation_enabled = True
                self.config.ui.log_font_size = 10
                self.config.ui.show_line_numbers = True
                self.config.ui.auto_scroll_log = True

            def update_general_config(self, **kwargs):
                for key, value in kwargs.items():
                    setattr(self.config.general, key, value)

            def update_linter_config(self, stage_id, **kwargs):
                if stage_id in self.config.linters:
                    for key, value in kwargs.items():
                        setattr(self.config.linters[stage_id], key, value)

            def update_ui_config(self, **kwargs):
                for key, value in kwargs.items():
                    setattr(self.config.ui, key, value)

            def save_config(self):
                pass  # Mock implementation

            def reset_to_defaults(self):
                self.__init__()  # Reset to default values

        # Use mock config manager
        config_manager = MockConfigManager()
        super().__init__(config_manager, parent)


# Export the compatibility layer
__all__ = [
    "BatchProcessingWidget",
    "ResultsDashboard",
    "IssueBrowser",
    "SettingsDialog",
]
