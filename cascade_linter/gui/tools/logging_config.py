# cascade_linter/gui/tools/logging_config.py
"""
Logging Configuration for Cascade Linter GUI

Integrates structlog + Rich for structured, colorized logging in PySide6.
Provides RichSignalHandler for Qt signal-based log routing to GUI components.

Usage:
    from cascade_linter.gui.tools.logging_config import RichSignalHandler, get_structlog_logger
    
    # Set up logging
    rich_handler = RichSignalHandler()
    rich_handler.html_ready.connect(log_viewer.append_html)
    log = get_structlog_logger(rich_handler)
    
    # Log structured events
    log.info("lint_stage_started", stage="Ruff", folder="/path/to/project")
"""

import io
import structlog
from rich.console import Console
from rich.markup import escape
from PySide6.QtCore import QObject, Signal
from typing import Dict, Any, Optional

__all__ = ["get_structlog_logger", "RichSignalHandler"]


class RichSignalHandler(QObject):
    """
    Routes Rich-rendered HTML log fragments into the GUI via a Qt signal.
    
    Features:
    - Converts structlog events to styled HTML fragments
    - Uses cross-platform Unicode symbols (BMP range only)
    - Emits Qt signals for thread-safe GUI integration
    - Preserves Rich markup and styling
    """
    
    html_ready = Signal(str)

    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
        
        # Create a Rich Console writing to an in-memory StringIO buffer
        self._console = Console(
            file=io.StringIO(),   # in-memory buffer
            markup=True,          # allow Rich markup (e.g., [bold red])
            emoji=False,          # avoid high-codepoint emoji for Windows compatibility
            highlight=False,      # no syntax highlighting needed here
            force_terminal=True,  # force ANSI output
            width=80,
        )
        
        # Initialize Unicode symbol support
        self._init_symbols()

    def _init_symbols(self):
        """Initialize cross-platform Unicode symbols (BMP range only)."""
        try:
            # Test if we can use BMP Unicode symbols
            test_symbols = "✔ ⚠ ◉ ◦ ℹ ⏳ → ✖"
            test_symbols.encode('utf-8')
            
            # Use Unicode symbols (Windows/Linux/macOS compatible)
            self.symbols = {
                'success': "✔",     # U+2714 Heavy Check Mark
                'error': "✖",       # U+2716 Heavy Multiplication X
                'warning': "⚠",     # U+26A0 Warning Sign
                'info': "ℹ",        # U+2139 Information Source
                'running': "⏳",     # U+23F3 Hourglass with Flowing Sand
                'arrow': "→",       # U+2192 Rightwards Arrow
                'bullet': "•",      # U+2022 Bullet
            }
            
        except (UnicodeEncodeError, UnicodeDecodeError):
            # Fallback to ASCII for legacy systems
            self.symbols = {
                'success': "+",
                'error': "X", 
                'warning': "!",
                'info': "i",
                'running': "~",
                'arrow': "->",
                'bullet': "*",
            }

    def emit(self, event_dict: Dict[str, Any]):
        """
        Called by structlog's final processor. We format the event as:
        "[timestamp] [SYMBOL LEVEL] event_name key=value key2=value2"
        with Rich-style markup and convert to HTML.
        """
        buf = self._console.file
        buf.truncate(0)
        buf.seek(0)

        # Extract structured fields
        ts = event_dict.get("timestamp", "")
        level = event_dict.get("level", "").upper()
        event_name = event_dict.get("event", "")
        
        # Get appropriate symbol and color for level
        level_symbol = self._get_level_symbol(level)
        level_color = self._get_level_color(level)

        # Build a Rich-formatted string
        # Format: 2025-06-01 12:00:00 [✔ INFO] lint_stage_started stage=Ruff folder=/…
        name_stamp = (
            f"[bold {level_color}]{level_symbol} {level}[/] "
            f"[dim cyan]{event_name}[/]"
        )

        # Append other key=value pairs
        details = ""
        for key, val in event_dict.items():
            if key in ("timestamp", "level", "logger", "event"):
                continue
            details += f" [white]{key}[/]=[magenta]{escape(str(val))}[/]"

        # Print into the in-memory console buffer
        self._console.print(f"{ts} {name_stamp}{details}")

        # Convert any ANSI styling in `buf` to inline-styled HTML
        html = self._console.export_html(
            code_format="ansi",     # interpret ANSI sequences
            inline_styles=True,     # use inline CSS styles
            full=False,             # do not include <html><body> wrappers
        )
        
        # Emit the HTML snippet for the GUI to consume
        self.html_ready.emit(html)

    def _get_level_symbol(self, level: str) -> str:
        """Get appropriate symbol for log level."""
        level_symbols = {
            'DEBUG': self.symbols['info'],
            'INFO': self.symbols['success'],
            'WARNING': self.symbols['warning'],
            'ERROR': self.symbols['error'],
            'CRITICAL': self.symbols['error']
        }
        return level_symbols.get(level, self.symbols['bullet'])

    def _get_level_color(self, level: str) -> str:
        """Get appropriate color for log level."""
        level_colors = {
            'DEBUG': 'blue',
            'INFO': 'green', 
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'bold red'
        }
        return level_colors.get(level, 'white')


