#!/usr/bin/env python3
"""
Enhanced Launcher for Cascade Linter GUI

Provides comprehensive startup with dependency checking, error handling,
and graceful degradation when components are missing.

Features:
- Dependency validation
- Graceful error handling
- Development vs production mode detection
- Comprehensive logging setup
- Theme system initialization
- Backend availability checking
"""

import sys
import logging
from pathlib import Path
from typing import Optional, List, Tuple

# Add the project root to Python path for imports
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


class DependencyChecker:
    """Checks for required dependencies and provides helpful error messages."""

    REQUIRED_PACKAGES = [
        ("PySide6", "PySide6", "GUI framework"),
        ("structlog", "structlog", "structured logging"),
        ("rich", "rich", "terminal formatting"),
    ]

    OPTIONAL_PACKAGES = [
        ("ruff", "ruff", "fast Python linter"),
        ("flake8", "flake8", "style guide enforcement"),
        ("pylint", "pylint", "deep code analysis"),
        ("bandit", "bandit", "security scanner"),
        ("mypy", "mypy", "static type checker"),
    ]

    @classmethod
    def check_package(cls, package_name: str) -> bool:
        """Check if a package is available."""
        try:
            __import__(package_name)
            return True
        except ImportError:
            return False

    @classmethod
    def check_all_dependencies(cls) -> Tuple[List[str], List[str]]:
        """
        Check all dependencies.

        Returns:
            Tuple of (missing_required, missing_optional)
        """
        missing_required = []
        missing_optional = []

        # Check required packages
        for import_name, pip_name, description in cls.REQUIRED_PACKAGES:
            if not cls.check_package(import_name):
                missing_required.append((pip_name, description))

        # Check optional packages
        for import_name, pip_name, description in cls.OPTIONAL_PACKAGES:
            if not cls.check_package(import_name):
                missing_optional.append((pip_name, description))

        return missing_required, missing_optional

    @classmethod
    def print_dependency_report(cls):
        """Print a comprehensive dependency report."""
        print("🔍 Checking dependencies...")

        missing_required, missing_optional = cls.check_all_dependencies()

        if not missing_required and not missing_optional:
            print("✅ All dependencies are available!")
            return True

        if missing_required:
            print("\n❌ Missing REQUIRED dependencies:")
            for package, description in missing_required:
                print(f"  • {package} - {description}")
            print("\nInstall required dependencies:")
            packages = " ".join([pkg for pkg, _ in missing_required])
            print(f"  pip install {packages}")

        if missing_optional:
            print("\n⚠️ Missing OPTIONAL dependencies:")
            for package, description in missing_optional:
                print(f"  • {package} - {description}")
            print("\nInstall optional dependencies (for full functionality):")
            packages = " ".join([pkg for pkg, _ in missing_optional])
            print(f"  pip install {packages}")

        return len(missing_required) == 0


