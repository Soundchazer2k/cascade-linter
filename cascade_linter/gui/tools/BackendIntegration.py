#!/usr/bin/env python3
"""
Backend Integration for Cascade Linter GUI
Connects PySide6 GUI to the actual linter backend
"""

import os
from typing import Optional, List, Dict, Any

from PySide6.QtCore import QObject, Signal, QRunnable, QThreadPool, Slot

# Import the backend modules
try:
    from cascade_linter.core import (
        CodeQualityRunner,
        LinterStage,
        LinterProgressCallback,
        LintingSession,
    )

    BACKEND_AVAILABLE = True
except ImportError as e:
    BACKEND_AVAILABLE = False
    IMPORT_ERROR = str(e)


class GUIProgressCallback(LinterProgressCallback):
    """Qt-compatible progress callback that emits signals"""

    def __init__(self, signals_emitter):
        """
        Initialize with a QObject that has the required signals

        Args:
            signals_emitter: QObject with these signals:
                - progressUpdated(str)
                - stageStarted(str)
                - stageFinished(str, bool, float)
        """
        self.signals = signals_emitter

        # Initialize parent with our internal methods
        super().__init__(
            progress_func=self._on_progress,
            stage_start_func=self._on_stage_start,
            stage_finish_func=self._on_stage_finish,
        )

    def _on_progress(self, message: str):
        """Internal progress handler - emits Qt signal"""
        if hasattr(self.signals, "progressUpdated"):
            self.signals.progressUpdated.emit(message)

    def _on_stage_start(self, stage_name: str):
        """Internal stage start handler - emits Qt signal"""
        if hasattr(self.signals, "stageStarted"):
            self.signals.stageStarted.emit(stage_name)

    def _on_stage_finish(self, stage_name: str, success: bool, duration: float):
        """Internal stage finish handler - emits Qt signal"""
        if hasattr(self.signals, "stageFinished"):
            self.signals.stageFinished.emit(stage_name, success, duration)


