# cascade_linter/gui/widgets/MetricCard.py

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, Property
from PySide6.QtGui import QPainter, QColor, QPen, QFont


class MetricCard(QWidget):
    """
    A metric display card widget showing an icon, title, and numeric value.

    Features:
    - Clean card-like appearance with rounded corners
    - Icon + title at top, large numeric value below
    - Smooth animations when value changes
    - Customizable colors and styling
    - Follows Nielsen's heuristics for clear information display
    """

    def __init__(self, title="Metric", value=0, icon="📊", parent=None):
        super().__init__(parent)
        self.setFixedSize(200, 100)

        # Data
        self._title = title
        self._icon = icon
        self._value = value
        self._animated_value = float(value)

        # Animation
        self._animation = QPropertyAnimation(self, b"animatedValue")
        self._animation.setDuration(300)
        self._animation.setEasingCurve(QEasingCurve.Type.OutCubic)

        # Setup UI
        self.init_ui()
        self.apply_styling()

    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(4)

        # Top row: Icon + Title
        top_layout = QHBoxLayout()
        top_layout.setSpacing(8)

        # Icon label
        self.icon_label = QLabel(self._icon)
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon_label.setFixedSize(24, 24)
        self.icon_label.setStyleSheet(
            """
            QLabel {
                font-size: 16pt;
                background: none;
                border: none;
            }
        """
        )
        top_layout.addWidget(self.icon_label)

        # Title label
        self.title_label = QLabel(self._title)
        self.title_label.setAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        )
        self.title_label.setStyleSheet(
            """
            QLabel {
                font-size: 11pt;
                font-weight: bold;
                background: none;
                border: none;
            }
        """
        )
        top_layout.addWidget(self.title_label, stretch=1)

        layout.addLayout(top_layout)

        # Value label (large number)
        self.value_label = QLabel(str(self._value))
        self.value_label.setObjectName("metricValue")
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.value_label.setStyleSheet(
            """
            QLabel#metricValue {
                font-size: 24pt;
                font-weight: bold;
                background: none;
                border: none;
                margin-top: 4px;
            }
        """
        )
        layout.addWidget(self.value_label, stretch=1)

    def apply_styling(self):
        """Apply card-like styling that respects themes"""
        self.setStyleSheet(
            """
            MetricCard {
                border: 1px solid palette(mid);
                border-radius: 8px;
                background-color: palette(base);
            }
            MetricCard:hover {
                border: 2px solid palette(highlight);
                background-color: palette(alternate-base);
            }
        """
        )

    def set_loading_state(self, is_loading=True):
        """Set the card to show loading state instead of static zeros"""
        if is_loading:
            self.value_label.setText("...")
            self.value_label.setStyleSheet(
                """
                QLabel#metricValue {
                    font-size: 18pt;
                    font-weight: bold;
                    background: none;
                    border: none;
                    margin-top: 4px;
                    color: palette(mid);
                }
            """
            )
        else:
            # Restore normal styling
            self.value_label.setStyleSheet(
                """
                QLabel#metricValue {
                    font-size: 24pt;
                    font-weight: bold;
                    background: none;
                    border: none;
                    margin-top: 4px;
                }
            """
            )

    def set_value(self, value):
        """Set the metric value with smooth animation"""
        if value == self._value:
            return

        old_value = self._value
        self._value = value

        # Animate value change
        self._animation.setStartValue(float(old_value))
        self._animation.setEndValue(float(value))
        self._animation.start()

    def get_value(self):
        """Get the current metric value"""
        return self._value

    def set_title(self, title):
        """Set the metric title"""
        self._title = title
        self.title_label.setText(title)

    def get_title(self):
        """Get the metric title"""
        return self._title

    def set_icon(self, icon):
        """Set the metric icon"""
        self._icon = icon
        self.icon_label.setText(icon)

    def get_icon(self):
        """Get the metric icon"""
        return self._icon

    # Property for animation
    @Property(float)
    def animatedValue(self):
        return self._animated_value

    @animatedValue.setter
    def animatedValue(self, value):
        self._animated_value = value
        # Update display with animated value
        display_value = int(round(value))
        self.value_label.setText(str(display_value))

    def paintEvent(self, event):
        """Custom paint event for additional visual effects"""
        super().paintEvent(event)

        # Optional: Add subtle glow effect when hovered
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Check if widget is under mouse
        if self.underMouse():
            # Draw subtle glow
            glow_color = QColor(114, 159, 207, 30)  # Semi-transparent blue
            pen = QPen(glow_color, 2)
            painter.setPen(pen)
            painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 8, 8)

    def enterEvent(self, event):
        """Handle mouse enter for hover effects"""
        super().enterEvent(event)
        self.update()  # Trigger repaint for glow effect

    def leaveEvent(self, event):
        """Handle mouse leave for hover effects"""
        super().leaveEvent(event)
        self.update()  # Trigger repaint to remove glow

    def sizeHint(self):
        """Provide size hint for layout managers"""
        from PySide6.QtCore import QSize

        return QSize(200, 100)

    def minimumSizeHint(self):
        """Provide minimum size hint"""
        from PySide6.QtCore import QSize

        return QSize(150, 80)


# --- DEMO/TEST CODE ---

if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication, QHBoxLayout, QWidget
    from PySide6.QtCore import QTimer

    app = QApplication(sys.argv)

    # Create test window
    window = QWidget()
    window.setWindowTitle("MetricCard Demo")
    window.resize(700, 150)
    window.setStyleSheet(
        """
        QWidget {
            background-color: #2e3436;
            color: #eeeeec;
        }
    """
    )

    layout = QHBoxLayout(window)
    layout.setSpacing(20)
    layout.setContentsMargins(20, 20, 20, 20)

    # Create test cards
    card1 = MetricCard("Total Files", "📁")
    card2 = MetricCard("Issues Found", "⚠️")
    card3 = MetricCard("Auto-Fixed", "🔧")

    layout.addWidget(card1)
    layout.addWidget(card2)
    layout.addWidget(card3)

    # Animate values for demo
    def update_values():
        import random

        card1.set_value(random.randint(50, 200))
        card2.set_value(random.randint(0, 50))
        card3.set_value(random.randint(0, 20))

    # Update every 2 seconds
    timer = QTimer()
    timer.timeout.connect(update_values)
    timer.start(2000)

    # Initial values
    update_values()

    window.show()
    sys.exit(app.exec())
