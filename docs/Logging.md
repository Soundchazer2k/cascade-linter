# Logging & Diagnostics

This document explains how to integrate **structlog** + **Rich** + **Smart Unicode** into the Cascade Linter CLI and GUI (PySide 6) to produce structured, colorized, cross-platform logs with intelligent Unicode support that gracefully handles Windows compatibility issues.

---

## 1. Why Use structlog + Rich + Smart Unicode?

1. **Structured Events** (`structlog`)
   
   - Emit log events with named fields (e.g., `stage`, `folder`, `issues`) instead of raw strings.
   
   - Example:
     
     ```python
     import structlog
     
     log = structlog.get_logger(__name__)
     log.info("lint_stage_started", stage="Ruff", folder="/path/to/project")
     log.warning("lint_issue", file="foo.py", line=42, message="unused import")
     ```
   
   - Downstream, structured events can be rendered or exported (JSON, key=value) for analysis.

2. **Rich Formatting** (`Rich`)
   
   - Render colorized, "pretty" output (tables, progress bars), then convert ANSI markup → HTML.
   
   - In a GUI, embed Rich's HTML into a `QTextEdit` with inline CSS to preserve styles.

3. **Smart Cross-Platform Unicode Support**
   
   - Uses intelligent Unicode symbol selection with automatic Windows compatibility fallbacks
   
   - Automatically detects environment capabilities and adapts symbol choice
   
   - Never crashes due to encoding issues, gracefully degrades to ASCII when needed

By combining `structlog` for structured events, `Rich` for colorized output, and smart Unicode handling, we can feed readable, styled logs into both CLI and GUI without blocking the event loop or encountering encoding errors.

---

## 2. The Windows Unicode Challenge

### 2.1 Root Cause Analysis

Windows historically uses legacy "code pages" (CP1252, CP437) instead of UTF-8 by default. This causes `'charmap' codec can't encode character` errors when trying to display Unicode symbols like ✔, ⚠, or ◉.

**Technical Details:**
- Python tries to encode Unicode symbols using the console's code page
- Legacy Windows code pages only support ~256 characters  
- Unicode symbols outside this range cause UnicodeEncodeError
- Error format: `'charmap' codec can't encode character '\\u2705'`

**Example Error:**
```
UnicodeEncodeError: 'charmap' codec can't encode character '✅' in position 0: character maps to <undefined>
```

### 2.2 Traditional Solutions (Suboptimal)

❌ **Remove all Unicode** - Loses visual appeal and hierarchy  
❌ **Force user configuration** - Poor user experience  
❌ **Only use ASCII** - Misses opportunity for beautiful output on modern systems  

### 2.3 Smart Unicode Strategy (Recommended)

✅ **Automatic detection and graceful degradation**  
✅ **Beautiful Unicode on capable systems**  
✅ **Functional ASCII fallback on legacy Windows**  
✅ **Zero user configuration required**  

---

## 3. Smart Unicode Implementation

### 3.1 Core Implementation (`logging_utils.py`)

