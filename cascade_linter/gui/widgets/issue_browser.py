#!/usr/bin/env python3
"""
Issue Browser Widget - Advanced issue visualization and navigation
FIXED: Uses core.py classes instead of duplicating them
"""

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTreeWidget,
    QTreeWidgetItem,
    QTextBrowser,
    QLabel,
    QPushButton,
    QSplitter,
    QGroupBox,
    QComboBox,
    QLineEdit,
    QFrame,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QColor

from typing import Dict, List, Optional
from pathlib import Path

# FIXED: Import from core.py instead of redefining
from cascade_linter.core import IssueItem, IssueSeverity


class IssueTreeWidget(QTreeWidget):
    """Custom tree widget for displaying issues by file"""

    issue_selected = Signal(object)  # Emits IssueItem when selected

    def __init__(self):
        super().__init__()
        self.setHeaderLabels(["File", "Issues", "Severity"])
        self.setAlternatingRowColors(True)
        self.setSortingEnabled(True)

        # Connect selection
        self.itemClicked.connect(self._on_item_clicked)

        # Store issues
        self.issues_by_file: Dict[str, List[IssueItem]] = {}

    def add_issues(self, issues: List[IssueItem]):
        """Add issues to the tree"""
        self.clear()
        self.issues_by_file.clear()

        # Group issues by file
        for issue in issues:
            if issue.file_path not in self.issues_by_file:
                self.issues_by_file[issue.file_path] = []
            self.issues_by_file[issue.file_path].append(issue)

        # Create tree items
        for file_path, file_issues in self.issues_by_file.items():
            file_item = QTreeWidgetItem(self)

            # File name and issue count
            file_name = Path(file_path).name
            issue_count = len(file_issues)
            file_item.setText(0, file_name)
            file_item.setText(1, str(issue_count))

            # Determine highest severity
            severities = [issue.severity for issue in file_issues]
            if any(sev == IssueSeverity.ERROR for sev in severities):
                file_item.setText(2, f"{IssueSeverity.ERROR.icon} Error")
                file_item.setForeground(2, QColor(IssueSeverity.ERROR.color))
            elif any(sev == IssueSeverity.WARNING for sev in severities):
                file_item.setText(2, f"{IssueSeverity.WARNING.icon} Warning")
                file_item.setForeground(2, QColor(IssueSeverity.WARNING.color))
            else:
                file_item.setText(2, f"{IssueSeverity.INFO.icon} Info")
                file_item.setForeground(2, QColor(IssueSeverity.INFO.color))

            # Set tooltip
            file_item.setToolTip(0, file_path)

            # Add issue items
            for issue in file_issues:
                issue_item = QTreeWidgetItem(file_item)
                issue_item.setText(
                    0, f"{issue.severity.icon} {issue.code}: {issue.message}"
                )
                issue_item.setText(1, f"Line {issue.line}, Column {issue.column}")
                issue_item.setText(2, issue.linter)

                # Store issue data
                issue_item.setData(0, Qt.UserRole, issue)

                # Set colors
                color = QColor(issue.severity.color)
                issue_item.setForeground(0, color)

        # Expand all items
        self.expandAll()

        # Resize columns
        self.resizeColumnToContents(0)
        self.resizeColumnToContents(1)
        self.resizeColumnToContents(2)

    def _on_item_clicked(self, item: QTreeWidgetItem, column: int):
        """Handle item click"""
        issue = item.data(0, Qt.UserRole)
        if isinstance(issue, IssueItem):
            self.issue_selected.emit(issue)


