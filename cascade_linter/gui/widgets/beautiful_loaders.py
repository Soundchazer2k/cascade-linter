# Beautiful Loaders - Pure PySide6 Implementation
# Cascade Linter GUI - Professional Loading Indicators
# No external dependencies - pure PySide6 animations

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PySide6.QtCore import (
    QTimer,
    Signal,
    QPropertyAnimation,
    QEasingCurve,
    QRect,
    QSequentialAnimationGroup,
)
from PySide6.QtGui import QFont, QPainter, QPen, QBrush, QColor
from PySide6.QtCore import Qt
import math
from typing import Optional


class BeautifulArcLoader(QWidget):
    """Beautiful arc-style loader using pure PySide6"""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setFixedSize(40, 40)
        self.angle = 0
        self.is_spinning = False

        # Animation timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_rotation)

    def start(self) -> None:
        """Start the loading animation"""
        self.is_spinning = True
        self.timer.start(50)  # Update every 50ms for smooth animation

    def stop(self) -> None:
        """Stop the loading animation"""
        self.is_spinning = False
        self.timer.stop()
        self.angle = 0
        self.update()

    def update_rotation(self) -> None:
        """Update the rotation angle"""
        self.angle = (self.angle + 10) % 360
        self.update()

    def paintEvent(self, event) -> None:
        """Paint the arc loader"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Setup pen
        pen = QPen(QColor("#2196F3"), 3)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)

        # Draw arc
        rect = QRect(5, 5, 30, 30)
        painter.drawArc(rect, self.angle * 16, 120 * 16)  # 120 degree arc


class BeautifulSpinner(QWidget):
    """Beautiful spinner using pure PySide6"""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setFixedSize(40, 40)
        self.rotation = 0
        self.is_spinning = False

        # Animation timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_rotation)

    def start(self) -> None:
        """Start the spinner animation"""
        self.is_spinning = True
        self.timer.start(100)  # Update every 100ms

    def stop(self) -> None:
        """Stop the spinner animation"""
        self.is_spinning = False
        self.timer.stop()
        self.rotation = 0
        self.update()

    def update_rotation(self) -> None:
        """Update the rotation"""
        self.rotation = (self.rotation + 30) % 360
        self.update()

    def paintEvent(self, event) -> None:
        """Paint the spinner"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Move to center
        painter.translate(20, 20)
        painter.rotate(self.rotation)

        # Draw spinner lines
        for i in range(8):
            opacity = 1.0 - (i * 0.1)
            color = QColor("#4CAF50")
            color.setAlphaF(opacity)

            pen = QPen(color, 2)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(pen)

            painter.drawLine(0, -15, 0, -10)
            painter.rotate(45)


class BeautifulDotsLoader(QWidget):
    """Beautiful three-dots loader using pure PySide6"""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setFixedSize(60, 20)
        self.dot_positions = [0, 0, 0]  # Y positions of dots
        self.is_animating = False

        # Animation timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_animation)
        self.animation_step = 0

    def start(self) -> None:
        """Start the dots animation"""
        self.is_animating = True
        self.timer.start(150)  # Update every 150ms

    def stop(self) -> None:
        """Stop the dots animation"""
        self.is_animating = False
        self.timer.stop()
        self.dot_positions = [0, 0, 0]
        self.animation_step = 0
        self.update()

    def update_animation(self) -> None:
        """Update the dots animation"""
        # Create wave effect
        for i in range(3):
            offset = (self.animation_step - i * 2) % 12
            if offset < 6:
                self.dot_positions[i] = int(5 * math.sin(offset * math.pi / 6))
            else:
                self.dot_positions[i] = 0

        self.animation_step += 1
        self.update()

    def paintEvent(self, event) -> None:
        """Paint the dots"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Draw three dots
        colors = ["#FF5722", "#FF9800", "#FFC107"]
        for i, color in enumerate(colors):
            brush = QBrush(QColor(color))
            painter.setBrush(brush)
            painter.setPen(Qt.PenStyle.NoPen)

            x = 15 + i * 15
            y = 10 + self.dot_positions[i]
            painter.drawEllipse(x - 3, y - 3, 6, 6)


class BeautifulLoadingWidget(QWidget):
    """
    Beautiful loading widget with multiple animation styles
    Pure PySide6 implementation - no external dependencies
    """

    loadingComplete = Signal()

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self) -> None:
        """Setup the beautiful loading widget UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)

        # Title
        title = QLabel("Beautiful Loading Indicators")
        title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        title.setStyleSheet("color: #E0E0E0; margin-bottom: 10px;")
        layout.addWidget(title)

        # Create different loading styles
        self.create_arc_loader(layout)
        self.create_spinner_loader(layout)
        self.create_dots_loader(layout)

    def create_arc_loader(self, layout: QVBoxLayout) -> None:
        """Create arc-style loader"""
        container = QWidget()
        container_layout = QHBoxLayout(container)

        # Label
        label = QLabel("Arc Loader:")
        label.setStyleSheet("color: #E0E0E0; min-width: 100px;")
        container_layout.addWidget(label)

        # Arc loader
        self.arc_loader = BeautifulArcLoader()
        container_layout.addWidget(self.arc_loader)

        container_layout.addStretch()
        layout.addWidget(container)

    def create_spinner_loader(self, layout: QVBoxLayout) -> None:
        """Create spinner-style loader"""
        container = QWidget()
        container_layout = QHBoxLayout(container)

        # Label
        label = QLabel("Spinner:")
        label.setStyleSheet("color: #E0E0E0; min-width: 100px;")
        container_layout.addWidget(label)

        # Spinner
        self.spinner = BeautifulSpinner()
        container_layout.addWidget(self.spinner)

        container_layout.addStretch()
        layout.addWidget(container)

    def create_dots_loader(self, layout: QVBoxLayout) -> None:
        """Create dots loader"""
        container = QWidget()
        container_layout = QHBoxLayout(container)

        # Label
        label = QLabel("3-Dots:")
        label.setStyleSheet("color: #E0E0E0; min-width: 100px;")
        container_layout.addWidget(label)

        # Dots loader
        self.dots_loader = BeautifulDotsLoader()
        container_layout.addWidget(self.dots_loader)

        container_layout.addStretch()
        layout.addWidget(container)

    def start_loading(self) -> None:
        """Start all loading animations"""
        self.arc_loader.start()
        self.spinner.start()
        self.dots_loader.start()

    def stop_loading(self) -> None:
        """Stop all loading animations"""
        self.arc_loader.stop()
        self.spinner.stop()
        self.dots_loader.stop()
        self.loadingComplete.emit()