```python
# cascade_linter/logging_utils.py

import sys
import os
import subprocess
from typing import Optional

class SmartSymbols:
    """Smart Unicode symbols with automatic Windows compatibility fallback"""
    
    def __init__(self):
        self.unicode_supported = self._test_unicode_support()
        if self.unicode_supported:
            self._setup_utf8_environment()
            self._use_unicode_symbols()
        else:
            self._use_ascii_symbols()
    
    def _test_unicode_support(self) -> bool:
        """Test if the current environment supports BMP Unicode symbols"""
        try:
            # Test BMP Unicode symbols (Windows-safe range)
            test_symbols = "✔ ⚠ ◉ ◦ ℹ ⏳ → ✖"
            
            # Try to encode using current stdout encoding
            encoding = getattr(sys.stdout, 'encoding', None) or 'utf-8'
            test_symbols.encode(encoding)
            return True
            
        except (UnicodeEncodeError, UnicodeDecodeError, LookupError, AttributeError):
            return False
    
    def _setup_utf8_environment(self):
        """Configure UTF-8 environment for cross-platform Unicode support"""
        
        if sys.platform == "win32":
            try:
                # Try to set console to UTF-8 (Windows 10+ feature)
                subprocess.run(['chcp', '65001'], shell=True, 
                             capture_output=True, check=False, timeout=2)
            except (subprocess.TimeoutExpired, FileNotFoundError):
                pass  # Graceful failure - not critical
        
        # Configure Python UTF-8 mode
        if hasattr(sys.stdout, 'reconfigure'):
            try:
                sys.stdout.reconfigure(encoding='utf-8', errors='replace')
                sys.stderr.reconfigure(encoding='utf-8', errors='replace')
            except (AttributeError, OSError):
                pass  # Graceful failure
                
        # Set environment variable for subprocess calls
        os.environ['PYTHONUTF8'] = '1'
    
    def _use_unicode_symbols(self):
        """Use beautiful BMP Unicode symbols (cross-platform safe)"""
        self.CRITICAL = "✖"      # U+2716 Heavy Multiplication X
        self.HIGH = "⚠"          # U+26A0 Warning Sign  
        self.MEDIUM = "◉"        # U+25C9 Fisheye
        self.LOW = "◦"           # U+25E6 White Bullet
        self.INFO = "ℹ"          # U+2139 Information Source
        self.SUCCESS = "✔"       # U+2714 Heavy Check Mark
        self.RUNNING = "⏳"       # U+23F3 Hourglass with Flowing Sand
        self.ARROW = "→"         # U+2192 Rightwards Arrow
        self.BULLET = "•"        # U+2022 Bullet
        self.INDENT = "  "       # Standard indent
        
        # Stage indicators
        self.STAGE_PENDING = "◦"    # Waiting
        self.STAGE_RUNNING = "⏳"    # In progress
        self.STAGE_SUCCESS = "✔"    # Completed successfully
        self.STAGE_ERROR = "✖"      # Failed
        self.STAGE_SKIPPED = "—"    # U+2014 Em Dash (skipped)
        
    def _use_ascii_symbols(self):
        """ASCII fallback symbols for legacy Windows systems"""
        self.CRITICAL = "X"
        self.HIGH = "!"
        self.MEDIUM = "*"
        self.LOW = "-"
        self.INFO = "i"
        self.SUCCESS = "+"
        self.RUNNING = "~"
        self.ARROW = "->"
        self.BULLET = "*"
        self.INDENT = "  "
        
        # Stage indicators
        self.STAGE_PENDING = "."
        self.STAGE_RUNNING = "~"
        self.STAGE_SUCCESS = "+"
        self.STAGE_ERROR = "X"
        self.STAGE_SKIPPED = "-"

# Global instance for easy access
symbols = SmartSymbols()
```

### 3.2 Integration with Rich Console

```python
# cascade_linter/rich_logging.py

import io
import structlog
from rich.console import Console
from rich.markup import escape
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from .logging_utils import symbols

class SmartRichConsole:
    """Rich Console with smart Unicode symbol integration"""
    
    def __init__(self, file=None, force_terminal=True):
        self.console = Console(
            file=file or io.StringIO(),
            markup=True,
            emoji=False,           # Disable high-codepoint emoji
            highlight=False,
            force_terminal=force_terminal,
            width=80,
        )
    
    def create_progress_table(self, stages_data):
        """Create a progress table using smart Unicode symbols"""
        table = Table(title="Cascade Linter Progress")
        table.add_column("Stage", style="bold")
        table.add_column("Status", justify="center")
        table.add_column("Issues", justify="right")
        table.add_column("Files", justify="right")
        table.add_column("Time", justify="right")
        
        for stage, data in stages_data.items():
            status_symbol = self._get_status_symbol(data['status'])
            issues = str(data.get('issues', 0))
            files = str(data.get('files', 0))
            time = f"{data.get('time', 0):.2f}s"
            
            table.add_row(stage, status_symbol, issues, files, time)
        
        return table
    
    def _get_status_symbol(self, status):
        """Get appropriate symbol based on status"""
        status_map = {
            'pending': symbols.STAGE_PENDING,
            'running': symbols.STAGE_RUNNING,
            'success': symbols.STAGE_SUCCESS,
            'error': symbols.STAGE_ERROR,
            'skipped': symbols.STAGE_SKIPPED
        }
        return status_map.get(status, symbols.STAGE_PENDING)
    
    def format_issue(self, severity, message, file_path=None, line=None):
        """Format an issue with appropriate severity symbol"""
        severity_symbols = {
            'critical': symbols.CRITICAL,
            'high': symbols.HIGH,
            'medium': symbols.MEDIUM,
            'low': symbols.LOW,
            'info': symbols.INFO
        }
        
        symbol = severity_symbols.get(severity.lower(), symbols.INFO)
        
        if file_path and line:
            return f"{symbol} {file_path}:{line} - {message}"
        elif file_path:
            return f"{symbol} {file_path} - {message}"
        else:
            return f"{symbol} {message}"
```

