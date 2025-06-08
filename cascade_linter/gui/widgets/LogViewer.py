# cascade_linter/gui/widgets/LogViewer.py

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTextEdit,
    QCheckBox,
    QLabel,
    QPushButton,
)
from PySide6.QtCore import Qt, Slot, Signal
from PySide6.QtGui import QFont, QTextCursor, QTextOption


class LogViewer(QWidget):
    """
    Advanced log viewer widget with HTML support and filtering capabilities.

    Features:
    - Rich HTML log display with syntax highlighting
    - Filter checkboxes for each linter stage (Ruff, Flake8, Pylint, Bandit, MyPy)
    - Auto-scroll option
    - Export functionality
    - Monospace font with good Unicode support
    - Real-time log appending from structlog + Rich
    - Clear and search functionality
    """

    # Signals
    exportRequested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        # Internal state
        self._auto_scroll = True
        self._line_count = 0
        self._max_lines = 1000  # Prevent memory issues

        # Initialize UI
        self.init_ui()
        self.apply_styling()

    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # Top filter row
        self.create_filter_row(layout)

        # Main log text area
        self.create_log_area(layout)

        # Bottom control row
        self.create_control_row(layout)

    def create_filter_row(self, parent_layout):
        """Create the filter checkbox row"""
        filter_widget = QWidget()
        filter_layout = QHBoxLayout(filter_widget)
        filter_layout.setContentsMargins(0, 0, 0, 0)
        filter_layout.setSpacing(12)

        # Filter label
        filter_label = QLabel("Show logs from:")
        filter_label.setStyleSheet("font-weight: bold;")
        filter_layout.addWidget(filter_label)

        # Create filter checkboxes for each linter
        self.filters = {}
        linters = [
            ("Ruff", "#e74c3c", True),  # Red
            ("Flake8", "#f39c12", True),  # Orange
            ("Pylint", "#9b59b6", True),  # Purple
            ("Bandit", "#e67e22", True),  # Dark orange
            ("MyPy", "#3498db", True),  # Blue
        ]

        for linter, color, checked in linters:
            checkbox = QCheckBox(linter)
            checkbox.setChecked(checked)
            checkbox.setToolTip(f"Show/hide logs from {linter} linter")
            checkbox.setStyleSheet(
                f"""
                QCheckBox {{
                    font-weight: bold;
                    color: {color};
                    spacing: 6px;
                }}
                QCheckBox::indicator {{
                    width: 16px;
                    height: 16px;
                }}
                QCheckBox::indicator:checked {{
                    background-color: {color};
                    border: 1px solid #888a85;
                    border-radius: 3px;
                }}
                QCheckBox::indicator:unchecked {{
                    background-color: #555753;
                    border: 1px solid #888a85;
                    border-radius: 3px;
                }}
            """
            )
            checkbox.stateChanged.connect(self.on_filter_changed)
            self.filters[linter] = checkbox
            filter_layout.addWidget(checkbox)

        filter_layout.addStretch()
        parent_layout.addWidget(filter_widget)

    def create_log_area(self, parent_layout):
        """Create the main log text area"""
        self.text_logs = QTextEdit()
        self.text_logs.setReadOnly(True)
        self.text_logs.setAcceptRichText(True)
        self.text_logs.setPlaceholderText(
            "Logs will appear here when linting starts..."
        )

        # Set monospace font with better sizing and readability
        font = QFont()
        font.setFamilies(["Consolas", "DejaVu Sans Mono", "Menlo", "monospace"])
        font.setPointSize(11)  # Increased from 10 for better readability
        font.setStyleHint(QFont.StyleHint.Monospace)
        self.text_logs.setFont(font)

        # Enable word wrap for better layout
        self.text_logs.setWordWrapMode(QTextOption.WrapMode.WordWrap)
        self.text_logs.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)

        # Set object name for CSS targeting
        self.text_logs.setObjectName("logTextArea")

        parent_layout.addWidget(self.text_logs, stretch=1)

    def create_control_row(self, parent_layout):
        """Create the bottom control row"""
        control_widget = QWidget()
        control_layout = QHBoxLayout(control_widget)
        control_layout.setContentsMargins(0, 0, 0, 0)
        control_layout.setSpacing(8)

        # Auto-scroll checkbox
        self.chk_auto_scroll = QCheckBox("Auto-scroll")
        self.chk_auto_scroll.setChecked(self._auto_scroll)
        self.chk_auto_scroll.setToolTip(
            "Automatically scroll to bottom when new logs arrive"
        )
        self.chk_auto_scroll.stateChanged.connect(self.on_auto_scroll_changed)
        control_layout.addWidget(self.chk_auto_scroll)

        # Line count label
        self.line_count_label = QLabel("Lines: 0")
        self.line_count_label.setStyleSheet("font-size: 9pt;")
        control_layout.addWidget(self.line_count_label)

        control_layout.addStretch()

        # Control buttons
        self.clear_btn = QPushButton("Clear")
        self.clear_btn.setToolTip("Clear all log content")
        self.clear_btn.clicked.connect(self.clear_logs)
        control_layout.addWidget(self.clear_btn)

        self.export_btn = QPushButton("Export")
        self.export_btn.setToolTip("Export logs to file")
        self.export_btn.clicked.connect(self.export_logs)
        control_layout.addWidget(self.export_btn)

        parent_layout.addWidget(control_widget)

    def apply_styling(self):
        """Apply consistent styling that respects themes"""
        self.setStyleSheet(
            """
            QTextEdit#logTextArea {
                background-color: palette(base);
                color: palette(text);
                border: 1px solid palette(mid);
                border-radius: 4px;
                padding: 8px;
                selection-background-color: palette(highlight);
                selection-color: palette(highlighted-text);
            }
            QPushButton {
                background-color: palette(button);
                border: 1px solid palette(mid);
                border-radius: 4px;
                padding: 6px 12px;
                min-width: 60px;
                color: palette(button-text);
            }
            QPushButton:hover {
                background-color: palette(highlight);
                border-color: palette(highlight);
                color: palette(highlighted-text);
            }
            QPushButton:pressed {
                background-color: palette(dark);
            }
            QCheckBox {
                color: palette(text);
                spacing: 6px;
            }
            QCheckBox::indicator {
                width: 14px;
                height: 14px;
                border: 1px solid palette(mid);
                border-radius: 3px;
                background-color: palette(base);
            }
            QCheckBox::indicator:checked {
                background-color: palette(highlight);
                border-color: palette(highlight);
            }
        """
        )

    # --- PUBLIC METHODS ---

    @Slot(str)
    def append_html(self, html_fragment):
        """
        Append HTML content to the log viewer.

        Args:
            html_fragment: HTML string to append (from structlog + Rich)
        """
        # Manage line count to prevent memory issues
        if self._line_count >= self._max_lines:
            self.trim_logs()

        # Wrap in div with margin for separation
        wrapped_html = (
            f'<div style="margin-bottom: 4px; line-height: 1.2;">{html_fragment}</div>'
        )

        # Move cursor to end and insert HTML
        cursor = self.text_logs.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.text_logs.setTextCursor(cursor)
        self.text_logs.insertHtml(wrapped_html)

        # Add newline for proper separation
        self.text_logs.insertPlainText("\n")

        # Update line count
        self._line_count += 1
        self.line_count_label.setText(f"Lines: {self._line_count}")

        # Auto-scroll if enabled
        if self._auto_scroll:
            self.scroll_to_bottom()

    def append_plain(self, text):
        """Append plain text (fallback for non-HTML logs)"""
        self.text_logs.append(text)
        self._line_count += 1
        self.line_count_label.setText(f"Lines: {self._line_count}")

        if self._auto_scroll:
            self.scroll_to_bottom()

    def clear_logs(self):
        """Clear all log content"""
        self.text_logs.clear()
        self._line_count = 0
        self.line_count_label.setText("Lines: 0")

    def get_plain_text(self):
        """Get log content as plain text"""
        return self.text_logs.toPlainText()

    def get_html(self):
        """Get log content as HTML"""
        return self.text_logs.toHtml()

    def set_auto_scroll(self, enabled):
        """Enable/disable auto-scrolling"""
        self._auto_scroll = enabled
        self.chk_auto_scroll.setChecked(enabled)

    def scroll_to_bottom(self):
        """Scroll to bottom of log"""
        scrollbar = self.text_logs.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def set_max_lines(self, max_lines):
        """Set maximum number of lines to keep in memory"""
        self._max_lines = max_lines

    # --- PRIVATE METHODS ---

    def trim_logs(self):
        """Remove old log entries to prevent memory issues"""
        # Keep only the last 75% of max_lines
        keep_lines = int(self._max_lines * 0.75)

        text = self.text_logs.toPlainText()
        lines = text.split("\n")

        if len(lines) > keep_lines:
            # Keep the most recent lines
            trimmed_lines = lines[-keep_lines:]
            self.text_logs.clear()
            self.text_logs.setPlainText("\n".join(trimmed_lines))
            self._line_count = len(trimmed_lines)

    # --- SLOT IMPLEMENTATIONS ---

    @Slot(int)
    def on_filter_changed(self, state):
        """Handle filter checkbox state change"""
        # TODO: Implement log filtering based on linter type
        # This would require tagging log entries with their source linter
        sender = self.sender()
        if sender:
            linter_name = sender.text()
            enabled = state == Qt.CheckState.Checked.value
            # For now, just update the UI state
            # Real filtering would need cooperation with the logging system

    @Slot(int)
    def on_auto_scroll_changed(self, state):
        """Handle auto-scroll checkbox change"""
        self._auto_scroll = state == Qt.CheckState.Checked.value

    @Slot()
    def export_logs(self):
        """Handle export button click"""
        self.exportRequested.emit()

    # --- EVENT OVERRIDES ---

    def wheelEvent(self, event):
        """Handle mouse wheel events (disable auto-scroll when user scrolls up)"""
        super().wheelEvent(event)

        # If user scrolls up, disable auto-scroll temporarily
        if event.angleDelta().y() > 0:  # Scrolling up
            scrollbar = self.text_logs.verticalScrollBar()
            if scrollbar.value() < scrollbar.maximum() - 10:
                # User is not at bottom, disable auto-scroll
                if self._auto_scroll:
                    self.set_auto_scroll(False)


