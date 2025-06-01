# cascade_linter/gui/widgets/LogViewer.py

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, 
    QCheckBox, QPushButton, QLabel, QScrollBar
)
from PySide6.QtCore import Qt, Slot, Signal
from PySide6.QtGui import QFont, QTextCursor


class LogViewer(QWidget):
    """
    Advanced log viewer widget with HTML support, filtering, and export functionality.
    Features:
    - Rich HTML log display with syntax highlighting
    - Per-linter filtering checkboxes (Ruff, Flake8, Pylint, Bandit, MyPy)
    - Auto-scroll capability
    - Export functionality
    - Monospace font with cross-platform fallback
    """
    
    log_exported = Signal(str)  # Emitted when logs are exported
    filter_changed = Signal(list)  # Emitted when filter selection changes
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.connect_signals()
        self._auto_scroll = True
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)
        
        # --- Filter Row (linter-type checkboxes) ---
        filter_container = QWidget()
        filter_layout = QHBoxLayout(filter_container)
        filter_layout.setContentsMargins(0, 0, 0, 0)
        
        # Filter label
        filter_label = QLabel("Show:")
        filter_label.setStyleSheet("font-weight: bold; color: #E0E0E0;")
        filter_layout.addWidget(filter_label)
        
        # Linter checkboxes
        self.chk_ruff = QCheckBox("Ruff")
        self.chk_flake8 = QCheckBox("Flake8")
        self.chk_pylint = QCheckBox("Pylint")
        self.chk_bandit = QCheckBox("Bandit")
        self.chk_mypy = QCheckBox("MyPy")
        
        # Style and configure checkboxes
        for checkbox, color in [
            (self.chk_ruff, "#4A90E2"),      # Blue
            (self.chk_flake8, "#50C878"),    # Green
            (self.chk_pylint, "#FFB347"),    # Orange
            (self.chk_bandit, "#FF6B6B"),    # Red
            (self.chk_mypy, "#9B59B6")       # Purple
        ]:
            checkbox.setChecked(True)
            checkbox.setStyleSheet(f"""
                QCheckBox {{
                    color: {color};
                    font-weight: bold;
                    spacing: 6px;
                }}
                QCheckBox::indicator {{
                    width: 16px;
                    height: 16px;
                    border: 2px solid {color};
                    border-radius: 3px;
                    background-color: transparent;
                }}
                QCheckBox::indicator:checked {{
                    background-color: {color};
                    border-color: {color};
                }}
                QCheckBox::indicator:hover {{
                    border-color: {color};
                    background-color: rgba({int(color[1:3], 16)}, {int(color[3:5], 16)}, {int(color[5:7], 16)}, 0.2);
                }}
            """)
            checkbox.setToolTip(f"Show logs from {checkbox.text()} linter")
            filter_layout.addWidget(checkbox)
        
        filter_layout.addStretch()
        
        # Export button
        self.btn_export = QPushButton("Export Logs")
        self.btn_export.setStyleSheet("""
            QPushButton {
                background-color: #357ABD;
                color: #E0E0E0;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #4A90E2;
            }
            QPushButton:pressed {
                background-color: #285F8D;
            }
        """)
        self.btn_export.setToolTip("Export current logs to file")
        filter_layout.addWidget(self.btn_export)
        
        layout.addWidget(filter_container)
        
        # --- Main HTML Log Area ---
        self.text_logs = QTextEdit()
        self.text_logs.setReadOnly(True)
        self.text_logs.setAcceptRichText(True)
        
        # Configure monospace font with broad cross-platform coverage
        font = QFont()
        font.setFamilies(["Consolas", "DejaVu Sans Mono", "Menlo", "monospace"])
        font.setPointSize(10)
        self.text_logs.setFont(font)
        
        # Style the text area
        self.text_logs.setStyleSheet("""
            QTextEdit {
                background-color: #1E1E1E;
                color: #E0E0E0;
                border: 1px solid #444444;
                border-radius: 4px;
                padding: 8px;
                selection-background-color: #357ABD;
                selection-color: #FFFFFF;
            }
            QScrollBar:vertical {
                background: #2E2E2E;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background: #555555;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #666666;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                background: none;
                height: 0px;
            }
        """)
        
        # Set placeholder text
        self.text_logs.setPlaceholderText(
            "Logs will appear here when linting starts...\n\n"
            "• Quick Lint (F5): Run Ruff only\n"
            "• Full Lint (Shift+F5): Run all linters\n"
            "• Use checkboxes above to filter log output"
        )
        
        layout.addWidget(self.text_logs, stretch=1)
        
        # --- Status Row ---
        status_container = QWidget()
        status_layout = QHBoxLayout(status_container)
        status_layout.setContentsMargins(0, 0, 0, 0)
        
        self.lbl_status = QLabel("Ready")
        self.lbl_status.setStyleSheet("color: #A0A0A0; font-size: 9pt;")
        status_layout.addWidget(self.lbl_status)
        
        status_layout.addStretch()
        
        # Auto-scroll checkbox
        self.chk_auto_scroll = QCheckBox("Auto-scroll")
        self.chk_auto_scroll.setChecked(True)
        self.chk_auto_scroll.setStyleSheet("""
            QCheckBox {
                color: #A0A0A0;
                font-size: 9pt;
            }
            QCheckBox::indicator {
                width: 14px;
                height: 14px;
                border: 1px solid #666666;
                border-radius: 2px;
                background-color: transparent;
            }
            QCheckBox::indicator:checked {
                background-color: #357ABD;
                border-color: #357ABD;
            }
        """)
        self.chk_auto_scroll.setToolTip("Automatically scroll to newest log entries")
        status_layout.addWidget(self.chk_auto_scroll)
        
        layout.addWidget(status_container)
        
    def connect_signals(self):
        """Connect internal signals to slots."""
        # Filter checkboxes
        for checkbox in [self.chk_ruff, self.chk_flake8, self.chk_pylint, 
                        self.chk_bandit, self.chk_mypy]:
            checkbox.toggled.connect(self._on_filter_changed)
            
        # Auto-scroll
        self.chk_auto_scroll.toggled.connect(self._on_auto_scroll_changed)
        
        # Export button
        self.btn_export.clicked.connect(self._on_export_clicked)
        
    @Slot(str)
    def append_html(self, html_fragment: str):
        """
        Append a fragment of HTML (with inline CSS) to the text_logs.
        Wraps in a <div> with bottom margin for separation.
        """
        if not html_fragment.strip():
            return
            
        wrapped = f'<div style="margin-bottom: 4px; font-family: Consolas, monospace;">{html_fragment}</div>'
        
        cursor = self.text_logs.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.text_logs.setTextCursor(cursor)
        self.text_logs.insertHtml(wrapped)
        self.text_logs.insertPlainText("\n")
        
        # Auto-scroll if enabled
        if self._auto_scroll:
            scrollbar = self.text_logs.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())
            
    @Slot(str)
    def append_text(self, text: str):
        """Append plain text to the log viewer."""
        if not text.strip():
            return
            
        self.text_logs.append(text)
        
        # Auto-scroll if enabled
        if self._auto_scroll:
            scrollbar = self.text_logs.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())
            
    @Slot()
    def clear_logs(self):
        """Clear all log content."""
        self.text_logs.clear()
        self.set_status("Logs cleared")
        
    @Slot(str)
    def set_status(self, status_text: str):
        """Update the status label."""
        self.lbl_status.setText(status_text)
        
    def get_active_filters(self) -> list:
        """Return list of active linter filters."""
        active_filters = []
        filter_mapping = {
            'ruff': self.chk_ruff,
            'flake8': self.chk_flake8,
            'pylint': self.chk_pylint,
            'bandit': self.chk_bandit,
            'mypy': self.chk_mypy
        }
        
        for linter, checkbox in filter_mapping.items():
            if checkbox.isChecked():
                active_filters.append(linter)
                
        return active_filters
        
    def set_filter_state(self, linter: str, enabled: bool):
        """Set the state of a specific linter filter."""
        filter_mapping = {
            'ruff': self.chk_ruff,
            'flake8': self.chk_flake8,
            'pylint': self.chk_pylint,
            'bandit': self.chk_bandit,
            'mypy': self.chk_mypy
        }
        
        if linter.lower() in filter_mapping:
            filter_mapping[linter.lower()].setChecked(enabled)
            
    @Slot()
    def _on_filter_changed(self):
        """Handle filter checkbox changes."""
        active_filters = self.get_active_filters()
        self.filter_changed.emit(active_filters)
        
        # Update status
        if not active_filters:
            self.set_status("No filters active - all logs hidden")
        elif len(active_filters) == 5:
            self.set_status("All filters active")
        else:
            self.set_status(f"Showing: {', '.join(active_filters)}")
            
    @Slot(bool)
    def _on_auto_scroll_changed(self, enabled: bool):
        """Handle auto-scroll checkbox changes."""
        self._auto_scroll = enabled
        if enabled:
            # Scroll to bottom immediately
            scrollbar = self.text_logs.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())
            
    @Slot()
    def _on_export_clicked(self):
        """Handle export button click."""
        content = self.text_logs.toPlainText()
        if not content.strip():
            self.set_status("No logs to export")
            return
            
        self.log_exported.emit(content)
        self.set_status("Export requested")
        
    def get_log_content(self) -> str:
        """Get the current log content as plain text."""
        return self.text_logs.toPlainText()
        
    def get_log_html(self) -> str:
        """Get the current log content as HTML."""
        return self.text_logs.toHtml()
        
    def set_auto_scroll(self, enabled: bool):
        """Programmatically set auto-scroll state."""
        self.chk_auto_scroll.setChecked(enabled)
        self._auto_scroll = enabled