---

## 4. PySide6 GUI Integration

### 4.1 RichSignalHandler for Qt Integration

```python
# cascade_linter/gui/tools/logging_config.py

import io
import structlog
from rich.console import Console
from rich.markup import escape
from PySide6.QtCore import QObject, Signal
from cascade_linter.logging_utils import symbols
from cascade_linter.rich_logging import SmartRichConsole

__all__ = ["get_structlog_logger", "RichSignalHandler"]

class RichSignalHandler(QObject):
    """
    Routes Rich-rendered HTML log fragments into the GUI via a Qt signal.
    Uses smart Unicode symbols for cross-platform compatibility.
    """
    html_ready = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        # Create a Rich Console writing to an in-memory StringIO buffer
        self._console = SmartRichConsole(
            file=io.StringIO(),
            force_terminal=True
        ).console

    def emit(self, event_dict: dict):
        """
        Called by structlog's final processor. Formats events with smart Unicode symbols.
        """
        buf = self._console.file
        buf.truncate(0)
        buf.seek(0)

        # Extract structured fields
        ts = event_dict.get("timestamp", "")
        level = event_dict.get("level", "").upper()
        event_name = event_dict.get("event", "")
        
        # Get appropriate symbol for level
        level_symbol = self._get_level_symbol(level)
        
        # Color choice based on level
        level_color = self._get_level_color(level)

        # Build a Rich-formatted string with smart Unicode
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

        # Convert any ANSI styling to inline-styled HTML
        html = self._console.export_html(
            code_format="ansi",
            inline_styles=True,
            full=False,
        )
        
        # Emit the HTML snippet for the GUI to consume
        self.html_ready.emit(html)
    
    def _get_level_symbol(self, level):
        """Get symbol for log level using smart Unicode"""
        level_symbols = {
            'DEBUG': symbols.INFO,
            'INFO': symbols.SUCCESS,
            'WARNING': symbols.HIGH,
            'ERROR': symbols.CRITICAL,
            'CRITICAL': symbols.CRITICAL
        }
        return level_symbols.get(level, symbols.INFO)
    
    def _get_level_color(self, level):
        """Get color for log level"""
        level_colors = {
            'DEBUG': 'blue',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'bold red'
        }
        return level_colors.get(level, 'white')

def get_structlog_logger(rich_handler: RichSignalHandler):
    """Configure structlog to use our RichSignalHandler with smart Unicode"""
    import logging

    # Basic stdlib logging
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
```

### 4.2 Enhanced LogViewer Widget

