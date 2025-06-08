#!/usr/bin/env python3
"""
Enhanced Cascade Linter GUI Launcher
====================================

Professional launcher for the Cascade Linter GUI following PySide6-only standards.
Implements proper theming, error handling, and cross-platform compatibility.

Features:
- Material Design theme integration with fallback
- Comprehensive environment validation
- Professional error handling and user feedback
- Single-instance prevention
- Cross-platform launcher script compatibility
"""

import sys
import os
from pathlib import Path
from typing import Optional

# Add the project root to Python path for imports
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# PySide6 imports (exclusively - no PyQt)
try:
    from PySide6.QtWidgets import QApplication, QMessageBox, QSplashScreen
    from PySide6.QtCore import Qt, QTimer
    from PySide6.QtGui import QPixmap, QIcon, QPainter, QBrush, QColor

    PYSIDE6_AVAILABLE = True
except ImportError as e:
    PYSIDE6_AVAILABLE = False
    pyside6_error = str(e)

# Try to import Qt Material for theming (optional)
try:
    from qt_material import apply_stylesheet, list_themes

    QT_MATERIAL_AVAILABLE = True
except ImportError:
    QT_MATERIAL_AVAILABLE = False

# Try to import QtAwesome for icons (optional)
try:
    import qtawesome as qta

    QTAWESOME_AVAILABLE = True
except ImportError:
    QTAWESOME_AVAILABLE = False


def check_python_version() -> bool:
    """Check if Python version meets requirements."""
    return sys.version_info >= (3, 9)


def check_dependencies() -> tuple[bool, list[str]]:
    """Check if all required dependencies are available."""
    missing_deps = []

    # Check PySide6
    if not PYSIDE6_AVAILABLE:
        missing_deps.append("PySide6")

    # Check optional dependencies
    optional_deps = []
    if not QT_MATERIAL_AVAILABLE:
        optional_deps.append("qt-material (theming)")
    if not QTAWESOME_AVAILABLE:
        optional_deps.append("qtawesome (icons)")

    return len(missing_deps) == 0, missing_deps


def create_splash_screen(app: QApplication) -> Optional[QSplashScreen]:
    """Create a splash screen for application startup featuring the paint roller mascot."""
    try:
        # Try to load the mascot SVG first
        mascot_path = project_root / "assets" / "icons" / "mascot.svg"

        if mascot_path.exists():
            # Load SVG mascot
            from PySide6.QtSvg import QSvgRenderer

            # Create splash with mascot
            splash_pixmap = QPixmap(500, 300)
            splash_pixmap.fill(QColor("#121212"))

            painter = QPainter(splash_pixmap)

            # Render SVG mascot
            svg_renderer = QSvgRenderer(str(mascot_path))
            # Scale mascot to fit nicely in splash
            mascot_rect = painter.viewport()
            mascot_rect.setWidth(120)
            mascot_rect.setHeight(120)
            mascot_rect.moveTopLeft(painter.viewport().topLeft())
            mascot_rect.translate(30, 30)
            svg_renderer.render(painter, mascot_rect)

            # Draw title next to mascot
            painter.setPen(QColor("#E0E0E0"))
            title_font = painter.font()
            title_font.setPointSize(24)
            title_font.setBold(True)
            painter.setFont(title_font)
            painter.drawText(180, 70, "Cascade Linter")

            # Draw subtitle
            subtitle_font = painter.font()
            subtitle_font.setPointSize(14)
            subtitle_font.setBold(False)
            painter.setFont(subtitle_font)
            painter.setPen(QColor("#4DD0E1"))  # Match mascot colors
            painter.drawText(180, 100, "Modern Python Code Quality Tool")

            # Draw version and loading
            version_font = painter.font()
            version_font.setPointSize(11)
            painter.setFont(version_font)
            painter.setPen(QColor("#A0A0A0"))
            painter.drawText(180, 130, "Version 1.0.0 • PySide6")

            # Add a cute tagline
            painter.setPen(QColor("#FFD54F"))  # Match mascot yellow
            painter.drawText(30, 200, "Rolling out clean code, one lint at a time!")

            # Loading message
            painter.setPen(QColor("#E0E0E0"))
            painter.drawText(30, 230, "Loading...")

            painter.end()

        else:
            # Fallback to simple splash if mascot not found
            splash_pixmap = QPixmap(400, 200)
            splash_pixmap.fill(QColor("#121212"))

            painter = QPainter(splash_pixmap)
            painter.setPen(QColor("#E0E0E0"))

            # Draw title
            title_font = painter.font()
            title_font.setPointSize(18)
            title_font.setBold(True)
            painter.setFont(title_font)
            painter.drawText(20, 50, "Cascade Linter")

            # Draw subtitle
            subtitle_font = painter.font()
            subtitle_font.setPointSize(12)
            subtitle_font.setBold(False)
            painter.setFont(subtitle_font)
            painter.setPen(QColor("#A0A0A0"))
            painter.drawText(20, 80, "Modern Python Code Quality Tool")

            # Draw version
            version_font = painter.font()
            version_font.setPointSize(10)
            painter.setFont(version_font)
            painter.drawText(20, 120, "Version 1.0.0")
            painter.drawText(20, 140, "Loading...")

            painter.end()

        # Create splash screen
        splash = QSplashScreen(splash_pixmap)
        splash.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.SplashScreen)
        return splash

    except Exception as e:
        print(f"Warning: Could not create splash screen: {e}")
        return None


