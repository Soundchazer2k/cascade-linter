class DependencyGraphWidget(QWidget):
    """Custom widget for visualizing dependency graphs"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.analysis_data = None
        self.setMinimumSize(400, 300)

    def set_analysis_data(self, data: Dict[str, Any]):
        """Set analysis data for visualization"""
        self.analysis_data = data
        self.update()  # Trigger repaint

    def paintEvent(self, event):
        """Custom paint event for dependency graph"""
        painter = QPainter(self)

        if not self.analysis_data:
            # Draw placeholder
            painter.setPen(QPen(QColor("#eeeeec"), 1))
            painter.drawText(self.rect(), "No analysis data available")
            return

        # Simple visualization - draw modules as colored circles
        modules = self.analysis_data.get("risk_assessments", {})
        if not modules:
            painter.drawText(self.rect(), "No module data available")
            return

        # Calculate positions for modules (simple grid layout)
        width = self.width()
        height = self.height()
        margin = 20

        module_list = list(modules.keys())
        if not module_list:
            return

        cols = int((len(module_list)) ** 0.5) + 1
        rows = (len(module_list) + cols - 1) // cols

        cell_width = (width - 2 * margin) / cols
        cell_height = (height - 2 * margin) / rows

        # Draw modules
        for i, (module_name, assessment) in enumerate(modules.items()):
            row = i // cols
            col = i % cols

            x = margin + col * cell_width + cell_width // 2
            y = margin + row * cell_height + cell_height // 2

            # Choose color based on risk level
            risk_level = assessment["risk_level"]
            if risk_level == "CRITICAL":
                color = QColor("#cc0000")
            elif risk_level == "MEDIUM":
                color = QColor("#f57900")
            else:
                color = QColor("#73d216")

            # Draw circle
            painter.setBrush(color)
            painter.setPen(QPen(QColor("#2e3436"), 2))
            radius = min(20, cell_width // 4, cell_height // 4)
            painter.drawEllipse(
                int(x - radius), int(y - radius), int(2 * radius), int(2 * radius)
            )

            # Draw module name (shortened)
            painter.setPen(QPen(QColor("#eeeeec"), 1))
            short_name = module_name.split(".")[-1]  # Just the last part
            if len(short_name) > 10:
                short_name = short_name[:8] + "..."

            text_rect = painter.fontMetrics().boundingRect(short_name)
            text_x = x - text_rect.width() // 2
            text_y = y + radius + 15
            painter.drawText(int(text_x), int(text_y), short_name)


class AnalysisThread(QThread):
    """Background thread for running dependency analysis"""

    progress = Signal(str, int)  # message, percentage
    completed = Signal(dict)  # results
    error = Signal(str)  # error message

    def __init__(self, project_paths: List[str]):
        super().__init__()
        self.project_paths = project_paths
        self.analyzer = DependencyAnalyzer()

    def run(self):
        """Run analysis in background thread"""
        try:
            self.progress.emit("Starting dependency analysis...", 10)

            # Run the analysis
            results = self.analyzer.analyze_project(self.project_paths)

            self.progress.emit("Analysis completed successfully", 100)
            self.completed.emit(results)

        except Exception as e:
            error_msg = f"Analysis failed: {str(e)}"
            if STRUCTLOG_AVAILABLE:
                logger.error("analysis_thread_error", error=str(e))
            self.error.emit(error_msg)


class AnalyticsBackend(QObject):
    """Qt-integrated analytics backend with signals"""

    analysisStarted = Signal()
    analysisProgress = Signal(str, int)  # message, percentage
    analysisCompleted = Signal(dict)  # results
    analysisError = Signal(str)  # error message

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_analysis = None
        self.analysis_thread = None
        self.mutex = QMutex()

    def start_analysis(self, project_paths: List[str]):
        """Start dependency analysis in background thread"""
        with QMutexLocker(self.mutex):
            if self.analysis_thread and self.analysis_thread.isRunning():
                return  # Analysis already running

            self.analysisStarted.emit()

            # Create and start analysis thread
            self.analysis_thread = AnalysisThread(project_paths)
            self.analysis_thread.progress.connect(self.analysisProgress.emit)
            self.analysis_thread.completed.connect(self._on_analysis_completed)
            self.analysis_thread.error.connect(self.analysisError.emit)
            self.analysis_thread.start()

    def _on_analysis_completed(self, results: dict):
        """Handle analysis completion"""
        self.current_analysis = results
        self.analysisCompleted.emit(results)

    def export_csv(self, filename: str) -> bool:
        """Export module risk data to CSV"""
        if not self.current_analysis:
            return False

        try:
            import csv

            with open(filename, "w", newline="", encoding="utf-8") as csvfile:
                writer = csv.writer(csvfile)

                # Write header
                writer.writerow(
                    [
                        "Module",
                        "Risk Level",
                        "Risk Score",
                        "Impact Score",
                        "Complexity",
                        "File Path",
                        "Size (Lines)",
                        "Risk Factors",
                    ]
                )

                # Write data
                risk_assessments = self.current_analysis.get("risk_assessments", {})
                modules = self.current_analysis.get("modules", {})

                for module_name, assessment in risk_assessments.items():
                    module_info = modules.get(module_name, {})

                    writer.writerow(
                        [
                            module_name,
                            assessment["risk_level"],
                            f"{assessment['risk_score']:.3f}",
                            f"{assessment['impact_score']:.3f}",
                            f"{assessment['complexity_score']:.1f}",
                            module_info.get("file_path", ""),
                            module_info.get("size_lines", 0),
                            "; ".join(assessment["risk_factors"]),
                        ]
                    )

            return True

        except Exception as e:
            if STRUCTLOG_AVAILABLE:
                logger.error("csv_export_failed", filename=filename, error=str(e))
            return False

    def export_json(self, filename: str) -> bool:
        """Export complete analysis to JSON"""
        if not self.current_analysis:
            return False

        try:
            with open(filename, "w", encoding="utf-8") as jsonfile:
                json.dump(self.current_analysis, jsonfile, indent=2, ensure_ascii=False)

            return True

        except Exception as e:
            if STRUCTLOG_AVAILABLE:
                logger.error("json_export_failed", filename=filename, error=str(e))
            return False

    def export_dot(self, filename: str) -> bool:
        """Export dependency graph to DOT format for Graphviz"""
        if not self.current_analysis:
            return False

        try:
            dependencies = self.current_analysis.get("dependencies", [])
            risk_assessments = self.current_analysis.get("risk_assessments", {})

            with open(filename, "w", encoding="utf-8") as dotfile:
                dotfile.write("digraph dependencies {\n")
                dotfile.write("  rankdir=LR;\n")
                dotfile.write("  node [shape=box, style=rounded];\n")

                # Add nodes with risk-based coloring
                modules = set()
                for dep in dependencies:
                    modules.add(dep["from_module"])
                    modules.add(dep["to_module"])

                for module in modules:
                    assessment = risk_assessments.get(module, {})
                    risk_level = assessment.get("risk_level", "LOW")

                    if risk_level == "CRITICAL":
                        color = "red"
                    elif risk_level == "MEDIUM":
                        color = "orange"
                    else:
                        color = "green"

                    # Use just the last part of module name for readability
                    display_name = module.split(".")[-1]
                    dotfile.write(
                        f'  "{module}" [label="{display_name}", color={color}];\n'
                    )

                # Add edges
                for dep in dependencies:
                    dotfile.write(
                        f'  "{dep["from_module"]}" -> "{dep["to_module"]}";\n'
                    )

                dotfile.write("}\n")

            return True

        except Exception as e:
            if STRUCTLOG_AVAILABLE:
                logger.error("dot_export_failed", filename=filename, error=str(e))
            return False


# Export functions for easy import
__all__ = [
    "DependencyAnalyzer",
    "AnalyticsBackend",
    "DependencyGraphWidget",
    "ModuleInfo",
    "DependencyEdge",
    "RiskAssessment",
]