```python
# cascade_linter/gui/widgets/LogViewer.py

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTextEdit, QCheckBox, 
    QHBoxLayout, QPushButton, QLabel
)
from PySide6.QtCore import Slot
from PySide6.QtGui import QFont
from cascade_linter.logging_utils import symbols

class LogViewer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # --- Filter Row with Smart Unicode Labels ---
        filter_layout = QHBoxLayout()
        filter_label = QLabel(f"{symbols.BULLET} Filter by linter:")
        filter_layout.addWidget(filter_label)
        
        self.chk_ruff = QCheckBox("Ruff")
        self.chk_flake = QCheckBox("Flake8")
        self.chk_pylint = QCheckBox("Pylint")
        self.chk_bandit = QCheckBox("Bandit")
        self.chk_mypy = QCheckBox("MyPy")
        
        for cb in (self.chk_ruff, self.chk_flake, self.chk_pylint, self.chk_bandit, self.chk_mypy):
            cb.setChecked(True)
            cb.setToolTip(f"Show logs from {cb.text()}")
            filter_layout.addWidget(cb)
        
        filter_layout.addStretch()
        
        # Export button with smart Unicode
        self.btn_export = QPushButton(f"{symbols.ARROW} Export Logs")
        self.btn_export.setToolTip("Export filtered logs to file")
        filter_layout.addWidget(self.btn_export)
        
        layout.addLayout(filter_layout)

        # --- Main HTML Log Area ---
        self.text_logs = QTextEdit()
        self.text_logs.setReadOnly(True)
        self.text_logs.setAcceptRichText(True)
        
        # Set font with broad Unicode coverage and fallback chain
        font = QFont()
        font.setFamily("Consolas, 'DejaVu Sans Mono', Menlo, 'Liberation Mono', monospace")
        font.setPointSize(10)
        self.text_logs.setFont(font)
        
        # Set placeholder with smart Unicode
        self.text_logs.setPlaceholderText(
            f"{symbols.INFO} Logs will appear here... {symbols.ARROW} Run a linting session to see output"
        )
        
        layout.addWidget(self.text_logs)

    @Slot(str)
    def append_html(self, html_fragment: str):
        """Append a fragment of HTML with smart Unicode support"""
        wrapped = f'<div style="margin-bottom:4px;font-family:Consolas,monospace;">{html_fragment}</div>'
        cursor = self.text_logs.textCursor()
        cursor.movePosition(cursor.End)
        self.text_logs.setTextCursor(cursor)
        self.text_logs.insertHtml(wrapped)
        self.text_logs.insertPlainText("\n")

        # Auto-scroll if enabled
        try:
            from cascade_linter.gui.tools.ConfigManager import ConfigManager
            if ConfigManager.get_bool("Interface/AutoScrollLog", True):
                vsb = self.text_logs.verticalScrollBar()
                vsb.setValue(vsb.maximum())
        except ImportError:
            # Fallback - always scroll
            vsb = self.text_logs.verticalScrollBar()
            vsb.setValue(vsb.maximum())
```

---

## 5. CLI Integration

### 5.1 Enhanced CLI with Smart Unicode

```python
# cascade_linter/cli_enhanced.py (excerpt)

from cascade_linter.logging_utils import symbols
from cascade_linter.rich_logging import SmartRichConsole
import structlog

class CLIProgressCallback:
    """CLI progress callback with smart Unicode symbols"""
    
    def __init__(self, simple_output=False):
        self.simple_output = simple_output
        self.console = SmartRichConsole() if not simple_output else None
        self.log = structlog.get_logger(__name__)
    
    def on_stage_start(self, stage, total_stages, files_to_process):
        """Called when a linting stage starts"""
        if self.simple_output:
            print(f"{symbols.STAGE_RUNNING} Starting {stage}...")
        else:
            self.console.console.print(
                f"[bold blue]{symbols.STAGE_RUNNING}[/] Starting [cyan]{stage}[/] "
                f"({total_stages} stages total, {files_to_process} files)"
            )
        
        self.log.info(
            "stage_started",
            stage=stage,
            total_stages=total_stages,
            files_to_process=files_to_process
        )
    
    def on_stage_finish(self, stage, duration, success, issue_count):
        """Called when a linting stage finishes"""
        symbol = symbols.STAGE_SUCCESS if success else symbols.STAGE_ERROR
        status = "completed" if success else "failed"
        
        if self.simple_output:
            print(f"{symbol} {stage} {status} in {duration:.2f}s ({issue_count} issues)")
        else:
            color = "green" if success else "red"
            self.console.console.print(
                f"[bold {color}]{symbol}[/] [cyan]{stage}[/] {status} "
                f"in {duration:.2f}s ([yellow]{issue_count}[/] issues)"
            )
        
        self.log.info(
            "stage_finished",
            stage=stage,
            duration=duration,
            success=success,
            issue_count=issue_count
        )
    
    def on_progress(self, current, total, current_file=None):
        """Called during stage execution for progress updates"""
        if current_file and not self.simple_output:
            progress_pct = (current / total) * 100 if total > 0 else 0
            self.console.console.print(
                f"{symbols.STAGE_RUNNING} Processing: [dim]{current_file}[/] "
                f"({current}/{total}, {progress_pct:.1f}%)",
                end='\r'
            )

def display_session_summary(session, simple_output=False):
    """Display session summary with smart Unicode symbols"""
    console = SmartRichConsole() if not simple_output else None
    
    # Overall success indicator
    overall_symbol = symbols.SUCCESS if session.success else symbols.CRITICAL
    
    if simple_output:
        print(f"\n{symbols.ARROW} Session Summary {symbols.ARROW}")
        print(f"{overall_symbol} Overall: {'SUCCESS' if session.success else 'FAILED'}")
        print(f"{symbols.BULLET} Total files: {session.total_files}")
        print(f"{symbols.BULLET} Total issues: {session.total_issues}")
        print(f"{symbols.BULLET} Auto-fixed: {session.auto_fixed_count}")
        print(f"{symbols.BULLET} Execution time: {session.execution_time:.2f}s")
    else:
        # Rich formatted output
        from rich.table import Table
        
        table = Table(title=f"{symbols.ARROW} Cascade Linter Session Summary")
        table.add_column("Metric", style="bold")
        table.add_column("Value", justify="right")
        
        overall_color = "green" if session.success else "red"
        status_text = "SUCCESS" if session.success else "FAILED"
        
        table.add_row("Overall Status", f"[{overall_color}]{overall_symbol} {status_text}[/]")
        table.add_row("Total Files", str(session.total_files))
        table.add_row("Total Issues", f"[yellow]{session.total_issues}[/]")
        table.add_row("Auto-Fixed", f"[green]{session.auto_fixed_count}[/]")
        table.add_row("Execution Time", f"{session.execution_time:.2f}s")
        
        console.console.print(table)
```

