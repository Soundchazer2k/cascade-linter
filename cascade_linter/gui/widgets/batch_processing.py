#!/usr/bin/env python3
"""
Fixed Batch Processing Module
Following external LLM recommendations:
1. Split out QtCore imports so QThread and Signal are always imported first
2. Let import errors fail fast instead of hiding them
3. Remove try/except blocks around critical imports
"""

# CRITICAL: Import QThread and Signal FIRST, outside any try/except blocks
from PySide6.QtCore import QThread, Signal, QMutex, QMutexLocker
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QListWidget,
    QListWidgetItem,
    QProgressBar,
    QTextEdit,
    QGroupBox,
    QSplitter,
    QWidget,
    QMessageBox,
    QFileDialog,
    QApplication,
)
from PySide6.QtGui import QDragEnterEvent, QDropEvent, QFont
from PySide6.QtCore import Qt

# Standard library imports
import sys
import time
from pathlib import Path
from datetime import datetime
from typing import Dict

# Project imports - let these fail fast if there are issues
from cascade_linter.core import CodeQualityRunner, LinterStage


class BatchJobWorker(QThread):
    """
    Worker thread for batch processing jobs
    Inherits from QThread (imported above) - should work now
    """

    # Signals for communication with main thread
    job_started = Signal(str)  # job_id
    job_progress = Signal(str, int)  # job_id, percentage
    job_finished = Signal(str, bool, str)  # job_id, success, results
    log_message = Signal(str, str)  # job_id, message

    def __init__(self):
        super().__init__()
        self.jobs_queue = []
        self.current_job = None
        self.should_stop = False
        self.mutex = QMutex()

    def add_job(self, job_data: Dict):
        """Add a job to the processing queue"""
        with QMutexLocker(self.mutex):
            self.jobs_queue.append(job_data)

    def stop_processing(self):
        """Signal the worker to stop processing"""
        with QMutexLocker(self.mutex):
            self.should_stop = True

    def run(self):
        """Main worker thread execution"""
        while not self.should_stop:
            # Get next job
            with QMutexLocker(self.mutex):
                if not self.jobs_queue:
                    break
                self.current_job = self.jobs_queue.pop(0)

            if self.current_job:
                self.process_job(self.current_job)
                self.current_job = None

            # Small delay to prevent busy waiting
            self.msleep(100)

    def process_job(self, job_data: Dict):
        """Process a single batch job"""
        job_id = job_data.get("id", "unknown")
        directory = job_data.get("directory", "")
        options = job_data.get("options", {})

        self.job_started.emit(job_id)
        self.log_message.emit(job_id, f"Starting batch processing: {directory}")

        try:
            # Create linter runner with refactored core
            runner = CodeQualityRunner(
                debug=options.get("debug", False), simple_output=False
            )

            # Use the new unified linting session approach with all 5 stages including MyPy
            stages = [
                LinterStage.RUFF,
                LinterStage.FLAKE8,
                LinterStage.PYLINT,
                LinterStage.BANDIT,
                LinterStage.MYPY,
            ]

            # Run complete linting session
            session = runner.run_linting_session(
                path=directory,
                stages=stages,
                check_only=options.get("check_only", False),
                unsafe_fixes=options.get("unsafe_fixes", False),
            )

            # Update progress
            self.job_progress.emit(job_id, 100)

            # Generate results summary from session
            results_summary = self.generate_session_summary(session)

            self.job_finished.emit(job_id, session.success, results_summary)
            self.log_message.emit(job_id, "Batch processing completed")

        except Exception as e:
            error_msg = f"Batch processing failed: {str(e)}"
            self.log_message.emit(job_id, error_msg)
            self.job_finished.emit(job_id, False, error_msg)

    def generate_session_summary(self, session) -> str:
        """Generate a summary of the linting session results"""
        if session.all_issues:
            total_issues = len(session.all_issues)
            files_with_issues = len(session.issues_by_file)
            return f"Found {total_issues} issues across {files_with_issues} files in {session.execution_time:.1f}s"
        else:
            return f"No issues found - code is clean! (completed in {session.execution_time:.1f}s)"


