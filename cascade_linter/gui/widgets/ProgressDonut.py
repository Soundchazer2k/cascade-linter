# cascade_linter/gui/widgets/ProgressDonut.py

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, Property, QTimer
from PySide6.QtGui import QPainter, QColor, QPen, QFont, QBrush
import math


class ProgressDonut(QWidget):
    """
    A circular progress donut widget for showing linter stage progress.

    Features:
    - Circular progress indicator with smooth animations
    - Custom colors and styling
    - Stage label centered in the donut
    - Smooth progress transitions with easing curves
    - Professional appearance matching the dark theme
    - Follows Nielsen's heuristics for clear progress indication
    """

    def __init__(self, title="Stage", parent=None):
        super().__init__(parent)
        self.setFixedSize(80, 80)

        # Data
        self._title = title
        self._progress = 0
        self._animated_progress = 0.0

        # Colors (matching dark theme)
        self._background_color = QColor("#555753")
        self._progress_color = QColor("#729fcf")  # Blue accent
        self._text_color = QColor("#eeeeec")
        self._border_color = QColor("#888a85")

        # Animation
        self._animation = QPropertyAnimation(self, b"animatedProgress")
        self._animation.setDuration(500)  # Slightly longer for smooth feel
        self._animation.setEasingCurve(QEasingCurve.Type.OutCubic)

        # Setup UI
        self.init_ui()
        self.apply_styling()

    def init_ui(self):
        """Initialize the user interface"""
        # We'll draw everything in paintEvent, so just set up the layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)

        # Optional: Add a tooltip
        self.setToolTip(f"{self._title} linter progress")

    def apply_styling(self):
        """Apply styling for hover effects"""
        self.setStyleSheet(
            """
            ProgressDonut {
                background: transparent;
            }
            ProgressDonut:hover {
                background: rgba(114, 159, 207, 0.1);
                border-radius: 40px;
            }
        """
        )

    def set_progress(self, progress):
        """Set the progress value with smooth animation (0-100)"""
        progress = max(0, min(100, progress))  # Clamp to 0-100

        if progress == self._progress:
            return

        old_progress = self._progress
        self._progress = progress

        # Animate progress change
        self._animation.setStartValue(float(old_progress))
        self._animation.setEndValue(float(progress))
        self._animation.start()

    def get_progress(self):
        """Get the current progress value"""
        return self._progress

    def set_title(self, title):
        """Set the donut title"""
        self._title = title
        self.setToolTip(f"{self._title} linter progress")
        self.update()

    def get_title(self):
        """Get the donut title"""
        return self._title

    def set_colors(self, background=None, progress=None, text=None, border=None):
        """Set custom colors for the donut"""
        if background:
            self._background_color = QColor(background)
        if progress:
            self._progress_color = QColor(progress)
        if text:
            self._text_color = QColor(text)
        if border:
            self._border_color = QColor(border)
        self.update()

    # Property for animation
    @Property(float)
    def animatedProgress(self):
        return self._animated_progress

    @animatedProgress.setter
    def animatedProgress(self, value):
        self._animated_progress = value
        self.update()  # Trigger repaint

    def paintEvent(self, event):
        """Custom paint event to draw the donut"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Get the square area for the donut
        rect = self.rect()
        size = min(rect.width(), rect.height()) - 8  # Leave margin
        x = (rect.width() - size) // 2
        y = (rect.height() - size) // 2
        donut_rect = rect.adjusted(x, y, -x, -y)

        # Draw background circle
        painter.setPen(QPen(self._border_color, 2))
        painter.setBrush(QBrush(self._background_color))
        painter.drawEllipse(donut_rect)

        # Draw progress arc
        if self._animated_progress > 0:
            # Calculate the arc span (360 degrees = full circle)
            span_angle = int(
                (self._animated_progress / 100.0) * 360 * 16
            )  # Qt uses 16ths of degrees

            # Create progress color with slight transparency for better appearance
            progress_color = QColor(self._progress_color)
            progress_color.setAlpha(220)

            # Draw the progress arc
            painter.setPen(QPen(progress_color, 3))
            painter.setBrush(QBrush(progress_color))

            # Start from top (-90 degrees) and go clockwise
            start_angle = -90 * 16  # Top of circle
            painter.drawPie(donut_rect, start_angle, span_angle)

        # Draw inner circle to create donut effect
        inner_margin = 15
        inner_rect = donut_rect.adjusted(
            inner_margin, inner_margin, -inner_margin, -inner_margin
        )
        painter.setPen(QPen(self._background_color, 1))
        painter.setBrush(QBrush(QColor("#2e3436")))  # Match main window background
        painter.drawEllipse(inner_rect)

        # Draw title text in center
        painter.setPen(QPen(self._text_color))
        font = QFont("Segoe UI", 7, QFont.Weight.Bold)  # Slightly larger font
        painter.setFont(font)

        # Calculate text position - move title up slightly to make room for percentage
        title_rect = inner_rect.adjusted(0, -6, 0, -6)  # Move up
        painter.drawText(title_rect, Qt.AlignmentFlag.AlignCenter, self._title)

        # Draw percentage text below title with better visibility
        # Always show percentage, even when 0
        percentage_text = f"{int(self._animated_progress)}%"

        # Use larger, bold font for percentage
        font_percent = QFont("Segoe UI", 8, QFont.Weight.Bold)
        painter.setFont(font_percent)

        # Use progress color when active, dimmed text color when at 0
        if self._animated_progress > 0:
            bright_color = QColor(self._progress_color)
            bright_color.setAlpha(255)  # Full opacity
            painter.setPen(QPen(bright_color))
        else:
            # Use dimmed text color for 0%
            dim_color = QColor(self._text_color)
            dim_color.setAlpha(150)  # Slightly dimmed
            painter.setPen(QPen(dim_color))

        # Position percentage below title
        percent_rect = inner_rect.adjusted(0, 6, 0, 6)  # Move down
        painter.drawText(percent_rect, Qt.AlignmentFlag.AlignCenter, percentage_text)

    def sizeHint(self):
        """Provide size hint for layout managers"""
        from PySide6.QtCore import QSize

        return QSize(80, 80)

    def minimumSizeHint(self):
        """Provide minimum size hint"""
        from PySide6.QtCore import QSize

        return QSize(60, 60)

    def enterEvent(self, event):
        """Handle mouse enter for hover effects"""
        super().enterEvent(event)
        self.update()  # Trigger repaint for hover effect

    def leaveEvent(self, event):
        """Handle mouse leave for hover effects"""
        super().leaveEvent(event)
        self.update()  # Trigger repaint to remove hover

    def reset(self):
        """Reset progress to 0"""
        self.set_progress(0)

    def complete(self):
        """Set progress to 100%"""
        self.set_progress(100)


# --- DEMO/TEST CODE ---

if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import (
        QApplication,
        QHBoxLayout,
        QVBoxLayout,
        QWidget,
        QPushButton,
    )
    from PySide6.QtCore import QTimer

    app = QApplication(sys.argv)

    # Create test window
    window = QWidget()
    window.setWindowTitle("ProgressDonut Demo")
    window.resize(500, 200)
    window.setStyleSheet(
        """
        QWidget {
            background-color: #2e3436;
            color: #eeeeec;
        }
    """
    )

    main_layout = QVBoxLayout(window)
    main_layout.setContentsMargins(20, 20, 20, 20)

    # Create test donuts
    donut_layout = QHBoxLayout()
    donut_layout.setSpacing(20)

    donut1 = ProgressDonut("Ruff")
    donut2 = ProgressDonut("Flake8")
    donut3 = ProgressDonut("Pylint")
    donut4 = ProgressDonut("Bandit")
    donut5 = ProgressDonut("MyPy")

    donuts = [donut1, donut2, donut3, donut4, donut5]

    for donut in donuts:
        donut_layout.addWidget(donut)

    main_layout.addLayout(donut_layout)

    # Create control buttons
    button_layout = QHBoxLayout()

    def simulate_progress():
        """Simulate progressive linting"""
        import random

        for i, donut in enumerate(donuts):
            # Stagger the progress updates
            def set_progress(d=donut, delay=i * 500):
                QTimer.singleShot(
                    delay, lambda d=d: d.set_progress(random.randint(0, 100))
                )

            set_progress()

    def reset_progress():
        """Reset all donuts to 0"""
        for donut in donuts:
            donut.set_progress(0)

    def complete_all():
        """Set all donuts to 100%"""
        for donut in donuts:
            donut.set_progress(100)

    simulate_btn = QPushButton("Simulate Progress")
    simulate_btn.clicked.connect(simulate_progress)
    button_layout.addWidget(simulate_btn)

    reset_btn = QPushButton("Reset All")
    reset_btn.clicked.connect(reset_progress)
    button_layout.addWidget(reset_btn)

    complete_btn = QPushButton("Complete All")
    complete_btn.clicked.connect(complete_all)
    button_layout.addWidget(complete_btn)

    main_layout.addLayout(button_layout)

    # Auto-demo timer
    demo_timer = QTimer()
    demo_timer.timeout.connect(simulate_progress)
    demo_timer.start(3000)  # Auto-simulate every 3 seconds

    window.show()
    sys.exit(app.exec())
