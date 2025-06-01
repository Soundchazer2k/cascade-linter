# cascade_linter/gui/widgets/ProgressDonut.py
"""
ProgressDonut Widget for Cascade Linter GUI

A circular progress indicator with custom painting for linter stage progress.
Follows Nielsen's heuristics for clear system status visibility.

Usage:
    from cascade_linter.gui.widgets.ProgressDonut import ProgressDonut
    
    donut = ProgressDonut("Ruff")
    donut.set_progress(75)  # 75% complete
    donut.set_status("running")  # running, completed, error, pending
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, Property
from PySide6.QtGui import QPainter, QPen, QBrush, QColor, QFont, QFontMetrics
import math
from typing import Optional


class ProgressDonut(QWidget):
    """
    A circular progress widget for displaying linter stage progress.
    
    Features:
    - Animated progress changes
    - Color-coded status (pending, running, completed, error)
    - Clean typography with stage name
    - Responsive sizing
    - Smooth animations
    """
    
    def __init__(self, stage_name: str, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        self.stage_name = stage_name
        self._progress = 0  # 0-100
        self._animated_progress = 0  # For smooth animation
        self.status = "pending"  # pending, running, completed, error
        self.show_percentage = True
        
        self._init_ui()
        self._setup_animation()
    
    def _init_ui(self):
        """Initialize the user interface."""
        self.setFixedSize(100, 120)  # Slightly taller to accommodate label
        self.setObjectName("ProgressDonut")
        
        # Layout for stage name label
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        
        # Add stretch to push label to bottom
        layout.addStretch()
        
        # Stage name label
        self.stage_label = QLabel(self.stage_name)
        self.stage_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.stage_label.setObjectName("stageLabel")
        self.stage_label.setStyleSheet("""
            QLabel#stageLabel {
                color: #E0E0E0;
                font-size: 10px;
                font-weight: normal;
                background: transparent;
            }
        """)
        layout.addWidget(self.stage_label)
    
    def _setup_animation(self):
        """Set up smooth progress animation."""
        self.animation = QPropertyAnimation(self, b"animatedProgress")
        self.animation.setDuration(300)  # 300ms animation
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)
    
    def get_animatedProgress(self):
        """Get animated progress value."""
        return self._animated_progress
    
    def set_animatedProgress(self, value):
        """Set animated progress value and trigger repaint."""
        self._animated_progress = value
        self.update()
    
    # Property for animation
    animatedProgress = Property(float, get_animatedProgress, set_animatedProgress)
    
    def set_progress(self, progress: int):
        """
        Set progress value with smooth animation.
        
        Args:
            progress: Progress value (0-100)
        """
        progress = max(0, min(100, progress))  # Clamp to 0-100
        
        if progress != self._progress:
            self._progress = progress
            
            # Animate to new progress value
            self.animation.setStartValue(self._animated_progress)
            self.animation.setEndValue(progress)
            self.animation.start()
            
            # Update tooltip
            self.setToolTip(f"{self.stage_name}: {progress}%")
    
    def set_status(self, status: str):
        """
        Set the status which affects the visual styling.
        
        Args:
            status: Status string - 'pending', 'running', 'completed', 'error'
        """
        self.status = status
        self.update()  # Trigger repaint with new colors
        
        # Update tooltip based on status
        status_text = {
            "pending": "Waiting to start",
            "running": f"Running... {self._progress}%",
            "completed": "Completed successfully",
            "error": "Error occurred"
        }.get(status, status)
        
        self.setToolTip(f"{self.stage_name}: {status_text}")
    
    def get_status_color(self):
        """Get the color for current status."""
        status_colors = {
            "pending": QColor("#555753"),      # Gray
            "running": QColor("#357ABD"),      # Blue
            "completed": QColor("#50FA7B"),    # Green
            "error": QColor("#FF5555")         # Red
        }
        return status_colors.get(self.status, QColor("#555753"))
    
    def get_background_color(self):
        """Get the background track color."""
        if self.status == "error":
            return QColor("#331111")  # Dark red tint
        elif self.status == "completed":
            return QColor("#113311")  # Dark green tint
        else:
            return QColor("#2e3436")  # Default dark gray
    
    def paintEvent(self, event):
        """Custom paint event to draw the circular progress."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Get colors
        fg_color = self.get_status_color()
        bg_color = self.get_background_color()
        
        # Calculate dimensions
        size = min(self.width(), self.height() - 30)  # Leave space for label
        x = (self.width() - size) // 2
        y = 5  # Small top margin
        
        # Pen settings
        pen_width = 8
        radius = (size - pen_width) // 2
        center_x = x + size // 2
        center_y = y + size // 2
        
        # Draw background circle (track)
        painter.setPen(QPen(bg_color, pen_width, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(center_x - radius, center_y - radius, radius * 2, radius * 2)
        
        # Draw progress arc
        if self._animated_progress > 0:
            painter.setPen(QPen(fg_color, pen_width, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            
            # Calculate arc span (progress as angle)
            start_angle = -90 * 16  # Start at top (12 o'clock), Qt uses 1/16th degree
            span_angle = int((self._animated_progress / 100) * 360 * 16)
            
            painter.drawArc(center_x - radius, center_y - radius, radius * 2, radius * 2, 
                          start_angle, span_angle)
        
        # Draw center text (percentage or status icon)
        if self.show_percentage and self.status in ["running", "completed"]:
            painter.setPen(QPen(QColor("#FFFFFF"), 1))
            
            # Draw percentage text
            if self._progress < 100:
                text = f"{int(self._animated_progress)}%"
                font = QFont()
                font.setPointSize(12)
                font.setBold(True)
            else:
                text = "✓"  # Checkmark for completed
                font = QFont()
                font.setPointSize(20)
                font.setBold(True)
            
            painter.setFont(font)
            
            # Center the text
            fm = QFontMetrics(font)
            text_width = fm.horizontalAdvance(text)
            text_height = fm.height()
            
            text_x = center_x - text_width // 2
            text_y = center_y + text_height // 4  # Slight vertical adjustment
            
            painter.drawText(text_x, text_y, text)
        
        elif self.status == "error":
            # Draw error symbol
            painter.setPen(QPen(QColor("#FF5555"), 3))
            painter.setFont(QFont("Arial", 16, QFont.Weight.Bold))
            painter.drawText(center_x - 8, center_y + 6, "✗")
        
        elif self.status == "pending":
            # Draw pending symbol (clock or dash)
            painter.setPen(QPen(QColor("#888888"), 2))
            painter.setFont(QFont("Arial", 14))
            painter.drawText(center_x - 6, center_y + 5, "—")
        
        super().paintEvent(event)
    
    def reset(self):
        """Reset progress to 0 and status to pending."""
        self.set_progress(0)
        self.set_status("pending")
    
    def complete(self):
        """Mark as completed (100% progress)."""
        self.set_progress(100)
        self.set_status("completed")
    
    def error(self):
        """Mark as error state."""
        self.set_status("error")
    
    def start(self):
        """Mark as started/running."""
        self.set_status("running")


if __name__ == "__main__":
    # Simple test of ProgressDonut
    import sys
    from PySide6.QtWidgets import QApplication, QHBoxLayout, QWidget, QPushButton, QVBoxLayout
    
    app = QApplication(sys.argv)
    
    # Test window
    window = QWidget()
    window.setWindowTitle("ProgressDonut Test")
    window.resize(600, 200)
    
    main_layout = QVBoxLayout(window)
    
    # Donuts layout
    donuts_layout = QHBoxLayout()
    
    # Create sample donuts
    donut1 = ProgressDonut("Ruff")
    donut1.set_progress(100)
    donut1.set_status("completed")
    
    donut2 = ProgressDonut("Flake8")
    donut2.set_progress(75)
    donut2.set_status("running")
    
    donut3 = ProgressDonut("Pylint")
    donut3.set_progress(30)
    donut3.set_status("error")
    
    donut4 = ProgressDonut("Bandit")
    donut4.set_progress(0)
    donut4.set_status("pending")
    
    donut5 = ProgressDonut("MyPy")
    donut5.set_progress(0)
    donut5.set_status("pending")
    
    donuts_layout.addWidget(donut1)
    donuts_layout.addWidget(donut2)
    donuts_layout.addWidget(donut3)
    donuts_layout.addWidget(donut4)
    donuts_layout.addWidget(donut5)
    donuts_layout.addStretch()
    
    main_layout.addLayout(donuts_layout)
    
    # Test buttons
    buttons_layout = QHBoxLayout()
    
    def test_progress():
        donut2.set_progress(85)
        donut3.set_progress(50)
        donut4.set_progress(25)
        donut4.set_status("running")
    
    def test_complete():
        donut2.complete()
        donut3.complete()
        donut4.complete()
        donut5.complete()
    
    def test_reset():
        for donut in [donut1, donut2, donut3, donut4, donut5]:
            donut.reset()
    
    btn_progress = QPushButton("Update Progress")
    btn_progress.clicked.connect(test_progress)
    
    btn_complete = QPushButton("Complete All")
    btn_complete.clicked.connect(test_complete)
    
    btn_reset = QPushButton("Reset All")
    btn_reset.clicked.connect(test_reset)
    
    buttons_layout.addWidget(btn_progress)
    buttons_layout.addWidget(btn_complete)
    buttons_layout.addWidget(btn_reset)
    buttons_layout.addStretch()
    
    main_layout.addLayout(buttons_layout)
    
    # Apply dark theme for testing
    app.setStyleSheet("""
        QWidget {
            background-color: #121212;
            color: #E0E0E0;
        }
        QPushButton {
            background-color: #357ABD;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
        }
        QPushButton:hover {
            background-color: #4A90E2;
        }
    """)
    
    window.show()
    sys.exit(app.exec())
