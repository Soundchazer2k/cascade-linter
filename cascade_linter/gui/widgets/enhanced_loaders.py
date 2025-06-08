# Enhanced Loaders - QT-PyQt-PySide-Custom-Widgets Integration
# Cascade Linter GUI - Advanced Loading Indicators
# Compatible with existing ProgressDonut.py - adds variety, doesn't replace

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PySide6.QtCore import QTimer, Signal, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QFont

try:
    # Import Custom Widgets with multiple fallback strategies
    CUSTOM_WIDGETS_AVAILABLE = False

    # Strategy 1: Try direct imports
    try:
        from Custom_Widgets.QCustomArcLoader import QCustomArcLoader
        from Custom_Widgets.QCustomSpinner import QCustomSpinner
        from Custom_Widgets.QCustom3CirclesLoader import QCustom3CirclesLoader

        CUSTOM_WIDGETS_AVAILABLE = True
        print("✅ Custom Widgets loaded successfully")
    except ImportError as e1:
        print(f"⚠️ Direct import failed: {e1}")

        # Strategy 2: Try alternative import path
        try:
            import Custom_Widgets

            QCustomArcLoader = getattr(Custom_Widgets, "QCustomArcLoader", None)
            QCustomSpinner = getattr(Custom_Widgets, "QCustomSpinner", None)
            QCustom3CirclesLoader = getattr(
                Custom_Widgets, "QCustom3CirclesLoader", None
            )

            if all([QCustomArcLoader, QCustomSpinner, QCustom3CirclesLoader]):
                CUSTOM_WIDGETS_AVAILABLE = True
                print("✅ Custom Widgets loaded via alternative method")
            else:
                raise ImportError("Widgets not found in module")

        except Exception as e2:
            print(f"⚠️ Alternative import failed: {e2}")
            print("Using fallback implementations")

except Exception as e:
    CUSTOM_WIDGETS_AVAILABLE = False
    print(f"QT-PyQt-PySide-Custom-Widgets not available: {e}")
    print("Using fallback implementations")


