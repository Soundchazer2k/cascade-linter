# cascade_linter/gui/dialogs/SettingsDialog.py

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QTabWidget,
    QWidget,
    QFormLayout,
    QCheckBox,
    QSpinBox,
    QComboBox,
    QLabel,
    QPushButton,
    QLineEdit,
    QGroupBox,
    QMessageBox,
    QApplication,
)
from PySide6.QtCore import Qt, Signal, Slot

try:
    from ..tools.ConfigManager import ConfigManager, ConfigDefaults

    CONFIG_AVAILABLE = True
except ImportError:
    CONFIG_AVAILABLE = False

try:
    from ..tools.ThemeLoader import ThemeLoader

    THEME_LOADER_AVAILABLE = True
except ImportError:
    THEME_LOADER_AVAILABLE = False


class SettingsDialog(QDialog):
    """Enhanced Settings Dialog with ThemeLoader integration."""

    themeChanged = Signal(str)
    settingsSaved = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings - Cascade Linter")
        self.setModal(True)
        self.resize(500, 400)

        # Store original theme for cancel functionality
        self.original_theme = None
        if THEME_LOADER_AVAILABLE:
            app = QApplication.instance()
            self.original_theme = ThemeLoader.get_current_theme(app) or "system"

        self._setup_ui()
        # Apply theme instead of hardcoded styling
        self._apply_theme()
        if CONFIG_AVAILABLE:
            self._load_settings()

    def _setup_ui(self):
        """Create basic UI with three tabs."""
        layout = QVBoxLayout(self)

        # Tab widget
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)

        # Create tabs
        self._create_general_tab()
        self._create_linters_tab()
        self._create_interface_tab()

        # Enhanced buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.btn_cancel = QPushButton("✖ Cancel")
        self.btn_cancel.setToolTip("Cancel changes and restore original theme")
        self.btn_apply = QPushButton("✓ Apply")
        self.btn_apply.setToolTip("Apply changes without closing")
        self.btn_save = QPushButton("💾 Save & Close")
        self.btn_save.setToolTip("Save all changes and close dialog")

        # Style the save button prominently
        self.btn_save.setStyleSheet(
            """
            QPushButton {
                background-color: #3465a4;
                color: white;
                font-weight: bold;
                padding: 10px 16px;
                font-size: 10pt;
            }
            QPushButton:hover {
                background-color: #204a87;
            }
        """
        )

        button_layout.addWidget(self.btn_cancel)
        button_layout.addWidget(self.btn_apply)
        button_layout.addWidget(self.btn_save)
        layout.addLayout(button_layout)

        # Connect buttons
        self.btn_cancel.clicked.connect(self._cancel_with_theme_restore)
        self.btn_apply.clicked.connect(self._apply_settings)
        self.btn_save.clicked.connect(self._save_settings)

    def _create_general_tab(self):
        """Create General tab with improved grouping and clarity."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Auto-Fix Configuration Group (better grouping of related settings)
        autofix_group = QGroupBox("Auto-Fix Configuration")
        autofix_form = QFormLayout(autofix_group)

        self.combo_mode = QComboBox()
        self.combo_mode.addItems(["Auto-Fix Mode", "Check-Only Mode"])
        self.combo_mode.setToolTip(
            "Choose whether to automatically fix issues or just report them"
        )

        self.chk_unsafe = QCheckBox("Apply unsafe fixes")
        self.chk_unsafe.setToolTip("Allow fixes that might change code behavior")

        self.chk_gitignore = QCheckBox("Respect .gitignore files")
        self.chk_gitignore.setToolTip("Skip files and directories listed in .gitignore")

        autofix_form.addRow("Default mode:", self.combo_mode)
        autofix_form.addRow("Options:", self.chk_unsafe)
        autofix_form.addRow("", self.chk_gitignore)

        layout.addWidget(autofix_group)

        # Default Linters Group (clearer section title)
        linters_group = QGroupBox("Default Enabled Linters")
        linters_group.setToolTip("Choose which linters to run by default")
        linters_layout = QVBoxLayout(linters_group)

        # Create a grid layout for better organization
        linters_grid = QHBoxLayout()

        # Column 1: Core linters
        core_col = QVBoxLayout()
        core_label = QLabel("Core Linters:")
        core_label.setStyleSheet("font-weight: bold; color: palette(highlight);")
        core_col.addWidget(core_label)

        self.chk_ruff = QCheckBox("Ruff (fast Python linter)")
        self.chk_flake8 = QCheckBox("Flake8 (style guide)")
        core_col.addWidget(self.chk_ruff)
        core_col.addWidget(self.chk_flake8)

        # Column 2: Analysis linters
        analysis_col = QVBoxLayout()
        analysis_label = QLabel("Analysis:")
        analysis_label.setStyleSheet("font-weight: bold; color: palette(highlight);")
        analysis_col.addWidget(analysis_label)

        self.chk_pylint = QCheckBox("Pylint (code quality)")
        self.chk_bandit = QCheckBox("Bandit (security)")
        self.chk_mypy = QCheckBox("MyPy (type checking)")
        analysis_col.addWidget(self.chk_pylint)
        analysis_col.addWidget(self.chk_bandit)
        analysis_col.addWidget(self.chk_mypy)

        linters_grid.addLayout(core_col)
        linters_grid.addLayout(analysis_col)
        linters_grid.addStretch()

        linters_layout.addLayout(linters_grid)
        layout.addWidget(linters_group)

        # Log Management Group (improved tooltips)
        log_group = QGroupBox("Log Management")
        log_form = QFormLayout(log_group)

        self.spin_keep_days = QSpinBox()
        self.spin_keep_days.setRange(1, 365)
        self.spin_keep_days.setValue(30)
        self.spin_keep_days.setSuffix(" days")
        self.spin_keep_days.setToolTip(
            "How long to keep log files before automatic cleanup"
        )

        self.spin_max_logs = QSpinBox()
        self.spin_max_logs.setRange(1, 1000)
        self.spin_max_logs.setValue(100)
        self.spin_max_logs.setSuffix(" files")
        self.spin_max_logs.setToolTip("Maximum number of log files to keep")

        log_form.addRow("Keep logs for:", self.spin_keep_days)
        log_form.addRow("Max log files:", self.spin_max_logs)

        layout.addWidget(log_group)
        layout.addStretch()

        self.tab_widget.addTab(tab, "General")

    def _create_linters_tab(self):
        """Create Linters tab with comprehensive controls."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Global Code Style Settings
        style_group = QGroupBox("Global Code Style")
        style_form = QFormLayout(style_group)

        self.spin_line_length = QSpinBox()
        self.spin_line_length.setRange(50, 200)
        self.spin_line_length.setValue(88)
        self.spin_line_length.setSuffix(" chars")

        self.combo_quote_style = QComboBox()
        self.combo_quote_style.addItems(["Double", "Single"])

        self.chk_import_sorting = QCheckBox("Enable import sorting")

        style_form.addRow("Max line length:", self.spin_line_length)
        style_form.addRow("Quote style:", self.combo_quote_style)
        style_form.addRow("", self.chk_import_sorting)

        layout.addWidget(style_group)

        # Ruff Configuration
        ruff_group = QGroupBox("Ruff Configuration")
        ruff_form = QFormLayout(ruff_group)

        self.edit_ruff_ignore = QLineEdit()
        self.edit_ruff_ignore.setPlaceholderText("E203,W503,F401")

        self.edit_ruff_select = QLineEdit()
        self.edit_ruff_select.setPlaceholderText("E,W,F,UP,B,SIM")

        self.chk_ruff_show_fixes = QCheckBox("Show available fixes")

        ruff_form.addRow("Ignore rules:", self.edit_ruff_ignore)
        ruff_form.addRow("Select rules:", self.edit_ruff_select)
        ruff_form.addRow("", self.chk_ruff_show_fixes)

        layout.addWidget(ruff_group)

        # Flake8 Configuration
        flake8_group = QGroupBox("Flake8 Configuration")
        flake8_form = QFormLayout(flake8_group)

        self.edit_flake8_ignore = QLineEdit()
        self.edit_flake8_ignore.setPlaceholderText("E203,W503")

        self.spin_flake8_complexity = QSpinBox()
        self.spin_flake8_complexity.setRange(1, 20)
        self.spin_flake8_complexity.setValue(10)

        flake8_form.addRow("Ignore rules:", self.edit_flake8_ignore)
        flake8_form.addRow("Max complexity:", self.spin_flake8_complexity)

        layout.addWidget(flake8_group)

        # Pylint Configuration
        pylint_group = QGroupBox("Pylint Configuration")
        pylint_form = QFormLayout(pylint_group)

        self.edit_pylint_disable = QLineEdit()
        self.edit_pylint_disable.setPlaceholderText("C0103,R0903")

        self.spin_pylint_jobs = QSpinBox()
        self.spin_pylint_jobs.setRange(1, 16)
        self.spin_pylint_jobs.setValue(1)

        pylint_form.addRow("Disable rules:", self.edit_pylint_disable)
        pylint_form.addRow("Parallel jobs:", self.spin_pylint_jobs)

        layout.addWidget(pylint_group)

        layout.addStretch()

        self.tab_widget.addTab(tab, "Linters")

    def _create_interface_tab(self):
        """Create Interface tab with comprehensive controls."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Theme Settings
        theme_group = QGroupBox("Theme")
        theme_form = QFormLayout(theme_group)

        # Enhanced theme selector with ThemeLoader integration
        self.combo_theme = QComboBox()
        if THEME_LOADER_AVAILABLE:
            # Use ThemeLoader's theme list for consistency
            for index, name, display_name in ThemeLoader.get_available_themes():
                self.combo_theme.addItem(display_name)
        else:
            # Fallback list
            self.combo_theme.addItems(
                [
                    "System Default",
                    "Light",
                    "Dark",
                    "Solarized Light",
                    "Solarized Dark",
                    "Dracula",
                    "Dweeb",
                    "Retro Green",
                    "Corps",
                ]
            )

        self.combo_theme.setToolTip(
            "Choose the application theme - changes apply immediately"
        )

        self.chk_animations = QCheckBox("Enable animations")

        theme_form.addRow("Theme:", self.combo_theme)
        theme_form.addRow("", self.chk_animations)

        layout.addWidget(theme_group)

        # Log Viewer Settings
        log_group = QGroupBox("Log Viewer")
        log_form = QFormLayout(log_group)

        self.spin_log_font_size = QSpinBox()
        self.spin_log_font_size.setRange(8, 20)
        self.spin_log_font_size.setValue(10)
        self.spin_log_font_size.setSuffix(" pt")

        self.chk_show_line_numbers = QCheckBox("Show line numbers")
        self.chk_auto_scroll = QCheckBox("Auto-scroll log")
        self.chk_word_wrap = QCheckBox("Enable word wrap")

        log_form.addRow("Font size:", self.spin_log_font_size)
        log_form.addRow("", self.chk_show_line_numbers)
        log_form.addRow("", self.chk_auto_scroll)
        log_form.addRow("", self.chk_word_wrap)

        layout.addWidget(log_group)

        # Window Settings
        window_group = QGroupBox("Window")
        window_form = QFormLayout(window_group)

        self.chk_remember_size = QCheckBox("Remember window size")
        self.chk_minimize_to_tray = QCheckBox("Minimize to system tray")
        self.chk_start_minimized = QCheckBox("Start minimized")

        window_form.addRow("", self.chk_remember_size)
        window_form.addRow("", self.chk_minimize_to_tray)
        window_form.addRow("", self.chk_start_minimized)

        layout.addWidget(window_group)

        # Keyboard Shortcuts Info
        shortcuts_group = QGroupBox("Keyboard Shortcuts")
        shortcuts_layout = QVBoxLayout(shortcuts_group)

        shortcuts_label = QLabel(
            "<b>Global Shortcuts:</b><br/>"
            "• F5: Quick Lint<br/>"
            "• Shift+F5: Full Lint<br/>"
            "• F6: Batch Processing<br/>"
            "• Ctrl+O: Open Directory<br/>"
            "• Ctrl+E: Export Results<br/>"
            "• Ctrl+,: Settings<br/>"
            "• F1: Help<br/>"
            "• Esc: Cancel/Close"
        )
        shortcuts_label.setWordWrap(True)
        shortcuts_label.setObjectName("shortcuts")
        shortcuts_label.setStyleSheet(
            """
            QLabel#shortcuts {
                color: #000000;
                background-color: rgba(240, 240, 240, 0.9);
                padding: 12px;
                border: 1px solid #cccccc;
                border-radius: 6px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 9pt;
            }
        """
        )
        shortcuts_layout.addWidget(shortcuts_label)

        layout.addWidget(shortcuts_group)

        layout.addStretch()

        # Connect theme changes for live preview
        self.combo_theme.currentIndexChanged.connect(self._on_theme_changed)

        self.tab_widget.addTab(tab, "Interface")

    def _apply_theme(self):
        """Apply current theme instead of hardcoded styling."""
        try:
            if THEME_LOADER_AVAILABLE:
                app = QApplication.instance()
                if app:
                    # Theme is already applied globally, just clear any hardcoded styles
                    self.setStyleSheet("")
            else:
                # Fallback minimal styling
                self.setStyleSheet(
                    """
                    QDialog {
                        font-family: "Segoe UI", "Ubuntu", sans-serif;
                        font-size: 10pt;
                    }
                """
                )
        except Exception as e:
            print(f"Error applying theme to settings dialog: {e}")
            # Clear any styling to let parent theme take over
            self.setStyleSheet("")

    def _load_settings(self):
        """Load settings from ConfigManager."""
        if not CONFIG_AVAILABLE:
            return

        try:
            ConfigDefaults.apply_defaults()

            # General Tab - Mode Settings
            check_only = ConfigManager.get_bool("General/CheckOnly", False)
            self.combo_mode.setCurrentIndex(1 if check_only else 0)
            self.chk_unsafe.setChecked(
                ConfigManager.get_bool("General/UnsafeFixes", False)
            )
            self.chk_gitignore.setChecked(
                ConfigManager.get_bool("General/RespectGitignore", True)
            )

            # General Tab - Linter Enablement
            self.chk_ruff.setChecked(
                ConfigManager.get_bool("Linters/RuffEnabled", True)
            )
            self.chk_flake8.setChecked(
                ConfigManager.get_bool("Linters/Flake8Enabled", True)
            )
            self.chk_pylint.setChecked(
                ConfigManager.get_bool("Linters/PylintEnabled", True)
            )
            self.chk_bandit.setChecked(
                ConfigManager.get_bool("Linters/BanditEnabled", True)
            )
            self.chk_mypy.setChecked(
                ConfigManager.get_bool("Linters/MyPyEnabled", True)
            )

            # General Tab - Log Management
            self.spin_keep_days.setValue(
                ConfigManager.get_int("General/KeepLogsDays", 30)
            )
            self.spin_max_logs.setValue(
                ConfigManager.get_int("General/MaxLogFiles", 100)
            )

            # Linters Tab - Global Settings
            self.spin_line_length.setValue(
                ConfigManager.get_int("Linters/MaxLineLength", 88)
            )
            quote_style = ConfigManager.get_string("Linters/QuoteStyle", "Double")
            self.combo_quote_style.setCurrentText(quote_style)
            self.chk_import_sorting.setChecked(
                ConfigManager.get_bool("Linters/ImportSorting", True)
            )

            # Linters Tab - Ruff Settings
            self.edit_ruff_ignore.setText(
                ConfigManager.get_string("Linters/RuffIgnore", "E203,W503,F401")
            )
            self.edit_ruff_select.setText(
                ConfigManager.get_string("Linters/RuffSelect", "E,W,F,UP,B,SIM")
            )
            self.chk_ruff_show_fixes.setChecked(
                ConfigManager.get_bool("Linters/RuffShowFixes", True)
            )

            # Linters Tab - Flake8 Settings
            self.edit_flake8_ignore.setText(
                ConfigManager.get_string("Linters/Flake8Ignore", "E203,W503")
            )
            self.spin_flake8_complexity.setValue(
                ConfigManager.get_int("Linters/Flake8Complexity", 10)
            )

            # Linters Tab - Pylint Settings
            self.edit_pylint_disable.setText(
                ConfigManager.get_string("Linters/PylintDisable", "C0103,R0903")
            )
            self.spin_pylint_jobs.setValue(
                ConfigManager.get_int("Linters/PylintJobs", 1)
            )

            # Interface Tab - Theme Settings
            theme_index = ConfigManager.get_int("Interface/Theme", 2)  # Default to Dark
            self.combo_theme.setCurrentIndex(theme_index)
            self.chk_animations.setChecked(
                ConfigManager.get_bool("Interface/AnimationsEnabled", True)
            )

            # Interface Tab - Log Viewer Settings
            self.spin_log_font_size.setValue(
                ConfigManager.get_int("Interface/LogFontSize", 10)
            )
            self.chk_show_line_numbers.setChecked(
                ConfigManager.get_bool("Interface/ShowLineNumbers", True)
            )
            self.chk_auto_scroll.setChecked(
                ConfigManager.get_bool("Interface/AutoScrollLog", True)
            )
            self.chk_word_wrap.setChecked(
                ConfigManager.get_bool("Interface/WordWrap", False)
            )

            # Interface Tab - Window Settings
            self.chk_remember_size.setChecked(
                ConfigManager.get_bool("Interface/RememberSize", True)
            )
            self.chk_minimize_to_tray.setChecked(
                ConfigManager.get_bool("Interface/MinimizeToTray", False)
            )
            self.chk_start_minimized.setChecked(
                ConfigManager.get_bool("Interface/StartMinimized", False)
            )

        except Exception as e:
            print(f"Error loading settings: {e}")

    @Slot()
    def _cancel_with_theme_restore(self):
        """Cancel and restore original theme."""
        if THEME_LOADER_AVAILABLE and self.original_theme:
            app = QApplication.instance()
            if app:
                ThemeLoader.load_theme(self.original_theme, app)
        self.reject()

    @Slot()
    def _apply_settings(self):
        """Apply settings without closing the dialog."""
        if not CONFIG_AVAILABLE:
            QMessageBox.information(
                self, "Settings", "Settings applied! (ConfigManager not available)"
            )
            return

        try:
            self._save_all_settings()
            self.settingsSaved.emit()
            QMessageBox.information(self, "Success", "Settings applied successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to apply settings: {e}")

    def _save_all_settings(self):
        """Helper method to save all settings without showing dialogs."""
        # General Tab - Mode Settings
        check_only = self.combo_mode.currentIndex() == 1
        ConfigManager.set_bool("General/CheckOnly", check_only)
        ConfigManager.set_bool("General/UnsafeFixes", self.chk_unsafe.isChecked())
        ConfigManager.set_bool(
            "General/RespectGitignore", self.chk_gitignore.isChecked()
        )

        # General Tab - Linter Enablement
        ConfigManager.set_bool("Linters/RuffEnabled", self.chk_ruff.isChecked())
        ConfigManager.set_bool("Linters/Flake8Enabled", self.chk_flake8.isChecked())
        ConfigManager.set_bool("Linters/PylintEnabled", self.chk_pylint.isChecked())
        ConfigManager.set_bool("Linters/BanditEnabled", self.chk_bandit.isChecked())
        ConfigManager.set_bool("Linters/MyPyEnabled", self.chk_mypy.isChecked())

        # General Tab - Log Management
        ConfigManager.set_int("General/KeepLogsDays", self.spin_keep_days.value())
        ConfigManager.set_int("General/MaxLogFiles", self.spin_max_logs.value())

        # Linters Tab - Global Settings
        ConfigManager.set_int("Linters/MaxLineLength", self.spin_line_length.value())
        ConfigManager.set_string(
            "Linters/QuoteStyle", self.combo_quote_style.currentText()
        )
        ConfigManager.set_bool(
            "Linters/ImportSorting", self.chk_import_sorting.isChecked()
        )

        # Linters Tab - Ruff Settings
        ConfigManager.set_string(
            "Linters/RuffIgnore", self.edit_ruff_ignore.text().strip()
        )
        ConfigManager.set_string(
            "Linters/RuffSelect", self.edit_ruff_select.text().strip()
        )
        ConfigManager.set_bool(
            "Linters/RuffShowFixes", self.chk_ruff_show_fixes.isChecked()
        )

        # Linters Tab - Flake8 Settings
        ConfigManager.set_string(
            "Linters/Flake8Ignore", self.edit_flake8_ignore.text().strip()
        )
        ConfigManager.set_int(
            "Linters/Flake8Complexity", self.spin_flake8_complexity.value()
        )

        # Linters Tab - Pylint Settings
        ConfigManager.set_string(
            "Linters/PylintDisable", self.edit_pylint_disable.text().strip()
        )
        ConfigManager.set_int("Linters/PylintJobs", self.spin_pylint_jobs.value())

        # Interface Tab - Theme Settings
        ConfigManager.set_int("Interface/Theme", self.combo_theme.currentIndex())
        ConfigManager.set_bool(
            "Interface/AnimationsEnabled", self.chk_animations.isChecked()
        )

        # Interface Tab - Log Viewer Settings
        ConfigManager.set_int("Interface/LogFontSize", self.spin_log_font_size.value())
        ConfigManager.set_bool(
            "Interface/ShowLineNumbers", self.chk_show_line_numbers.isChecked()
        )
        ConfigManager.set_bool(
            "Interface/AutoScrollLog", self.chk_auto_scroll.isChecked()
        )
        ConfigManager.set_bool("Interface/WordWrap", self.chk_word_wrap.isChecked())

        # Interface Tab - Window Settings
        ConfigManager.set_bool(
            "Interface/RememberSize", self.chk_remember_size.isChecked()
        )
        ConfigManager.set_bool(
            "Interface/MinimizeToTray", self.chk_minimize_to_tray.isChecked()
        )
        ConfigManager.set_bool(
            "Interface/StartMinimized", self.chk_start_minimized.isChecked()
        )

    @Slot()
    def _save_settings(self):
        """Save all settings and close dialog."""
        if not CONFIG_AVAILABLE:
            QMessageBox.information(
                self, "Settings", "Settings saved! (ConfigManager not available)"
            )
            self.accept()
            return

        try:
            self._save_all_settings()

            # Update the original theme since we're accepting changes
            if THEME_LOADER_AVAILABLE:
                app = QApplication.instance()
                if app:
                    self.original_theme = ThemeLoader.get_current_theme(app)

            # Emit signal for theme changes and other updates
            self.settingsSaved.emit()

            QMessageBox.information(self, "Success", "Settings saved successfully!")
            self.accept()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save settings: {e}")

    @Slot(int)
    def _on_theme_changed(self, theme_index: int):
        """Handle theme changes with live preview."""
        if THEME_LOADER_AVAILABLE:
            app = QApplication.instance()
            if app:
                theme_name = ThemeLoader.get_theme_name_by_index(theme_index)
                success = ThemeLoader.load_theme(theme_name, app)
                if success:
                    self.themeChanged.emit(theme_name)
        else:
            # Fallback: emit theme name based on index
            theme_names = [
                "system",
                "light",
                "dark",
                "solarized-light",
                "solarized-dark",
                "dracula",
                "dweeb",
                "retro-green",
                "corps",
            ]
            if 0 <= theme_index < len(theme_names):
                self.themeChanged.emit(theme_names[theme_index])


def show_settings_dialog(parent=None):
    """Convenience function to show the settings dialog."""
    dialog = SettingsDialog(parent)
    accepted = dialog.exec() == QDialog.Accepted
    return accepted, dialog


if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    dialog = SettingsDialog()
    dialog.show()
    sys.exit(app.exec())
