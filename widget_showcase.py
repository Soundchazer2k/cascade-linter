#!/usr/bin/env python3
"""
Widget Showcase - Clean Demo
============================

Professional demonstration of MetricCard and ProgressDonut widgets
without any debug artifacts or ugly styling.

Features:
- Clean transparent backgrounds
- Proper text rendering
- Beautiful rounded corners
- Smooth hover effects
- Professional color scheme
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont

# Import our custom widgets
from cascade_linter.gui.widgets.MetricCard import MetricCard
from cascade_linter.gui.widgets.ProgressDonut import ProgressDonut


class WidgetShowcase(QMainWindow):
    """Clean showcase of our custom widgets."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cascade Linter Dashboard - Widget Showcase")
        self.setGeometry(200, 200, 1000, 600)

        # Apply clean dark theme
        self.setStyleSheet(
            """
            QMainWindow {
                background-color: #1a1a1a;
                color: #E0E0E0;
            }
            QWidget {
                background-color: transparent;
                color: #E0E0E0;
            }
            QLabel {
                color: #E0E0E0;
            }
            QPushButton {
                background-color: #357ABD;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 11pt;
            }
            QPushButton:hover {
                background-color: #4A90E2;
            }
            QPushButton:pressed {
                background-color: #285F8D;
            }
            QFrame {
                background-color: #2a2a2a;
                border: 1px solid #404040;
                border-radius: 12px;
                margin: 8px;
                padding: 16px;
            }
        """
        )

        self.init_ui()

    def init_ui(self):
        """Initialize the user interface."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # Header
        header = QLabel("Cascade Linter Dashboard")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setStyleSheet(
            """
            QLabel {
                font-size: 28pt;
                font-weight: bold;
                color: #4DD0E1;
                margin-bottom: 10px;
            }
        """
        )
        main_layout.addWidget(header)

        subtitle = QLabel("MetricCard + ProgressDonut Widget Integration")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet(
            """
            QLabel {
                font-size: 14pt;
                color: #A0A0A0;
                margin-bottom: 20px;
            }
        """
        )
        main_layout.addWidget(subtitle)

        # Metrics Section
        metrics_frame = QFrame()
        main_layout.addWidget(metrics_frame)

        metrics_layout = QVBoxLayout(metrics_frame)

        metrics_title = QLabel("📊 Linting Results Summary")
        metrics_title.setStyleSheet(
            "font-size: 16pt; font-weight: bold; color: #FFFFFF; margin-bottom: 12px;"
        )
        metrics_layout.addWidget(metrics_title)

        # MetricCards Row
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(20)

        # Create metric cards with clear values
        self.card_total = MetricCard("Total Files", "📁")
        self.card_total.set_value(142)

        self.card_issues = MetricCard("Issues Found", "⚠️")
        self.card_issues.set_value(28)
        self.card_issues.set_card_type("warning")

        self.card_fixed = MetricCard("Auto-Fixed", "🔧")
        self.card_fixed.set_value(15)
        self.card_fixed.set_card_type("success")

        self.card_manual = MetricCard("Manual Review", "👁️")
        self.card_manual.set_value(12)
        self.card_manual.set_card_type("error")

        cards_layout.addWidget(self.card_total)
        cards_layout.addWidget(self.card_issues)
        cards_layout.addWidget(self.card_fixed)
        cards_layout.addWidget(self.card_manual)
        cards_layout.addStretch()

        metrics_layout.addLayout(cards_layout)

        # Progress Section
        progress_frame = QFrame()
        main_layout.addWidget(progress_frame)

        progress_layout = QVBoxLayout(progress_frame)

        progress_title = QLabel("⚡ Linting Stages Progress")
        progress_title.setStyleSheet(
            "font-size: 16pt; font-weight: bold; color: #FFFFFF; margin-bottom: 12px;"
        )
        progress_layout.addWidget(progress_title)

        # ProgressDonuts Row
        donuts_layout = QHBoxLayout()
        donuts_layout.setSpacing(30)

        # Create progress donuts with different completion levels
        self.donut_ruff = ProgressDonut("Ruff")
        self.donut_ruff.set_progress(100)

        self.donut_flake = ProgressDonut("Flake8")
        self.donut_flake.set_progress(75)

        self.donut_pylint = ProgressDonut("Pylint")
        self.donut_pylint.set_progress(50)

        self.donut_bandit = ProgressDonut("Bandit")
        self.donut_bandit.set_progress(90)

        self.donut_mypy = ProgressDonut("MyPy")
        self.donut_mypy.set_progress(65)

        donuts_layout.addWidget(self.donut_ruff)
        donuts_layout.addWidget(self.donut_flake)
        donuts_layout.addWidget(self.donut_pylint)
        donuts_layout.addWidget(self.donut_bandit)
        donuts_layout.addWidget(self.donut_mypy)
        donuts_layout.addStretch()

        progress_layout.addLayout(donuts_layout)

        # Controls
        controls_layout = QHBoxLayout()
        controls_layout.setContentsMargins(0, 20, 0, 0)

        demo_btn = QPushButton("🚀 Full Linting Demo")
        demo_btn.clicked.connect(self.run_demo_animation)
        controls_layout.addWidget(demo_btn)

        metrics_btn = QPushButton("📊 Test Metrics Only")
        metrics_btn.clicked.connect(self.test_metrics_only)
        controls_layout.addWidget(metrics_btn)

        progress_btn = QPushButton("⚡ Test Progress Only")
        progress_btn.clicked.connect(self.test_progress_only)
        controls_layout.addWidget(progress_btn)

        reset_btn = QPushButton("🔄 Reset All")
        reset_btn.clicked.connect(self.reset_all)
        controls_layout.addWidget(reset_btn)

        controls_layout.addStretch()

        main_layout.addLayout(controls_layout)

        # Status
        self.status_label = QLabel("Progress test complete!")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet(
            """
            QLabel {
                font-size: 12pt;
                color: #A0A0A0;
                margin-top: 10px;
            }
        """
        )
        main_layout.addWidget(self.status_label)

    def run_demo_animation(self):
        """Run a full demonstration with both metrics and progress."""
        self.status_label.setText("🚀 Running full linting demonstration...")

        # Reset first
        self.reset_all(silent=True)

        # Animate metrics
        QTimer.singleShot(500, lambda: self.card_total.set_value(142))
        QTimer.singleShot(800, lambda: self.card_issues.set_value(28))
        QTimer.singleShot(1100, lambda: self.card_fixed.set_value(15))
        QTimer.singleShot(1400, lambda: self.card_manual.set_value(12))

        # Animate progress
        QTimer.singleShot(2000, lambda: self.donut_ruff.set_progress(100))
        QTimer.singleShot(2500, lambda: self.donut_flake.set_progress(75))
        QTimer.singleShot(3000, lambda: self.donut_pylint.set_progress(50))
        QTimer.singleShot(3500, lambda: self.donut_bandit.set_progress(90))
        QTimer.singleShot(4000, lambda: self.donut_mypy.set_progress(65))

        QTimer.singleShot(
            4500,
            lambda: self.status_label.setText(
                "✅ Linting complete! Found 28 issues, auto-fixed 15."
            ),
        )

    def test_metrics_only(self):
        """Test only the MetricCard widgets."""
        self.status_label.setText("📊 Testing MetricCard widgets...")

        # Set specific