class EnhancedLoadingWidget(QWidget):
    """
    Enhanced loading widget that provides multiple loading animation styles
    Complements the existing ProgressDonut - doesn't replace it
    """

    loadingComplete = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        """Setup the enhanced loading widget UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)

        # Title
        title = QLabel("Enhanced Loading Indicators")
        title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        title.setStyleSheet("color: #E0E0E0; margin-bottom: 10px;")
        layout.addWidget(title)

        # Create different loading styles
        self.create_arc_loader(layout)
        self.create_spinner_loader(layout)
        self.create_circles_loader(layout)

    def create_arc_loader(self, layout):
        """Create arc-style loader"""
        if not CUSTOM_WIDGETS_AVAILABLE:
            fallback = QLabel("Arc Loader (requires QT-PyQt-PySide-Custom-Widgets)")
            fallback.setStyleSheet("color: #888; font-style: italic;")
            layout.addWidget(fallback)
            return

        container = QWidget()
        container_layout = QHBoxLayout(container)

        # Label
        label = QLabel("Arc Loader:")
        label.setStyleSheet("color: #E0E0E0; min-width: 100px;")
        container_layout.addWidget(label)

        # Arc loader
        self.arc_loader = QCustomArcLoader()
        self.arc_loader.setFixedSize(40, 40)
        container_layout.addWidget(self.arc_loader)

        container_layout.addStretch()
        layout.addWidget(container)

    def create_spinner_loader(self, layout):
        """Create spinner-style loader"""
        if not CUSTOM_WIDGETS_AVAILABLE:
            fallback = QLabel("Spinner Loader (requires QT-PyQt-PySide-Custom-Widgets)")
            fallback.setStyleSheet("color: #888; font-style: italic;")
            layout.addWidget(fallback)
            return

        container = QWidget()
        container_layout = QHBoxLayout(container)

        # Label
        label = QLabel("Spinner:")
        label.setStyleSheet("color: #E0E0E0; min-width: 100px;")
        container_layout.addWidget(label)

        # Spinner
        self.spinner = QCustomSpinner()
        self.spinner.setFixedSize(40, 40)
        container_layout.addWidget(self.spinner)

        container_layout.addStretch()
        layout.addWidget(container)

    def create_circles_loader(self, layout):
        """Create 3-circles loader"""
        if not CUSTOM_WIDGETS_AVAILABLE:
            fallback = QLabel(
                "3-Circles Loader (requires QT-PyQt-PySide-Custom-Widgets)"
            )
            fallback.setStyleSheet("color: #888; font-style: italic;")
            layout.addWidget(fallback)
            return

        container = QWidget()
        container_layout = QHBoxLayout(container)

        # Label
        label = QLabel("3-Circles:")
        label.setStyleSheet("color: #E0E0E0; min-width: 100px;")
        container_layout.addWidget(label)

        # 3-circles loader
        self.circles_loader = QCustom3CirclesLoader()
        self.circles_loader.setFixedSize(60, 40)
        container_layout.addWidget(self.circles_loader)

        container_layout.addStretch()
        layout.addWidget(container)

    def start_loading(self):
        """Start all loading animations"""
        if not CUSTOM_WIDGETS_AVAILABLE:
            return

        if hasattr(self, "arc_loader"):
            self.arc_loader.start()
        if hasattr(self, "spinner"):
            self.spinner.start()
        if hasattr(self, "circles_loader"):
            self.circles_loader.start()

    def stop_loading(self):
        """Stop all loading animations"""
        if not CUSTOM_WIDGETS_AVAILABLE:
            return

        if hasattr(self, "arc_loader"):
            self.arc_loader.stop()
        if hasattr(self, "spinner"):
            self.spinner.stop()
        if hasattr(self, "circles_loader"):
            self.circles_loader.stop()

        self.loadingComplete.emit()


class LinterStageLoader(QWidget):
    """
    Specialized loader for the 5-stage linter process
    Shows different animations for each stage: Ruff → Flake8 → Pylint → Bandit → MyPy
    """

    stageCompleted = Signal(str)  # Emits stage name when complete

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_stage = 0
        self.stages = ["Ruff", "Flake8", "Pylint", "Bandit", "MyPy"]
        self.setup_ui()

    def setup_ui(self):
        """Setup the linter stage loader UI"""
        layout = QVBoxLayout(self)

        # Stage indicator
        self.stage_label = QLabel("Ready to start linting")
        self.stage_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        self.stage_label.setStyleSheet("color: #4CAF50; margin-bottom: 15px;")
        layout.addWidget(self.stage_label)

        # Loader container
        loader_container = QWidget()
        loader_layout = QHBoxLayout(loader_container)

        if CUSTOM_WIDGETS_AVAILABLE:
            self.stage_loader = QCustomSpinner()
            self.stage_loader.setFixedSize(30, 30)
            loader_layout.addWidget(self.stage_loader)
        else:
            fallback = QLabel("⏳")
            fallback.setStyleSheet("font-size: 24px;")
            loader_layout.addWidget(fallback)

        loader_layout.addStretch()
        layout.addWidget(loader_container)

    def start_stage(self, stage_name: str):
        """Start a specific linting stage"""
        self.stage_label.setText(f"Running {stage_name}...")
        self.stage_label.setStyleSheet("color: #2196F3; margin-bottom: 15px;")

        if CUSTOM_WIDGETS_AVAILABLE and hasattr(self, "stage_loader"):
            self.stage_loader.start()

    def complete_stage(self, stage_name: str):
        """Mark a stage as complete"""
        self.stage_label.setText(f"✓ {stage_name} completed")
        self.stage_label.setStyleSheet("color: #4CAF50; margin-bottom: 15px;")

        if CUSTOM_WIDGETS_AVAILABLE and hasattr(self, "stage_loader"):
            self.stage_loader.stop()

        self.stageCompleted.emit(stage_name)

    def start_next_stage(self):
        """Move to the next linting stage"""
        if self.current_stage < len(self.stages):
            stage_name = self.stages[self.current_stage]
            self.start_stage(stage_name)
            self.current_stage += 1
        else:
            self.complete_all_stages()

    def complete_all_stages(self):
        """Mark all linting stages as complete"""
        self.stage_label.setText("🎉 All linting stages completed!")
        self.stage_label.setStyleSheet("color: #4CAF50; margin-bottom: 15px;")

        if CUSTOM_WIDGETS_AVAILABLE and hasattr(self, "stage_loader"):
            self.stage_loader.stop()

    def reset(self):
        """Reset the loader to initial state"""
        self.current_stage = 0
        self.stage_label.setText("Ready to start linting")
        self.stage_label.setStyleSheet("color: #4CAF50; margin-bottom: 15px;")

        if CUSTOM_WIDGETS_AVAILABLE and hasattr(self, "stage_loader"):
            self.stage_loader.stop()


# Export the widgets for use in main application
__all__ = ["EnhancedLoadingWidget", "LinterStageLoader", "CUSTOM_WIDGETS_AVAILABLE"]
