# cascade_linter/gui/dialogs/HelpPopup.py

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QWidget,
    QApplication,
)
from PySide6.QtCore import Qt, QPropertyAnimation, QRect, QEasingCurve
from PySide6.QtGui import QFont


class HelpPopup(QDialog):
    """
    Animated help popup dialog with smooth zoom in/out animations.

    Features:
    - Smooth scale animation (0.8 → 1.0 → 0.8)
    - Bounce easing curve for premium feel
    - Auto-sizing based on content
    - Dark theme styling
    - Contextual help content for linter rules
    """

    def __init__(self, title: str, content: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Help")
        self.setModal(True)
        self.setAttribute(Qt.WA_DeleteOnClose)

        # Remove window frame for custom styling
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)

        # Setup animations
        self._scale_animation = QPropertyAnimation(self, b"geometry")
        self._scale_animation.setDuration(300)
        self._scale_animation.setEasingCurve(QEasingCurve.OutBack)  # Bounce effect

        self._opacity_effect = None  # Will be set in show_animated()

        self._setup_ui(title, content)
        self._apply_styling()

    def _setup_ui(self, title: str, content: str):
        """Create the UI layout with title, content, and close button."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(16)

        # Title
        self.title_label = QLabel(title)
        self.title_label.setObjectName("helpTitle")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        self.title_label.setFont(title_font)
        main_layout.addWidget(self.title_label)

        # Scrollable content area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QScrollArea.NoFrame)
        scroll_area.setMaximumHeight(400)

        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)

        # Parse and create content (support for HTML-like formatting)
        self.content_label = QLabel(content)
        self.content_label.setWordWrap(True)
        self.content_label.setTextFormat(Qt.RichText)
        self.content_label.setOpenExternalLinks(False)

        content_layout.addWidget(self.content_label)
        scroll_area.setWidget(content_widget)
        main_layout.addWidget(scroll_area)

        # Close button
        self.close_button = QPushButton("Got it!")
        self.close_button.setObjectName("primaryButton")
        self.close_button.clicked.connect(self.close_animated)
        self.close_button.setDefault(True)
        main_layout.addWidget(self.close_button, alignment=Qt.AlignRight)

        # Size constraints
        self.setMinimumSize(400, 200)
        self.setMaximumSize(600, 500)

    def _apply_styling(self):
        """Apply dark theme styling to the popup."""
        self.setStyleSheet(
            """
            HelpPopup {
                background-color: #2e3436;
                border: 2px solid #729fcf;
                border-radius: 8px;
            }
            
            QLabel#helpTitle {
                color: #729fcf;
                font-weight: bold;
                font-size: 16px;
                margin-bottom: 12px;
            }
            
            QLabel {
                color: #eeeeec;
                font-size: 13px;
                line-height: 1.4;
            }
            
            QPushButton#primaryButton {
                background-color: #3465a4;
                color: white;
                border: 1px solid #204a87;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 13px;
                font-weight: bold;
            }
            
            QPushButton#primaryButton:hover {
                background-color: #204a87;
            }
            
            QPushButton#primaryButton:pressed {
                background-color: #1a3a6b;
            }
            
            QScrollArea {
                background-color: transparent;
                border: none;
            }
            
            QScrollBar:vertical {
                background: #555753;
                width: 8px;
                border-radius: 4px;
            }
            
            QScrollBar::handle:vertical {
                background: #729fcf;
                border-radius: 4px;
                min-height: 20px;
            }
            
            QScrollBar::handle:vertical:hover {
                background: #3465a4;
            }
        """
        )

    def show_animated(self):
        """Show the dialog with smooth zoom-in animation."""
        # Position dialog in center of parent or screen
        self._center_on_parent()

        # Store final geometry
        final_rect = self.geometry()

        # Start with scaled-down version (80% size)
        start_rect = QRect(final_rect)
        start_rect.setWidth(int(final_rect.width() * 0.8))
        start_rect.setHeight(int(final_rect.height() * 0.8))
        start_rect.moveCenter(final_rect.center())

        # Set initial state
        self.setGeometry(start_rect)
        self.show()

        # Animate to full size
        self._scale_animation.setStartValue(start_rect)
        self._scale_animation.setEndValue(final_rect)
        self._scale_animation.start()

    def close_animated(self):
        """Close the dialog with smooth zoom-out animation."""
        # Current geometry
        current_rect = self.geometry()

        # Target geometry (80% size)
        target_rect = QRect(current_rect)
        target_rect.setWidth(int(current_rect.width() * 0.8))
        target_rect.setHeight(int(current_rect.height() * 0.8))
        target_rect.moveCenter(current_rect.center())

        # Setup close animation
        self._scale_animation.finished.connect(self.accept)
        self._scale_animation.setStartValue(current_rect)
        self._scale_animation.setEndValue(target_rect)
        self._scale_animation.setEasingCurve(QEasingCurve.InBack)  # Smooth zoom out
        self._scale_animation.start()

    def _center_on_parent(self):
        """Center the dialog on parent widget or screen."""
        self.adjustSize()  # Adjust to content size

        if self.parent():
            parent_rect = self.parent().geometry()
            self.move(
                parent_rect.x() + (parent_rect.width() - self.width()) // 2,
                parent_rect.y() + (parent_rect.height() - self.height()) // 2,
            )
        else:
            # Center on screen
            screen = QApplication.primaryScreen().geometry()
            self.move(
                (screen.width() - self.width()) // 2,
                (screen.height() - self.height()) // 2,
            )


class HelpContent:
    """Static class containing all help content for linter configuration."""

    @staticmethod
    def ruff_rules_help() -> str:
        return """
        <p><b>🦀 Ruff Rule Configuration</b></p>
        <p>Ruff uses rule codes to identify different types of issues. Here are the most common ones:</p>
        
        <p><b style="color: #8ae234;">🔧 Auto-Fixable Rules (Safe to ignore if you prefer manual fixes):</b></p>
        <ul>
        <li><b style="color: #fce94f;">F401</b> - Unused imports</li>
        <li><b style="color: #fce94f;">E501</b> - Line too long (over 88 characters)</li>
        <li><b style="color: #fce94f;">W291</b> - Trailing whitespace</li>
        <li><b style="color: #fce94f;">I001</b> - Import sorting</li>
        <li><b style="color: #fce94f;">E203</b> - Whitespace before colon (conflicts with Black)</li>
        <li><b style="color: #fce94f;">W503</b> - Line break before binary operator</li>
        </ul>
        
        <p><b style="color: #fcaf3e;">⚠️ Code Quality Rules (Consider carefully before ignoring):</b></p>
        <ul>
        <li><b style="color: #fce94f;">F841</b> - Unused variables</li>
        <li><b style="color: #fce94f;">E711</b> - Comparison to None should use 'is'</li>
        <li><b style="color: #fce94f;">E712</b> - Comparison to True should use 'if cond:'</li>
        <li><b style="color: #fce94f;">F811</b> - Redefined name</li>
        </ul>
        
        <div style="background: #3c4043; border-left: 3px solid #729fcf; padding: 8px 12px; margin: 8px 0; font-family: 'Consolas', monospace; font-size: 12px;">
        <b>Example:</b> To ignore unused imports and line length:<br>
        <span style="color: #fce94f; font-weight: bold;">F401,E501</span>
        </div>
        
        <p><b>💡 Tip:</b> Start with common rules like <span style="color: #fce94f;">E203,W503</span> if using Black formatter.</p>
        """

    @staticmethod
    def flake8_rules_help() -> str:
        return """
        <p><b>🐍 Flake8 Rule Configuration</b></p>
        <p>Flake8 combines PyFlakes, pycodestyle, and McCabe complexity checks:</p>
        
        <p><b style="color: #8ae234;">📏 Style Rules (pycodestyle):</b></p>
        <ul>
        <li><b style="color: #fce94f;">E1xx</b> - Indentation errors</li>
        <li><b style="color: #fce94f;">E2xx</b> - Whitespace errors</li>
        <li><b style="color: #fce94f;">E3xx</b> - Blank line errors</li>
        <li><b style="color: #fce94f;">E4xx</b> - Import errors</li>
        <li><b style="color: #fce94f;">E5xx</b> - Line length errors</li>
        <li><b style="color: #fce94f;">W1xx-W6xx</b> - Warnings (whitespace, deprecation)</li>
        </ul>
        
        <p><b style="color: #8ae234;">🔍 Logic Rules (PyFlakes):</b></p>
        <ul>
        <li><b style="color: #fce94f;">F4xx</b> - Import issues</li>
        <li><b style="color: #fce94f;">F8xx</b> - Name errors, unused variables</li>
        <li><b style="color: #fce94f;">F9xx</b> - Syntax errors</li>
        </ul>
        
        <p><b style="color: #8ae234;">🧠 Complexity Rules (McCabe):</b></p>
        <ul>
        <li><b style="color: #fce94f;">C901</b> - Function too complex</li>
        </ul>
        
        <div style="background: #3c4043; border-left: 3px solid #729fcf; padding: 8px 12px; margin: 8px 0; font-family: 'Consolas', monospace; font-size: 12px;">
        <b>Black compatibility example:</b><br>
        <span style="color: #fce94f; font-weight: bold;">E203,W503</span>
        </div>
        """

    @staticmethod
    def pylint_rules_help() -> str:
        return """
        <p><b>🔍 Pylint Warning Configuration</b></p>
        <p>Pylint uses a category-based system for warnings and errors:</p>
        
        <p><b style="color: #8ae234;">📚 Convention Warnings (C):</b></p>
        <ul>
        <li><b style="color: #fce94f;">C0114</b> - Missing module docstring</li>
        <li><b style="color: #fce94f;">C0115</b> - Missing class docstring</li>
        <li><b style="color: #fce94f;">C0116</b> - Missing function docstring</li>
        <li><b style="color: #fce94f;">C0103</b> - Invalid name (doesn't conform to naming convention)</li>
        <li><b style="color: #fce94f;">C0301</b> - Line too long</li>
        </ul>
        
        <p><b style="color: #8ae234;">♻️ Refactoring Suggestions (R):</b></p>
        <ul>
        <li><b style="color: #fce94f;">R0903</b> - Too few public methods</li>
        <li><b style="color: #fce94f;">R0913</b> - Too many arguments</li>
        <li><b style="color: #fce94f;">R1705</b> - Unnecessary else after return</li>
        </ul>
        
        <p><b style="color: #8ae234;">⚠️ Warnings (W):</b></p>
        <ul>
        <li><b style="color: #fce94f;">W0613</b> - Unused argument</li>
        <li><b style="color: #fce94f;">W0622</b> - Redefining built-in</li>
        <li><b style="color: #fce94f;">W0212</b> - Accessing protected member</li>
        </ul>
        
        <div style="background: #3c4043; border-left: 3px solid #729fcf; padding: 8px 12px; margin: 8px 0; font-family: 'Consolas', monospace; font-size: 12px;">
        <b>Common setup for beginners:</b><br>
        <span style="color: #fce94f; font-weight: bold;">C0114,C0115,C0116</span><br>
        <em>(Disables docstring requirements)</em>
        </div>
        
        <p><b>💡 Tip:</b> Start by disabling docstring warnings if you're learning, then gradually enable them as you improve your code documentation.</p>
        """

    @staticmethod
    def unsafe_fixes_help() -> str:
        return """
        <p><b>⚡ Unsafe Fixes Explanation</b></p>
        <p>Ruff can apply two types of fixes to your code:</p>
        
        <p><b style="color: #8ae234;">✅ Safe Fixes (Always Applied):</b></p>
        <ul>
        <li>Removing unused imports</li>
        <li>Fixing whitespace and formatting</li>
        <li>Sorting imports</li>
        <li>Adding missing commas</li>
        </ul>
        
        <p><b style="color: #fcaf3e;">⚡ Unsafe Fixes (Require This Option):</b></p>
        <ul>
        <li>Removing unused variables (might break code)</li>
        <li>Converting string formatting styles</li>
        <li>Replacing deprecated functions</li>
        <li>Modifying comprehensions</li>
        </ul>
        
        <div style="background: #3c4043; border-left: 3px solid #fcaf3e; padding: 8px 12px; margin: 8px 0; font-family: 'Consolas', monospace; font-size: 12px;">
        <b>Example Unsafe Fix:</b><br>
        <code>name = input("Name: ")  # Unused variable</code><br>
        ⬇️ Unsafe fix removes it entirely<br>
        <code># Variable removed - might break other code!</code>
        </div>
        
        <p><b style="color: #ef2929;">⚠️ Warning:</b> Only enable this if you understand the changes being made and have version control backup!</p>
        
        <p><b>💡 Recommendation:</b> Run with check-only mode first to preview what would be changed.</p>
        """