class BatchProcessingDialog(QDialog):
    """
    Batch processing dialog for linting multiple directories
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.worker_thread = None
        self.jobs = {}  # job_id -> job_data
        self.setup_ui()
        self.setup_drag_drop()

    def setup_ui(self):
        """Setup the user interface"""
        self.setWindowTitle("Batch Processing - Cascade Linter")
        self.setMinimumSize(800, 600)
        self.resize(1000, 700)

        # Main layout
        layout = QVBoxLayout(self)

        # Header
        header = QLabel("🔄 Batch Processing")
        header.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        layout.addWidget(header)

        # Splitter for job queue and results
        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter)

        # Left side: Job queue
        queue_widget = self.setup_queue_widget()
        splitter.addWidget(queue_widget)

        # Right side: Results and logs
        results_widget = self.setup_results_widget()
        splitter.addWidget(results_widget)

        # Bottom: Controls
        controls_layout = QHBoxLayout()

        self.add_directory_btn = QPushButton("📁 Add Directory")
        self.add_directory_btn.clicked.connect(self.add_directory)
        controls_layout.addWidget(self.add_directory_btn)

        self.start_batch_btn = QPushButton("▶️ Start Batch")
        self.start_batch_btn.clicked.connect(self.start_batch_processing)
        controls_layout.addWidget(self.start_batch_btn)

        self.stop_batch_btn = QPushButton("⏹️ Stop Batch")
        self.stop_batch_btn.clicked.connect(self.stop_batch_processing)
        self.stop_batch_btn.setEnabled(False)
        controls_layout.addWidget(self.stop_batch_btn)

        controls_layout.addStretch()

        self.close_btn = QPushButton("✖️ Close")
        self.close_btn.clicked.connect(self.close)
        controls_layout.addWidget(self.close_btn)

        layout.addLayout(controls_layout)

    def setup_queue_widget(self) -> QWidget:
        """Setup the job queue widget"""
        group = QGroupBox("📋 Job Queue")
        layout = QVBoxLayout(group)

        # Drag and drop instructions
        instructions = QLabel(
            "💡 Drag and drop folders here or use 'Add Directory' button"
        )
        instructions.setStyleSheet("color: #666; font-style: italic; margin: 5px;")
        layout.addWidget(instructions)

        # Job list
        self.job_list = QListWidget()
        self.job_list.setMinimumHeight(300)
        layout.addWidget(self.job_list)

        return group

    def setup_results_widget(self) -> QWidget:
        """Setup the results and logs widget"""
        group = QGroupBox("📊 Results & Logs")
        layout = QVBoxLayout(group)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # Results text area
        self.results_text = QTextEdit()
        self.results_text.setMinimumHeight(200)
        self.results_text.setFont(QFont("Consolas", 9))
        layout.addWidget(self.results_text)

        # Export button
        export_btn = QPushButton("💾 Export Results")
        export_btn.clicked.connect(self.export_results)
        layout.addWidget(export_btn)

        return group

    def setup_drag_drop(self):
        """Enable drag and drop functionality"""
        self.setAcceptDrops(True)
        self.job_list.setAcceptDrops(True)

    def dragEnterEvent(self, event: QDragEnterEvent):
        """Handle drag enter events"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        """Handle drop events"""
        urls = event.mimeData().urls()
        for url in urls:
            if url.isLocalFile():
                path = Path(url.toLocalFile())
                if path.is_dir():
                    self.add_directory_to_queue(str(path))

    def add_directory(self):
        """Add directory through file dialog"""
        directory = QFileDialog.getExistingDirectory(
            self, "Select Directory for Batch Processing"
        )
        if directory:
            self.add_directory_to_queue(directory)

    def add_directory_to_queue(self, directory: str):
        """Add a directory to the processing queue"""
        job_id = f"job_{len(self.jobs) + 1}_{int(time.time())}"

        job_data = {
            "id": job_id,
            "directory": directory,
            "options": {"check_only": False, "unsafe_fixes": False, "debug": False},
            "status": "queued",
            "added_time": datetime.now(),
        }

        self.jobs[job_id] = job_data

        # Add to UI list
        item_text = f"📁 {Path(directory).name} ({directory})"
        item = QListWidgetItem(item_text)
        item.setData(Qt.ItemDataRole.UserRole, job_id)
        self.job_list.addItem(item)

        self.log_message(f"Added to queue: {directory}")

    def start_batch_processing(self):
        """Start the batch processing"""
        if not self.jobs:
            QMessageBox.information(
                self, "No Jobs", "Please add directories to process."
            )
            return

        # Create and start worker thread
        self.worker_thread = BatchJobWorker()

        # Connect signals
        self.worker_thread.job_started.connect(self.on_job_started)
        self.worker_thread.job_progress.connect(self.on_job_progress)
        self.worker_thread.job_finished.connect(self.on_job_finished)
        self.worker_thread.log_message.connect(self.on_log_message)

        # Add jobs to worker
        for job_data in self.jobs.values():
            if job_data["status"] == "queued":
                self.worker_thread.add_job(job_data)

        # Update UI
        self.start_batch_btn.setEnabled(False)
        self.stop_batch_btn.setEnabled(True)
        self.progress_bar.setVisible(True)

        # Start processing
        self.worker_thread.start()
        self.log_message("🚀 Started batch processing...")

    def stop_batch_processing(self):
        """Stop the batch processing"""
        if self.worker_thread and self.worker_thread.isRunning():
            self.worker_thread.stop_processing()
            self.worker_thread.wait(5000)  # Wait up to 5 seconds

            if self.worker_thread.isRunning():
                self.worker_thread.terminate()
                self.worker_thread.wait()

        # Update UI
        self.start_batch_btn.setEnabled(True)
        self.stop_batch_btn.setEnabled(False)
        self.progress_bar.setVisible(False)

        self.log_message("⏹️ Batch processing stopped")

    def on_job_started(self, job_id: str):
        """Handle job started signal"""
        if job_id in self.jobs:
            self.jobs[job_id]["status"] = "running"
            self.log_message(f"▶️ Started: {self.jobs[job_id]['directory']}")

    def on_job_progress(self, job_id: str, percentage: int):
        """Handle job progress signal"""
        self.progress_bar.setValue(percentage)

    def on_job_finished(self, job_id: str, success: bool, results: str):
        """Handle job finished signal"""
        if job_id in self.jobs:
            self.jobs[job_id]["status"] = "completed" if success else "failed"
            self.jobs[job_id]["results"] = results

            status_icon = "✅" if success else "❌"
            directory = self.jobs[job_id]["directory"]
            self.log_message(f"{status_icon} Completed: {directory}")
            self.log_message(f"   Results: {results}")

        # Check if all jobs are done
        all_done = all(
            job["status"] in ["completed", "failed"] for job in self.jobs.values()
        )

        if all_done:
            self.start_batch_btn.setEnabled(True)
            self.stop_batch_btn.setEnabled(False)
            self.progress_bar.setVisible(False)
            self.log_message("🎉 All batch jobs completed!")

    def on_log_message(self, job_id: str, message: str):
        """Handle log message signal"""
        self.log_message(f"[{job_id}] {message}")

    def log_message(self, message: str):
        """Add a message to the results log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.results_text.append(f"[{timestamp}] {message}")

    def export_results(self):
        """Export results to file"""
        if not self.jobs:
            QMessageBox.information(self, "No Results", "No batch jobs to export.")
            return

        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Export Batch Results",
            f"batch_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            "Text Files (*.txt);;All Files (*)",
        )

        if filename:
            try:
                with open(filename, "w", encoding="utf-8") as f:
                    f.write("CASCADE LINTER BATCH PROCESSING RESULTS\n")
                    f.write("=" * 50 + "\n")
                    f.write(
                        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                    )

                    for job_id, job_data in self.jobs.items():
                        f.write(f"Job: {job_id}\n")
                        f.write(f"Directory: {job_data['directory']}\n")
                        f.write(f"Status: {job_data['status']}\n")
                        if "results" in job_data:
                            f.write(f"Results: {job_data['results']}\n")
                        f.write("-" * 30 + "\n")

                    f.write("\nLOG:\n")
                    f.write(self.results_text.toPlainText())

                QMessageBox.information(
                    self, "Export Complete", f"Results exported to:\n{filename}"
                )

            except Exception as e:
                QMessageBox.warning(
                    self, "Export Error", f"Failed to export results:\n{str(e)}"
                )

    def closeEvent(self, event):
        """Handle dialog close event"""
        if self.worker_thread and self.worker_thread.isRunning():
            reply = QMessageBox.question(
                self,
                "Stop Processing?",
                "Batch processing is running. Stop and close?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )

            if reply == QMessageBox.StandardButton.Yes:
                self.stop_batch_processing()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()


def add_batch_processing_to_main_window(main_window):
    """
    Add batch processing menu item to main window
    This function is called by enhanced_launcher.py
    """
    try:
        # Add Tools menu if it doesn't exist
        if not hasattr(main_window, "tools_menu"):
            main_window.tools_menu = main_window.menuBar().addMenu("🔧 Tools")

        # Add batch processing action
        batch_action = main_window.tools_menu.addAction("🔄 Batch Processing")
        batch_action.setStatusTip("Process multiple directories in batch")
        batch_action.triggered.connect(
            lambda: open_batch_processing_dialog(main_window)
        )

        return True

    except Exception as e:
        print(f"Error adding batch processing menu: {e}")
        return False


def open_batch_processing_dialog(parent=None):
    """Open the batch processing dialog"""
    try:
        dialog = BatchProcessingDialog(parent)
        dialog.exec()
    except Exception as e:
        print(f"Error opening batch processing dialog: {e}")
        if parent:
            QMessageBox.warning(
                parent, "Error", f"Failed to open batch processing:\n{str(e)}"
            )


# Test the module standalone
if __name__ == "__main__":
    app = QApplication(sys.argv)

    print("🧪 Testing Batch Processing Module Standalone")
    print("=" * 50)

    try:
        dialog = BatchProcessingDialog()
        print("✅ BatchProcessingDialog created successfully")
        print("✅ QThread import working correctly")

        dialog.show()
        sys.exit(app.exec())

    except Exception as e:
        print(f"❌ Standalone test failed: {e}")
        import traceback

        traceback.print_exc()
