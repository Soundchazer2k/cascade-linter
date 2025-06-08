#!/usr/bin/env python3
"""
Enhanced Main Window for Cascade Linter - Professional Code Quality Tool
========================================================================

Features:
- Two-tab layout: "Run Analysis" and "Analytics"
- Professional integration with existing widgets
- Real backend integration for linting and analysis
- Clean, functional UI following user specifications
"""

import sys
from pathlib import Path
from typing import List, Dict, Optional, Any

# PySide6 imports
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QTabWidget,
    QGroupBox,
    QLabel,
    QPushButton,
    QListWidget,
    QProgressBar,
    QFileDialog,
    QApplication,
    QMessageBox,
    QTextEdit,
)
from PySide6.QtCore import Qt, Signal, Slot, QThread
from PySide6.QtGui import QFont, QAction, QKeySequence

# Import existing widgets with proper typing
METRIC_CARD_AVAILABLE = False
LOG_VIEWER_AVAILABLE = False
ANALYTICS_TAB_AVAILABLE = False

MetricCard = None
LogViewer = None
create_analytics_tab = None

try:
    from cascade_linter.gui.widgets.MetricCard import MetricCard

    METRIC_CARD_AVAILABLE = True
except ImportError:
    pass

try:
    from cascade_linter.gui.widgets.LogViewer import LogViewer

    LOG_VIEWER_AVAILABLE = True
except ImportError:
    pass

try:
    from cascade_linter.gui.widgets.analytics_tab import create_analytics_tab

    ANALYTICS_TAB_AVAILABLE = True
except ImportError:
    pass

# Settings dialog import
try:
    from cascade_linter.gui.dialogs.SettingsDialog import show_settings_dialog

    SETTINGS_DIALOG_AVAILABLE = True
except ImportError:
    SETTINGS_DIALOG_AVAILABLE = False

from cascade_linter.gui.tools.beginner_helpers import BeginnerFriendlyHelpers


class LintingWorker(QThread):
    """Worker thread for running linting operations"""

    progress_updated = Signal(str, int)  # linter_name, progress_percentage
    stage_completed = Signal(str)  # linter_name
    linting_completed = Signal(dict)  # results
    log_message = Signal(str)  # log_html

    def __init__(
        self,
        directories: List[str],
        quick_mode: bool = False,
        main_window: Optional["ModernMainWindow"] = None,
    ):
        super().__init__()
        self.directories = directories
        self.quick_mode = quick_mode
        self.main_window = main_window  # Reference to main window for beginner mode
        self.process = None
        # Accumulate metrics across directories
        self.total_files = 0
        self.total_issues = 0
        self.total_fixed = 0

    def run(self) -> None:
        """Run the linting process"""
        try:
            if self.quick_mode:
                # Quick lint (Ruff only)
                self.run_quick_lint()
            else:
                # Full cascade lint
                self.run_full_lint()
        except Exception as e:
            self.log_message.emit(
                f'<span style="color: #cc0000;">ERROR: {str(e)}</span>'
            )

    def run_quick_lint(self) -> None:
        """Run real quick lint (Ruff only) with detailed results"""
        self.log_message.emit(
            '<span style="color: #2196F3;">🚀 Quick Lint started (Ruff-only mode)</span>'
        )

        for directory in self.directories:
            self.log_message.emit(
                f'<span style="color: #FFC107;">📁 Analyzing directory: {directory}</span>'
            )

            try:
                # Import and run real linting
                from cascade_linter.core import run_cascade_lint

                # Create progress callback
                callback = self.create_progress_callback()

                # Run actual linting
                session = run_cascade_lint(
                    path=directory, stages=["ruff"], callback=callback, debug=False
                )

                # Process and display detailed results
                self.process_session_results(session)

            except ImportError:
                # Fallback to simulated results if core is unavailable
                self.log_message.emit(
                    '<span style="color: #FF9800;">⚠️ Core CLI unavailable, running in demo mode</span>'
                )
                self.run_fallback_quick_lint()
            except Exception as e:
                self.log_message.emit(
                    f'<span style="color: #FF5722;">❌ Error analyzing {directory}: {str(e)}</span>'
                )

        # Final completion with real accumulated metrics
        results = {
            "success": True,
            "total_files": self.total_files,
            "issues_found": self.total_issues,
            "auto_fixed": self.total_fixed,
        }
        self.linting_completed.emit(results)

    def run_fallback_quick_lint(self) -> None:
        """Fallback quick lint for demo purposes"""
        # Simulate Ruff progress
        for progress in range(0, 101, 10):
            if self.isInterruptionRequested():
                return
            self.progress_updated.emit("ruff", progress)
            self.msleep(100)

        self.stage_completed.emit("Ruff")
        self.log_message.emit(
            '<span style="color: #4CAF50;">✓ Ruff completed (demo mode)</span>'
        )

    def run_fallback_full_lint(self) -> None:
        """Fallback full lint for demo purposes"""
        linters = ["ruff", "flake8", "pylint", "bandit", "mypy"]
        linter_names = ["Ruff", "Flake8", "Pylint", "Bandit", "MyPy"]

        for linter, name in zip(linters, linter_names):
            if self.isInterruptionRequested():
                return

            self.log_message.emit(
                f'<span style="color: #2196F3;">▶ Starting {name} (demo mode)...</span>'
            )

            # Simulate progress for this linter
            for progress in range(0, 101, 5):
                if self.isInterruptionRequested():
                    return
                self.progress_updated.emit(linter, progress)
                self.msleep(50)

            self.stage_completed.emit(name)
            self.log_message.emit(
                f'<span style="color: #4CAF50;">✓ {name} completed (demo mode)</span>'
            )

    def create_progress_callback(self):
        """Create a callback for progress updates"""
        try:
            from cascade_linter.core import LinterProgressCallback

            class GUIProgressCallback(LinterProgressCallback):
                def __init__(self, worker):
                    super().__init__()
                    self.worker = worker

                def on_progress(self, message: str):
                    self.worker.log_message.emit(
                        f'<span style="color: #9E9E9E;">{message}</span>'
                    )

                def on_stage_start(self, stage_name: str):
                    self.worker.progress_updated.emit(stage_name.lower(), 0)
                    self.worker.log_message.emit(
                        f'<span style="color: #2196F3;">▶ Starting {stage_name}...</span>'
                    )

                def on_stage_finish(
                    self, stage_name: str, success: bool, duration: float
                ):
                    self.worker.progress_updated.emit(stage_name.lower(), 100)
                    self.worker.stage_completed.emit(stage_name)

                    status = "✅ completed" if success else "❌ failed"
                    color = "#4CAF50" if success else "#FF5722"
                    self.worker.log_message.emit(
                        f'<span style="color: {color};">{stage_name} {status} in {duration:.2f}s</span>'
                    )

            return GUIProgressCallback(self)
        except ImportError:
            return None

    def process_session_results(self, session) -> None:
        """Process and display detailed session results"""
        # Accumulate metrics
        self.total_files += session.total_files_with_issues
        self.total_issues += session.total_issues
        self.total_fixed += session.total_fixes_applied

        # Display summary
        self.log_message.emit(
            f'<span style="color: #4CAF50;">📊 Analysis complete: {session.total_issues} issues found in {session.total_files_with_issues} files</span>'
        )

        if session.total_fixes_applied > 0:
            self.log_message.emit(
                f'<span style="color: #4CAF50;">🔧 {session.total_fixes_applied} issues automatically fixed</span>'
            )

        # Display detailed issues by file
        if session.issues_by_file:
            self.log_message.emit(
                '<span style="color: #FF9800;">⚠️ Detailed Issues Found:</span>'
            )

            for file_path, issues in sorted(session.issues_by_file.items()):
                # Show file header
                from pathlib import Path

                try:
                    relative_path = str(Path(file_path).relative_to(Path.cwd()))
                except ValueError:
                    relative_path = file_path

                self.log_message.emit(
                    f'<span style="color: #2196F3; font-weight: bold;">📄 {relative_path} ({len(issues)} issues)</span>'
                )

                # Sort issues by line number
                sorted_issues = sorted(issues, key=lambda x: (x.line, x.column))

                for issue in sorted_issues:
                    # Check if we should use beginner-friendly formatting
                    if self.main_window and self.main_window.beginner_mode:
                        # Use beginner-friendly formatting
                        friendly_line = (
                            BeginnerFriendlyHelpers.format_friendly_error_line(
                                issue.code, issue.message, issue.line, issue.column
                            )
                        )
                        self.log_message.emit(friendly_line)
                    else:
                        # Standard formatting
                        severity_colors = {
                            "error": "#FF5722",
                            "warning": "#FF9800",
                            "info": "#2196F3",
                        }
                        color = severity_colors.get(
                            issue.severity.severity_name, "#FF9800"
                        )

                        # Format the issue line
                        fixable_icon = "🔧" if issue.fixable else "👨‍💻"
                        issue_line = (
                            f'<span style="color: {color};">   {fixable_icon} Line {issue.line}:{issue.column} '
                            f"[{issue.code}] {issue.message}</span>"
                        )
                        self.log_message.emit(issue_line)

                # Add some spacing
                self.log_message.emit('<span style="color: #555;">   </span>')

    def run_full_lint(self) -> None:
        """Run real full lint (all 5 stages) with detailed results"""
        self.log_message.emit(
            '<span style="color: #4CAF50;">🚀 Full Lint started (5-stage cascade)</span>'
        )

        last_session = None  # Store the last session for export

        for directory in self.directories:
            self.log_message.emit(
                f'<span style="color: #FFC107;">📁 Analyzing directory: {directory}</span>'
            )

            try:
                # Import and run real linting
                from cascade_linter.core import run_cascade_lint

                # Create progress callback
                callback = self.create_progress_callback()

                # Run actual linting with all 5 stages explicitly
                session = run_cascade_lint(
                    path=directory,
                    stages=["ruff", "flake8", "pylint", "bandit", "mypy"],
                    callback=callback,
                    debug=False,
                )

                # Store the session for export (use the last one if multiple directories)
                last_session = session

                # Process and display detailed results
                self.process_session_results(session)

            except ImportError:
                # Fallback to simulated results if core is unavailable
                self.log_message.emit(
                    '<span style="color: #FF9800;">⚠️ Core CLI unavailable, running in demo mode</span>'
                )
                self.run_fallback_full_lint()
            except Exception as e:
                self.log_message.emit(
                    f'<span style="color: #FF5722;">❌ Error analyzing {directory}: {str(e)}</span>'
                )

        # Final completion with real accumulated metrics and session
        results = {
            "success": True,
            "total_files": self.total_files,
            "issues_found": self.total_issues,
            "auto_fixed": self.total_fixed,
            "session": last_session,  # Include the session for export
        }
        self.linting_completed.emit(results)