class LinterWorker(QRunnable):
    """Worker thread for running linting operations"""

    def __init__(
        self,
        directories: List[str],
        stages: Optional[List[str]] = None,
        check_only: bool = False,
        unsafe_fixes: bool = False,
        signals_emitter=None,
    ):
        super().__init__()
        self.directories = directories
        self.stages = stages or ["ruff", "flake8"]
        self.check_only = check_only
        self.unsafe_fixes = unsafe_fixes
        self.signals = signals_emitter
        self.is_cancelled = False

    def run(self):
        """Run the linting operation in background thread"""
        if not BACKEND_AVAILABLE:
            error_msg = f"Backend not available: {IMPORT_ERROR}"
            if self.signals and hasattr(self.signals, "errorOccurred"):
                self.signals.errorOccurred.emit(error_msg)
            return

        try:
            # Create progress callback
            callback = GUIProgressCallback(self.signals) if self.signals else None

            # Create runner with gitignore support
            runner = CodeQualityRunner(
                debug=False, simple_output=True, respect_gitignore=True
            )

            # Convert stage names to LinterStage enums
            stage_objects = []
            stage_map = {stage.command: stage for stage in LinterStage}
            for stage_name in self.stages:
                if stage_name in stage_map:
                    stage_objects.append(stage_map[stage_name])

            all_sessions = []

            # Process each directory
            for i, directory in enumerate(self.directories):
                if self.is_cancelled:
                    break

                if callback:
                    callback.on_progress(
                        f"Processing directory {i+1}/{len(self.directories)}: {directory}"
                    )

                # Validate directory exists
                if not os.path.exists(directory):
                    if self.signals and hasattr(self.signals, "errorOccurred"):
                        self.signals.errorOccurred.emit(
                            f"Directory not found: {directory}"
                        )
                    continue

                # Run linting session for this directory
                session = runner.run_linting_session(
                    path=directory,
                    stages=stage_objects,
                    check_only=self.check_only,
                    unsafe_fixes=self.unsafe_fixes,
                    callback=callback,
                )

                all_sessions.append(session)

                # Emit session results
                if self.signals and hasattr(self.signals, "sessionCompleted"):
                    self.signals.sessionCompleted.emit(
                        directory, self._serialize_session(session)
                    )

            # Emit overall completion
            if self.signals and hasattr(self.signals, "allCompleted"):
                combined_results = self._combine_sessions(all_sessions)
                self.signals.allCompleted.emit(combined_results)

        except Exception as e:
            if self.signals and hasattr(self.signals, "errorOccurred"):
                self.signals.errorOccurred.emit(str(e))

    def cancel(self):
        """Cancel the operation"""
        self.is_cancelled = True

    def _serialize_session(self, session: "LintingSession") -> Dict[str, Any]:
        """Convert session to serializable dictionary for Qt signals"""
        return {
            "target_path": session.target_path,
            "success": session.success,
            "execution_time": session.execution_time,
            "total_issues": session.total_issues,
            "total_fixes_applied": session.total_fixes_applied,
            "total_files_with_issues": session.total_files_with_issues,
            "stage_results": {
                stage.command: {
                    "success": result.success,
                    "execution_time": result.execution_time,
                    "issue_count": result.issue_count,
                    "fixes_count": result.fixes_count,
                    "initial_issue_count": result.initial_issue_count,
                }
                for stage, result in session.stage_results.items()
            },
            "raw_log": session.raw_log,
        }

    def _combine_sessions(self, sessions: List["LintingSession"]) -> Dict[str, Any]:
        """Combine multiple sessions into overall statistics"""
        if not sessions:
            return {
                "total_directories": 0,
                "total_issues": 0,
                "total_fixes": 0,
                "total_time": 0.0,
                "overall_success": True,
                "directories_processed": [],
            }

        return {
            "total_directories": len(sessions),
            "total_issues": sum(s.total_issues for s in sessions),
            "total_fixes": sum(s.total_fixes_applied for s in sessions),
            "total_time": sum(s.execution_time for s in sessions),
            "overall_success": all(s.success for s in sessions),
            "directories_processed": [s.target_path for s in sessions],
        }