---

## 6. Font Fallback Strategy

### 6.1 Cross-Platform Font Configuration

```python
# cascade_linter/gui/tools/FontManager.py

from PySide6.QtGui import QFont, QFontDatabase
from cascade_linter.logging_utils import symbols

class FontManager:
    """Manages cross-platform font selection for optimal Unicode display"""
    
    @staticmethod
    def get_optimal_monospace_font():
        """Get best available monospace font with Unicode support"""
        
        # Font preference order (best Unicode support first)
        font_preferences = [
            "Consolas",              # Windows - excellent Unicode
            "DejaVu Sans Mono",      # Linux - comprehensive Unicode
            "Menlo",                 # macOS - good Unicode support
            "Liberation Mono",       # Cross-platform
            "Courier New",           # Fallback
            "monospace"              # System default
        ]
        
        font_db = QFontDatabase()
        available_families = font_db.families()
        
        for preferred_font in font_preferences:
            if preferred_font in available_families:
                font = QFont(preferred_font)
                font.setPointSize(10)
                font.setFixedPitch(True)
                return font
        
        # Ultimate fallback
        font = QFont()
        font.setFamily("monospace")
        font.setPointSize(10)
        font.setFixedPitch(True)
        return font
    
    @staticmethod
    def test_font_unicode_support(font):
        """Test if font can display our Unicode symbols"""
        font_metrics = QFont(font)
        
        # Test key symbols
        test_symbols = [
            symbols.SUCCESS,    # ✔
            symbols.CRITICAL,   # ✖  
            symbols.HIGH,       # ⚠
            symbols.RUNNING,    # ⏳
            symbols.ARROW       # →
        ]
        
        for symbol in test_symbols:
            if not font_metrics.canDisplay(symbol):
                return False
        
        return True
```

---

## 7. Implementation Checklist

### 7.1 CLI Integration
- [ ] Install dependencies: `structlog`, `rich`
- [ ] Create `cascade_linter/logging_utils.py` with `SmartSymbols` class
- [ ] Create `cascade_linter/rich_logging.py` with `SmartRichConsole`
- [ ] Update CLI progress callbacks to use smart Unicode symbols
- [ ] Test on Windows, macOS, and Linux terminals
- [ ] Verify graceful ASCII fallback on legacy Windows systems

### 7.2 GUI Integration  
- [ ] Create `cascade_linter/gui/tools/logging_config.py` with `RichSignalHandler`
- [ ] Update `LogViewer.py` to use optimal font selection
- [ ] Wire `RichSignalHandler.html_ready` signal to `LogViewer.append_html`
- [ ] Test theme integration with smart Unicode symbols
- [ ] Verify HTML rendering preserves Unicode symbols correctly