class IssueDetailWidget(QWidget):
    """Widget showing detailed information about selected issue"""

    def __init__(self):
        super().__init__()
        self._setup_ui()
        self.current_issue: Optional[IssueItem] = None

    def _setup_ui(self):
        """Set up the UI"""
        layout = QVBoxLayout(self)

        # Issue header
        self.header_frame = QFrame()
        self.header_frame.setFrameStyle(QFrame.StyledPanel)
        header_layout = QVBoxLayout(self.header_frame)

        self.issue_title = QLabel("No issue selected")
        self.issue_title.setFont(QFont("", 12, QFont.Bold))
        header_layout.addWidget(self.issue_title)

        self.issue_location = QLabel("")
        self.issue_location.setStyleSheet("color: gray;")
        header_layout.addWidget(self.issue_location)

        layout.addWidget(self.header_frame)

        # Code context
        code_group = QGroupBox("Code Context")
        code_layout = QVBoxLayout(code_group)

        self.code_viewer = QTextBrowser()
        self.code_viewer.setFont(QFont("Consolas, Monaco, monospace", 10))
        self.code_viewer.setMaximumHeight(200)
        code_layout.addWidget(self.code_viewer)

        layout.addWidget(code_group)

        # Issue details
        details_group = QGroupBox("Issue Details")
        details_layout = QVBoxLayout(details_group)

        self.details_text = QTextBrowser()
        self.details_text.setMaximumHeight(150)
        details_layout.addWidget(self.details_text)

        layout.addWidget(details_group)

        # Actions
        actions_layout = QHBoxLayout()

        self.fix_button = QPushButton("🔧 Auto-fix")
        self.fix_button.setEnabled(False)
        actions_layout.addWidget(self.fix_button)

        self.ignore_button = QPushButton("🚫 Ignore")
        self.ignore_button.setEnabled(False)
        actions_layout.addWidget(self.ignore_button)

        actions_layout.addStretch()

        self.open_file_button = QPushButton("📁 Open File")
        self.open_file_button.setEnabled(False)
        actions_layout.addWidget(self.open_file_button)

        layout.addLayout(actions_layout)

        layout.addStretch()

    def show_issue(self, issue: IssueItem):
        """Display details for the selected issue"""
        self.current_issue = issue

        # Update header
        severity_icon = issue.severity.icon
        self.issue_title.setText(f"{severity_icon} {issue.code}: {issue.message}")

        location_text = f"📁 {issue.file_path} • 📍 Line {issue.line}, Column {issue.column} • 🔧 {issue.linter}"
        self.issue_location.setText(location_text)

        # Load code context (simplified for now)
        self._load_code_context(issue)

        # Update details
        details_html = f"""
        <h3>Issue Information</h3>
        <p><strong>Code:</strong> {issue.code}</p>
        <p><strong>Severity:</strong> {issue.severity.severity_name.title()}</p>
        <p><strong>Linter:</strong> {issue.linter.title()}</p>
        <p><strong>Message:</strong> {issue.message}</p>
        
        <h3>Resolution</h3>
        <p>{self._get_resolution_advice(issue)}</p>
        """

        self.details_text.setHtml(details_html)

        # Enable buttons
        self.fix_button.setEnabled(True)
        self.ignore_button.setEnabled(True)
        self.open_file_button.setEnabled(True)

    def _load_code_context(self, issue: IssueItem):
        """Load and display code context around the issue"""
        try:
            file_path = Path(issue.file_path)
            if file_path.exists():
                with open(file_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()

                # Get context lines (3 before, issue line, 3 after)
                start_line = max(0, issue.line - 4)
                end_line = min(len(lines), issue.line + 3)

                context_html = (
                    "<pre style='background: #2b2b2b; color: #ffffff; padding: 10px;'>"
                )

                for i in range(start_line, end_line):
                    line_num = i + 1
                    line_content = lines[i].rstrip()

                    if line_num == issue.line:
                        # Highlight the issue line
                        context_html += f"<span style='background: #ff4444; color: white;'>{line_num:4d}: {line_content}</span>\n"
                        # Add pointer to issue column
                        pointer = " " * (6 + issue.column - 1) + "^"
                        context_html += (
                            f"<span style='color: #ff4444;'>{pointer}</span>\n"
                        )
                    else:
                        context_html += f"<span style='color: #888;'>{line_num:4d}:</span> {line_content}\n"

                context_html += "</pre>"
                self.code_viewer.setHtml(context_html)
            else:
                self.code_viewer.setText("File not found or not accessible")

        except Exception as e:
            self.code_viewer.setText(f"Error loading file: {e}")

    def _get_resolution_advice(self, issue: IssueItem) -> str:
        """Get resolution advice for the issue"""
        advice_map = {
            "F401": "This import is unused. Consider removing it or using it in your code.",
            "E302": "Add two blank lines before class/function definitions.",
            "W291": "Remove trailing whitespace from the end of the line.",
            "E501": "Break this line into multiple lines to stay under the length limit.",
            "F821": "This variable is undefined. Check for typos or import the necessary module.",
            "mypy-error": "This is a type checking error. Review the types and annotations in your code.",
        }

        return advice_map.get(
            issue.code,
            "Review the linter documentation for specific guidance on resolving this issue.",
        )


class IssueBrowserWidget(QWidget):
    """Complete issue browser with tree view and details"""

    def __init__(self):
        super().__init__()
        self._setup_ui()
        self.all_issues: List[IssueItem] = []

    def _setup_ui(self):
        """Set up the complete UI"""
        layout = QVBoxLayout(self)

        # Filters and controls
        controls_layout = QHBoxLayout()

        # Filter by severity
        controls_layout.addWidget(QLabel("Filter:"))

        self.severity_filter = QComboBox()
        self.severity_filter.addItems(["All", "Errors", "Warnings", "Info", "Style"])
        self.severity_filter.currentTextChanged.connect(self._apply_filters)
        controls_layout.addWidget(self.severity_filter)

        # Filter by linter - FIXED: Now includes MyPy
        self.linter_filter = QComboBox()
        self.linter_filter.addItems(
            [
                "All Linters",
                "Ruff",
                "Flake8",
                "Pylint",
                "Bandit",
                "MyPy",
            ]  # Added MyPy here
        )
        self.linter_filter.currentTextChanged.connect(self._apply_filters)
        controls_layout.addWidget(self.linter_filter)

        # Search
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search issues...")
        self.search_input.textChanged.connect(self._apply_filters)
        controls_layout.addWidget(self.search_input)

        controls_layout.addStretch()

        # Issue count
        self.issue_count_label = QLabel("No issues")
        controls_layout.addWidget(self.issue_count_label)

        layout.addLayout(controls_layout)

        # Main splitter
        splitter = QSplitter(Qt.Horizontal)

        # Issue tree
        self.issue_tree = IssueTreeWidget()
        self.issue_tree.issue_selected.connect(self._on_issue_selected)
        splitter.addWidget(self.issue_tree)

        # Issue details
        self.issue_detail = IssueDetailWidget()
        splitter.addWidget(self.issue_detail)

        # Set splitter proportions (60% tree, 40% details)
        splitter.setStretchFactor(0, 6)
        splitter.setStretchFactor(1, 4)

        layout.addWidget(splitter)

    def load_issues(self, issues: List[IssueItem]):
        """Load issues into the browser"""
        self.all_issues = issues

        # FIXED: Reset filters to show all issues by default
        self.severity_filter.setCurrentText("All")
        self.linter_filter.setCurrentText("All Linters")
        self.search_input.clear()

        self._apply_filters()

    def _apply_filters(self):
        """Apply current filters to the issue list"""
        filtered_issues = self.all_issues.copy()

        # Filter by severity
        severity_filter = self.severity_filter.currentText()
        if severity_filter != "All":
            severity_map = {
                "Errors": IssueSeverity.ERROR,
                "Warnings": IssueSeverity.WARNING,
                "Info": IssueSeverity.INFO,
                "Style": IssueSeverity.INFO,  # Map style to info
            }
            if severity_filter in severity_map:
                target_severity = severity_map[severity_filter]
                filtered_issues = [
                    issue
                    for issue in filtered_issues
                    if issue.severity == target_severity
                ]

        # Filter by linter
        linter_filter = self.linter_filter.currentText()
        if linter_filter != "All Linters":
            linter_name = linter_filter.lower()
            filtered_issues = [
                issue
                for issue in filtered_issues
                if issue.linter.lower() == linter_name
            ]

        # Filter by search text
        search_text = self.search_input.text().lower()
        if search_text:
            filtered_issues = [
                issue
                for issue in filtered_issues
                if (
                    search_text in issue.message.lower()
                    or search_text in issue.code.lower()
                    or search_text in Path(issue.file_path).name.lower()
                )
            ]

        # Update tree
        self.issue_tree.add_issues(filtered_issues)

        # Update count
        count = len(filtered_issues)
        total = len(self.all_issues)
        if count == total:
            self.issue_count_label.setText(f"{count} issues")
        else:
            self.issue_count_label.setText(f"{count} of {total} issues")

    def _on_issue_selected(self, issue: IssueItem):
        """Handle issue selection"""
        self.issue_detail.show_issue(issue)


# Example usage and test data
def create_sample_issues() -> List[IssueItem]:
    """Create sample issues for testing"""
    return [
        IssueItem(
            "src/main.py", 15, 10, "F401", "'os' imported but unused", "error", "ruff"
        ),
        IssueItem(
            "src/main.py", 23, 1, "E302", "expected 2 blank lines", "style", "flake8"
        ),
        IssueItem(
            "src/utils.py", 8, 25, "W291", "trailing whitespace", "warning", "ruff"
        ),
        IssueItem(
            "src/config.py",
            45,
            80,
            "E501",
            "line too long (88 > 79 characters)",
            "style",
            "flake8",
        ),
        IssueItem(
            "tests/test_main.py",
            12,
            5,
            "F821",
            "undefined name 'undefined_var'",
            "error",
            "ruff",
        ),
        # Add MyPy examples
        IssueItem(
            "src/main.py",
            30,
            15,
            "mypy-error",
            "Argument 1 to 'foo' has incompatible type",
            "error",
            "mypy",
        ),
        IssueItem(
            "src/utils.py",
            42,
            8,
            "mypy-error",
            "Function is missing a return type annotation",
            "info",
            "mypy",
        ),
    ]


if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)

    # Create and show the issue browser
    browser = IssueBrowserWidget()
    browser.load_issues(create_sample_issues())
    browser.resize(1000, 600)
    browser.show()

    sys.exit(app.exec())
