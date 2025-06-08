# cascade_linter/gui/widgets/analytics_tab.py
"""
Analytics Tab Widget - Real dependency analysis integration
Uses the working simple_analytics.py backend for actual Python AST analysis
"""

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QProgressBar,
    QGroupBox,
    QFrame,
    QSplitter,
    QComboBox,
    QFileDialog,
)
from PySide6.QtCore import Qt, Signal, QThread, QTimer
from PySide6.QtGui import QFont, QPalette, QPainter, QColor
from typing import List, Dict, Any, Optional
import os
from datetime import datetime

# Import our working analytics backend
try:
    from cascade_linter.gui.tools.simple_analytics import SimpleDependencyAnalyzer

    ANALYTICS_BACKEND_AVAILABLE = True
except ImportError:
    ANALYTICS_BACKEND_AVAILABLE = False


class AnalyticsWorker(QThread):
    """Worker thread for running dependency analysis"""

    progress_updated = Signal(str)
    analysis_completed = Signal(dict)
    analysis_failed = Signal(str)

    def __init__(self, directories: List[str]):
        super().__init__()
        self.directories = directories
        self.analyzer = SimpleDependencyAnalyzer()

    def run(self):
        """Run the analysis in background thread"""
        try:
            self.progress_updated.emit("Initializing analysis...")

            # Run analysis on all directories
            results = self.analyzer.analyze_project(self.directories)

            self.progress_updated.emit("Analysis complete!")
            self.analysis_completed.emit(results)

        except Exception as e:
            self.analysis_failed.emit(f"Analysis failed: {str(e)}")


