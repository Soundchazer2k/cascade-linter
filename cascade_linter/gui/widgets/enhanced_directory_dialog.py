#!/usr/bin/env python3
"""
Enhanced directory dialog for Cascade Linter GUI
Adds intelligent directory detection and validation
"""

import os
from pathlib import Path
from typing import List, Tuple, Optional
import fnmatch


class SmartPathValidator:
    """Intelligent path validation and Python project detection"""

    PYTHON_INDICATORS = [
        "*.py",
        "pyproject.toml",
        "setup.py",
        "requirements.txt",
        "Pipfile",
        "setup.cfg",
        "tox.ini",
        "__pycache__",
        "*.pyx",  # Cython files
    ]

    EXCLUDE_PATTERNS = [
        "node_modules",
        ".git",
        "__pycache__",
        "*.egg-info",
        "dist",
        "build",
        ".tox",
        ".pytest_cache",
        ".mypy_cache",
    ]

    def __init__(self):
        self.last_scan_results = {}

    def is_python_project(self, path: Path) -> Tuple[bool, str, dict]:
        """
        Determine if a directory contains a Python project
        Returns: (is_python_project, confidence_reason, scan_info)
        """
        if not path.exists() or not path.is_dir():
            return False, "Path doesn't exist or isn't a directory", {}

        scan_info = {
            "python_files": 0,
            "config_files": [],
            "subdirectories": 0,
            "total_size_mb": 0,
            "estimated_scan_time": 0,
        }

        # Quick scan for Python indicators
        python_files = 0
        config_files = []

        try:
            # Scan up to 1000 files for performance
            file_count = 0
            for root, dirs, files in os.walk(path):
                # Skip excluded directories
                dirs[:] = [
                    d
                    for d in dirs
                    if not any(
                        fnmatch.fnmatch(d, pattern) for pattern in self.EXCLUDE_PATTERNS
                    )
                ]

                for file in files:
                    file_count += 1
                    if file_count > 1000:  # Limit for performance
                        break

                    if file.endswith(".py"):
                        python_files += 1
                    elif file in [
                        "pyproject.toml",
                        "setup.py",
                        "requirements.txt",
                        "Pipfile",
                    ]:
                        config_files.append(file)

                if file_count > 1000:
                    break

            scan_info["python_files"] = python_files
            scan_info["config_files"] = config_files

            # Determine confidence
            if python_files == 0 and not config_files:
                return False, "No Python files or configuration found", scan_info
            elif python_files > 10 or config_files:
                confidence = "High confidence Python project"
            elif python_files > 0:
                confidence = f"Found {python_files} Python files"
            else:
                confidence = f"Found config files: {', '.join(config_files)}"

            # Estimate scan time
            scan_info["estimated_scan_time"] = min(
                python_files * 0.1, 60
            )  # Max 1 minute estimate

            return True, confidence, scan_info

        except Exception as e:
            return False, f"Error scanning directory: {str(e)}", scan_info

    def get_directory_recommendations(self, path: Path) -> List[str]:
        """Get recommendations for improving linting experience"""
        recommendations = []

        if not (path / ".gitignore").exists():
            recommendations.append(
                "Consider adding a .gitignore file to exclude unnecessary files"
            )

        if not any(
            (path / config).exists() for config in ["pyproject.toml", "setup.cfg"]
        ):
            recommendations.append(
                "Consider adding pyproject.toml for project configuration"
            )

        if (path / "requirements.txt").exists() and not (path / "venv").exists():
            recommendations.append(
                "Consider using a virtual environment (venv) for dependencies"
            )

        return recommendations


class EnhancedDirectoryDialog:
    """Enhanced directory selection with smart validation"""

    def __init__(self, parent=None):
        self.parent = parent
        self.validator = SmartPathValidator()

    def select_directory_with_validation(self) -> Optional[Tuple[Path, dict]]:
        """Select directory with intelligent validation and preview"""
        from PySide6.QtWidgets import (
            QFileDialog,
            QMessageBox,
            QDialog,
            QVBoxLayout,
            QLabel,
            QTextEdit,
            QPushButton,
            QHBoxLayout,
        )

        # Standard directory selection
        directory = QFileDialog.getExistingDirectory(
            self.parent,
            "Select Python Project Directory",
            str(Path.home()),
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks,
        )

        if not directory:
            return None

        path = Path(directory)
        is_python, reason, scan_info = self.validator.is_python_project(path)

        if not is_python:
            # Show warning dialog with option to proceed anyway
            reply = QMessageBox.question(
                self.parent,
                "Directory Validation",
                f"This directory may not contain a Python project.\n\n"
                f"Reason: {reason}\n\n"
                f"Do you want to proceed anyway?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )

            if reply == QMessageBox.No:
                return None

        # Show project preview dialog
        preview_dialog = QDialog(self.parent)
        preview_dialog.setWindowTitle("Project Preview")
        preview_dialog.setMinimumSize(500, 400)

        layout = QVBoxLayout(preview_dialog)

        # Project info
        info_label = QLabel(f"<h3>Project: {path.name}</h3>")
        layout.addWidget(info_label)

        # Scan results
        results_text = QTextEdit()
        results_text.setReadOnly(True)
        results_content = f"""
<b>Scan Results:</b><br>
• Python files found: {scan_info.get("python_files", 0)}<br>
• Configuration files: {", ".join(scan_info.get("config_files", [])) or "None"}<br>
• Estimated scan time: {scan_info.get("estimated_scan_time", 0):.1f} seconds<br>
• Confidence: {reason}<br><br>

<b>Recommendations:</b><br>
"""
        recommendations = self.validator.get_directory_recommendations(path)
        for rec in recommendations:
            results_content += f"• {rec}<br>"

        if not recommendations:
            results_content += "• Project looks well-configured!<br>"

        results_text.setHtml(results_content)
        layout.addWidget(results_text)

        # Buttons
        button_layout = QHBoxLayout()
        proceed_btn = QPushButton("Proceed with Linting")
        cancel_btn = QPushButton("Cancel")

        proceed_btn.clicked.connect(preview_dialog.accept)
        cancel_btn.clicked.connect(preview_dialog.reject)

        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(proceed_btn)
        layout.addLayout(button_layout)

        if preview_dialog.exec() == QDialog.Accepted:
            return path, scan_info

        return None