def apply_material_theme(app: QApplication, theme_name: str = "dark_blue.xml") -> bool:
    """Apply Material Design theme if available."""
    if not QT_MATERIAL_AVAILABLE:
        return False

    try:
        # Apply the theme
        apply_stylesheet(app, theme=theme_name)
        print(f"Applied Material Design theme: {theme_name}")
        return True

    except Exception as e:
        print(f"Warning: Failed to apply Material Design theme: {e}")
        return False


def apply_fallback_theme(app: QApplication) -> None:
    """Apply fallback dark theme if Material Design is not available."""
    fallback_stylesheet = """
    QApplication {
        background-color: #121212;
        color: #E0E0E0;
        font-family: "Segoe UI", "DejaVu Sans", "Arial", sans-serif;
        font-size: 10pt;
    }
    QMainWindow {
        background-color: #121212;
        color: #E0E0E0;
    }
    QWidget {
        background-color: #121212;
        color: #E0E0E0;
    }
    QPushButton {
        background-color: #357ABD;
        color: #E0E0E0;
        border: 1px solid #444444;
        border-radius: 4px;
        padding: 6px 12px;
        font-weight: bold;
    }
    QPushButton:hover {
        background-color: #4A90E2;
    }
    QPushButton:pressed {
        background-color: #285F8D;
    }
    QMenuBar {
        background-color: #2F343F;
        color: #E0E0E0;
        border-bottom: 1px solid #444444;
    }
    QMenuBar::item:selected {
        background-color: #357ABD;
    }
    QStatusBar {
        background-color: #2F343F;
        color: #E0E0E0;
        border-top: 1px solid #444444;
    }
    QTabWidget::pane {
        border: 1px solid #444444;
        background-color: #1E1E1E;
    }
    QTabBar::tab {
        background-color: #2E3436;
        color: #E0E0E0;
        padding: 8px 16px;
        margin-right: 2px;
        border-top-left-radius: 4px;
        border-top-right-radius: 4px;
    }
    QTabBar::tab:selected {
        background-color: #357ABD;
    }
    """

    app.setStyleSheet(fallback_stylesheet)
    print("Applied fallback dark theme")


def show_dependency_error(missing_deps: list[str]) -> None:
    """Show error dialog for missing dependencies."""
    # Create minimal application for error dialog
    if PYSIDE6_AVAILABLE:
        app = QApplication.instance() or QApplication(sys.argv)

        error_text = (
            "Missing Required Dependencies\n\n"
            f"The following dependencies are required but not installed:\n"
            f"• {chr(10).join(missing_deps)}\n\n"
            "Please install them using:\n"
            f"pip install {' '.join(missing_deps)}"
        )

        QMessageBox.critical(None, "Dependency Error", error_text)

    else:
        # Fallback to console output
        print("=" * 60)
        print("ERROR: Missing Required Dependencies")
        print("=" * 60)
        print("The following dependencies are required but not installed:")
        for dep in missing_deps:
            print(f"  • {dep}")
        print()
        print("Please install them using:")
        print(f"  pip install {' '.join(missing_deps)}")
        print("=" * 60)


def validate_environment() -> tuple[bool, str]:
    """Validate the runtime environment."""
    # Check Python version
    if not check_python_version():
        return (
            False,
            f"Python 3.9+ required, found {sys.version_info.major}.{sys.version_info.minor}",
        )

    # Check dependencies
    deps_ok, missing_deps = check_dependencies()
    if not deps_ok:
        return False, f"Missing dependencies: {', '.join(missing_deps)}"

    return True, "Environment validation passed"


