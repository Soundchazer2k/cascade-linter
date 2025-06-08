            self.actions_layout.addWidget(checkbox)
        
        # Add stretch to push items to top
        self.actions_layout.addStretch()
    
    # --- PUBLIC METHODS FOR MAIN WINDOW INTEGRATION ---
    
    def set_directories_from_main_window(self, directories: List[str]):
        """Set directories to analyze from main window"""
        self.directories_to_analyze = directories.copy()
        if directories:
            self.btn_run_analysis.setEnabled(True)
            self.lbl_status.setText(f"Ready to analyze {len(directories)} directories")
            self.lbl_status.setStyleSheet("QLabel { color: #73d216; font-weight: bold; }")
        else:
            self.btn_run_analysis.setEnabled(False)
            self.lbl_status.setText("No directories selected")
            self.lbl_status.setStyleSheet("QLabel { color: #f57900; font-weight: bold; }")
    
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
        
        total_modules = self.current_analysis.get('total_modules', 0)
        risk_distribution = self.current_analysis.get('risk_distribution', {})
        critical_count = risk_distribution.get('CRITICAL', 0)
        
        if critical_count > 0:
            return f"Analysis: {total_modules} modules, {critical_count} critical issues"
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
        warning_label.setStyleSheet("""
            QLabel {
                background-color: #2e3436;
                border: 2px solid #f57900;
                border-radius: 8px;
                color: #eeeeec;
                font-size: 12pt;
                padding: 30px;
                line-height: 1.5;
            }
        """)
        
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
        return EnhancedAnalyticsTab(parent)
    else:
        return MockAnalyticsTab(parent)


# Export the main class
__all__ = ['EnhancedAnalyticsTab', 'MockAnalyticsTab', 'create_analytics_tab']
