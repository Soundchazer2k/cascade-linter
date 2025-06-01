# cascade_linter/gui/widgets/MetricCard.py
"""
MetricCard Widget for Cascade Linter GUI

A modern card widget displaying metrics with icon, label, and value.
Follows Nielsen's heuristics for clear information hierarchy and recognition.

Usage:
    from cascade_linter.gui.widgets.MetricCard import MetricCard
    
    card = MetricCard("Total Files", "fa5s.folder")
    card.set_value(42)
    card.set_subtitle("Python files")
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QRect
from PySide6.QtGui import QPainter, QPen, QBrush, QColor, QFont
from typing import Optional


class MetricCard(QWidget):
    """
    A card widget for displaying key metrics with visual hierarchy.
    
    Features:
    - Icon + title + value layout
    - Rounded corners with subtle shadow
    - Animated value changes
    - Customizable colors for different metric types
    - Responsive text sizing
    """
    
    def __init__(self, title: str, icon_name: str = "", parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        self.title = title
        self.icon_name = icon_name
        self.current_value = 0
        self.target_value = 0
        self.subtitle = ""
        self.card_type = "default"  # default, success, warning, error
        
        self._init_ui()
        self._setup_animations()
        self._apply_styling()
    
    def _init_ui(self):
        """Initialize the user interface layout."""
        self.setFixedSize(180, 100)
        self.setObjectName("MetricCard")
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(4)
        
        # Top row: Icon + Title
        top_layout = QHBoxLayout()
        top_layout.setContentsMargins(0, 0, 0, 0)
        
        # Icon (placeholder - we'll use text for now since QtAwesome requires setup)
        self.icon_label = QLabel("📊")  # Default icon
        self.icon_label.setFixedSize(20, 20)
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon_label.setObjectName("cardIcon")
        top_layout.addWidget(self.icon_label)
        
        # Title
        self.title_label = QLabel(self.title)
        self.title_label.setObjectName("cardTitle")
        self.title_label.setWordWrap(True)
        top_layout.addWidget(self.title_label, 1)
        
        layout.addLayout(top_layout)
        
        # Value (large, prominent)
        self.value_label = QLabel("0")
        self.value_label.setObjectName("cardValue")
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignBottom)
        layout.addWidget(self.value_label, 1)
        
        # Subtitle (optional, smaller text)
        self.subtitle_label = QLabel("")
        self.subtitle_label.setObjectName("cardSubtitle")
        self.subtitle_label.setVisible(False)
        layout.addWidget(self.subtitle_label)
    
    def _setup_animations(self):
        """Set up animations for value changes."""
        # For now, we'll implement simple value updates
        # Animation could be added later with QPropertyAnimation
        pass
    
    def _apply_styling(self):
        """Apply styling based on current theme and card type."""
        # Base styling - this will be enhanced by QSS themes
        self.setStyleSheet("""
            MetricCard {
                background-color: transparent;
                border: 1px solid #555753;
                border-radius: 8px;
                padding: 4px;
            }
            
            MetricCard:hover {
                border-color: #357ABD;
            }
            
            QLabel#cardIcon {
                color: #357ABD;
                font-size: 16px;
            }
            
            QLabel#cardTitle {
                color: #E0E0E0;
                font-size: 11px;
                font-weight: normal;
            }
            
            QLabel#cardValue {
                color: #FFFFFF;
                font-size: 24px;
                font-weight: bold;
            }
            
            QLabel#cardSubtitle {
                color: #AAAAAA;
                font-size: 9px;
            }
        """)
    
    def set_value(self, value: int):
        """
        Set the metric value with optional animation.
        
        Args:
            value: New value to display
        """
        self.target_value = value
        self.current_value = value  # For now, no animation
        self.value_label.setText(str(value))
        
        # Update tooltip with additional context
        self.setToolTip(f"{self.title}: {value}")
    
    def set_subtitle(self, subtitle: str):
        """
        Set optional subtitle text.
        
        Args:
            subtitle: Subtitle text to display below value
        """
        self.subtitle = subtitle
        self.subtitle_label.setText(subtitle)
        self.subtitle_label.setVisible(bool(subtitle))
    
    def set_icon(self, icon_text: str):
        """
        Set the icon (using text/emoji for now).
        
        Args:
            icon_text: Icon character or emoji to display
        """
        self.icon_label.setText(icon_text)
    
    def set_card_type(self, card_type: str):
        """
        Set the card type for different visual styling.
        
        Args:
            card_type: Type of card - 'default', 'success', 'warning', 'error'
        """
        self.card_type = card_type
        
        # Update styling based on type
        type_colors = {
            "default": "#357ABD",
            "success": "#50FA7B", 
            "warning": "#F1FA8C",
            "error": "#FF5555"
        }
        
        color = type_colors.get(card_type, "#357ABD")
        
        # Update icon color
        self.icon_label.setStyleSheet(f"color: {color}; font-size: 16px;")
        
        # Update border color on hover
        self.setStyleSheet(f"""
            MetricCard {{
                background-color: transparent;
                border: 1px solid #555753;
                border-radius: 8px;
                padding: 4px;
            }}
            
            MetricCard:hover {{
                border-color: {color};
            }}
            
            QLabel#cardTitle {{
                color: #E0E0E0;
                font-size: 11px;
                font-weight: normal;
            }}
            
            QLabel#cardValue {{
                color: #FFFFFF;
                font-size: 24px;
                font-weight: bold;
            }}
            
            QLabel#cardSubtitle {{
                color: #AAAAAA;
                font-size: 9px;
            }}
        """)
    
    def paintEvent(self, event):
        """Custom paint event for card background and shadow."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Get current background color from theme
        bg_color = self.palette().color(self.palette().ColorRole.Window)
        
        # Draw subtle shadow (optional, for neumorphic effect)
        shadow_color = QColor(0, 0, 0, 20)
        shadow_rect = QRect(2, 2, self.width() - 2, self.height() - 2)
        painter.setBrush(QBrush(shadow_color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(shadow_rect, 8, 8)
        
        # Draw main card background
        card_rect = QRect(0, 0, self.width() - 2, self.height() - 2)
        painter.setBrush(QBrush(bg_color))
        
        # Border color based on hover state
        border_color = QColor("#357ABD") if self.underMouse() else QColor("#555753")
        painter.setPen(QPen(border_color, 1))
        painter.drawRoundedRect(card_rect, 8, 8)
        
        super().paintEvent(event)
    
    def enterEvent(self, event):
        """Handle mouse enter for hover effects."""
        self.update()  # Trigger repaint for hover border
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        """Handle mouse leave for hover effects."""
        self.update()  # Trigger repaint to remove hover border
        super().leaveEvent(event)


if __name__ == "__main__":
    # Simple test of MetricCard
    import sys
    from PySide6.QtWidgets import QApplication, QHBoxLayout, QWidget
    
    app = QApplication(sys.argv)
    
    # Test window with sample cards
    window = QWidget()
    window.setWindowTitle("MetricCard Test")
    window.resize(600, 150)
    
    layout = QHBoxLayout(window)
    
    # Create sample cards
    card1 = MetricCard("Total Files", "📁")
    card1.set_value(112)
    card1.set_subtitle("Python files")
    
    card2 = MetricCard("Issues Found", "⚠️")
    card2.set_value(42)
    card2.set_card_type("warning")
    
    card3 = MetricCard("Auto-Fixed", "🔧")
    card3.set_value(8)
    card3.set_card_type("success")
    
    layout.addWidget(card1)
    layout.addWidget(card2)
    layout.addWidget(card3)
    layout.addStretch()
    
    # Apply dark theme for testing
    app.setStyleSheet("""
        QWidget {
            background-color: #121212;
            color: #E0E0E0;
        }
    """)
    
    window.show()
    sys.exit(app.exec())