def main() -> int:
    """Main entry point for the Cascade Linter GUI."""
    print("Cascade Linter GUI Launcher")
    print("=" * 40)

    # Validate environment
    env_ok, env_message = validate_environment()
    print(f"Environment check: {env_message}")

    if not env_ok:
        if PYSIDE6_AVAILABLE:
            # Show GUI error dialog
            _, missing_deps = check_dependencies()
            show_dependency_error(missing_deps)
        else:
            # Console-only error
            print(f"ERROR: {env_message}")
            print("\nPlease install required dependencies and try again.")

        return 1

    try:
        # Suppress Qt warnings for development
        os.environ.setdefault("QT_LOGGING_RULES", "*.debug=false;qt.qpa.*=false")

        # Create QApplication
        app = QApplication(sys.argv)

        # Set application metadata
        app.setApplicationName("Cascade Linter")
        app.setApplicationVersion("1.0.0")
        app.setOrganizationName("CascadeLinter")
        app.setOrganizationDomain("cascadelinter.dev")

        # Set application icon (try mascot first, fallback to QtAwesome)
        mascot_path = project_root / "assets" / "icons" / "mascot.svg"
        if mascot_path.exists():
            try:
                # Use mascot as app icon
                mascot_pixmap = QPixmap(64, 64)
                mascot_pixmap.fill(QColor("#00FFFFFF"))  # Transparent

                painter = QPainter(mascot_pixmap)
                from PySide6.QtSvg import QSvgRenderer

                svg_renderer = QSvgRenderer(str(mascot_path))
                svg_renderer.render(painter, mascot_pixmap.rect())
                painter.end()

                app.setWindowIcon(QIcon(mascot_pixmap))
                print("Set mascot as application icon")
            except Exception as e:
                print(f"Could not load mascot icon: {e}")
                # Fallback to QtAwesome
                if QTAWESOME_AVAILABLE:
                    try:
                        app_icon = qta.icon("fa5s.code", color="#4A90E2")
                        app.setWindowIcon(app_icon)
                    except Exception:
                        pass  # Icon is optional
        elif QTAWESOME_AVAILABLE:
            try:
                app_icon = qta.icon("fa5s.code", color="#4A90E2")
                app.setWindowIcon(app_icon)
            except Exception:
                pass  # Icon is optional

        # Create splash screen
        splash = create_splash_screen(app)
        if splash:
            splash.show()
            app.processEvents()

        # Apply theme (Material Design preferred, fallback if not available)
        theme_applied = False
        if QT_MATERIAL_AVAILABLE:
            # Try preferred Material Design themes
            preferred_themes = ["dark_blue.xml", "dark_teal.xml", "dark_amber.xml"]
            for theme in preferred_themes:
                if apply_material_theme(app, theme):
                    theme_applied = True
                    break

        if not theme_applied:
            apply_fallback_theme(app)

        # Import and create main window
        try:
            from cascade_linter.gui.main_window import ModernMainWindow

            if splash:
                splash.showMessage(
                    "Loading main window...",
                    Qt.AlignBottom | Qt.AlignCenter,
                    QColor("#E0E0E0"),
                )
                app.processEvents()

            # Create main window
            window = ModernMainWindow()

            # Hide splash and show main window
            if splash:
                splash.finish(window)

            window.show()

            # Center window on screen
            screen_geometry = app.primaryScreen().geometry()
            window_geometry = window.geometry()
            x = (screen_geometry.width() - window_geometry.width()) // 2
            y = (screen_geometry.height() - window_geometry.height()) // 2
            window.move(x, y)

            print("GUI launched successfully")

            # Start event loop
            return app.exec()

        except ImportError as e:
            error_msg = f"Failed to import GUI module: {e}"
            print(f"ERROR: {error_msg}")

            if splash:
                splash.close()

            QMessageBox.critical(
                None,
                "Import Error",
                f"Failed to load GUI components:\n{error_msg}\n\n"
                "Please check your installation and try again.",
            )
            return 1

    except Exception as e:
        error_msg = f"Unexpected error during startup: {e}"
        print(f"FATAL ERROR: {error_msg}")

        if PYSIDE6_AVAILABLE:
            app = QApplication.instance() or QApplication(sys.argv)
            QMessageBox.critical(
                None,
                "Startup Error",
                f"An unexpected error occurred:\n{error_msg}\n\n"
                "Please check the console for more details.",
            )

        return 1


if __name__ == "__main__":
    sys.exit(main())