### 7.3 Cross-Platform Testing
- [ ] **Windows 10/11**: Test with both legacy console and Windows Terminal
- [ ] **Windows 7/8**: Verify ASCII fallback works correctly
- [ ] **macOS**: Test Terminal.app and iTerm2 compatibility
- [ ] **Linux**: Test major distributions (Ubuntu, Fedora, Arch)
- [ ] **Font Testing**: Verify symbol display across different font configurations

---

## 8. Troubleshooting Guide

### 8.1 Common Issues

**Issue**: Unicode symbols not displaying on Windows  
**Solution**: Check if `symbols.unicode_supported` is `False`. The system should automatically fall back to ASCII symbols.

**Issue**: HTML export doesn't preserve symbols  
**Solution**: Ensure HTML files are saved with UTF-8 encoding and include `<meta charset="utf-8">` tag.

**Issue**: Terminal hangs during Unicode detection  
**Solution**: The detection has a 2-second timeout. If hanging persists, check subprocess permissions and consider disabling `chcp` calls.

**Issue**: Rich export_html() produces empty output  
**Solution**: Ensure Rich Console has `force_terminal=True` and content was actually written to the buffer.

**Issue**: Qt signals not emitting HTML fragments  
**Solution**: Verify `RichSignalHandler` is properly connected and `structlog.configure()` was called with the handler.

### 8.2 Debug Commands

```python
# Test Unicode support directly
from cascade_linter.logging_utils import SmartSymbols
symbols = SmartSymbols()
print(f"Unicode supported: {symbols.unicode_supported}")
print(f"Success symbol: '{symbols.SUCCESS}'")
print(f"Error symbol: '{symbols.CRITICAL}'")

# Test Rich console output
from cascade_linter.rich_logging import SmartRichConsole
console = SmartRichConsole()
console.console.print(f"Test: {symbols.SUCCESS} Success {symbols.CRITICAL} Error")

# Test structlog integration
import structlog
from cascade_linter.gui.tools.logging_config import RichSignalHandler, get_structlog_logger

handler = RichSignalHandler()
log = get_structlog_logger(handler)
log.info("test_event", stage="Ruff", files=42)
```

### 8.3 Environment Variables

Set these environment variables to control behavior:

```bash
# Force Unicode mode (override detection)
export CASCADE_FORCE_UNICODE=1

# Force ASCII mode (disable Unicode)
export CASCADE_FORCE_ASCII=1

# Enable debug logging for symbol detection
export CASCADE_DEBUG_UNICODE=1

# Set custom font for Qt GUI
export CASCADE_FONT_FAMILY="DejaVu Sans Mono"
```

---

## 9. Best Practices

### 9.1 Symbol Usage Guidelines

1. **Consistency**: Always use the same symbol for the same meaning across CLI and GUI
2. **Hierarchy**: Use visual weight to indicate importance (✖ > ⚠ > ◉ > ◦)
3. **Context**: Choose symbols appropriate for the context (⏳ for progress, ✔ for completion)
4. **Accessibility**: Ensure symbols enhance rather than replace text descriptions

### 9.2 Performance Guidelines

1. **Initialize Once**: Create `SmartSymbols` instance once and reuse
2. **Lazy Loading**: Use lazy initialization for better startup performance
3. **Caching**: Cache Unicode detection results when possible
4. **Fallback Fast**: Make ASCII fallback path as fast as Unicode path

---

## 10. Conclusion

The smart Unicode logging system provides:

✅ **Cross-platform compatibility** - Works on Windows, macOS, and Linux  
✅ **Graceful degradation** - ASCII fallback for legacy systems  
✅ **Visual hierarchy** - Meaningful symbols enhance readability  
✅ **Zero configuration** - Automatic detection and adaptation  
✅ **Future-proof** - Extensible design for new features  

This system transforms the Cascade Linter from a text-based tool into a visually rich, professional application while maintaining universal compatibility.

For implementation questions or issues, refer to the troubleshooting section or create an issue in the project repository.