# --- DEMO/TEST CODE ---

if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication, QVBoxLayout, QWidget
    from PySide6.QtCore import QTimer

    app = QApplication(sys.argv)

    # Create test window
    window = QWidget()
    window.setWindowTitle("LogViewer Demo")
    window.resize(800, 600)
    window.setStyleSheet(
        """
        QWidget {
            background-color: #2e3436;
            color: #eeeeec;
        }
    """
    )

    layout = QVBoxLayout(window)

    # Create log viewer
    log_viewer = LogViewer()
    layout.addWidget(log_viewer)

    # Demo data
    sample_logs = [
        '<span style="color: #e74c3c;"><b>[Ruff]</b></span> Starting analysis...',
        '<span style="color: #e74c3c;">[Ruff]</span> Found 3 issues in <code>main.py</code>',
        '<span style="color: #8ae234;">✅</span> <span style="color: #e74c3c;">[Ruff]</span> Completed in 1.2s',
        '<span style="color: #f39c12;"><b>[Flake8]</b></span> Starting analysis...',
        '<span style="color: #f39c12;">[Flake8]</span> Checking code style...',
        '<span style="color: #f39c12;">[Flake8]</span> Found 2 style issues',
        '<span style="color: #8ae234;">✅</span> <span style="color: #f39c12;">[Flake8]</span> Completed in 0.8s',
        '<span style="color: #9b59b6;"><b>[Pylint]</b></span> Starting deep analysis...',
        '<span style="color: #9b59b6;">[Pylint]</span> Analyzing code structure...',
        '<span style="color: #fcaf3e;">⚠️</span> <span style="color: #9b59b6;">[Pylint]</span> Found 1 warning',
        '<span style="color: #8ae234;">✅</span> <span style="color: #9b59b6;">[Pylint]</span> Completed in 2.1s',
    ]

    # Add sample logs progressively
    def add_sample_log():
        if hasattr(add_sample_log, "log_index"):
            log_index = add_sample_log.log_index
        else:
            log_index = 0

        if log_index < len(sample_logs):
            log_viewer.append_html(sample_logs[log_index])
            add_sample_log.log_index = log_index + 1
        else:
            add_sample_log.log_index = 0  # Reset for continuous demo

    # Timer for demo
    timer = QTimer()
    timer.timeout.connect(add_sample_log)
    timer.start(1000)  # Add new log every second

    window.show()
    sys.exit(app.exec())
