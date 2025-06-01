#!/usr/bin/env python3
"""
Batch Processing System for Cascade Linter GUI
Provides multi-directory linting with parallel execution and queue management.
"""

from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any
from uuid import uuid4

from PySide6.QtCore import QObject, Signal, QThread, QTimer
from PySide6.QtWidgets import QApplication

from .core import CodeQualityRunner, LintingSession


class BatchJobStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


class BatchJobPriority(Enum):
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4


@dataclass
class BatchJob:
    """Represents a single linting job in a batch operation."""

    id: str = field(default_factory=lambda: str(uuid4()))
    name: str = ""
    path: Path = field(default_factory=Path)
    priority: BatchJobPriority = BatchJobPriority.NORMAL
    status: BatchJobStatus = BatchJobStatus.PENDING

    # Configuration
    config: Dict[str, Any] = field(default_factory=dict)
    stages: List[str] = field(
        default_factory=lambda: ["ruff", "flake8", "pylint", "bandit"]
    )

    # Execution tracking
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    progress: float = 0.0

    # Results
    session: Optional[LintingSession] = None
    error_message: Optional[str] = None

    @property
    def duration(self) -> Optional[float]:
        """Calculate job execution duration."""
        if self.started_at and self.finished_at:
            return (self.finished_at - self.started_at).total_seconds()
        return None

    @property
    def is_completed(self) -> bool:
        """Check if job is in a terminal state."""
        return self.status in [
            BatchJobStatus.COMPLETED,
            BatchJobStatus.FAILED,
            BatchJobStatus.CANCELLED,
        ]

    def to_dict(self) -> Dict[str, Any]:
        """Convert job to dictionary for serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "path": str(self.path),
            "priority": self.priority.value,
            "status": self.status.value,
            "progress": self.progress,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "finished_at": self.finished_at.isoformat() if self.finished_at else None,
            "duration": self.duration,
            "error_message": self.error_message,
            "config": self.config,
            "stages": self.stages,
        }


@dataclass
class BatchResults:
    """Aggregated results from a batch operation."""

    batch_id: str
    jobs: List[BatchJob] = field(default_factory=list)

    # Timing
    started_at: datetime = field(default_factory=datetime.now)
    finished_at: Optional[datetime] = None

    # Aggregate statistics
    total_files: int = 0
    total_issues: int = 0
    total_fixed_issues: int = 0

    # Job statistics
    completed_jobs: int = 0
    failed_jobs: int = 0
    cancelled_jobs: int = 0

    @property
    def duration(self) -> Optional[float]:
        """Total batch execution time."""
        if self.finished_at:
            return (self.finished_at - self.started_at).total_seconds()
        return None

    @property
    def success_rate(self) -> float:
        """Percentage of jobs that completed successfully."""
        total_jobs = len(self.jobs)
        if total_jobs == 0:
            return 0.0
        return (self.completed_jobs / total_jobs) * 100

    def update_statistics(self):
        """Recalculate aggregate statistics from job results."""
        self.completed_jobs = sum(
            1 for job in self.jobs if job.status == BatchJobStatus.COMPLETED
        )
        self.failed_jobs = sum(
            1 for job in self.jobs if job.status == BatchJobStatus.FAILED
        )
        self.cancelled_jobs = sum(
            1 for job in self.jobs if job.status == BatchJobStatus.CANCELLED
        )

        # Aggregate file and issue counts
        self.total_files = 0
        self.total_issues = 0
        self.total_fixed_issues = 0

        for job in self.jobs:
            if job.session and job.status == BatchJobStatus.COMPLETED:
                self.total_files += job.session.total_files
                self.total_issues += len(job.session.all_issues)
                # Add fixed issues count when available
                # self.total_fixed_issues += job.session.fixed_issues_count


class BatchSignals(QObject):
    """Qt signals for batch processing events."""

    # Batch-level signals
    batch_started = Signal(str)  # batch_id
    batch_finished = Signal(str, object)  # batch_id, BatchResults
    batch_progress_updated = Signal(str, float)  # batch_id, overall_progress
    batch_cancelled = Signal(str)  # batch_id

    # Job-level signals
    job_started = Signal(str, str)  # batch_id, job_id
    job_finished = Signal(str, str, bool)  # batch_id, job_id, success
    job_progress_updated = Signal(str, str, float)  # batch_id, job_id, progress
    job_status_changed = Signal(str, str, str)  # batch_id, job_id, status

    # Error signals
    job_error = Signal(str, str, str)  # batch_id, job_id, error_message
    batch_error = Signal(str, str)  # batch_id, error_message


class BatchWorkerThread(QThread):
    """Worker thread for executing batch jobs."""

    def __init__(self, batch_manager, batch_id: str, max_workers: int = 4):
        super().__init__()
        self.batch_manager = batch_manager
        self.batch_id = batch_id
        self.max_workers = max_workers
        self.is_cancelled = False

    def run(self):
        """Execute batch jobs with parallel processing."""
        try:
            batch = self.batch_manager.get_batch(self.batch_id)
            if not batch:
                return

            # Get pending jobs sorted by priority
            jobs = [job for job in batch.jobs if job.status == BatchJobStatus.PENDING]
            jobs.sort(key=lambda j: j.priority.value, reverse=True)

            if not jobs:
                return

            # Execute jobs with thread pool
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                # Submit all jobs
                future_to_job = {
                    executor.submit(self._execute_job, job): job for job in jobs
                }

                # Process completed jobs
                for future in as_completed(future_to_job):
                    if self.is_cancelled:
                        break

                    job = future_to_job[future]
                    try:
                        future.result()  # This will raise any exceptions
                    except Exception as e:
                        self._handle_job_error(job, str(e))

            # Finalize batch
            if not self.is_cancelled:
                self.batch_manager._finalize_batch(self.batch_id)

        except Exception as e:
            self.batch_manager.signals.batch_error.emit(self.batch_id, str(e))

    def _execute_job(self, job: BatchJob):
        """Execute a single job."""
        if self.is_cancelled:
            return

        try:
            # Update job status
            job.status = BatchJobStatus.RUNNING
            job.started_at = datetime.now()
            self.batch_manager.signals.job_started.emit(self.batch_id, job.id)
            self.batch_manager.signals.job_status_changed.emit(
                self.batch_id, job.id, job.status.value
            )

            # Create linter runner with job configuration
            runner = CodeQualityRunner(
                simple_output=job.config.get("simple_output", False),
                debug=job.config.get("debug", False),
            )

            # Create progress callback
            def progress_callback(progress: float):
                if not self.is_cancelled:
                    job.progress = progress
                    self.batch_manager.signals.job_progress_updated.emit(
                        self.batch_id, job.id, progress
                    )
                    self.batch_manager._update_batch_progress(self.batch_id)

            # Run linting session
            session = runner.run_linting_session(
                path=str(job.path),
                check_only=job.config.get("check_only", False),
                unsafe_fixes=job.config.get("unsafe_fixes", False),
                stages=job.stages,
                progress_callback=progress_callback,
            )

            # Store results
            job.session = session
            job.status = BatchJobStatus.COMPLETED
            job.finished_at = datetime.now()
            job.progress = 100.0

            self.batch_manager.signals.job_finished.emit(self.batch_id, job.id, True)
            self.batch_manager.signals.job_status_changed.emit(
                self.batch_id, job.id, job.status.value
            )

        except Exception as e:
            self._handle_job_error(job, str(e))

    def _handle_job_error(self, job: BatchJob, error_message: str):
        """Handle job execution error."""
        job.status = BatchJobStatus.FAILED
        job.error_message = error_message
        job.finished_at = datetime.now()

        self.batch_manager.signals.job_error.emit(self.batch_id, job.id, error_message)
        self.batch_manager.signals.job_finished.emit(self.batch_id, job.id, False)
        self.batch_manager.signals.job_status_changed.emit(
            self.batch_id, job.id, job.status.value
        )

    def cancel(self):
        """Cancel the batch execution."""
        self.is_cancelled = True


class BatchManager(QObject):
    """Manages batch processing operations."""

    def __init__(self, max_concurrent_batches: int = 2, max_workers_per_batch: int = 4):
        super().__init__()
        self.max_concurrent_batches = max_concurrent_batches
        self.max_workers_per_batch = max_workers_per_batch

        # Storage
        self.batches: Dict[str, BatchResults] = {}
        self.worker_threads: Dict[str, BatchWorkerThread] = {}

        # Signals
        self.signals = BatchSignals()

        # Progress update timer
        self.progress_timer = QTimer()
        self.progress_timer.timeout.connect(self._emit_progress_updates)
        self.progress_timer.start(500)  # Update every 500ms

    def create_batch(self, jobs: List[BatchJob], batch_name: str = "") -> str:
        """Create a new batch with the given jobs."""
        batch_id = str(uuid4())

        # Set job names if not provided
        for i, job in enumerate(jobs):
            if not job.name:
                job.name = f"{job.path.name} ({i + 1})"

        # Create batch results
        batch = BatchResults(batch_id=batch_id, jobs=jobs)

        self.batches[batch_id] = batch
        return batch_id

    def start_batch(self, batch_id: str) -> bool:
        """Start executing a batch."""
        if batch_id not in self.batches:
            return False

        if len(self.worker_threads) >= self.max_concurrent_batches:
            return False  # Too many concurrent batches

        # Create and start worker thread
        worker = BatchWorkerThread(self, batch_id, self.max_workers_per_batch)
        self.worker_threads[batch_id] = worker

        # Connect signals
        worker.finished.connect(lambda: self._cleanup_worker(batch_id))

        # Start execution
        batch = self.batches[batch_id]
        batch.started_at = datetime.now()

        worker.start()
        self.signals.batch_started.emit(batch_id)

        return True

    def cancel_batch(self, batch_id: str) -> bool:
        """Cancel a running batch."""
        if batch_id not in self.worker_threads:
            return False

        worker = self.worker_threads[batch_id]
        worker.cancel()

        # Update job statuses
        batch = self.batches.get(batch_id)
        if batch:
            for job in batch.jobs:
                if job.status in [BatchJobStatus.PENDING, BatchJobStatus.RUNNING]:
                    job.status = BatchJobStatus.CANCELLED
                    job.finished_at = datetime.now()

        self.signals.batch_cancelled.emit(batch_id)
        return True

    def get_batch(self, batch_id: str) -> Optional[BatchResults]:
        """Get batch results by ID."""
        return self.batches.get(batch_id)

    def get_active_batches(self) -> Dict[str, BatchResults]:
        """Get all currently running batches."""
        return {
            batch_id: batch
            for batch_id, batch in self.batches.items()
            if batch_id in self.worker_threads
        }

    def get_all_batches(self) -> Dict[str, BatchResults]:
        """Get all batches (active and completed)."""
        return self.batches.copy()

    def _update_batch_progress(self, batch_id: str):
        """Update overall batch progress."""
        batch = self.batches.get(batch_id)
        if not batch:
            return

        if not batch.jobs:
            return

        # Calculate overall progress
        total_progress = sum(job.progress for job in batch.jobs)
        overall_progress = total_progress / len(batch.jobs)

        self.signals.batch_progress_updated.emit(batch_id, overall_progress)

    def _finalize_batch(self, batch_id: str):
        """Finalize batch execution."""
        batch = self.batches.get(batch_id)
        if not batch:
            return

        batch.finished_at = datetime.now()
        batch.update_statistics()

        self.signals.batch_finished.emit(batch_id, batch)

    def _cleanup_worker(self, batch_id: str):
        """Clean up completed worker thread."""
        if batch_id in self.worker_threads:
            del self.worker_threads[batch_id]

    def _emit_progress_updates(self):
        """Emit progress updates for all active batches."""
        for batch_id in list(self.worker_threads.keys()):
            self._update_batch_progress(batch_id)

    def cleanup_completed_batches(self, max_history: int = 50):
        """Clean up old completed batches to prevent memory leaks."""
        completed_batches = [
            (batch_id, batch)
            for batch_id, batch in self.batches.items()
            if batch_id not in self.worker_threads and batch.finished_at
        ]

        if len(completed_batches) > max_history:
            # Sort by completion time and keep only the most recent
            completed_batches.sort(key=lambda x: x[1].finished_at, reverse=True)

            for batch_id, _ in completed_batches[max_history:]:
                del self.batches[batch_id]


# Helper functions for creating common batch configurations


def create_batch_from_directories(directories: List[Path], **config) -> List[BatchJob]:
    """Create batch jobs from a list of directories."""
    jobs = []

    for directory in directories:
        if directory.is_dir():
            job = BatchJob(name=directory.name, path=directory, config=config.copy())
            jobs.append(job)

    return jobs


def create_batch_with_priorities(job_configs: List[Dict[str, Any]]) -> List[BatchJob]:
    """Create batch jobs with custom priorities and configurations."""
    jobs = []

    for config in job_configs:
        job = BatchJob(
            name=config.get("name", ""),
            path=Path(config["path"]),
            priority=BatchJobPriority(
                config.get("priority", BatchJobPriority.NORMAL.value)
            ),
            config=config.get("linting_config", {}),
            stages=config.get("stages", ["ruff", "flake8", "pylint", "bandit"]),
        )
        jobs.append(job)

    return jobs


# Example usage and testing
if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)

    # Create batch manager
    batch_manager = BatchManager()

    # Connect signals for testing
    batch_manager.signals.batch_started.connect(
        lambda batch_id: print(f"Batch started: {batch_id}")
    )
    batch_manager.signals.batch_finished.connect(
        lambda batch_id, results: print(
            f"Batch finished: {batch_id}, Success rate: {results.success_rate:.1f}%"
        )
    )
    batch_manager.signals.job_finished.connect(
        lambda batch_id, job_id, success: print(
            f"Job finished: {job_id}, Success: {success}"
        )
    )

    # Create test batch
    test_dirs = [Path("."), Path("../")]  # Current and parent directory
    jobs = create_batch_from_directories(test_dirs, check_only=True)

    batch_id = batch_manager.create_batch(jobs, "Test Batch")
    batch_manager.start_batch(batch_id)

    sys.exit(app.exec())
