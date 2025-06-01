#!/usr/bin/env python3
"""
Results Dashboard Widget - Beautiful metrics and visual feedback
FIXED: PySide6 compatible (removed pyqtProperty)
"""

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QFrame,
    QGroupBox,
)
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, Property
from PySide6.QtGui import QPainter, QColor, QFont, QPen
from typing import Dict


class MetricCard(QFrame):
    """Beautiful metric display card"""

    def __init__(
        self, title: str, value: str, icon: str = "📊", color: str = "#3498db"
    ):
        super().__init__()
        self.setFrameStyle(QFrame.StyledPanel)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {color}20;
                border: 2px solid {color};
                border-radius: 8px;
                padding: 12px;
                margin: 4px;
            }}
        """)

        layout = QVBoxLayout(self)

        # Icon and title
        header_layout = QHBoxLayout()

        icon_label = QLabel(icon)
        icon_label.setFont(QFont("", 20))
        header_layout.addWidget(icon_label)

        title_label = QLabel(title)
        title_label.setFont(QFont("", 10, QFont.Bold))
        title_label.setStyleSheet("color: gray;")
        header_layout.addWidget(title_label)
        header_layout.addStretch()

        layout.addLayout(header_layout)

        # Value
        self.value_label = QLabel(value)
        self.value_label.setFont(QFont("", 24, QFont.Bold))
        self.value_label.setStyleSheet(f"color: {color};")
        layout.addWidget(self.value_label)

    def update_value(self, value: str):
        """Update the displayed value"""
        self.value_label.setText(value)


class CircularProgressWidget(QWidget):
    """Animated circular progress indicator - FIXED for PySide6"""

    def __init__(self, size: int = 100):
        super().__init__()
        self.setFixedSize(size, size)
        self._progress = 0
        self.max_progress = 100
        self.color = QColor("#3498db")

        # Animation - FIXED: Use Property instead of pyqtProperty
        self.animation = QPropertyAnimation(self, b"progress")
        self.animation.setDuration(1000)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)

    def get_progress(self):
        return self._progress

    def set_progress(self, value):
        self._progress = value
        self.update()

    # FIXED: Use Property for PySide6
    progress = Property(int, get_progress, set_progress)

    def animate_to_progress(self, value: int):
        """Set progress with animation"""
        self.animation.setStartValue(self._progress)
        self.animation.setEndValue(value)
        self.animation.start()

    def paintEvent(self, event):
        """Custom paint for circular progress"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Background circle
        painter.setPen(QPen(QColor("#ecf0f1"), 8))
        painter.drawEllipse(10, 10, self.width() - 20, self.height() - 20)

        # Progress arc
        painter.setPen(QPen(self.color, 8))
        start_angle = 90 * 16  # Start from top
        span_angle = -(self._progress / self.max_progress) * 360 * 16
        painter.drawArc(
            10, 10, self.width() - 20, self.height() - 20, start_angle, span_angle
        )

        # Progress text
        painter.setPen(QPen(QColor("#2c3e50")))
        painter.setFont(QFont("", 12, QFont.Bold))
        painter.drawText(self.rect(), Qt.AlignCenter, f"{self._progress}%")


class ResultsDashboard(QWidget):
    """Beautiful results dashboard with metrics and charts"""

    def __init__(self):
        super().__init__()
        self._setup_ui()

    def _setup_ui(self):
        """Set up the dashboard UI"""
        layout = QVBoxLayout(self)

        # Title
        title = QLabel("📊 Linting Results Dashboard")
        title.setFont(QFont("", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("margin: 10px; color: #2c3e50;")
        layout.addWidget(title)

        # Metrics grid
        metrics_group = QGroupBox("📈 Summary Metrics")
        metrics_layout = QGridLayout(metrics_group)

        # Create metric cards
        self.total_files_card = MetricCard("Total Files", "0", "📁", "#3498db")
        self.issues_found_card = MetricCard("Issues Found", "0", "🔍", "#e74c3c")
        self.fixed_issues_card = MetricCard("Auto-Fixed", "0", "🔧", "#27ae60")
        self.time_taken_card = MetricCard("Time Taken", "0.0s", "⏱️", "#f39c12")

        metrics_layout.addWidget(self.total_files_card, 0, 0)
        metrics_layout.addWidget(self.issues_found_card, 0, 1)
        metrics_layout.addWidget(self.fixed_issues_card, 1, 0)
        metrics_layout.addWidget(self.time_taken_card, 1, 1)

        layout.addWidget(metrics_group)

        # Progress indicators
        progress_group = QGroupBox("🎯 Linting Stage Progress")
        progress_layout = QHBoxLayout(progress_group)

        self.stage_indicators = {}
        stages = [
            ("ruff", "🚀 Ruff", "#3498db"),
            ("flake8", "🔍 Flake8", "#f39c12"),
            ("pylint", "🧠 Pylint", "#27ae60"),
            ("bandit", "🛡️ Bandit", "#e74c3c"),
            ("mypy", "🎯 MyPy", "#9b59b6"),
        ]

        for stage_id, stage_name, color in stages:
            stage_widget = QWidget()
            stage_layout = QVBoxLayout(stage_widget)

            # Circular progress
            progress = CircularProgressWidget(80)
            progress.color = QColor(color)
            stage_layout.addWidget(progress, alignment=Qt.AlignCenter)

            # Stage name
            name_label = QLabel(stage_name)
            name_label.setAlignment(Qt.AlignCenter)
            name_label.setFont(QFont("", 9))
            stage_layout.addWidget(name_label)

            self.stage_indicators[stage_id] = progress
            progress_layout.addWidget(stage_widget)

        layout.addWidget(progress_group)

        # Add stretch to push everything to top
        layout.addStretch()

    def update_dashboard(self, session_data: Dict):
        """Update dashboard with linting session data"""
        # Update metric cards
        self.total_files_card.update_value(str(session_data.get("total_files", 0)))
        self.issues_found_card.update_value(str(session_data.get("total_issues", 0)))
        self.fixed_issues_card.update_value(str(session_data.get("fixed_issues", 0)))
        self.time_taken_card.update_value(f"{session_data.get('total_time', 0):.1f}s")

        # Update stage progress with animation
        for stage_id, progress_widget in self.stage_indicators.items():
            if stage_id in session_data.get("stage_results", {}):
                # Determine progress based on success/failure
                stage_result = session_data["stage_results"][stage_id]
                progress = 100 if stage_result else 50  # 100% if passed, 50% if failed
                progress_widget.animate_to_progress(progress)
            else:
                progress_widget.animate_to_progress(0)  # Not run yet

    def reset_dashboard(self):
        """Reset dashboard to initial state"""
        self.total_files_card.update_value("0")
        self.issues_found_card.update_value("0")
        self.fixed_issues_card.update_value("0")
        self.time_taken_card.update_value("0.0s")

        # Reset all progress indicators
        for progress_widget in self.stage_indicators.values():
            progress_widget.animate_to_progress(0)
