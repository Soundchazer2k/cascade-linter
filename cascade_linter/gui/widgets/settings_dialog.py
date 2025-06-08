#!/usr/bin/env python3
"""
Settings Dialog and Advanced Functionality Widgets
FIXED: PySide6 compatible imports
"""

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QTabWidget,
    QGroupBox,
    QCheckBox,
    QSpinBox,
    QComboBox,
    QPushButton,
    QFormLayout,
    QFileDialog,
    QMessageBox,
    QTextEdit,
    QWidget,
)
from PySide6.QtCore import QSettings
from PySide6.QtGui import (
    QKeySequence,
    QShortcut,
)  # FIXED: QShortcut is in QtGui, not QtWidgets
from datetime import datetime
import json
from typing import List


class SettingsDialog(QDialog):
    """Comprehensive settings dialog with tabbed interface"""

    def __init__(self, config_manager, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.setWindowTitle("⚙️ Cascade Linter Settings")
        self.setModal(True)
        self.resize(600, 500)
        self._setup_ui()
        self._load_settings()

    def _setup_ui(self):
        """Set up the settings dialog UI"""
        layout = QVBoxLayout(self)

        # Tab widget
        tab_widget = QTabWidget()

        # General tab
        general_tab = self._create_general_tab()
        tab_widget.addTab(general_tab, "🔧 General")

        # Linters tab
        linters_tab = self._create_linters_tab()
        tab_widget.addTab(linters_tab, "🔍 Linters")

        # UI tab
        ui_tab = self._create_ui_tab()
        tab_widget.addTab(ui_tab, "🎨 Interface")

        layout.addWidget(tab_widget)

        # Buttons
        buttons_layout = QHBoxLayout()

        restore_button = QPushButton("🔄 Restore Defaults")
        restore_button.clicked.connect(self._restore_defaults)
        buttons_layout.addWidget(restore_button)

        buttons_layout.addStretch()

        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_button)

        save_button = QPushButton("💾 Save")
        save_button.clicked.connect(self._save_settings)
        save_button.setDefault(True)
        buttons_layout.addWidget(save_button)

        layout.addLayout(buttons_layout)

    def _create_general_tab(self):
        """Create general settings tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Default behavior group
        behavior_group = QGroupBox("Default Behavior")
        behavior_layout = QFormLayout(behavior_group)

        self.check_only_cb = QCheckBox("Check only (don't auto-fix)")
        behavior_layout.addRow("Default Mode:", self.check_only_cb)

        self.unsafe_fixes_cb = QCheckBox("Apply unsafe fixes")
        behavior_layout.addRow("Unsafe Fixes:", self.unsafe_fixes_cb)

        self.respect_gitignore_cb = QCheckBox("Respect .gitignore files")
        behavior_layout.addRow("GitIgnore:", self.respect_gitignore_cb)

        layout.addWidget(behavior_group)

        # Log management group
        log_group = QGroupBox("Log Management")
        log_layout = QFormLayout(log_group)

        self.auto_save_logs_cb = QCheckBox("Automatically save logs")
        log_layout.addRow("Auto-save:", self.auto_save_logs_cb)

        self.log_retention_spin = QSpinBox()
        self.log_retention_spin.setRange(1, 365)
        self.log_retention_spin.setSuffix(" days")
        log_layout.addRow("Keep logs:", self.log_retention_spin)

        self.max_log_files_spin = QSpinBox()
        self.max_log_files_spin.setRange(10, 1000)
        self.max_log_files_spin.setSuffix(" files")
        log_layout.addRow("Max log files:", self.max_log_files_spin)

        layout.addWidget(log_group)
        layout.addStretch()

        return widget

    def _create_linters_tab(self):
        """Create linter-specific settings tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Linter stages group
        stages_group = QGroupBox("Default Linter Stages")
        stages_layout = QVBoxLayout(stages_group)

        self.stage_checkboxes = {}
        stages = [
            ("ruff", "🚀 Ruff - Primary linter and formatter"),
            ("flake8", "🔍 Flake8 - Style guide enforcement"),
            ("pylint", "🧠 Pylint - Deep code analysis"),
            ("bandit", "🛡️ Bandit - Security vulnerability scanner"),
            ("mypy", "🎯 MyPy - Static type checker"),
        ]

        for stage_id, description in stages:
            cb = QCheckBox(description)
            self.stage_checkboxes[stage_id] = cb
            stages_layout.addWidget(cb)

        layout.addWidget(stages_group)

        # Line length group
        line_length_group = QGroupBox("Code Style")
        line_length_layout = QFormLayout(line_length_group)

        self.line_length_spin = QSpinBox()
        self.line_length_spin.setRange(60, 120)
        self.line_length_spin.setSuffix(" characters")
        line_length_layout.addRow("Max line length:", self.line_length_spin)

        layout.addWidget(line_length_group)
        layout.addStretch()

        return widget

    def _create_ui_tab(self):
        """Create UI settings tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Theme group
        theme_group = QGroupBox("Appearance")
        theme_layout = QFormLayout(theme_group)

        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["System", "Light", "Dark"])
        theme_layout.addRow("Theme:", self.theme_combo)

        self.animation_cb = QCheckBox("Enable animations")
        theme_layout.addRow("Animations:", self.animation_cb)

        layout.addWidget(theme_group)

        # Log viewer group
        log_viewer_group = QGroupBox("Log Viewer")
        log_viewer_layout = QFormLayout(log_viewer_group)

        self.log_font_size_spin = QSpinBox()
        self.log_font_size_spin.setRange(8, 16)
        self.log_font_size_spin.setSuffix(" pt")
        log_viewer_layout.addRow("Font size:", self.log_font_size_spin)

        self.show_line_numbers_cb = QCheckBox("Show line numbers")
        log_viewer_layout.addRow("Line numbers:", self.show_line_numbers_cb)

        self.auto_scroll_cb = QCheckBox("Auto-scroll log")
        log_viewer_layout.addRow("Auto-scroll:", self.auto_scroll_cb)

        layout.addWidget(log_viewer_group)

        # Keyboard shortcuts info
        shortcuts_group = QGroupBox("Keyboard Shortcuts")
        shortcuts_layout = QVBoxLayout(shortcuts_group)

        shortcuts_text = QTextEdit()
        shortcuts_text.setMaximumHeight(120)
        shortcuts_text.setReadOnly(True)
        shortcuts_text.setHtml(
            """
        <b>Available Shortcuts:</b><br>
        • <b>F5</b> - Start Linting<br>
        • <b>Escape</b> - Stop Linting<br>
        • <b>Ctrl+O</b> - Browse Directory<br>
        • <b>Ctrl+S</b> - Save Log<br>
        • <b>Ctrl+E</b> - Export Results<br>
        • <b>F1</b> - Switch to Issues Tab<br>
        • <b>F2</b> - Switch to Dashboard Tab<br>
        • <b>F3</b> - Switch to Log Tab
        """
        )
        shortcuts_layout.addWidget(shortcuts_text)

        layout.addWidget(shortcuts_group)
        layout.addStretch()

        return widget

    def _load_settings(self):
        """Load current settings into the dialog"""
        config = self.config_manager.config

        # General settings
        self.check_only_cb.setChecked(config.general.check_only_default)
        self.unsafe_fixes_cb.setChecked(config.general.unsafe_fixes_default)
        self.respect_gitignore_cb.setChecked(config.general.respect_gitignore)
        self.auto_save_logs_cb.setChecked(config.general.auto_save_logs)
        self.log_retention_spin.setValue(config.general.log_retention_days)
        self.max_log_files_spin.setValue(config.general.max_log_files)

        # Linter settings
        for stage_id, cb in self.stage_checkboxes.items():
            if stage_id in config.linters:
                cb.setChecked(config.linters[stage_id].enabled)

        if "ruff" in config.linters:
            self.line_length_spin.setValue(config.linters["ruff"].max_line_length)

        # UI settings
        theme_map = {"system": 0, "light": 1, "dark": 2}
        self.theme_combo.setCurrentIndex(theme_map.get(config.ui.theme.value, 0))
        self.animation_cb.setChecked(config.ui.animation_enabled)
        self.log_font_size_spin.setValue(config.ui.log_font_size)
        self.show_line_numbers_cb.setChecked(config.ui.show_line_numbers)
        self.auto_scroll_cb.setChecked(config.ui.auto_scroll_log)

    def _save_settings(self):
        """Save settings and close dialog"""
        # Update general settings
        self.config_manager.update_general_config(
            check_only_default=self.check_only_cb.isChecked(),
            unsafe_fixes_default=self.unsafe_fixes_cb.isChecked(),
            respect_gitignore=self.respect_gitignore_cb.isChecked(),
            auto_save_logs=self.auto_save_logs_cb.isChecked(),
            log_retention_days=self.log_retention_spin.value(),
            max_log_files=self.max_log_files_spin.value(),
        )

        # Update linter settings
        for stage_id, cb in self.stage_checkboxes.items():
            self.config_manager.update_linter_config(
                stage_id,
                enabled=cb.isChecked(),
                max_line_length=self.line_length_spin.value(),
            )

        # Update UI settings
        theme_values = ["system", "light", "dark"]
        from ...config import ThemeMode

        theme = ThemeMode(theme_values[self.theme_combo.currentIndex()])

        self.config_manager.update_ui_config(
            theme=theme,
            animation_enabled=self.animation_cb.isChecked(),
            log_font_size=self.log_font_size_spin.value(),
            show_line_numbers=self.show_line_numbers_cb.isChecked(),
            auto_scroll_log=self.auto_scroll_cb.isChecked(),
        )

        # Save to file
        self.config_manager.save_config()

        QMessageBox.information(
            self, "Settings Saved", "Settings have been saved successfully!"
        )
        self.accept()

    def _restore_defaults(self):
        """Restore default settings"""
        reply = QMessageBox.question(
            self,
            "Restore Defaults",
            "Are you sure you want to restore all settings to defaults?",
            QMessageBox.Yes | QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            self.config_manager.reset_to_defaults()
            self._load_settings()
            QMessageBox.information(
                self,
                "Defaults Restored",
                "All settings have been restored to defaults.",
            )


class ExportDialog(QDialog):
    """Export linting results dialog"""

    def __init__(self, session_data, parent=None):
        super().__init__(parent)
        self.session_data = session_data
        self.setWindowTitle("📤 Export Results")
        self.setModal(True)
        self.resize(400, 300)
        self._setup_ui()

    def _setup_ui(self):
        """Set up export dialog UI"""
        layout = QVBoxLayout(self)

        # Export format group
        format_group = QGroupBox("Export Format")
        format_layout = QVBoxLayout(format_group)

        self.format_combo = QComboBox()
        self.format_combo.addItems(["HTML Report", "JSON Data", "Text Summary"])
        format_layout.addWidget(self.format_combo)

        layout.addWidget(format_group)

        # Export options group
        options_group = QGroupBox("Export Options")
        options_layout = QVBoxLayout(options_group)

        self.include_code_cb = QCheckBox("Include code context")
        self.include_code_cb.setChecked(True)

        self.include_stats_cb = QCheckBox("Include statistics")
        self.include_stats_cb.setChecked(True)

        options_layout.addWidget(self.include_code_cb)
        options_layout.addWidget(self.include_stats_cb)

        layout.addWidget(options_group)

        # Buttons
        buttons_layout = QHBoxLayout()

        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_button)

        export_button = QPushButton("📤 Export")
        export_button.clicked.connect(self._export_results)
        export_button.setDefault(True)
        buttons_layout.addWidget(export_button)

        layout.addLayout(buttons_layout)

    def _export_results(self):
        """Export results in selected format"""
        format_name = self.format_combo.currentText()

        # Get save location
        filters = {
            "HTML Report": "HTML Files (*.html)",
            "JSON Data": "JSON Files (*.json)",
            "Text Summary": "Text Files (*.txt)",
        }

        filename, _ = QFileDialog.getSaveFileName(
            self,
            f"Save {format_name}",
            f"linting_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            filters[format_name],
        )

        if filename:
            try:
                if format_name == "HTML Report":
                    self._export_html(filename)
                elif format_name == "JSON Data":
                    self._export_json(filename)
                else:  # Text Summary
                    self._export_text(filename)

                QMessageBox.information(
                    self, "Export Complete", f"Results exported to:\n{filename}"
                )
                self.accept()

            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"Failed to export: {e}")

    def _export_html(self, filename):
        """Export as HTML report"""
        html_content = self._generate_html_report()
        with open(filename, "w", encoding="utf-8") as f:
            f.write(html_content)

    def _export_json(self, filename):
        """Export as JSON data"""
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(self.session_data, f, indent=2, default=str)

    def _export_text(self, filename):
        """Export as plain text"""
        text_content = self._generate_text_report()
        with open(filename, "w", encoding="utf-8") as f:
            f.write(text_content)

    def _generate_html_report(self):
        """Generate HTML report"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Cascade Linter Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background: #3498db; color: white; padding: 20px; border-radius: 8px; }}
                .stats {{ display: flex; gap: 20px; margin: 20px 0; }}
                .stat-card {{ background: #f8f9fa; padding: 15px; border-radius: 8px; flex: 1; }}
                .issues {{ margin: 20px 0; }}
                .issue {{ background: #fff3cd; padding: 10px; margin: 10px 0; border-left: 4px solid #ffc107; }}
                .error {{ border-left-color: #dc3545; background: #f8d7da; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🌊 Cascade Linter Report</h1>
                <p>Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
            </div>
            
            <div class="stats">
                <div class="stat-card">
                    <h3>📁 Files Analyzed</h3>
                    <p>{self.session_data.get("total_files", 0)}</p>
                </div>
                <div class="stat-card">
                    <h3>🔍 Issues Found</h3>
                    <p>{self.session_data.get("total_issues", 0)}</p>
                </div>
                <div class="stat-card">
                    <h3>⏱️ Time Taken</h3>
                    <p>{self.session_data.get("total_time", 0):.1f}s</p>
                </div>
            </div>
            
            <div class="issues">
                <h2>Issues Summary</h2>
                <p>Detailed issue analysis would be generated here based on session data.</p>
            </div>
        </body>
        </html>
        """

    def _generate_text_report(self):
        """Generate text report"""
        return f"""
CASCADE LINTER REPORT
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

SUMMARY:
- Files Analyzed: {self.session_data.get("total_files", 0)}
- Issues Found: {self.session_data.get("total_issues", 0)}
- Time Taken: {self.session_data.get("total_time", 0):.1f}s

STAGE RESULTS:
{
            chr(10).join(
                f"- {stage}: {'PASSED' if result else 'FAILED'}"
                for stage, result in self.session_data.get("stage_results", {}).items()
            )
        }

---
Report generated by Cascade Linter GUI
        """


class RecentProjectsManager:
    """Manage recent projects list"""

    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.settings = QSettings("CascadeLinter", "RecentProjects")

    def add_project(self, path: str):
        """Add project to recent list"""
        recent = self.get_recent_projects()

        # Remove if already exists
        if path in recent:
            recent.remove(path)

        # Add to front
        recent.insert(0, path)

        # Keep only last 10
        recent = recent[:10]

        # Save
        self.settings.setValue("recent_projects", recent)

    def get_recent_projects(self) -> List[str]:
        """Get list of recent projects"""
        return self.settings.value("recent_projects", [])

    def clear_recent_projects(self):
        """Clear recent projects list"""
        self.settings.remove("recent_projects")


def setup_keyboard_shortcuts(main_window):
    """Set up keyboard shortcuts for the main window"""
    shortcuts = [
        ("F5", main_window._start_linting),
        ("Escape", main_window._stop_linting),
        ("Ctrl+O", main_window._browse_path),
        ("Ctrl+S", main_window._save_log),
        ("Ctrl+E", main_window._export_results),
        ("Ctrl+Shift+C", main_window.log_viewer.clear),
        ("F1", lambda: main_window.results_tabs.setCurrentIndex(0)),  # Issues tab
        ("F2", lambda: main_window.results_tabs.setCurrentIndex(1)),  # Dashboard tab
        ("F3", lambda: main_window.results_tabs.setCurrentIndex(2)),  # Log tab
    ]

    for key_sequence, slot in shortcuts:
        shortcut = QShortcut(QKeySequence(key_sequence), main_window)
        shortcut.activated.connect(slot)