class BackendManager(QObject):
    """Manages backend integration for the GUI"""

    # Define all signals that the GUI will connect to
    progressUpdated = Signal(str)
    stageStarted = Signal(str)
    stageFinished = Signal(str, bool, float)  # stage_name, success, duration
    sessionCompleted = Signal(str, dict)  # directory, session_data
    allCompleted = Signal(dict)  # combined_results
    errorOccurred = Signal(str)  # error_message

    def __init__(self, parent=None):
        super().__init__(parent)
        self.thread_pool = QThreadPool.globalInstance()
        self.current_worker = None
        self.available_stages = ["ruff", "flake8", "pylint", "bandit", "mypy"]

    def is_backend_available(self) -> bool:
        """Check if backend is available"""
        return BACKEND_AVAILABLE

    def get_backend_error(self) -> str:
        """Get backend import error if any"""
        return IMPORT_ERROR if not BACKEND_AVAILABLE else ""

    def get_available_stages(self) -> List[str]:
        """Get list of available linter stages"""
        return self.available_stages.copy()

    def validate_environment(self) -> Dict[str, bool]:
        """Check which linting tools are available"""
        if not BACKEND_AVAILABLE:
            return {stage: False for stage in self.available_stages}

        try:
            runner = CodeQualityRunner(debug=False)
            tools_status = runner.validate_environment()
            # Map from LinterStage command names to our stage names
            return {
                "ruff": tools_status.get("ruff", False),
                "flake8": tools_status.get("flake8", False),
                "pylint": tools_status.get("pylint", False),
                "bandit": tools_status.get("bandit", False),
                "mypy": tools_status.get("mypy", False),
            }
        except Exception:
            return {stage: False for stage in self.available_stages}

    @Slot(list, list, bool, bool)
    def start_linting(
        self,
        directories: List[str],
        stages: List[str] = None,
        check_only: bool = False,
        unsafe_fixes: bool = False,
    ):
        """Start linting operation in background thread"""

        if not BACKEND_AVAILABLE:
            self.errorOccurred.emit(f"Backend not available: {IMPORT_ERROR}")
            return

        if not directories:
            self.errorOccurred.emit("No directories selected")
            return

        # Cancel any existing operation
        self.cancel_linting()

        # Create and start worker
        self.current_worker = LinterWorker(
            directories=directories,
            stages=stages or ["ruff", "flake8"],
            check_only=check_only,
            unsafe_fixes=unsafe_fixes,
            signals_emitter=self,
        )

        self.thread_pool.start(self.current_worker)

    @Slot()
    def cancel_linting(self):
        """Cancel current linting operation"""
        if self.current_worker:
            self.current_worker.cancel()
            self.current_worker = None
            self.progressUpdated.emit("Operation cancelled by user")

    def is_running(self) -> bool:
        """Check if a linting operation is currently running"""
        return self.current_worker is not None

    @Slot(str)
    def lint_single_directory(self, directory: str):
        """Convenience method to lint a single directory with default settings"""
        self.start_linting([directory])

    def get_stage_info(self, stage_name: str) -> Dict[str, Any]:
        """Get information about a specific linter stage"""
        stage_info = {
            "ruff": {
                "name": "Ruff",
                "description": "Fast Python linter and formatter",
                "has_autofix": True,
                "icon": "fa5s.magic",
            },
            "flake8": {
                "name": "Flake8",
                "description": "Style guide enforcement",
                "has_autofix": False,
                "icon": "fa5s.check-circle",
            },
            "pylint": {
                "name": "Pylint",
                "description": "Deep code analysis",
                "has_autofix": False,
                "icon": "fa5s.search",
            },
            "bandit": {
                "name": "Bandit",
                "description": "Security vulnerability scanner",
                "has_autofix": False,
                "icon": "fa5s.shield-alt",
            },
            "mypy": {
                "name": "MyPy",
                "description": "Static type checker",
                "has_autofix": False,
                "icon": "fa5s.check-double",
            },
        }

        return stage_info.get(
            stage_name,
            {
                "name": stage_name.title(),
                "description": "Unknown linter",
                "has_autofix": False,
                "icon": "fa5s.cog",
            },
        )


# Factory function for easy import
def create_backend_manager(parent=None) -> BackendManager:
    """Create and return a BackendManager instance"""
    return BackendManager(parent)


# Convenience functions for testing
def test_backend_availability() -> bool:
    """Test if backend is available and working"""
    try:
        manager = BackendManager()
        return manager.is_backend_available()
    except Exception:
        return False


def get_backend_status() -> Dict[str, Any]:
    """Get comprehensive backend status for diagnostics"""
    manager = BackendManager()

    status = {
        "backend_available": manager.is_backend_available(),
        "import_error": manager.get_backend_error(),
        "available_stages": manager.get_available_stages(),
        "environment_validation": {},
    }

    if manager.is_backend_available():
        try:
            status["environment_validation"] = manager.validate_environment()
        except Exception as e:
            status["environment_validation_error"] = str(e)

    return status


if __name__ == "__main__":
    # Test the backend integration
    print("🔧 Testing Backend Integration")
    print("=" * 50)

    status = get_backend_status()

    print(f"Backend Available: {status['backend_available']}")
    if not status["backend_available"]:
        print(f"Import Error: {status['import_error']}")

    print(f"Available Stages: {', '.join(status['available_stages'])}")

    if "environment_validation" in status:
        print("\nEnvironment Validation:")
        for tool, available in status["environment_validation"].items():
            status_icon = "✅" if available else "❌"
            print(f"   {status_icon} {tool}")

    print("\n✅ Backend integration test complete!")