class LinterStageLoader(QWidget):
    """
    Specialized loader for the 5-stage linter process
    Beautiful animations for each stage: Ruff → Flake8 → Pylint → Bandit → MyPy
    """

    stageCompleted = Signal(str)  # Emits stage name when complete

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.current_stage = 0
        self.stages = ["Ruff", "Flake8", "Pylint", "Bandit", "MyPy"]
        self.setup_ui()

    def setup_ui(self) -> None:
        """Setup the linter stage loader UI"""
        layout = QVBoxLayout(self)

        # Stage indicator
        self.stage_label = QLabel("Ready to start linting")
        self.stage_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        self.stage_label.setStyleSheet("color: #4CAF50; margin-bottom: 15px;")
        layout.addWidget(self.stage_label)

        # Loader container
        loader_container = QWidget()
        loader_layout = QHBoxLayout(loader_container)

        # Use beautiful spinner
        self.stage_loader = BeautifulSpinner()
        loader_layout.addWidget(self.stage_loader)

        loader_layout.addStretch()
        layout.addWidget(loader_container)

    def start_stage(self, stage_name: str) -> None:
        """Start a specific linting stage"""
        self.stage_label.setText(f"Running {stage_name}...")
        self.stage_label.setStyleSheet("color: #2196F3; margin-bottom: 15px;")
        self.stage_loader.start()

    def complete_stage(self, stage_name: str) -> None:
        """Mark a stage as complete"""
        self.stage_label.setText(f"✓ {stage_name} completed")
        self.stage_label.setStyleSheet("color: #4CAF50; margin-bottom: 15px;")
        self.stage_loader.stop()
        self.stageCompleted.emit(stage_name)

    def start_next_stage(self) -> None:
        """Move to the next linting stage"""
        if self.current_stage < len(self.stages):
            stage_name = self.stages[self.current_stage]
            self.start_stage(stage_name)
            self.current_stage += 1
        else:
            self.complete_all_stages()

    def complete_all_stages(self) -> None:
        """Mark all linting stages as complete"""
        self.stage_label.setText("🎉 All linting stages completed!")
        self.stage_label.setStyleSheet("color: #4CAF50; margin-bottom: 15px;")
        self.stage_loader.stop()

    def reset(self) -> None:
        """Reset the loader to initial state"""
        self.current_stage = 0
        self.stage_label.setText("Ready to start linting")
        self.stage_label.setStyleSheet("color: #4CAF50; margin-bottom: 15px;")
        self.stage_loader.stop()


# Export the widgets for use in main application
__all__ = [
    "BeautifulLoadingWidget",
    "LinterStageLoader",
    "BeautifulArcLoader",
    "BeautifulSpinner",
    "BeautifulDotsLoader",
]
