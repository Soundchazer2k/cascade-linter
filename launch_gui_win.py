#!/usr/bin/env python3
"""
Simple Windows-compatible launcher for Cascade Linter GUI with backend integration
"""

import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def main():
    """Launch the Cascade Linter GUI"""
    print("ROCKET Launching Cascade Linter GUI with Real Backend")
    print("=" * 60)

    try:
        # Test backend availability first
        from cascade_linter.gui.tools.BackendIntegration import (
            test_backend_availability,
        )

        if not test_backend_availability():
            print(
                "WARNING Warning: Backend not fully available. Some features may not work."
            )
            input("Press Enter to continue anyway, or Ctrl+C to abort...")
        else:
            print("CHECK Backend is available and ready!")

        # Import and run the GUI
        from PySide6.QtWidgets import QApplication
        from cascade_linter.gui.main_window import MainWindow

        app = QApplication(sys.argv)

        # Create and show main window
        window = MainWindow()
        window.show()

        print("\nLIGHTBULB Usage Tips:")
        print("   1. Click 'Add Directory' to select a Python project")
        print("   2. Click 'Run Analysis' to start real linting")
        print("   3. Watch the progress bars show real linter execution")
        print("   4. Check the Analytics tab for detailed results")

        # Run the application
        return app.exec()

    except ImportError as e:
        print(f"X Import Error: {e}")
        print("\nWRENCH Please ensure:")
        print("   1. PySide6 is installed: pip install PySide6")
        print("   2. cascade_linter package is available")
        print("   3. All linting tools are installed (ruff, flake8, etc.)")
        return 1

    except Exception as e:
        print(f"X Unexpected error: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