class RiskDistributionWidget(QWidget):
    """Mini bar chart widget for risk distribution visualization"""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.critical_count = 0
        self.medium_count = 0
        self.low_count = 0
        self.setFixedHeight(60)
        self.setMinimumWidth(200)

    def update_data(self, critical: int, medium: int, low: int) -> None:
        """Update the risk distribution data"""
        self.critical_count = critical
        self.medium_count = medium
        self.low_count = low
        self.update()  # Trigger repaint

    def paintEvent(self, event) -> None:
        """Custom paint event to draw the mini bar chart"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Calculate total and proportions
        total = self.critical_count + self.medium_count + self.low_count
        if total == 0:
            return

        width = self.width() - 20  # Leave margins
        height = 30
        x_start = 10
        y_start = 15

        # Calculate bar widths
        critical_width = int((self.critical_count / total) * width) if total > 0 else 0
        medium_width = int((self.medium_count / total) * width) if total > 0 else 0
        low_width = width - critical_width - medium_width  # Remaining space

        # Draw bars
        current_x = x_start

        # Critical (red)
        if critical_width > 0:
            painter.fillRect(
                current_x, y_start, critical_width, height, QColor("#cc0000")
            )
            current_x += critical_width

        # Medium (orange)
        if medium_width > 0:
            painter.fillRect(
                current_x, y_start, medium_width, height, QColor("#f57900")
            )
            current_x += medium_width

        # Low (green)
        if low_width > 0:
            painter.fillRect(current_x, y_start, low_width, height, QColor("#73d216"))

        # Draw labels
        painter.setPen(QColor("#daffd4"))  # Retro green theme text color
        font = QFont()
        font.setPointSize(8)
        painter.setFont(font)

        # Draw counts below bars
        painter.drawText(x_start, y_start + height + 15, f"🔴 {self.critical_count}")
        painter.drawText(x_start + 60, y_start + height + 15, f"🟡 {self.medium_count}")
        painter.drawText(x_start + 120, y_start + height + 15, f"🟢 {self.low_count}")


class AnalyticsTab(QWidget):
    """Real Analytics Tab with live dependency analysis"""

    # Signals for main window integration
    analysisStarted = Signal()
    analysisCompleted = Signal(dict)
    statusChanged = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        # State
        self.directories_to_analyze: List[str] = []
        self.current_analysis: Optional[Dict[str, Any]] = None
        self.worker_thread: Optional[AnalyticsWorker] = None

        # Initialize UI
        self.init_ui()

        # Auto-refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_display)
        self.refresh_timer.start(5000)  # Refresh every 5 seconds if needed

    def init_ui(self):
        """Initialize the user interface"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(8)

        # === HEADER SECTION ===
        header_layout = QHBoxLayout()

        # Title
        title_label = QLabel("📊 Dependency Analytics")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        # Run Analysis Button
        self.btn_run_analysis = QPushButton("🔍 Run Analysis")
        self.btn_run_analysis.setEnabled(False)
        self.btn_run_analysis.clicked.connect(self.start_analysis)
        self.btn_run_analysis.setMinimumHeight(32)
        header_layout.addWidget(self.btn_run_analysis)

        # Export Button
        self.btn_export = QPushButton("📤 Export")
        self.btn_export.setEnabled(False)
        self.btn_export.clicked.connect(self.export_results)
        self.btn_export.setMinimumHeight(32)
        header_layout.addWidget(self.btn_export)

        main_layout.addLayout(header_layout)

        # === STATUS SECTION ===
        self.lbl_status = QLabel("Ready - Select directories to analyze")
        self.lbl_status.setStyleSheet(
            "QLabel { color: palette(highlight); font-weight: bold; }"
        )
        main_layout.addWidget(self.lbl_status)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)

        # === CONTENT SECTION ===
        content_splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left panel: Project Health Summary
        self.create_summary_panel(content_splitter)

        # Right panel: Detailed Results
        self.create_details_panel(content_splitter)

        content_splitter.setStretchFactor(0, 1)  # Summary panel gets 1/3
        content_splitter.setStretchFactor(1, 2)  # Details panel gets 2/3

        main_layout.addWidget(content_splitter, 1)  # Expand to fill space

    def create_summary_panel(self, parent):
        """Create the project health summary panel"""
        summary_frame = QFrame()
        summary_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        summary_layout = QVBoxLayout(summary_frame)

        # Project Health Card
        health_group = QGroupBox("📈 Project Health")
        health_layout = QGridLayout(health_group)

        # Health Grade
        self.lbl_health_grade = QLabel("—")
        self.lbl_health_grade.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_health_grade.setStyleSheet(
            """
            QLabel {
                font-size: 36pt;
                font-weight: bold;
                color: #73d216;
                border: 2px solid #73d216;
                border-radius: 8px;
                padding: 20px;
            }
        """
        )
        health_layout.addWidget(self.lbl_health_grade, 0, 0, 1, 2)

        # Metrics
        health_layout.addWidget(QLabel("Total Modules:"), 1, 0)
        self.lbl_total_modules = QLabel("0")
        self.lbl_total_modules.setStyleSheet("font-weight: bold;")
        health_layout.addWidget(self.lbl_total_modules, 1, 1)

        health_layout.addWidget(QLabel("Average Risk:"), 2, 0)
        self.lbl_avg_risk = QLabel("0.0")
        self.lbl_avg_risk.setStyleSheet("font-weight: bold;")
        health_layout.addWidget(self.lbl_avg_risk, 2, 1)

        summary_layout.addWidget(health_group)

        # Risk Distribution Card
        risk_group = QGroupBox("⚠️ Risk Distribution")
        risk_layout = QGridLayout(risk_group)

        # Risk Distribution Widget
        self.risk_distribution_widget = RiskDistributionWidget()
        risk_layout.addWidget(self.risk_distribution_widget, 0, 0, 1, 3)

        summary_layout.addWidget(risk_group)
        summary_layout.addStretch()

        parent.addWidget(summary_frame)

    def create_details_panel(self, parent):
        """Create the detailed results panel"""
        details_frame = QFrame()
        details_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        details_layout = QVBoxLayout(details_frame)

        # Filter controls
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Filter by risk:"))

        self.risk_filter = QComboBox()
        self.risk_filter.addItems(["All", "Critical", "Medium", "Low"])
        self.risk_filter.currentTextChanged.connect(self.apply_risk_filter)
        filter_layout.addWidget(self.risk_filter)

        filter_layout.addStretch()
        details_layout.addLayout(filter_layout)

        # Results table
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(6)
        self.results_table.setHorizontalHeaderLabels(
            ["Module", "Risk Level", "Lines", "Complexity", "Risk Factors", "File Path"]
        )

        # Configure table
        header = self.results_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)

        self.results_table.setAlternatingRowColors(True)
        self.results_table.setSelectionBehavior(
            self.results_table.SelectionBehavior.SelectRows
        )

        details_layout.addWidget(self.results_table)
        parent.addWidget(details_frame)

    def start_analysis(self):
        """Start dependency analysis in background thread"""
        if not self.directories_to_analyze:
            self.lbl_status.setText("No directories selected for analysis")
            self.lbl_status.setStyleSheet(
                "QLabel { color: palette(window-text); font-weight: bold; }"
            )
            return

        if not ANALYTICS_BACKEND_AVAILABLE:
            self.lbl_status.setText("Analytics backend not available")
            self.lbl_status.setStyleSheet(
                "QLabel { color: palette(window-text); font-weight: bold; }"
            )
            return

        # Prepare UI for analysis
        self.btn_run_analysis.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.lbl_status.setText("Starting dependency analysis...")
        self.lbl_status.setStyleSheet(
            "QLabel { color: palette(highlight); font-weight: bold; }"
        )

        # Emit signal for main window
        self.analysisStarted.emit()

        # Start worker thread
        self.worker_thread = AnalyticsWorker(self.directories_to_analyze)
        self.worker_thread.progress_updated.connect(self.on_progress_updated)
        self.worker_thread.analysis_completed.connect(self.on_analysis_completed)
        self.worker_thread.analysis_failed.connect(self.on_analysis_failed)
        self.worker_thread.start()

    def on_progress_updated(self, message: str):
        """Handle progress updates from worker thread"""
        self.lbl_status.setText(message)
        self.statusChanged.emit(message)

    def on_analysis_completed(self, results: Dict[str, Any]):
        """Handle completed analysis results"""
        self.current_analysis = results

        # Update UI
        self.progress_bar.setVisible(False)
        self.btn_run_analysis.setEnabled(True)
        self.btn_export.setEnabled(True)

        # Update display
        self.update_summary_display(results)
        self.update_details_table(results)

        # Update status
        total_modules = results.get("total_modules", 0)
        risk_distribution = results.get("risk_distribution", {})
        critical_count = risk_distribution.get("CRITICAL", 0)

        if critical_count > 0:
            self.lbl_status.setText(
                f"Analysis complete: {total_modules} modules, {critical_count} critical risks"
            )
            self.lbl_status.setStyleSheet(
                "QLabel { color: palette(window-text); font-weight: bold; }"
            )
        else:
            self.lbl_status.setText(
                f"Analysis complete: {total_modules} modules, all healthy"
            )
            self.lbl_status.setStyleSheet(
                "QLabel { color: palette(highlight); font-weight: bold; }"
            )

        # Emit signal for main window
        self.analysisCompleted.emit(results)

    def on_analysis_failed(self, error_message: str):
        """Handle analysis failure"""
        self.progress_bar.setVisible(False)
        self.btn_run_analysis.setEnabled(True)
        self.lbl_status.setText(f"Analysis failed: {error_message}")
        self.lbl_status.setStyleSheet(
            "QLabel { color: palette(window-text); font-weight: bold; }"
        )

    def update_summary_display(self, results: Dict[str, Any]):
        """Update the project health summary display"""
        project_health = results.get("project_health", {})
        risk_distribution = results.get("risk_distribution", {})

        # Health grade
        health_grade = project_health.get("health_grade", "—")
        self.lbl_health_grade.setText(health_grade)

        # Color based on grade
        if health_grade in ["A", "B"]:
            color = "#73d216"  # Green
        elif health_grade == "C":
            color = "#f57900"  # Orange
        else:
            color = "#cc0000"  # Red

        self.lbl_health_grade.setStyleSheet(
            f"""
            QLabel {{
                font-size: 36pt;
                font-weight: bold;
                color: {color};
                border: 2px solid {color};
                border-radius: 8px;
                padding: 20px;
            }}
        """
        )

        # Metrics
        self.lbl_total_modules.setText(str(results.get("total_modules", 0)))
        avg_risk = project_health.get("average_risk_score", 0)
        self.lbl_avg_risk.setText(f"{avg_risk:.2f}")

        # Risk distribution
        self.risk_distribution_widget.update_data(
            risk_distribution.get("CRITICAL", 0),
            risk_distribution.get("MEDIUM", 0),
            risk_distribution.get("LOW", 0),
        )

    def update_details_table(self, results: Dict[str, Any]):
        """Update the detailed results table"""
        modules = results.get("modules", {})
        risk_assessments = results.get("risk_assessments", {})

        # Clear existing data
        self.results_table.setRowCount(0)

        # Populate table
        for module_name, module_info in modules.items():
            assessment = risk_assessments.get(module_name, {})

            row = self.results_table.rowCount()
            self.results_table.insertRow(row)

            # Module name
            self.results_table.setItem(row, 0, QTableWidgetItem(module_name))

            # Risk level with color
            risk_level = assessment.get("risk_level", "LOW")
            risk_item = QTableWidgetItem(risk_level)
            if risk_level == "CRITICAL":
                risk_item.setBackground(QPalette().color(QPalette.ColorRole.Window))
                risk_item.setForeground(QPalette().color(QPalette.ColorRole.WindowText))
            self.results_table.setItem(row, 1, risk_item)

            # Lines of code
            lines = module_info.get("size_lines", 0)
            self.results_table.setItem(row, 2, QTableWidgetItem(str(lines)))

            # Complexity score
            complexity = module_info.get("complexity_score", 0)
            self.results_table.setItem(row, 3, QTableWidgetItem(f"{complexity:.1f}"))

            # Risk factors
            risk_factors = assessment.get("risk_factors", [])
            factors_text = "; ".join(risk_factors) if risk_factors else "None"
            self.results_table.setItem(row, 4, QTableWidgetItem(factors_text))

            # File path
            file_path = module_info.get("file_path", "")
            # Show relative path for readability
            if os.path.isabs(file_path):
                try:
                    file_path = os.path.relpath(file_path)
                except ValueError:
                    pass  # Keep absolute path if relpath fails
            self.results_table.setItem(row, 5, QTableWidgetItem(file_path))

        # Apply current filter
        self.apply_risk_filter()

    def apply_risk_filter(self):
        """Apply risk level filter to the table"""
        filter_text = self.risk_filter.currentText()

        if filter_text == "All":
            # Show all rows
            for row in range(self.results_table.rowCount()):
                self.results_table.setRowHidden(row, False)
        else:
            # Hide rows that don't match filter
            for row in range(self.results_table.rowCount()):
                risk_item = self.results_table.item(row, 1)
                if risk_item:
                    should_hide = risk_item.text() != filter_text.upper()
                    self.results_table.setRowHidden(row, should_hide)

    def export_results(self):
        """Export analysis results with comprehensive format options"""
        if not self.current_analysis:
            self.lbl_status.setText("No analysis data to export")
            self.lbl_status.setStyleSheet(
                "QLabel { color: palette(window-text); font-weight: bold; }"
            )
            return

        from datetime import datetime

        # Offer multiple export formats
        filename, selected_filter = QFileDialog.getSaveFileName(
            self,
            "Export Analysis Results",
            f"dependency_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            "JSON Report (*.json);;CSV Data (*.csv);;HTML Report (*.html);;Detailed Summary (*.txt);;All Formats (*.*)",
        )

        if filename:
            try:
                if filename.endswith(".json") or "JSON" in selected_filter:
                    self.export_to_json(filename)
                elif filename.endswith(".csv") or "CSV" in selected_filter:
                    self.export_to_csv(filename)
                elif filename.endswith(".html") or "HTML" in selected_filter:
                    self.export_to_html(filename)
                elif filename.endswith(".txt") or "Summary" in selected_filter:
                    self.export_to_text_summary(filename)
                else:
                    # Default to JSON if unclear
                    if not filename.endswith((".json", ".csv", ".html", ".txt")):
                        filename += ".json"
                    self.export_to_json(filename)

                self.lbl_status.setText(f"Results exported to {filename}")
                self.lbl_status.setStyleSheet(
                    "QLabel { color: palette(highlight); font-weight: bold; }"
                )
            except Exception as e:
                self.lbl_status.setText(f"Export failed: {str(e)}")
                self.lbl_status.setStyleSheet(
                    "QLabel { color: palette(window-text); font-weight: bold; }"
                )

    def export_to_json(self, filename: str):
        """Export comprehensive JSON report"""
        import json

        # Enhanced JSON with metadata
        export_data = {
            "metadata": {
                "export_timestamp": datetime.now().isoformat(),
                "tool_name": "Cascade Linter",
                "tool_version": "1.0.0",
                "analysis_type": "Dependency Analysis",
            },
            "summary": {
                "total_modules": self.current_analysis.get("total_modules", 0),
                "risk_distribution": self.current_analysis.get("risk_distribution", {}),
                "project_health": self.current_analysis.get("project_health", {}),
            },
            "detailed_results": self.current_analysis,
        }

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)

    def export_to_csv(self, filename: str):
        """Export results to CSV format"""
        import csv

        with open(filename, "w", newline="") as csvfile:
            writer = csv.writer(csvfile)

            # Header
            writer.writerow(
                [
                    "Module",
                    "Risk Level",
                    "Lines",
                    "Complexity",
                    "Risk Factors",
                    "File Path",
                ]
            )

            # Data from table
            for row in range(self.results_table.rowCount()):
                if not self.results_table.isRowHidden(row):
                    row_data = []
                    for col in range(self.results_table.columnCount()):
                        item = self.results_table.item(row, col)
                        row_data.append(item.text() if item else "")
                    writer.writerow(row_data)

    def export_to_html(self, filename: str):
        """Export results to professional HTML report"""

        # Get analysis data
        total_modules = self.current_analysis.get("total_modules", 0)
        risk_distribution = self.current_analysis.get("risk_distribution", {})
        modules = self.current_analysis.get("modules", {})
        risk_assessments = self.current_analysis.get("risk_assessments", {})

        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cascade Linter - Dependency Analysis Report</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 20px; background: #f5f5f5; }}
        .header {{ background: #2c3e50; color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }}
        .summary {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 20px; }}
        .metric-card {{ background: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .metric-value {{ font-size: 24px; font-weight: bold; color: #3498db; }}
        .table-container {{ background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        table {{ width: 100%; border-collapse: collapse; }}
        th {{ background: #34495e; color: white; padding: 12px; text-align: left; }}
        td {{ padding: 10px; border-bottom: 1px solid #ecf0f1; }}
        tr:nth-child(even) {{ background: #f8f9fa; }}
        .risk-critical {{ background: #e74c3c; color: white; padding: 4px 8px; border-radius: 4px; }}
        .risk-medium {{ background: #f39c12; color: white; padding: 4px 8px; border-radius: 4px; }}
        .risk-low {{ background: #27ae60; color: white; padding: 4px 8px; border-radius: 4px; }}
        .footer {{ margin-top: 20px; text-align: center; color: #7f8c8d; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🔍 Cascade Linter - Dependency Analysis Report</h1>
        <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
    
    <div class="summary">
        <div class="metric-card">
            <h3>Total Modules</h3>
            <div class="metric-value">{total_modules}</div>
        </div>
        <div class="metric-card">
            <h3>Critical Risks</h3>
            <div class="metric-value" style="color: #e74c3c;">{risk_distribution.get('CRITICAL', 0)}</div>
        </div>
        <div class="metric-card">
            <h3>Medium Risks</h3>
            <div class="metric-value" style="color: #f39c12;">{risk_distribution.get('MEDIUM', 0)}</div>
        </div>
        <div class="metric-card">
            <h3>Low Risks</h3>
            <div class="metric-value" style="color: #27ae60;">{risk_distribution.get('LOW', 0)}</div>
        </div>
    </div>
    
    <div class="table-container">
        <table>
            <thead>
                <tr>
                    <th>Module</th>
                    <th>Risk Level</th>
                    <th>Lines</th>
                    <th>Complexity</th>
                    <th>Risk Factors</th>
                    <th>File Path</th>
                </tr>
            </thead>
            <tbody>
"""

        # Add table rows
        for module_name, module_info in modules.items():
            assessment = risk_assessments.get(module_name, {})
            risk_level = assessment.get("risk_level", "LOW")
            risk_class = f"risk-{risk_level.lower()}"

            lines = module_info.get("size_lines", 0)
            complexity = module_info.get("complexity_score", 0)
            risk_factors = assessment.get("risk_factors", [])
            factors_text = "; ".join(risk_factors) if risk_factors else "None"
            file_path = module_info.get("file_path", "")

            html_content += f"""
                <tr>
                    <td><strong>{module_name}</strong></td>
                    <td><span class="{risk_class}">{risk_level}</span></td>
                    <td>{lines}</td>
                    <td>{complexity:.1f}</td>
                    <td>{factors_text}</td>
                    <td><code>{file_path}</code></td>
                </tr>
"""

        html_content += """
            </tbody>
        </table>
    </div>
    
    <div class="footer">
        <p>Report generated by Cascade Linter - Professional Code Quality Tool</p>
    </div>
</body>
</html>
"""

        with open(filename, "w", encoding="utf-8") as f:
            f.write(html_content)

    def export_to_text_summary(self, filename: str):
        """Export a comprehensive text summary of the analysis"""

        # Get analysis data
        total_modules = self.current_analysis.get("total_modules", 0)
        risk_distribution = self.current_analysis.get("risk_distribution", {})
        project_health = self.current_analysis.get("project_health", {})
        modules = self.current_analysis.get("modules", {})
        risk_assessments = self.current_analysis.get("risk_assessments", {})

        # Create comprehensive text report
        report_lines = [
            "=" * 80,
            "🔍 CASCADE LINTER - DEPENDENCY ANALYSIS REPORT",
            "=" * 80,
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "Tool Version: Cascade Linter v1.0.0",
            "",
            "📊 EXECUTIVE SUMMARY",
            "-" * 40,
            f"Total Modules Analyzed: {total_modules}",
            f"Critical Risk Modules: {risk_distribution.get('CRITICAL', 0)}",
            f"Medium Risk Modules: {risk_distribution.get('MEDIUM', 0)}",
            f"Low Risk Modules: {risk_distribution.get('LOW', 0)}",
            "",
            f"Overall Project Health: {project_health.get('grade', 'N/A')}",
            f"Average Risk Score: {project_health.get('average_risk', 0.0):.2f}",
            "",
            "🚨 HIGH-PRIORITY ISSUES",
            "-" * 40,
        ]

        # Add critical and medium risk modules
        critical_modules = [
            (name, info, risk_assessments.get(name, {}))
            for name, info in modules.items()
            if risk_assessments.get(name, {}).get("risk_level")
            in ["CRITICAL", "MEDIUM"]
        ]

        critical_modules.sort(
            key=lambda x: (
                0 if x[2].get("risk_level") == "CRITICAL" else 1,
                -x[1].get("size_lines", 0),
            )
        )

        if critical_modules:
            for i, (module_name, module_info, assessment) in enumerate(
                critical_modules[:10], 1
            ):
                risk_level = assessment.get("risk_level", "LOW")
                lines = module_info.get("size_lines", 0)
                complexity = module_info.get("complexity_score", 0)
                risk_factors = assessment.get("risk_factors", [])

                report_lines.extend(
                    [
                        f"{i:2d}. {module_name}",
                        f"    Risk Level: {risk_level}",
                        f"    Lines of Code: {lines}",
                        f"    Complexity Score: {complexity:.1f}",
                        f"    Risk Factors: {', '.join(risk_factors) if risk_factors else 'None'}",
                        f"    File: {module_info.get('file_path', 'N/A')}",
                        "",
                    ]
                )
        else:
            report_lines.append("✅ No high-priority issues found!")
            report_lines.append("")

        # Add recommendations
        report_lines.extend(
            [
                "💡 RECOMMENDATIONS",
                "-" * 40,
            ]
        )

        if risk_distribution.get("CRITICAL", 0) > 0:
            report_lines.extend(
                [
                    "🔴 CRITICAL ACTIONS NEEDED:",
                    f"   • {risk_distribution['CRITICAL']} modules require immediate attention",
                    "   • Focus on reducing complexity and file size",
                    "   • Consider refactoring large modules (>500 lines)",
                    "",
                ]
            )

        if risk_distribution.get("MEDIUM", 0) > 0:
            report_lines.extend(
                [
                    "🟡 MEDIUM PRIORITY:",
                    f"   • {risk_distribution['MEDIUM']} modules need improvement",
                    "   • Review and simplify complex functions",
                    "   • Add documentation and tests",
                    "",
                ]
            )

        if (
            risk_distribution.get("CRITICAL", 0) == 0
            and risk_distribution.get("MEDIUM", 0) == 0
        ):
            report_lines.extend(
                [
                    "🎉 EXCELLENT CODE QUALITY!",
                    "   • No critical or medium risk issues found",
                    "   • Continue following current best practices",
                    "   • Regular monitoring recommended",
                    "",
                ]
            )

        report_lines.extend(
            [
                "📈 NEXT STEPS",
                "-" * 40,
                "1. Address critical risk modules first",
                "2. Implement code review practices",
                "3. Set up automated quality gates",
                "4. Schedule regular dependency analysis",
                "5. Monitor complexity metrics over time",
                "",
                "=" * 80,
                "End of Report - Cascade Linter Professional Code Quality Tool",
                "=" * 80,
            ]
        )

        with open(filename, "w", encoding="utf-8") as f:
            f.write("\n".join(report_lines))

    def refresh_display(self):
        """Refresh display if needed"""
        # This could check for file changes and trigger re-analysis
        pass

    # --- PUBLIC METHODS FOR MAIN WINDOW INTEGRATION ---

    def set_directories_from_main_window(self, directories: List[str]):
        """Set directories to analyze from main window"""
        self.directories_to_analyze = directories.copy()
        if directories:
            self.btn_run_analysis.setEnabled(True)
            self.lbl_status.setText(f"Ready to analyze {len(directories)} directories")
            self.lbl_status.setStyleSheet(
                "QLabel { color: palette(highlight); font-weight: bold; }"
            )
        else:
            self.btn_run_analysis.setEnabled(False)
            self.lbl_status.setText("No directories selected")
            self.lbl_status.setStyleSheet(
                "QLabel { color: palette(window-text); font-weight: bold; }"
            )

    def get_current_analysis(self) -> Optional[Dict[str, Any]]:
        """Get current analysis results"""
        return self.current_analysis

    def has_analysis_data(self) -> bool:
        """Check if analysis data is available"""
        return self.current_analysis is not None

    def get_analysis_summary(self) -> str:
        """Get a summary of current analysis for status display"""
        if not self.current_analysis:
            return "No analysis data available"

        total_modules = self.current_analysis.get("total_modules", 0)
        risk_distribution = self.current_analysis.get("risk_distribution", {})
        critical_count = risk_distribution.get("CRITICAL", 0)

        if critical_count > 0:
            return (
                f"Analysis: {total_modules} modules, {critical_count} critical issues"
            )
        else:
            return f"Analysis: {total_modules} modules, all healthy"


# Fallback implementation for when backend is not available
class MockAnalyticsTab(QWidget):
    """Mock analytics tab that shows backend unavailable message"""

    analysisStarted = Signal()
    analysisCompleted = Signal(dict)
    statusChanged = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        # Warning message
        warning_label = QLabel(
            "⚠️ Analytics Backend Not Available\n\n"
            "The dependency analysis backend is not installed or configured.\n"
            "Please install the required dependencies:\n\n"
            "• Python AST parsing libraries\n"
            "• Analytics backend module\n\n"
            "Contact support for installation assistance."
        )
        warning_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        warning_label.setStyleSheet(
            """
            QLabel {
                background-color: #2e3436;
                border: 2px solid #f57900;
                border-radius: 8px;
                color: #eeeeec;
                font-size: 12pt;
                padding: 30px;
                line-height: 1.5;
            }
        """
        )

        layout.addWidget(warning_label)
        layout.addStretch()

    def set_directories_from_main_window(self, directories: List[str]):
        """Stub method for interface compatibility"""
        pass

    def get_current_analysis(self) -> Optional[Dict[str, Any]]:
        """Stub method for interface compatibility"""
        return None

    def has_analysis_data(self) -> bool:
        """Stub method for interface compatibility"""
        return False

    def get_analysis_summary(self) -> str:
        """Stub method for interface compatibility"""
        return "Analytics backend not available"


# Factory function to create the appropriate analytics tab
def create_analytics_tab(parent=None) -> QWidget:
    """Factory function to create analytics tab with proper backend detection"""
    if ANALYTICS_BACKEND_AVAILABLE:
        return AnalyticsTab(parent)
    else:
        return MockAnalyticsTab(parent)


# Export the main class
__all__ = ["AnalyticsTab", "MockAnalyticsTab", "create_analytics_tab"]
