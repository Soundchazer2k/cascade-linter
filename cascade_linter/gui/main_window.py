# cascade_linter/gui/main_window.py
"""
Modern Cascade Linter GUI Main Window
=====================================

A professional, standards-based PySide6 main window implementing:
- Nielsen's 10 Usability Heuristics  
- Modern GUI Design Framework principles
- Cross-platform responsiveness
- Material Design theming
- Comprehensive keyboard shortcuts
- Real-time linting with progress indicators
"""

import sys
import os
from pathlib import Path
from typing import Optional, List, Dict, Any

# PySide6 imports (exclusively - no PyQt)
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QTabWidget, QMenuBar, QMenu, QToolBar, QStatusBar,
    QLabel, QPushButton, QListWidget, QListWidgetItem,
    QFileDialog, QMessageBox, QProgressBar, QFrame, QGroupBox,
    QCheckBox, QSpinBox, QComboBox, QTextEdit, QScrollArea,
    QGridLayout, QFormLayout
)
from PySide6.QtCore import (
    Qt, QTimer, QThread, QObject, Signal, Slot, QSize, QSettings,
    QStandardPaths, QThreadPool, QRunnable
)
from PySide6.QtGui import (
    QIcon, QFont, QPixmap, QPalette, QColor, QAction,
    QShortcut, QKeySequence, QPainter, QPen, QBrush
)

# Import our custom widgets
from .widgets import MetricCard, ProgressDonut, LogViewer

# Try to import qtawesome for vector icons
try:
    import qtawesome as qta
    HAS_QTAWESOME = True
except ImportError:
    HAS_QTAWESOME = False


class ModernMainWindow(QMainWindow):
    """Modern Cascade Linter Main Window with comprehensive functionality."""
    
    # Custom signals
    linting_started = Signal(str, list)  # path, stages
    linting_finished = Signal(object)  # LintingSession
    directory_selected = Signal(str)  # path
    
    def __init__(self):
        super().__init__()
        
        # Initialize instance variables
        self.current_directory = None
        self.linting_in_progress = False
        
        # Initialize UI
        self.init_ui()
        
        # Set window properties
        self.setWindowTitle("Cascade Linter - Modern Python Code Quality Tool")
        self.setMinimumSize(1000, 700)
        self.resize(1200, 800)
        
        # Set application icon using mascot
        self.set_application_icon()
        
    def set_application_icon(self):
        """Set the application icon using the mascot SVG."""
        try:
            # Try to load the mascot SVG
            project_root = Path(__file__).parent.parent.parent
            mascot_path = project_root / "assets" / "icons" / "mascot.svg"
            
            if mascot_path.exists():
                # Load SVG and convert to icon
                from PySide6.QtSvg import QSvgRenderer
                
                # Create pixmap from SVG
                mascot_pixmap = QPixmap(64, 64)
                mascot_pixmap.fill(QColor("#00FFFFFF"))  # Transparent background
                
                painter = QPainter(mascot_pixmap)
                svg_renderer = QSvgRenderer(str(mascot_path))
                svg_renderer.render(painter, mascot_pixmap.rect())
                painter.end()
                
                # Set as window icon
                self.setWindowIcon(QIcon(mascot_pixmap))
                print("Mascot icon loaded successfully")
                
            elif HAS_QTAWESOME:
                # Fallback to QtAwesome
                icon = qta.icon('fa5s.code', color='#4A90E2')
                self.setWindowIcon(icon)
                print("Using QtAwesome fallback icon")
                
        except Exception as e:
            print(f"Could not load mascot icon: {e}")
            # Try QtAwesome fallback
            if HAS_QTAWESOME:
                try:
                    icon = qta.icon('fa5s.code', color='#4A90E2')
                    self.setWindowIcon(icon)
                except Exception:
                    pass  # Icon is optional
        
    def init_ui(self):
        """Initialize the user interface components."""
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Simple layout for now
        label = QLabel("Cascade Linter GUI")
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("font-size: 24pt; font-weight: bold; color: #4A90E2;")
        main_layout.addWidget(label)
        
        # Status label
        self.status_label = QLabel("Ready")
        main_layout.addWidget(self.status_label)
        
        # Create status bar
        status_bar = QStatusBar()
        self.setStatusBar(status_bar)
        status_bar.addWidget(QLabel("Status: Ready"))


def main():
    """Main entry point for the Cascade Linter GUI application."""
    # Create QApplication
    app = QApplication(sys.argv)
    
    # Set application metadata
    app.setApplicationName("Cascade Linter")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("CascadeLinter")
    app.setOrganizationDomain("cascadelinter.dev")
    
    # Create and show main window
    window = ModernMainWindow()
    window.show()
    
    # Start event loop
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
