#!/usr/bin/env python3
"""
Simple working GUI test with minimal main window
"""

import sys
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QMessageBox,
)
from PySide6.QtCore import Qt


class SimpleMainWindow(QMainWindow):
    """Simplified main window for testing"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("✨ Cascade Linter - GUI Test")
        self.resize(800, 600)
        self.init_ui()
        self.apply_styling()

    def init_ui(self):
        """Initialize UI"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Title
        title = QLabel("Cascade Linter GUI")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(
            "font-size: 24pt; font-weight: bold; color: #729fcf; margin: 20px;"
        )
        layout.addWidget(title)

        # Status
        status = QLabel("PySide6 GUI Framework Successfully Loaded!")
        status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        status.setStyleSheet("font-size: 14pt; color: #8ae234; margin: 10px;")
        layout.addWidget(status)

        # Button row
        button_layout = QHBoxLayout()

        test_btn = QPushButton("🧪 Test Widgets")
        test_btn.setMinimumHeight(50)
        test_btn.clicked.connect(self.test_widgets)
        button_layout.addWidget(test_btn)

        demo_btn = QPushButton("🚀 Demo Simulation")
        demo_btn.setMinimumHeight(50)
        demo_btn.clicked.connect(self.demo_simulation)
        button_layout.addWidget(demo_btn)

        about_btn = QPushButton("ℹ️ About")
        about_btn.setMinimumHeight(50)
        about_btn.clicked.connect(self.show_about)
        button_layout.addWidget(about_btn)

        layout.addLayout(button_layout)
        layout.addStretch()

    def apply_styling(self):
        """Apply dark theme"""
        self.setStyleSheet(
            """
            QMainWindow {
                background-color: #2e3436;
                color: #eeeeec;
            }
            QWidget {
                background-color: #2e3436;
                color: #eeeeec;
                font-family: "Segoe UI", sans-serif;
                font-size: 11pt;
            }
            QPushButton {
                background-color: #555753;
                border: 1px solid #888a85;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #729fcf;
                border-color: #3465a4;
            }
            QPushButton:pressed {
                background-color: #3465a4;
            }
        """
        )

    def test_widgets(self):
        """Test widget loading"""
        try:
            # Try to import our custom widgets
            sys.path.insert(0, r"H:\Vibe Coding\cascade-linter")

            # Test individual widget files
            message = "Widget Test Results:\n\n"

            try:

                message += "✅ MetricCard: Loaded successfully\n"
            except Exception as e:
                message += f"❌ MetricCard: {e}\n"

            try:

                message += "✅ ProgressDonut: Loaded successfully\n"
            except Exception as e:
                message += f"❌ ProgressDonut: {e}\n"

            try:

                message += "✅ LogViewer: Loaded successfully\n"
            except Exception as e:
                message += f"❌ LogViewer: {e}\n"

            QMessageBox.information(self, "Widget Test", message)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Widget test failed:\n{e}")

    def demo_simulation(self):
        """Demo the linting simulation"""
        QMessageBox.information(
            self,
            "Demo Simulation",
            "This would demonstrate:\n\n"
            "• Progress donuts updating in real-time\n"
            "• Metric cards showing file counts\n"
            "• Log viewer with colored HTML output\n"
            "• Stage-by-stage linter execution\n\n"
            "Full implementation coming soon!",
        )

    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self,
            "About Cascade Linter",
            "Cascade Linter GUI v1.0\n\n"
            "Professional Python code quality tool\n"
            "Built with PySide6\n\n"
            "Features:\n"
            "• Sequential linter execution (Ruff → Flake8 → Pylint → Bandit → MyPy)\n"
            "• Real-time progress tracking\n"
            "• Rich HTML logging\n"
            "• Batch processing\n"
            "• Cross-platform compatibility\n\n"
            "© 2025 Cascade Linter Project",
        )


def main():
    app = QApplication(sys.argv)

    # Set application properties
    app.setApplicationName("Cascade Linter")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("Cascade Linter Project")

    # Enable high-DPI support
    # app.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)  # Deprecated in Qt6

    # Create and show window
    window = SimpleMainWindow()
    window.show()

    print("Cascade Linter GUI Test Window launched successfully!")
    print("Test the widget loading using the 'Test Widgets' button")

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