class ModernMainWindow(QMainWindow):
    """
    Enhanced Main Window for Cascade Linter - Professional Code Quality Tool

    Two-tab layout following user specifications:
    1. Run Analysis - Directory selection, linting progress, activity log
    2. Analytics - Dependency analysis, risk assessment, action items
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cascade Linter – Professional Code Quality")
        self.setGeometry(100, 100, 1200, 800)

        # State
        self.selected_directories: List[str] = []
        self.current_worker: Optional[LintingWorker] = None
        self.progress_bars: Dict[str, QProgressBar] = {}
        self.percentage_labels: Dict[str, QLabel] = {}

        # Initialize beginner mode state
        self.beginner_mode = False

        # Setup UI
        self.setup_ui()
        self.apply_theme()

    def setup_ui(self):
        """Setup the main UI layout"""
        # Create menu bar
        self.create_menu_bar()

        # Create central tab widget
        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)

        # Create tabs
        self.run_tab = self.create_run_analysis_tab()
        self.analytics_tab = self.create_analytics_tab()
        self.autofix_tab = self.create_autofix_tab()

        # Add tabs to tab widget
        self.tab_widget.addTab(self.run_tab, "Run Analysis")
        self.tab_widget.addTab(self.analytics_tab, "Analytics")
        self.tab_widget.addTab(self.autofix_tab, "🔧 Auto-Fix")

        # Create status bar
        self.create_status_bar()

    def create_menu_bar(self):
        """Create the application menu bar"""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("&File")

        open_action = QAction("&Open Directory", self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(self.add_directory)
        file_menu.addAction(open_action)

        file_menu.addSeparator()

        exit_action = QAction("E&xit", self)
        exit_action.setShortcut(QKeySequence("Ctrl+Q"))
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Tools menu
        tools_menu = menubar.addMenu("&Tools")

        quick_lint_action = QAction("&Quick Lint (Ruff)", self)
        quick_lint_action.setShortcut(QKeySequence("F5"))
        quick_lint_action.triggered.connect(self.start_quick_lint)
        tools_menu.addAction(quick_lint_action)

        full_lint_action = QAction("&Full Lint (All)", self)
        full_lint_action.setShortcut(QKeySequence("Shift+F5"))
        full_lint_action.triggered.connect(self.start_full_lint)
        tools_menu.addAction(full_lint_action)

        # Settings menu
        settings_menu = menubar.addMenu("&Settings")

        settings_action = QAction("&Preferences...", self)
        settings_action.setShortcut(QKeySequence("Ctrl+,"))
        settings_action.triggered.connect(self.show_settings)
        settings_menu.addAction(settings_action)

        # Help menu
        help_menu = menubar.addMenu("&Help")

        # Add beginner mode toggle to settings menu
        settings_menu.addSeparator()

        self.beginner_mode_action = QAction("🎓 &Beginner Mode", self)
        self.beginner_mode_action.setCheckable(True)
        self.beginner_mode_action.setChecked(self.beginner_mode)
        self.beginner_mode_action.setToolTip(
            "Show extra explanations and learning tips"
        )
        self.beginner_mode_action.triggered.connect(self.toggle_beginner_mode)
        settings_menu.addAction(self.beginner_mode_action)

    def create_run_analysis_tab(self):
        """Create the Run Analysis tab exactly as specified"""
        tab_widget = QWidget()
        layout = QVBoxLayout(tab_widget)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        # Top section: Three-column layout
        top_layout = QHBoxLayout()

        # === LEFT: Selected Directories ===
        dir_group = QGroupBox("📁 Selected Directories:")
        dir_layout = QVBoxLayout(dir_group)

        # Directory list
        self.dir_list = QListWidget()
        self.dir_list.setMinimumHeight(200)
        dir_layout.addWidget(self.dir_list)

        # Directory buttons
        self.add_dir_btn = QPushButton("Add Directory")
        self.add_dir_btn.clicked.connect(self.add_directory)
        dir_layout.addWidget(self.add_dir_btn)

        self.remove_dir_btn = QPushButton("Remove Selected")
        self.remove_dir_btn.clicked.connect(self.remove_selected_directory)
        dir_layout.addWidget(self.remove_dir_btn)

        self.clear_dirs_btn = QPushButton("Clear All")
        self.clear_dirs_btn.clicked.connect(self.clear_all_directories)
        dir_layout.addWidget(self.clear_dirs_btn)

        dir_layout.addStretch()
        top_layout.addWidget(dir_group, 1)

        # === CENTER: Metrics Overview + Progress ===
        center_widget = QWidget()
        center_layout = QVBoxLayout(center_widget)

        # Metrics Overview
        metrics_group = QGroupBox("📊 Metrics Overview:")
        metrics_layout = QHBoxLayout(metrics_group)

        if MetricCard:
            self.card_total = MetricCard("Total Files", 0, "📁")
            self.card_issues = MetricCard("Issues Found", 0, "⚠️")
            self.card_fixed = MetricCard("Auto-Fixed", 0, "🔧")

            metrics_layout.addWidget(self.card_total)
            metrics_layout.addWidget(self.card_issues)
            metrics_layout.addWidget(self.card_fixed)
        else:
            # Fallback if MetricCard not available
            self.card_total = QLabel("📁 Total Files: 0")
            self.card_issues = QLabel("⚠️ Issues Found: 0")
            self.card_fixed = QLabel("🔧 Auto-Fixed: 0")

            metrics_layout.addWidget(self.card_total)
            metrics_layout.addWidget(self.card_issues)
            metrics_layout.addWidget(self.card_fixed)

        metrics_layout.addStretch()
        center_layout.addWidget(metrics_group)

        # Linter Progress Section
        progress_group = QGroupBox("🎯 Linter Progress (5-Stage Cascade):")
        progress_layout = QGridLayout(progress_group)

        linters = ["ruff", "flake8", "pylint", "bandit", "mypy"]
        linter_names = ["🔧 Ruff", "🐍 Flake8", "🔍 Pylint", "🛡️ Bandit", "📝 MyPy"]

        for i, (linter, name) in enumerate(zip(linters, linter_names)):
            # Linter name label
            name_label = QLabel(name)
            name_label.setMinimumWidth(80)
            progress_layout.addWidget(name_label, i, 0)

            # Progress bar
            progress_bar = QProgressBar()
            progress_bar.setMinimum(0)
            progress_bar.setMaximum(100)
            progress_bar.setValue(0)
            progress_bar.setFormat("%v%")
            progress_layout.addWidget(progress_bar, i, 1)

            # Percentage label
            percent_label = QLabel("0%")
            percent_label.setMinimumWidth(40)
            percent_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            progress_layout.addWidget(percent_label, i, 2)

            # Store references
            self.progress_bars[linter] = progress_bar
            self.percentage_labels[linter] = percent_label

        center_layout.addWidget(progress_group)
        center_layout.addStretch()

        top_layout.addWidget(center_widget, 2)

        # === RIGHT: Run Analysis Button ===
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)

        self.run_btn = QPushButton("🚀 Run Analysis")
        self.run_btn.setMinimumHeight(50)
        self.run_btn.setMinimumWidth(150)
        self.run_btn.clicked.connect(self.start_full_lint)
        right_layout.addWidget(self.run_btn)

        self.quick_btn = QPushButton("⚡ Quick Lint (Ruff)")
        self.quick_btn.setMinimumHeight(40)
        self.quick_btn.clicked.connect(self.start_quick_lint)
        right_layout.addWidget(self.quick_btn)

        self.stop_btn = QPushButton("⏹️ Stop")
        self.stop_btn.setMinimumHeight(40)
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self.stop_linting)
        right_layout.addWidget(self.stop_btn)

        # Export button for linting results
        self.export_btn = QPushButton("📤 Export Results")
        self.export_btn.setMinimumHeight(40)
        self.export_btn.setEnabled(False)  # Initially disabled
        self.export_btn.clicked.connect(self.export_linting_results)
        right_layout.addWidget(self.export_btn)

        right_layout.addStretch()

        top_layout.addWidget(right_widget, 1)

        layout.addLayout(top_layout)

        # === BOTTOM: Activity Log ===
        log_group = QGroupBox("📝 Activity Log:")
        log_layout = QVBoxLayout(log_group)

        if LogViewer:
            self.log_viewer = LogViewer()
        else:
            # Fallback
            self.log_viewer = QTextEdit()
            self.log_viewer.setReadOnly(True)
            self.log_viewer.setPlaceholderText(
                "Logs will appear here when linting starts..."
            )

        self.log_viewer.setMinimumHeight(200)
        log_layout.addWidget(self.log_viewer)

        layout.addWidget(log_group, 1)  # Expand to fill space

        return tab_widget

    def create_analytics_tab(self):
        """Create the Analytics tab using existing analytics widget"""
        if create_analytics_tab:
            # Use existing analytics tab
            analytics_widget = create_analytics_tab(self)
            self.analytics_tab = analytics_widget
        else:
            # Fallback analytics tab
            analytics_widget = QWidget()
            layout = QVBoxLayout(analytics_widget)

            label = QLabel("📊 Analytics Dashboard")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setFont(QFont("Segoe UI", 16))
            layout.addWidget(label)

            placeholder = QLabel(
                "Advanced dependency analysis and reporting features will be available here."
            )
            placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(placeholder)

            self.analytics_tab = analytics_widget

        return analytics_widget

    def create_autofix_tab(self):
        """Create the Auto-Fix tab for intelligent automatic issue fixing"""
        tab_widget = QWidget()
        layout = QVBoxLayout(tab_widget)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        # Header section
        header_group = QGroupBox("🔧 Intelligent Auto-Fix")
        header_layout = QVBoxLayout(header_group)

        description = QLabel(
            "Automatically detects and fixes safe formatting issues from linting results.\n"
            "This tool analyzes your linting log and only fixes issues that are 100% safe (no logic changes)."
        )
        description.setWordWrap(True)
        header_layout.addWidget(description)

        layout.addWidget(header_group)

        # Status and controls section
        controls_group = QGroupBox("📊 Analysis Status")
        controls_layout = QHBoxLayout(controls_group)

        # Status labels
        status_layout = QVBoxLayout()
        self.autofix_status_label = QLabel(
            "Status: Ready - Run a linting analysis first"
        )
        self.autofix_issues_found = QLabel("Fixable Issues: Not analyzed yet")
        self.autofix_last_session = QLabel("Last Analysis: None")

        status_layout.addWidget(self.autofix_status_label)
        status_layout.addWidget(self.autofix_issues_found)
        status_layout.addWidget(self.autofix_last_session)

        controls_layout.addLayout(status_layout)

        # Control buttons
        button_layout = QVBoxLayout()

        self.autofix_analyze_btn = QPushButton("🔍 Analyze Current Results")
        self.autofix_analyze_btn.setMinimumHeight(40)
        self.autofix_analyze_btn.setEnabled(False)
        self.autofix_analyze_btn.clicked.connect(self.analyze_fixable_issues)
        button_layout.addWidget(self.autofix_analyze_btn)

        self.autofix_run_btn = QPushButton("🔧 Auto-Fix Safe Issues")
        self.autofix_run_btn.setMinimumHeight(40)
        self.autofix_run_btn.setEnabled(False)
        self.autofix_run_btn.clicked.connect(self.run_auto_fix)
        button_layout.addWidget(self.autofix_run_btn)

        self.autofix_preview_btn = QPushButton("👀 Preview Changes")
        self.autofix_preview_btn.setMinimumHeight(40)
        self.autofix_preview_btn.setEnabled(False)
        self.autofix_preview_btn.clicked.connect(self.preview_autofix_changes)
        button_layout.addWidget(self.autofix_preview_btn)

        button_layout.addStretch()
        controls_layout.addLayout(button_layout)

        layout.addWidget(controls_group)

        # Fixable issues details section
        details_group = QGroupBox("🎯 Fixable Issues Detected")
        details_layout = QVBoxLayout(details_group)

        # Safe issues list
        self.autofix_safe_list = QListWidget()
        self.autofix_safe_list.setMinimumHeight(150)
        details_layout.addWidget(QLabel("Safe to auto-fix (no logic changes):"))
        details_layout.addWidget(self.autofix_safe_list)

        # Unsafe issues list
        self.autofix_unsafe_list = QListWidget()
        self.autofix_unsafe_list.setMinimumHeight(100)
        details_layout.addWidget(QLabel("Requires manual review:"))
        details_layout.addWidget(self.autofix_unsafe_list)

        layout.addWidget(details_group)

        # Auto-fix activity log
        autofix_log_group = QGroupBox("📝 Auto-Fix Activity Log")
        autofix_log_layout = QVBoxLayout(autofix_log_group)

        self.autofix_log = QTextEdit()
        self.autofix_log.setMinimumHeight(200)
        self.autofix_log.setReadOnly(True)
        autofix_log_layout.addWidget(self.autofix_log)

        layout.addWidget(autofix_log_group)

        # Initialize autofix data
        self.fixable_issues = []
        self.unsafe_issues = []
        self.current_session = None

        return tab_widget

    def create_status_bar(self):
        """Create the status bar"""
        self.status_label = QLabel("Ready - Select directories and start linting")
        self.statusBar().addWidget(self.status_label)

    def apply_theme(self):
        """Apply the current theme using ThemeLoader"""
        try:
            from .tools.ThemeLoader import ThemeLoader

            app = QApplication.instance()
            if app:
                # Try to get current theme from config or default to dark
                try:
                    from .tools.ConfigManager import ConfigManager

                    theme_index = ConfigManager.get_int(
                        "Interface/Theme", 2
                    )  # Default to dark
                    theme_name = ThemeLoader.get_theme_name_by_index(theme_index)
                    if not theme_name:
                        theme_name = "dark"
                except ImportError:
                    theme_name = "dark"

                success = ThemeLoader.load_theme(theme_name, app)
                if not success:
                    # Fallback to basic dark theme if ThemeLoader fails
                    self.apply_fallback_styling()
            else:
                self.apply_fallback_styling()
        except ImportError:
            # ThemeLoader not available, use fallback
            self.apply_fallback_styling()

    def apply_fallback_styling(self):
        """Fallback basic styling if ThemeLoader is unavailable"""
        style = """
        QMainWindow {
            background-color: #121212;
            color: #E0E0E0;
        }
        QWidget {
            background-color: #121212;
            color: #E0E0E0;
        }
        QTabWidget::pane {
            border: 1px solid #444;
            background-color: #1E1E1E;
            border-radius: 4px;
        }
        QTabBar::tab {
            background-color: #2D2D2D;
            color: #E0E0E0;
            padding: 10px 16px;
            margin: 1px;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
            border: 1px solid #444;
            border-bottom: none;
        }
        QTabBar::tab:selected {
            background-color: #4CAF50;
            color: white;
            border-color: #4CAF50;
        }
        QTabBar::tab:hover:!selected {
            background-color: #3D3D3D;
        }
        QGroupBox {
            font-weight: bold;
            border: 2px solid #555;
            border-radius: 8px;
            margin-top: 12px;
            padding-top: 12px;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            subcontrol-position: top left;
            left: 10px;
            padding: 0 8px 0 8px;
            background-color: #121212;
        }
        QPushButton {
            background-color: #2196F3;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #1976D2;
        }
        QPushButton:pressed {
            background-color: #1565C0;
        }
        QPushButton:disabled {
            background-color: #555;
            color: #888;
        }
        QListWidget {
            background-color: #1E1E1E;
            border: 1px solid #333;
            border-radius: 4px;
        }
        QProgressBar {
            border: 2px solid #333;
            border-radius: 5px;
            text-align: center;
            background-color: #1E1E1E;
        }
        QProgressBar::chunk {
            background-color: #4CAF50;
            border-radius: 3px;
        }
        QLabel {
            color: #E0E0E0;
        }
        QMenuBar {
            background-color: #2D2D2D;
            color: #E0E0E0;
        }
        QMenuBar::item:selected {
            background-color: #4CAF50;
        }
        QMenu {
            background-color: #2D2D2D;
            color: #E0E0E0;
            border: 1px solid #333;
        }
        QMenu::item:selected {
            background-color: #4CAF50;
        }
        """
        self.setStyleSheet(style)

    # === DIRECTORY MANAGEMENT ===

    @Slot()
    def add_directory(self):
        """Add a directory for analysis"""
        directory = QFileDialog.getExistingDirectory(
            self, "Select Python Project Directory", str(Path.home())
        )

        if directory:
            # Check for duplicates
            if directory not in self.selected_directories:
                self.selected_directories.append(directory)
                self.dir_list.addItem(directory)
                self.update_ui_state()
            else:
                QMessageBox.information(
                    self,
                    "Duplicate Directory",
                    f"Directory already added:\n{directory}",
                )

    @Slot()
    def remove_selected_directory(self):
        """Remove selected directory"""
        current_row = self.dir_list.currentRow()
        if current_row >= 0:
            item = self.dir_list.takeItem(current_row)
            if item:
                self.selected_directories.remove(item.text())
                self.update_ui_state()

    @Slot()
    def clear_all_directories(self):
        """Clear all directories"""
        self.dir_list.clear()
        self.selected_directories.clear()
        self.update_ui_state()

    def update_ui_state(self):
        """Update UI state based on selections"""
        has_dirs = len(self.selected_directories) > 0
        self.run_btn.setEnabled(has_dirs)
        self.quick_btn.setEnabled(has_dirs)
        self.remove_dir_btn.setEnabled(self.dir_list.currentRow() >= 0)
        self.clear_dirs_btn.setEnabled(has_dirs)

        # Update analytics tab if available
        if hasattr(self.analytics_tab, "set_directories_from_main_window"):
            self.analytics_tab.set_directories_from_main_window(
                self.selected_directories
            )

    # === LINTING OPERATIONS ===

    @Slot()
    def start_quick_lint(self):
        """Start quick lint (Ruff only)"""
        if not self.selected_directories:
            QMessageBox.warning(
                self,
                "No Directories",
                "Please select at least one directory to analyze.",
            )
            return

        self.start_linting(quick_mode=True)

    @Slot()
    def start_full_lint(self):
        """Start full lint (all 5 stages)"""
        if not self.selected_directories:
            QMessageBox.warning(
                self,
                "No Directories",
                "Please select at least one directory to analyze.",
            )
            return

        self.start_linting(quick_mode=False)

    def start_linting(self, quick_mode: bool = False):
        """Start linting process"""
        # Reset progress
        self.reset_progress()

        # Update UI state
        self.run_btn.setEnabled(False)
        self.quick_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)

        # Update status
        mode_text = "Quick Lint" if quick_mode else "Full Lint"
        self.status_label.setText(f"{mode_text}: Starting...")

        # Start worker thread
        self.current_worker = LintingWorker(self.selected_directories, quick_mode, self)
        self.current_worker.progress_updated.connect(self.on_progress_updated)
        self.current_worker.stage_completed.connect(self.on_stage_completed)
        self.current_worker.linting_completed.connect(self.on_linting_completed)
        self.current_worker.log_message.connect(self.on_log_message)
        self.current_worker.start()

    @Slot()
    def stop_linting(self):
        """Stop linting process"""
        if self.current_worker:
            self.current_worker.requestInterruption()
            self.current_worker.wait(5000)  # Wait up to 5 seconds
            self.current_worker = None

        # Reset UI state
        self.run_btn.setEnabled(True)
        self.quick_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)

        self.status_label.setText("⏹️ Linting stopped by user")
        self.on_log_message('<span style="color: #FF9800;">⏹️ Linting stopped</span>')

    def reset_progress(self):
        """Reset all progress indicators"""
        for progress_bar in self.progress_bars.values():
            progress_bar.setValue(0)
        for label in self.percentage_labels.values():
            label.setText("0%")

    # === SIGNAL HANDLERS ===

    @Slot(str, int)
    def on_progress_updated(self, linter_name: str, progress: int):
        """Handle progress updates"""
        if linter_name in self.progress_bars:
            self.progress_bars[linter_name].setValue(progress)
            self.percentage_labels[linter_name].setText(f"{progress}%")

        self.status_label.setText(f"Running {linter_name.title()}... {progress}%")

    @Slot(str)
    def on_stage_completed(self, linter_name: str):
        """Handle stage completion"""
        if linter_name.lower() in self.progress_bars:
            self.progress_bars[linter_name.lower()].setValue(100)
            self.percentage_labels[linter_name.lower()].setText("100%")

    @Slot(dict)
    def on_linting_completed(self, results: Dict[str, Any]):
        """Handle linting completion"""
        # Store session object separately
        self.current_session = results.get("session")

        # Store results for export, excluding non-serializable session object
        self.last_linting_results = {k: v for k, v in results.items() if k != "session"}

        # Update metrics
        if MetricCard and hasattr(self, "card_total"):
            self.card_total.set_value(results.get("total_files", 0))
            self.card_issues.set_value(results.get("issues_found", 0))
            self.card_fixed.set_value(results.get("auto_fixed", 0))

        # Reset UI state
        self.run_btn.setEnabled(True)
        self.quick_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.export_btn.setEnabled(True)  # Enable export after completion

        # Enable auto-fix analysis if we have a session
        if hasattr(self, "autofix_analyze_btn") and self.current_session:
            self.autofix_analyze_btn.setEnabled(True)
            if hasattr(self, "autofix_status_label"):
                self.autofix_status_label.setText(
                    "Status: New analysis available - Click 'Analyze Current Results'"
                )

        # Update status
        total = results.get("total_files", 0)
        issues = results.get("issues_found", 0)
        fixed = results.get("auto_fixed", 0)
        self.status_label.setText(
            f"✅ Linting complete: {total} files, {issues} issues, {fixed} auto-fixed"
        )

        self.on_log_message(
            '<span style="color: #4CAF50;">🎉 Linting completed successfully!</span>'
        )

        # Clean up worker
        self.current_worker = None

    @Slot(str)
    def on_log_message(self, html_message: str):
        """Handle log messages"""
        if hasattr(self.log_viewer, "append_html"):
            self.log_viewer.append_html(html_message)
        else:
            # Fallback for basic QTextEdit
            self.log_viewer.append(html_message)

    @Slot()
    def show_settings(self):
        """Show the settings dialog"""
        if SETTINGS_DIALOG_AVAILABLE:
            try:
                from .dialogs.SettingsDialog import SettingsDialog

                dialog = SettingsDialog(self)

                # Connect theme change signal to refresh our theme
                dialog.themeChanged.connect(self.on_theme_changed)
                dialog.settingsSaved.connect(self.on_settings_saved)

                dialog.exec()
            except Exception as e:
                QMessageBox.warning(
                    self, "Settings Error", f"Failed to open settings dialog:\n{str(e)}"
                )
        else:
            QMessageBox.information(
                self,
                "Settings Unavailable",
                "Settings dialog is not available.\nPlease check if all components are properly installed.",
            )

    @Slot(str)
    def on_theme_changed(self, theme_name: str):
        """Handle theme change from settings dialog"""
        # Theme is already applied by settings dialog, just refresh if needed
        pass

    @Slot()
    def on_settings_saved(self):
        """Handle settings save completion"""
        # Refresh theme to ensure consistency
        self.apply_theme()

    @Slot()
    def toggle_beginner_mode(self) -> None:
        """Toggle beginner mode on/off"""
        self.beginner_mode = self.beginner_mode_action.isChecked()

        # Update status bar to show current mode
        mode_text = (
            "🎓 Beginner Mode: ON" if self.beginner_mode else "Professional Mode"
        )
        self.status_label.setText(f"Ready - {mode_text}")

        # Add a visual indication in the activity log
        if hasattr(self, "log_viewer") and self.log_viewer:
            if self.beginner_mode:
                welcome_msg = """
                <div style="background: #1f5e4a; padding: 12px; border-radius: 6px; margin: 8px 0; border-left: 4px solid #93e7ae;">
                    <span style="color: #93e7ae; font-weight: bold;">🎓 Beginner Mode Activated!</span><br>
                    <span style="color: #daffd4; font-size: 11px;">
                        Error messages will now include explanations and learning tips. 
                        Look for priority badges: 🚨 URGENT, ⚠️ SOON, 💡 IMPROVE
                    </span>
                </div>
                """
            else:
                welcome_msg = """
                <div style="background: #0a2c24; padding: 12px; border-radius: 6px; margin: 8px 0; border-left: 4px solid #17815d;">
                    <span style="color: #daffd4; font-weight: bold;">👨‍💻 Professional Mode</span><br>
                    <span style="color: #93e7ae; font-size: 11px;">
                        Standard error display mode activated.
                    </span>
                </div>
                """

            if hasattr(self.log_viewer, "append_html"):
                self.log_viewer.append_html(welcome_msg)
            elif hasattr(self.log_viewer, "append"):
                self.log_viewer.append(
                    "🎓 Beginner mode toggled"
                    if self.beginner_mode
                    else "👨‍💻 Professional mode activated"
                )

    @Slot()
    def export_linting_results(self):
        """Export linting results with multiple format options"""
        if not hasattr(self, "last_linting_results") or not self.last_linting_results:
            QMessageBox.information(
                self, "No Data", "No linting results available to export."
            )
            return

        from PySide6.QtWidgets import QFileDialog
        from datetime import datetime

        # Offer multiple export formats including comprehensive JSON
        filename, selected_filter = QFileDialog.getSaveFileName(
            self,
            "Export Linting Results",
            f"linting_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            "Comprehensive JSON Report (*.json);;JSON Summary (*.json);;CSV Data (*.csv);;HTML Report (*.html);;Detailed Text Report (*.txt);;Activity Log (*.txt);;All Formats (*.*)",
        )

        if filename:
            try:
                # Route to appropriate export method based on selection
                if "Activity Log Only" in selected_filter:
                    if not filename.endswith(".txt"):
                        filename = filename.rsplit(".", 1)[0] + ".txt"
                    self._export_activity_log(filename)
                elif "Basic JSON" in selected_filter:
                    if not filename.endswith(".json"):
                        filename = filename.rsplit(".", 1)[0] + ".json"
                    self._export_to_json(filename)
                elif (
                    filename.endswith(".json")
                    or "Comprehensive JSON" in selected_filter
                    or "JSON" in selected_filter
                ):
                    self._export_comprehensive_json(filename)
                elif filename.endswith(".csv") or "CSV" in selected_filter:
                    self._export_to_csv(filename)
                elif filename.endswith(".html") or "HTML" in selected_filter:
                    self._export_to_html(filename)
                elif filename.endswith(".txt") or "Text Summary" in selected_filter:
                    self._export_to_text(filename)
                else:
                    # Default to comprehensive JSON if unclear
                    if not filename.endswith((".json", ".csv", ".html", ".txt")):
                        filename += ".json"
                    self._export_comprehensive_json(filename)

                self.status_label.setText(f"📤 Results exported to {filename}")
                QMessageBox.information(
                    self,
                    "Export Complete",
                    f"Results successfully exported to:\n{filename}",
                )
            except Exception as e:
                error_msg = f"Export failed: {str(e)}"
                self.status_label.setText(error_msg)
                QMessageBox.warning(self, "Export Error", error_msg)

    def _export_comprehensive_json(self, filename: str):
        """Export comprehensive linting results with all log data and session details"""
        import json
        from datetime import datetime

        # Create comprehensive export data
        export_data = {
            "metadata": {
                "export_timestamp": datetime.now().isoformat(),
                "tool_name": "Cascade Linter",
                "tool_version": "1.0.0",
                "analysis_type": "Comprehensive Code Quality Analysis",
                "export_format_version": "2.0",
            },
            "summary": {
                "total_files": self.last_linting_results.get("total_files", 0),
                "total_issues": self.last_linting_results.get("issues_found", 0),
                "total_fixes_applied": self.last_linting_results.get("auto_fixed", 0),
                "analysis_successful": self.last_linting_results.get("success", False),
            },
        }

        # Capture activity log content (this is the rich data from your logs!)
        if hasattr(self, "log_viewer") and self.log_viewer:
            try:
                if hasattr(self.log_viewer, "toPlainText"):
                    log_content = self.log_viewer.toPlainText()
                    if log_content:
                        log_lines = log_content.split("\n")
                        export_data["activity_log"] = {
                            "log_lines": log_lines,
                            "total_lines": len(log_lines),
                            "note": "Complete activity log from GUI session",
                        }
                elif hasattr(self.log_viewer, "toHtml"):
                    # Try HTML version if available
                    html_content = self.log_viewer.toHtml()
                    if html_content:
                        export_data["activity_log_html"] = html_content
            except Exception as e:
                export_data["log_extraction_error"] = f"Could not extract log data: {e}"

        # Enhanced session data extraction
        if hasattr(self, "current_session") and self.current_session:
            session_data = {}
            try:
                # Basic session info
                for attr in [
                    "target_path",
                    "total_files_analyzed",
                    "total_files_with_issues",
                    "total_issues",
                ]:
                    if hasattr(self.current_session, attr):
                        value = getattr(self.current_session, attr, None)
                        if value is not None:
                            session_data[attr] = (
                                str(value)
                                if not isinstance(value, (int, float, bool))
                                else value
                            )

                # Timing info
                for time_attr in ["start_time", "end_time"]:
                    if hasattr(self.current_session, time_attr):
                        time_val = getattr(self.current_session, time_attr, None)
                        if time_val:
                            session_data[time_attr] = (
                                time_val.isoformat()
                                if hasattr(time_val, "isoformat")
                                else str(time_val)
                            )

                # Calculate duration if possible
                if "start_time" in session_data and "end_time" in session_data:
                    try:
                        start = getattr(self.current_session, "start_time", None)
                        end = getattr(self.current_session, "end_time", None)
                        if (
                            start
                            and end
                            and hasattr(start, "timestamp")
                            and hasattr(end, "timestamp")
                        ):
                            duration = end.timestamp() - start.timestamp()
                            session_data["duration_seconds"] = round(duration, 2)
                            session_data["duration_formatted"] = (
                                f"{duration:.2f} seconds"
                            )
                    except:
                        pass

                if session_data:
                    export_data["session_info"] = session_data

            except Exception as e:
                export_data["session_extraction_error"] = (
                    f"Could not serialize session data: {e}"
                )

        # Add all available results data
        export_data["detailed_results"] = self.last_linting_results

        # Include directories analyzed
        if hasattr(self, "directories_list") and self.directories_list:
            try:
                directories = []
                for i in range(self.directories_list.count()):
                    item = self.directories_list.item(i)
                    if item:
                        directories.append(item.text())
                if directories:
                    export_data["analyzed_directories"] = directories
            except:
                pass

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)

    def _export_activity_log(self, filename: str):
        """Export just the activity log as a text file"""
        from datetime import datetime

        if hasattr(self, "log_viewer") and self.log_viewer:
            try:
                if hasattr(self.log_viewer, "toPlainText"):
                    log_content = self.log_viewer.toPlainText()
                    if log_content:
                        with open(filename, "w", encoding="utf-8") as f:
                            f.write("CASCADE LINTER - ACTIVITY LOG\n")
                            f.write("=" * 50 + "\n")
                            f.write(
                                f"Exported: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                            )
                            f.write(log_content)
                    else:
                        with open(filename, "w", encoding="utf-8") as f:
                            f.write("No log content available to export.\n")
                else:
                    with open(filename, "w", encoding="utf-8") as f:
                        f.write("Log viewer does not support text export.\n")
            except Exception as e:
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(f"Error exporting log: {e}\n")
        else:
            with open(filename, "w", encoding="utf-8") as f:
                f.write("No log viewer available.\n")

    def _export_to_csv(self, filename: str):
        """Export linting results to CSV format - simplified for now"""
        import csv

        with open(filename, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Metric", "Value"])
            writer.writerow(
                ["Total Files", self.last_linting_results.get("total_files", 0)]
            )
            writer.writerow(
                ["Issues Found", self.last_linting_results.get("issues_found", 0)]
            )
            writer.writerow(
                ["Auto-Fixed", self.last_linting_results.get("auto_fixed", 0)]
            )

    def _export_to_html(self, filename: str):
        """Export linting results to HTML format"""
        from datetime import datetime

        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Cascade Linter Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        .metric {{ display: inline-block; margin: 20px; padding: 20px; background: #f0f0f0; border-radius: 8px; }}
        .metric-value {{ font-size: 2em; font-weight: bold; color: #333; }}
        .metric-label {{ color: #666; margin-top: 5px; }}
    </style>
</head>
<body>
    <h1>🔍 Cascade Linter Report</h1>
    <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    
    <div class="metric">
        <div class="metric-value">{self.last_linting_results.get('total_files', 0)}</div>
        <div class="metric-label">📁 Files Analyzed</div>
    </div>
    <div class="metric">
        <div class="metric-value">{self.last_linting_results.get('issues_found', 0)}</div>
        <div class="metric-label">⚠️ Issues Found</div>
    </div>
    <div class="metric">
        <div class="metric-value">{self.last_linting_results.get('auto_fixed', 0)}</div>
        <div class="metric-label">🔧 Auto-Fixed</div>
    </div>
</body>
</html>
        """

        with open(filename, "w", encoding="utf-8") as f:
            f.write(html_content)

    def _export_to_text(self, filename: str):
        """Export linting results to text format"""
        from datetime import datetime

        content = f"""
CASCADE LINTER REPORT
=====================
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

SUMMARY
-------
📁 Files Analyzed: {self.last_linting_results.get('total_files', 0)}
⚠️ Issues Found: {self.last_linting_results.get('issues_found', 0)}
🔧 Auto-Fixed: {self.last_linting_results.get('auto_fixed', 0)}

End of Report
        """

        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)

    # === AUTO-FIX METHODS ===

    @Slot()
    def analyze_fixable_issues(self):
        """Analyze current linting results to identify fixable issues"""
        # Force a fresh analysis instead of using cached session data
        # This ensures we analyze the current state of files, not old cached data
        if not self.selected_directories:
            self.autofix_log.append(
                "<span style='color: #FF5722;'>❌ No directories selected. Please select directories first.</span>"
            )
            return

        self.autofix_log.append(
            "<span style='color: #4CAF50;'>🔍 Running fresh analysis for auto-fix potential...</span>"
        )

        # Run a quick fresh analysis to get current session data
        self._run_fresh_analysis_for_autofix()

        # Now analyze the fresh session data
        self._analyze_session_for_fixable_issues()

    def _run_fresh_analysis_for_autofix(self):
        """Run a quick fresh analysis specifically for auto-fix to avoid cached data"""
        try:
            from cascade_linter.core import CodeQualityRunner, LinterStage

            # Create a fresh runner with gitignore support
            runner = CodeQualityRunner(
                debug=False, simple_output=True, respect_gitignore=True
            )

            # Run quick analysis on selected directories
            for directory in self.selected_directories:
                self.autofix_log.append(
                    f"<span style='color: #2196F3;'>📁 Analyzing {directory}...</span>"
                )

                # Run same analysis as Run Analysis tab to get all issues
                fresh_session = runner.run_linting_session(
                    path=directory,
                    stages=[
                        LinterStage.RUFF,
                        LinterStage.FLAKE8,
                    ],  # Include Flake8 for formatting issues
                    check_only=True,
                )

                # Update current session with fresh data
                self.current_session = fresh_session
                break  # Just analyze the first directory for now

            self.autofix_log.append(
                "<span style='color: #4CAF50;'>✅ Fresh analysis complete</span>"
            )

        except Exception as e:
            self.autofix_log.append(
                f"<span style='color: #FF5722;'>❌ Fresh analysis failed: {str(e)}</span>"
            )
            self.autofix_log.append(
                "<span style='color: #FF9800;'>⚠️ Using cached session data as fallback</span>"
            )

    def _analyze_session_for_fixable_issues(self):
        """Analyze the current session for fixable issues"""
        # Define safe-to-fix issue codes
        safe_codes = {
            "W291": "trailing whitespace",
            "W293": "blank line contains whitespace",
            "W292": "no newline at end of file",
            "W391": "blank line at end of file",
            "E231": 'missing whitespace after ","',
            "E225": "missing whitespace around operator",
            "E303": "too many blank lines",
            "E302": "expected 2 blank lines",
            "E305": "expected 2 blank lines after class or function definition",
            "E501": "line too long (can be auto-formatted safely)",
            "COM812": "trailing comma missing",
            "UP007": "use X | Y for type union",  # Ruff modernization
            "UP006": "use list instead of List for type annotations",
            "I001": "import block is un-sorted or un-formatted",  # isort issues
        }

        # Clear previous results
        self.fixable_issues = []
        self.unsafe_issues = []
        self.autofix_safe_list.clear()
        self.autofix_unsafe_list.clear()

        # Analyze session issues
        total_fixable = 0
        total_unsafe = 0

        try:
            if (
                hasattr(self.current_session, "issues_by_file")
                and self.current_session.issues_by_file
            ):
                for file_path, issues in self.current_session.issues_by_file.items():
                    for issue in issues:
                        is_safe = issue.code in safe_codes

                        issue_info = {
                            "file": file_path,
                            "line": issue.line,
                            "column": issue.column,
                            "code": issue.code,
                            "message": issue.message,
                            "description": safe_codes.get(issue.code, "Unknown issue"),
                        }

                        if is_safe:
                            self.fixable_issues.append(issue_info)
                            total_fixable += 1

                            # Add to safe list
                            list_item = f"[{issue.code}] {file_path}:{issue.line} - {safe_codes.get(issue.code, issue.message)}"
                            self.autofix_safe_list.addItem(list_item)
                        else:
                            self.unsafe_issues.append(issue_info)
                            total_unsafe += 1

                            # Add to unsafe list
                            list_item = f"[{issue.code}] {file_path}:{issue.line} - {issue.message}"
                            self.autofix_unsafe_list.addItem(list_item)

            # Update status
            self.autofix_status_label.setText(
                f"Status: Analysis complete - {total_fixable} fixable, {total_unsafe} require review"
            )
            self.autofix_issues_found.setText(
                f"Fixable Issues: {total_fixable} safe auto-fixes available"
            )

            from datetime import datetime

            self.autofix_last_session.setText(
                f"Last Analysis: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )

            # Enable buttons if we have fixable issues
            has_fixable = total_fixable > 0
            self.autofix_run_btn.setEnabled(has_fixable)
            self.autofix_preview_btn.setEnabled(has_fixable)

            # Log results
            self.autofix_log.append(
                "<span style='color: #4CAF50;'>✅ Analysis complete:</span>"
            )
            self.autofix_log.append(
                f"<span style='color: #4CAF50;'>   • {total_fixable} issues can be auto-fixed safely</span>"
            )
            self.autofix_log.append(
                f"<span style='color: #FF9800;'>   • {total_unsafe} issues require manual review</span>"
            )

            if total_fixable > 0:
                self.autofix_log.append(
                    "<span style='color: #2196F3;'>💡 Click 'Auto-Fix Safe Issues' to apply fixes automatically.</span>"
                )

        except Exception as e:
            self.autofix_log.append(
                f"<span style='color: #FF5722;'>❌ Error analyzing issues: {str(e)}</span>"
            )

    @Slot()
    def preview_autofix_changes(self):
        """Preview what changes would be made by auto-fix"""
        if not self.fixable_issues:
            self.autofix_log.append(
                "<span style='color: #FF5722;'>❌ No fixable issues to preview.</span>"
            )
            return

        self.autofix_log.append(
            "<span style='color: #4CAF50;'>👀 Previewing auto-fix changes...</span>"
        )

        # Group issues by file
        files_to_fix = {}
        for issue in self.fixable_issues:
            file_path = issue["file"]
            if file_path not in files_to_fix:
                files_to_fix[file_path] = []
            files_to_fix[file_path].append(issue)

        self.autofix_log.append(
            f"<span style='color: #2196F3;'>📋 Will process {len(files_to_fix)} files:</span>"
        )

        for file_path, issues in files_to_fix.items():
            from pathlib import Path

            try:
                relative_path = str(Path(file_path).relative_to(Path.cwd()))
            except ValueError:
                relative_path = file_path

            self.autofix_log.append(
                f"<span style='color: #FFC107;'>📄 {relative_path} ({len(issues)} fixes)</span>"
            )

            # Group by fix type
            fix_types = {}
            for issue in issues:
                fix_type = issue["description"]
                if fix_type not in fix_types:
                    fix_types[fix_type] = 0
                fix_types[fix_type] += 1

            for fix_type, count in fix_types.items():
                self.autofix_log.append(
                    f"<span style='color: #E0E0E0;'>   • {fix_type}: {count} fixes</span>"
                )

        self.autofix_log.append(
            "<span style='color: #4CAF50;'>ℹ️ These fixes are 100% safe - no logic changes will be made.</span>"
        )

    @Slot()
    def run_auto_fix(self):
        """Run automatic fixes on safe issues"""
        if not self.fixable_issues:
            self.autofix_log.append(
                "<span style='color: #FF5722;'>❌ No fixable issues available.</span>"
            )
            return

        self.autofix_log.append(
            "<span style='color: #4CAF50;'>🔧 Starting auto-fix process...</span>"
        )

        # Group issues by file
        files_to_fix = {}
        for issue in self.fixable_issues:
            file_path = issue["file"]
            if file_path not in files_to_fix:
                files_to_fix[file_path] = []
            files_to_fix[file_path].append(issue)

        fixed_count = 0
        error_count = 0

        try:
            import subprocess
            import sys
            from pathlib import Path

            # Process each file
            for file_path, issues in files_to_fix.items():
                try:
                    relative_path = str(Path(file_path).relative_to(Path.cwd()))
                except ValueError:
                    relative_path = file_path

                self.autofix_log.append(
                    f"<span style='color: #2196F3;'>🔧 Fixing {relative_path}...</span>"
                )

                # Use Ruff's auto-fix (fixes specific detected issues)
                # Only use safe fixes by default - unsafe fixes require explicit user consent
                ruff_cmd = [
                    sys.executable,
                    "-m",
                    "ruff",
                    "check",
                    file_path,
                    "--fix",
                ]

                # TODO: Add settings option for unsafe fixes
                # if self.settings_allow_unsafe_fixes:
                #     ruff_cmd.append("--unsafe-fixes")

                ruff_result = subprocess.run(
                    ruff_cmd,
                    capture_output=True,
                    text=True,
                )

                if ruff_result.returncode in [0, 1]:  # 0=clean, 1=fixed issues
                    self.autofix_log.append(
                        "<span style='color: #4CAF50;'>   ✅ Ruff auto-fix applied</span>"
                    )

                    # Also apply Black formatting for consistent style
                    black_result = subprocess.run(
                        [
                            sys.executable,
                            "-m",
                            "black",
                            file_path,
                            "--line-length",
                            "88",
                            "--quiet",
                        ],
                        capture_output=True,
                        text=True,
                    )

                    if black_result.returncode == 0:
                        self.autofix_log.append(
                            "<span style='color: #4CAF50;'>   ✅ Black formatting applied</span>"
                        )
                else:
                    self.autofix_log.append(
                        f"<span style='color: #FF9800;'>   ⚠️ Could not auto-fix {relative_path}</span>"
                    )
                    error_count += 1
                    continue

                # Count actual fixes by running analysis before and after
                # Count issues before fixing
                issues_before = len(issues)

                # Run quick check after fixing to count remaining issues
                check_result = subprocess.run(
                    [
                        sys.executable,
                        "-m",
                        "ruff",
                        "check",
                        file_path,
                    ],
                    capture_output=True,
                    text=True,
                )

                # Count remaining issues after fixing
                issues_after = (
                    len(check_result.stdout.split("\n"))
                    if check_result.stdout.strip()
                    else 0
                )

                # Calculate actual fixes applied
                file_fixes = max(0, issues_before - issues_after)
                fixed_count += file_fixes

                if file_fixes > 0:
                    self.autofix_log.append(
                        f"<span style='color: #4CAF50;'>   📊 {file_fixes} issues actually fixed ({issues_before} → {issues_after})</span>"
                    )
                else:
                    self.autofix_log.append(
                        "<span style='color: #FFC107;'>   📊 No issues fixed for this file</span>"
                    )

        except Exception as e:
            self.autofix_log.append(
                f"<span style='color: #FF5722;'>❌ Error during auto-fix: {str(e)}</span>"
            )
            error_count += 1

        # Final summary
        if fixed_count > 0:
            self.autofix_log.append(
                f"<span style='color: #4CAF50;'>🎉 Auto-fix complete! {fixed_count} issues fixed across {len(files_to_fix)} files.</span>"
            )

            if error_count == 0:
                self.autofix_log.append(
                    "<span style='color: #4CAF50;'>💡 Tip: Re-run analysis to see the improvements!</span>"
                )
            else:
                self.autofix_log.append(
                    f"<span style='color: #FF9800;'>⚠️ {error_count} files had issues during fixing.</span>"
                )

            # Suggest re-running analysis
            self.autofix_analyze_btn.setEnabled(True)
            self.autofix_status_label.setText(
                "Status: Auto-fix complete - Run analysis again to verify"
            )
        else:
            self.autofix_log.append(
                "<span style='color: #FF5722;'>❌ No issues were fixed. Check the error messages above.</span>"
            )


def main():
    """Main entry point"""
    app = QApplication(sys.argv)
    app.setApplicationName("Cascade Linter")
    app.setApplicationVersion("1.0.0")

    window = ModernMainWindow()
    window.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