def get_structlog_logger(rich_handler: RichSignalHandler):
    """
    Configure structlog so that each event is forwarded to rich_handler.emit().

    Returns a BoundLogger instance. Calls to `log.info(...)` will eventually
    call rich_handler.emit(html_snippet).
    
    Args:
        rich_handler: RichSignalHandler instance to route events to
        
    Returns:
        structlog.BoundLogger: Configured logger instance
    """
    import logging

    # Basic stdlib logging (optional, here for completeness)
    logging.basicConfig(level=logging.INFO)

    structlog.configure(
        processors=[
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,
            structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            # Final processor routes to our RichSignalHandler
            lambda logger, name, event_dict: rich_handler.emit(event_dict)
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    return structlog.get_logger("cascade_linter")


# Convenience functions for common log patterns
class LogPatterns:
    """Common logging patterns for the Cascade Linter."""
    
    @staticmethod
    def log_stage_start(logger, stage: str, folder: str, files_count: int = 0):
        """Log the start of a linting stage."""
        logger.info(
            "lint_stage_started",
            stage=stage,
            folder=folder,
            files_count=files_count
        )
    
    @staticmethod
    def log_stage_finish(logger, stage: str, folder: str, 
                        issues: int, duration: float, success: bool = True):
        """Log the completion of a linting stage."""
        level = "info" if success else "error"
        getattr(logger, level)(
            "lint_stage_finished",
            stage=stage,
            folder=folder,
            issues=issues,
            duration=duration,
            success=success
        )
    
    @staticmethod
    def log_issue_found(logger, file_path: str, line: int, 
                       severity: str, message: str, rule: str = ""):
        """Log a specific linting issue."""
        logger.warning(
            "lint_issue_found",
            file=file_path,
            line=line,
            severity=severity,
            message=message,
            rule=rule
        )
    
    @staticmethod
    def log_session_summary(logger, total_files: int, total_issues: int,
                           auto_fixed: int, duration: float, success: bool):
        """Log overall session summary."""
        level = "info" if success else "error"
        getattr(logger, level)(
            "session_completed",
            total_files=total_files,
            total_issues=total_issues,
            auto_fixed=auto_fixed,
            duration=duration,
            success=success
        )


if __name__ == "__main__":
    # Test the logging configuration
    import sys
    from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit
    from PySide6.QtCore import QTimer
    
    app = QApplication(sys.argv)
    
    # Create test window
    window = QWidget()
    window.setWindowTitle("Logging Config Test")
    window.resize(600, 400)
    
    layout = QVBoxLayout(window)
    
    # Create log viewer
    log_viewer = QTextEdit()
    log_viewer.setReadOnly(True)
    log_viewer.setAcceptRichText(True)
    log_viewer.setStyleSheet("""
        QTextEdit {
            background-color: #121212;
            color: #E0E0E0;
            font-family: 'Consolas', monospace;
            font-size: 10px;
        }
    """)
    layout.addWidget(log_viewer)
    
    # Set up logging
    rich_handler = RichSignalHandler()
    rich_handler.html_ready.connect(
        lambda html: log_viewer.insertHtml(f'<div style="margin-bottom:4px;">{html}</div>')
    )
    log = get_structlog_logger(rich_handler)
    
    # Create timer for test log messages
    timer = QTimer()
    timer.timeout.connect(lambda: log.info("test_message", counter=timer.property("counter") or 0))
    timer.timeout.connect(lambda: timer.setProperty("counter", (timer.property("counter") or 0) + 1))
    
    # Test different log levels
    def test_logging():
        log.info("application_started", version="1.0.0")
        log.info("lint_stage_started", stage="Ruff", folder="/example/project")
        log.warning("lint_issue_found", file="example.py", line=42, message="unused import")
        log.error("lint_stage_failed", stage="Pylint", error="Tool not found")
        log.info("session_completed", total_issues=15, duration=12.3)
    
    # Start test
    QTimer.singleShot(500, test_logging)
    
    window.show()
    print("Logging configuration test window opened")
    print("Check the text area for formatted log output")
    
    sys.exit(app.exec())