class CascadeLinterLauncher:
    """Main launcher for the Cascade Linter GUI application."""

    def __init__(self):
        self.logger = self._setup_logging()
        self.app = None
        self.main_window = None

    def _setup_logging(self) -> logging.Logger:
        """Setup logging for the launcher."""
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )
        return logging.getLogger(__name__)

    def _check_python_version(self) -> bool:
        """Ensure Python version is compatible."""
        if sys.version_info < (3, 9):
            print(f"❌ Python 3.9+ required, but you have {sys.version}")
            print("Please upgrade Python to continue.")
            return False

        print(
            f"✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        )
        return True

    def _check_qt_availability(self) -> bool:
        """Check if PySide6 is properly installed and can create an application."""
        try:
            from PySide6.QtWidgets import QApplication
            from PySide6.QtCore import Qt

            print("✅ PySide6 GUI framework available")
            return True
        except ImportError as e:
            print(f"❌ PySide6 not available: {e}")
            print("Install with: pip install PySide6")
            return False
        except Exception as e:
            print(f"❌ PySide6 error: {e}")
            return False

    def _initialize_qt_application(self) -> bool:
        """Initialize the Qt application."""
        try:
            from PySide6.QtWidgets import QApplication
            from PySide6.QtCore import Qt

            # Set up Qt application
            QApplication.setAttribute(
                Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True
            )
            QApplication.setAttribute(
                Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True
            )

            # Create application instance
            self.app = QApplication.instance()
            if self.app is None:
                self.app = QApplication(sys.argv)

            # Set application metadata
            self.app.setApplicationName("Cascade Linter")
            self.app.setApplicationVersion("1.0.0")
            self.app.setOrganizationName("Cascade Linter Project")
            self.app.setOrganizationDomain("cascade-linter.dev")

            print("✅ Qt application initialized")
            return True

        except Exception as e:
            print(f"❌ Failed to initialize Qt application: {e}")
            return False

    def _check_theme_system(self) -> bool:
        """Verify the theme system is working."""
        try:
            from cascade_linter.gui.tools.ThemeLoader import ThemeLoader

            # Check if themes directory exists
            if not ThemeLoader.validate_themes_directory():
                print("⚠️ Some theme files missing, but system theme available")
                return True  # Still functional with system theme

            print("✅ Theme system fully functional")
            return True

        except ImportError:
            print("⚠️ ThemeLoader not available, using default styling")
            return True  # Still functional without themes
        except Exception as e:
            print(f"⚠️ Theme system error: {e}")
            return True  # Still functional

    def _check_backend_integration(self) -> bool:
        """Check backend integration availability."""
        try:
            from cascade_linter.core import LinterRunner
            from cascade_linter.gui.tools.BackendIntegration import (
                create_backend_manager,
            )

            # Test core linter
            runner = LinterRunner()
            print("✅ Core linter backend available")

            # Test backend integration
            backend_manager = create_backend_manager()
            if backend_manager:
                print("✅ Backend integration fully functional")
            else:
                print("⚠️ Backend integration limited (fallback mode)")

            return True

        except ImportError as e:
            print(f"⚠️ Backend integration not available: {e}")
            return True  # GUI can still function without backend
        except Exception as e:
            print(f"⚠️ Backend integration error: {e}")
            return True

    def _create_main_window(self) -> bool:
        """Create and show the main window."""
        try:
            from cascade_linter.gui.main_window import MainWindow

            self.main_window = MainWindow()

            # Apply initial theme
            try:
                from cascade_linter.gui.tools.ThemeLoader import ThemeLoader
                from cascade_linter.gui.tools.ConfigManager import ConfigManager

                # Load saved theme or default to dark
                theme_index = ConfigManager.get_int(
                    "Interface/Theme", 2
                )  # Default to dark
                theme_name = ThemeLoader.get_theme_name_by_index(theme_index)
                ThemeLoader.load_theme(theme_name, self.app)
                print(f"✅ Applied theme: {theme_name}")

            except Exception as e:
                print(f"⚠️ Theme application failed: {e}, using default")

            # Show the window
            self.main_window.show()
            print("✅ Main window created and displayed")
            return True

        except Exception as e:
            print(f"❌ Failed to create main window: {e}")
            self.logger.exception("Main window creation failed")
            return False

    def _show_startup_message(self):
        """Show a friendly startup message."""
        print("\n" + "=" * 60)
        print("🚀 Cascade Linter GUI - Professional Code Quality Tool")
        print("=" * 60)
        print("Welcome! Starting the application...")
        print()

    def _show_success_message(self):
        """Show success message when everything is ready."""
        print("\n" + "=" * 60)
        print("🎉 Application launched successfully!")
        print("=" * 60)
        print("📖 Quick Start:")
        print("  1. Add directories with Ctrl+D")
        print("  2. Select linters (Ruff recommended)")
        print("  3. Click 'Run Analysis' or press F5")
        print("  4. Explore themes in Settings menu")
        print("\n🔧 Keyboard shortcuts: F1 (Quick), F2 (Standard), F3 (Full)")
        print("=" * 60)

    def launch(self, args: Optional[List[str]] = None) -> int:
        """
        Launch the Cascade Linter GUI application.

        Args:
            args: Command line arguments (optional)

        Returns:
            Exit code (0 for success, 1 for failure)
        """
        self._show_startup_message()

        # Step 1: Check Python version
        if not self._check_python_version():
            return 1

        # Step 2: Check dependencies
        if not DependencyChecker.print_dependency_report():
            print("\n❌ Cannot start: missing required dependencies")
            return 1

        # Step 3: Check Qt availability
        if not self._check_qt_availability():
            return 1

        # Step 4: Initialize Qt application
        if not self._initialize_qt_application():
            return 1

        # Step 5: Check theme system
        self._check_theme_system()

        # Step 6: Check backend integration
        self._check_backend_integration()

        # Step 7: Create main window
        if not self._create_main_window():
            return 1

        # Step 8: Show success message
        self._show_success_message()

        # Step 9: Run the application
        try:
            exit_code = self.app.exec()
            print("\n👋 Application closed gracefully")
            return exit_code

        except KeyboardInterrupt:
            print("\n⏹ Application interrupted by user")
            return 0
        except Exception as e:
            print(f"\n💥 Application crashed: {e}")
            self.logger.exception("Application crashed")
            return 1


def main():
    """Entry point for the launcher."""
    # Handle command line arguments
    import argparse

    parser = argparse.ArgumentParser(
        description="Cascade Linter GUI - Professional Code Quality Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python launch_enhanced.py              # Normal startup
  python launch_enhanced.py --check-deps # Check dependencies only
  python launch_enhanced.py --help       # Show this help

For more information, see docs/USER_GUIDE.md
        """,
    )

    parser.add_argument(
        "--check-deps",
        action="store_true",
        help="Only check dependencies, don't launch GUI",
    )

    parser.add_argument("--debug", action="store_true", help="Enable debug logging")

    args = parser.parse_args()

    # Handle --check-deps flag
    if args.check_deps:
        print("🔍 Dependency Check Mode")
        print("=" * 40)
        if DependencyChecker.print_dependency_report():
            print("\n✅ All required dependencies available!")
            return 0
        else:
            print("\n❌ Some required dependencies missing!")
            return 1

    # Handle --debug flag
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        print("🐛 Debug logging enabled")

    # Launch the application
    launcher = CascadeLinterLauncher()
    return launcher.launch()


if __name__ == "__main__":
    sys.exit(main())
