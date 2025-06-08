from typing import Dict, Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTextEdit, QFrame, QScrollArea
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont


class ErrorExplanationWidget(QWidget):
    """
    Beginner-friendly error code explanation widget that shows:
    - What the error means in plain English
    - Why it matters for code quality  
    - How to fix it with examples
    - Links to learn more
    """
    
    show_help_requested = Signal(str, str)  # title, content
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_error_code = ""
        self.explanations = self._load_explanations()
        self.init_ui()
        
    def init_ui(self) -> None:
        """Initialize the UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        
        # Header
        header_layout = QHBoxLayout()
        
        self.title_label = QLabel("📚 Error Code Explanation")
        title_font = QFont()
        title_font.setPointSize(12)
        title_font.setBold(True)
        self.title_label.setFont(title_font)
        
        self.help_button = QPushButton("❓ More Help")
        self.help_button.setMaximumWidth(100)
        self.help_button.clicked.connect(self._show_detailed_help)
        
        header_layout.addWidget(self.title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.help_button)
        
        layout.addLayout(header_layout)
        
        # Content area
        self.content_area = QTextEdit()
        self.content_area.setMaximumHeight(200)
        self.content_area.setReadOnly(True)
        self.content_area.setStyleSheet("""
            QTextEdit {
                background-color: #0a2c24;
                color: #daffd4;
                border: 1px solid #17815d;
                border-radius: 4px;
                font-family: 'Segoe UI', sans-serif;
                font-size: 11pt;
                padding: 8px;
            }
        """)
        
        layout.addWidget(self.content_area)
        
        # Show initial message
        self.show_welcome_message()
        
    def show_welcome_message(self) -> None:
        """Show welcome message when no error is selected"""
        self.content_area.setHtml("""
            <div style="text-align: center; padding: 20px;">
                <h3 style="color: #93e7ae;">👋 Welcome to Error Explanations!</h3>
                <p>Click on any error in the logs above to see:</p>
                <ul style="text-align: left; margin: 10px 20px;">
                    <li><strong>What it means</strong> in plain English</li>
                    <li><strong>Why it matters</strong> for your code</li>
                    <li><strong>How to fix it</strong> with examples</li>
                    <li><strong>Tips to prevent it</strong> in the future</li>
                </ul>
                <p style="color: #93e7ae; font-style: italic;">
                    Perfect for learning while you lint! 🚀
                </p>
            </div>
        """)
        
    def explain_error(self, error_code: str) -> None:
        """Show explanation for a specific error code"""
        self.current_error_code = error_code
        
        if error_code in self.explanations:
            explanation = self.explanations[error_code]
            self._show_explanation(error_code, explanation)
        else:
            self._show_unknown_error(error_code)
            
    def _show_explanation(self, code: str, explanation: Dict[str, str]) -> None:
        """Display the explanation for an error code"""
        html_content = f"""
        <div style="padding: 10px;">
            <h2 style="color: #93e7ae; margin-bottom: 10px;">
                🔍 {code}: {explanation['title']}
            </h2>
            
            <div style="background: #1f5e4a; padding: 8px; border-radius: 4px; margin: 8px 0;">
                <strong style="color: #daffd4;">What it means:</strong><br>
                {explanation['description']}
            </div>
            
            <div style="background: #17815d; padding: 8px; border-radius: 4px; margin: 8px 0;">
                <strong style="color: #05130f;">Why it matters:</strong><br>
                {explanation['importance']}
            </div>
            
            <div style="background: #0a2c24; padding: 8px; border-radius: 4px; margin: 8px 0;">
                <strong style="color: #93e7ae;">How to fix:</strong><br>
                {explanation['fix']}
            </div>
            
            {explanation.get('example', '')}
            
            <p style="color: #93e7ae; font-style: italic; margin-top: 10px;">
                💡 {explanation.get('prevention', 'Use linters regularly to catch issues early!')}
            </p>
        </div>
        """
        
        self.content_area.setHtml(html_content)
        
    def _show_unknown_error(self, code: str) -> None:
        """Show message for unknown error codes"""
        html_content = f"""
        <div style="padding: 10px; text-align: center;">
            <h3 style="color: #93e7ae;">🤔 Unknown Error Code: {code}</h3>
            <p>This error code isn't in our beginner-friendly database yet, but here's how to learn more:</p>
            
            <div style="background: #1f5e4a; padding: 10px; border-radius: 4px; margin: 10px 0; text-align: left;">
                <strong>Quick Research Tips:</strong><br>
                • Search "{code} Python lint" in your browser<br>
                • Check the official docs for your linter<br>
                • Look at the error message context in your code<br>
                • Ask on Stack Overflow with the error code
            </div>
            
            <p style="color: #93e7ae;">
                Want to help? <strong>Report this error code</strong> so we can add it to our database!
            </p>
        </div>
        """
        
        self.content_area.setHtml(html_content)
        
    def _show_detailed_help(self) -> None:
        """Show detailed help popup"""
        if self.current_error_code and self.current_error_code in self.explanations:
            explanation = self.explanations[self.current_error_code]
            title = f"Detailed Help: {self.current_error_code}"
            content = self._generate_detailed_help_content(self.current_error_code, explanation)
        else:
            title = "Getting Started with Error Codes"
            content = self._generate_general_help_content()
            
        self.show_help_requested.emit(title, content)
        
    def _generate_detailed_help_content(self, code: str, explanation: Dict[str, str]) -> str:
        """Generate detailed help content for a specific error"""
        return f"""
        <h2>{code}: {explanation['title']}</h2>
        
        <h3>📖 Full Description</h3>
        <p>{explanation['description']}</p>
        
        <h3>🎯 Why This Matters</h3>
        <p>{explanation['importance']}</p>
        
        <h3>🔧 Step-by-Step Fix</h3>
        <p>{explanation['fix']}</p>
        
        {explanation.get('example', '')}
        
        <h3>🛡️ Prevention Tips</h3>
        <p>{explanation.get('prevention', 'Use automated linting in your IDE and CI/CD pipeline.')}</p>
        
        <h3>📚 Learn More</h3>
        <ul>
        <li>Search "<strong>{code} Python</strong>" for official documentation</li>
        <li>Check PEP 8 style guide for style-related issues</li>
        <li>Use <code>--explain {code}</code> in command line for quick reference</li>
        </ul>
        """
        
    def _generate_general_help_content(self) -> str:
        """Generate general help content about error codes"""
        return """
        <h2>🎓 Understanding Error Codes</h2>
        
        <p>Error codes help you identify and fix issues in your Python code. Here's what the letters mean:</p>
        
        <h3>📝 Code Prefixes</h3>
        <ul>
        <li><strong>E</strong> - Error (style violations, PEP 8 issues)</li>
        <li><strong>W</strong> - Warning (potential problems)</li>
        <li><strong>F</strong> - Fatal (syntax errors, undefined names)</li>
        <li><strong>C</strong> - Convention (code style suggestions)</li>
        <li><strong>R</strong> - Refactor (code structure improvements)</li>
        </ul>
        
        <h3>🎯 Priority Guide for Beginners</h3>
        <ol>
        <li><strong>Fix F-codes first</strong> - These break your code</li>
        <li><strong>Address E-codes next</strong> - These improve readability</li>
        <li><strong>Consider W-codes</strong> - These prevent future problems</li>
        <li><strong>Learn from C/R-codes</strong> - These teach best practices</li>
        </ol>
        
        <h3>💡 Pro Tips</h3>
        <ul>
        <li>Start with auto-fixable issues (use our Auto-Fix tab!)</li>
        <li>Focus on one file at a time to avoid overwhelm</li>
        <li>Use this explanation panel to learn as you go</li>
        <li>Set up your IDE to show these errors in real-time</li>
        </ul>
        """
        
    def _load_explanations(self) -> Dict[str, Dict[str, str]]:
        """Load beginner-friendly error code explanations"""
        return {
            "E501": {
                "title": "Line Too Long",
                "description": "Your line has more characters than the recommended limit (usually 79 or 88 characters).",
                "importance": "Long lines are hard to read on smaller screens and in code reviews. They make your code less accessible to other developers.",
                "fix": "Break the line into multiple lines using parentheses, backslashes, or by splitting strings. Many IDEs can do this automatically.",
                "example": """
                <div style="background: #0a2c24; padding: 8px; border-radius: 4px; margin: 8px 0; font-family: monospace;">
                    <strong style="color: #ff5555;">❌ Too long:</strong><br>
                    <code>result = some_very_long_function_name(argument1, argument2, argument3, argument4)</code><br><br>
                    <strong style="color: #50fa7b;">✅ Better:</strong><br>
                    <code>result = some_very_long_function_name(<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;argument1, argument2,<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;argument3, argument4<br>
                    )</code>
                </div>
                """,
                "prevention": "Set up line length guides in your IDE and enable auto-formatting on save."
            },
            
            "F401": {
                "title": "Unused Import",
                "description": "You imported a module or function but never used it in your code.",
                "importance": "Unused imports clutter your code, slow down startup time, and can confuse other developers about what dependencies are actually needed.",
                "fix": "Remove the import line, or if you plan to use it later, add a comment explaining why it's there.",
                "example": """
                <div style="background: #0a2c24; padding: 8px; border-radius: 4px; margin: 8px 0; font-family: monospace;">
                    <strong style="color: #ff5555;">❌ Unused:</strong><br>
                    <code>import os  # Never used anywhere</code><br><br>
                    <strong style="color: #50fa7b;">✅ Solution:</strong><br>
                    <code># Remove the import, or use it:<br>
                    import os<br>
                    current_dir = os.getcwd()</code>
                </div>
                """,
                "prevention": "Use IDE extensions that highlight unused imports, and clean them up regularly."
            },
            
            "W291": {
                "title": "Trailing Whitespace",
                "description": "There are invisible spaces or tabs at the end of a line.",
                "importance": "Trailing whitespace is invisible but causes unnecessary changes in version control and can confuse some text processing tools.",
                "fix": "Remove spaces/tabs from the end of the line. Most editors can do this automatically.",
                "example": """
                <div style="background: #0a2c24; padding: 8px; border-radius: 4px; margin: 8px 0; font-family: monospace;">
                    <strong style="color: #ff5555;">❌ With trailing spaces:</strong><br>
                    <code>def hello():___</code> (underscores represent spaces)<br><br>
                    <strong style="color: #50fa7b;">✅ Clean:</strong><br>
                    <code>def hello():</code>
                </div>
                """,
                "prevention": "Enable 'trim trailing whitespace on save' in your editor settings."
            },
            
            "F841": {
                "title": "Unused Variable",
                "description": "You assigned a value to a variable but never used it anywhere in your code.",
                "importance": "Unused variables suggest incomplete code, potential bugs, or unnecessary complexity. They also consume memory for no reason.",
                "fix": "Either use the variable in your code, or remove the assignment. If you need it for debugging, prefix the name with underscore.",
                "example": """
                <div style="background: #0a2c24; padding: 8px; border-radius: 4px; margin: 8px 0; font-family: monospace;">
                    <strong style="color: #ff5555;">❌ Unused:</strong><br>
                    <code>name = input("Your name: ")<br>
                    print("Hello world!")  # name is never used</code><br><br>
                    <strong style="color: #50fa7b;">✅ Fixed:</strong><br>
                    <code>name = input("Your name: ")<br>
                    print(f"Hello {name}!")</code>
                </div>
                """,
                "prevention": "Use variables immediately after creating them, or consider if you actually need them."
            },
            
            "C0114": {
                "title": "Missing Module Docstring",
                "description": "Your Python file doesn't have a docstring at the top explaining what it does.",
                "importance": "Module docstrings help other developers (and future you!) understand the purpose of your code file.",
                "fix": "Add a triple-quoted string at the very top of your file describing what it does.",
                "example": """
                <div style="background: #0a2c24; padding: 8px; border-radius: 4px; margin: 8px 0; font-family: monospace;">
                    <strong style="color: #50fa7b;">✅ Good example:</strong><br>
                    <code>"""<br>
                    This module handles user authentication and login.<br>
                    <br>
                    Contains functions for password validation, session management,<br>
                    and user profile operations.<br>
                    """<br><br>
                    import hashlib<br>
                    # ... rest of your code</code>
                </div>
                """,
                "prevention": "Start new files with a docstring explaining their purpose before writing any code."
            },
            
            "E302": {
                "title": "Expected 2 Blank Lines",
                "description": "PEP 8 style guide requires 2 blank lines before top-level function and class definitions.",
                "importance": "Consistent spacing makes code more readable and follows Python community standards.",
                "fix": "Add an extra blank line before your function or class definition.",
                "example": """
                <div style="background: #0a2c24; padding: 8px; border-radius: 4px; margin: 8px 0; font-family: monospace;">
                    <strong style="color: #ff5555;">❌ Only 1 blank line:</strong><br>
                    <code>import sys<br>
                    <br>
                    def main():</code><br><br>
                    <strong style="color: #50fa7b;">✅ Proper spacing:</strong><br>
                    <code>import sys<br>
                    <br>
                    <br>
                    def main():</code>
                </div>
                """,
                "prevention": "Use an auto-formatter like Black that handles spacing automatically."
            }
        } 