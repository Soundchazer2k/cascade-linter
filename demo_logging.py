#!/usr/bin/env python3
"""
Demonstration of the Cascade Linter GUI with working structured logging
"""

import sys
import os

# Add the project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer
from cascade_linter.gui.main_window import MainWindow


def demo_logging_in_action():
    """Demonstrate the logging system working in real-time"""
    app = QApplication(sys.argv)

    # Create and show the main window
    window = MainWindow()
    window.show()

    # If logging is available, demonstrate it
    if hasattr(window, "logger") and window.logger:
        print("\n[DEMO] Logging Demo Starting...")
        print("Watch the Activity Log in the GUI for beautiful structured logs!")

        def demo_sequence():
            """Demonstrate various log types"""
            # Simulate some realistic application events
            window.logger.info("demo_started", session_id="demo_123")

            # Simulate directory operations
            QTimer.singleShot(
                1000,
                lambda: window.logger.info(
                    "directory_scanned",
                    path="/example/project",
                    files_found=45,
                    python_files=32,
                ),
            )

            QTimer.singleShot(
                2000,
                lambda: window.logger.info(
                    "linter_stage_started", stage="Ruff", mode="auto_fix"
                ),
            )

            QTimer.singleShot(
                3000,
                lambda: window.logger.warning(
                    "lint_issue_found",
                    file="example.py",
                    line=42,
                    rule="F401",
                    message="unused import",
                ),
            )

            QTimer.singleShot(
                4000,
                lambda: window.logger.info(
                    "lint_issue_fixed",
                    file="example.py",
                    rule="F401",
                    action="removed_import",
                ),
            )

            QTimer.singleShot(
                5000,
                lambda: window.logger.info(
                    "linter_stage_finished",
                    stage="Ruff",
                    duration_ms=1234,
                    issues_found=3,
                    issues_fixed=1,
                ),
            )

            QTimer.singleShot(
                6000,
                lambda: window.logger.error(
                    "linter_binary_missing",
                    stage="Pylint",
                    error="Command not found: pylint",
                    suggestion="Install pylint with: pip install pylint",
                ),
            )

            QTimer.singleShot(
                7000,
                lambda: window.logger.info(
                    "session_completed",
                    total_duration_ms=5678,
                    total_issues=3,
                    total_fixed=1,
                    overall_success=True,
                ),
            )

            QTimer.singleShot(
                8000,
                lambda: window.logger.info(
                    "demo_completed",
                    message="This demonstrates the beautiful structured logging!",
                ),
            )

        # Start the demo sequence after a short delay
        QTimer.singleShot(500, demo_sequence)
    else:
        print("[WARNING] Logging not available - running in basic mode")

    # Run the application
    return app.exec()


if __name__ == "__main__":
    print("[DEMO] Cascade Linter GUI - Logging Demo")
    print("=" * 50)
    print("This demonstrates the structured logging system in action.")
    print("Open the GUI and watch the 'Activity Log' section!")
    print("=" * 50)

    exit_code = demo_logging_in_action()
    sys.exit(exit_code)
