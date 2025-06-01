# cascade_linter/gui/tools/LogExporter.py
"""
Log Export Utility for Cascade Linter GUI

Provides export functionality for logs in multiple formats (JSON, TXT, HTML).
Follows the self-contained tool pattern with no UI dependencies.

Usage:
    from cascade_linter.gui.tools.LogExporter import LogExporter
    
    # Export to JSON
    success = LogExporter.export_to_json(log_data, "logs.json")
    
    # Export to TXT
    success = LogExporter.export_to_txt(log_data, "logs.txt")
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, List, Union
from datetime import datetime


class LogExporter:
    """
    Self-contained log export utility.
    
    Supports multiple export formats without requiring GUI components.
    All methods are static for easy use throughout the application.
    """
    
    @staticmethod
    def export_to_json(log_data: Union[Dict[str, Any], List[Dict[str, Any]]], file_path: str) -> bool:
        """
        Export log data to JSON format.
        
        Args:
            log_data: Log data (dict or list of dicts)
            file_path: Output file path
            
        Returns:
            bool: True if export successful, False otherwise
        """
        try:
            # Ensure directory exists
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Prepare export data with metadata
            export_data = {
                "export_timestamp": datetime.now().isoformat(),
                "export_tool": "Cascade Linter v1.0.0",
                "data": log_data
            }
            
            # Write JSON with pretty formatting
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False, default=str)
            
            return True
            
        except Exception as e:
            print(f"Error exporting to JSON: {e}")
            return False
    
    @staticmethod
    def export_to_txt(log_data: Union[Dict[str, Any], str], file_path: str) -> bool:
        """
        Export log data to plain text format.
        
        Args:
            log_data: Log data (string or dict with log content)
            file_path: Output file path
            
        Returns:
            bool: True if export successful, False otherwise
        """
        try:
            # Ensure directory exists
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Convert log data to text
            if isinstance(log_data, str):
                log_text = log_data
            elif isinstance(log_data, dict) and "log" in log_data:
                log_text = log_data["log"]
            else:
                # Convert dict/list to readable text format
                log_text = LogExporter._format_data_as_text(log_data)
            
            # Add header
            header = f"""Cascade Linter Log Export
========================
Export Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Tool: Cascade Linter v1.0.0

""" + "="*50 + "\n\n"
            
            # Write to file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(header)
                f.write(log_text)
            
            return True
            
        except Exception as e:
            print(f"Error exporting to TXT: {e}")
            return False
    
    @staticmethod
    def export_to_html(log_data: Union[str, Dict[str, Any]], file_path: str, 
                      title: str = "Cascade Linter Logs") -> bool:
        """
        Export log data to HTML format with styling.
        
        Args:
            log_data: Log data (HTML string or dict with log content)
            file_path: Output file path
            title: HTML document title
            
        Returns:
            bool: True if export successful, False otherwise
        """
        try:
            # Ensure directory exists
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Extract HTML content
            if isinstance(log_data, str):
                log_html = log_data
            elif isinstance(log_data, dict) and "log" in log_data:
                log_html = log_data["log"]
            else:
                log_html = LogExporter._format_data_as_html(log_data)
            
            # Create full HTML document
            html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{
            font-family: 'Consolas', 'DejaVu Sans Mono', 'Menlo', monospace;
            background-color: #121212;
            color: #E0E0E0;
            margin: 20px;
            line-height: 1.4;
        }}
        .header {{
            border-bottom: 2px solid #357ABD;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }}
        .header h1 {{
            color: #357ABD;
            margin: 0;
        }}
        .export-info {{
            color: #AAAAAA;
            font-size: 12px;
            margin-top: 5px;
        }}
        .log-content {{
            background-color: #1E1E1E;
            border: 1px solid #555753;
            border-radius: 4px;
            padding: 15px;
            max-height: 80vh;
            overflow-y: auto;
        }}
        .log-line {{
            margin-bottom: 4px;
        }}
        /* Preserve inline styles from Rich output */
        pre {{
            margin: 0;
            white-space: pre-wrap;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{title}</h1>
        <div class="export-info">
            Exported: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | 
            Tool: Cascade Linter v1.0.0
        </div>
    </div>
    <div class="log-content">
        {log_html}
    </div>
</body>
</html>"""
            
            # Write to file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(html_template)
            
            return True
            
        except Exception as e:
            print(f"Error exporting to HTML: {e}")
            return False
    
    @staticmethod
    def _format_data_as_text(data: Any) -> str:
        """Convert structured data to readable text format."""
        if isinstance(data, dict):
            lines = []
            for key, value in data.items():
                if isinstance(value, (dict, list)):
                    lines.append(f"{key}:")
                    lines.append(LogExporter._format_data_as_text(value))
                else:
                    lines.append(f"{key}: {value}")
            return "\n".join(lines)
        elif isinstance(data, list):
            lines = []
            for i, item in enumerate(data):
                lines.append(f"[{i}] {LogExporter._format_data_as_text(item)}")
            return "\n".join(lines)
        else:
            return str(data)
    
    @staticmethod
    def _format_data_as_html(data: Any) -> str:
        """Convert structured data to HTML format."""
        if isinstance(data, dict):
            html_lines = []
            for key, value in data.items():
                if isinstance(value, (dict, list)):
                    html_lines.append(f"<strong>{key}:</strong><br>")
                    html_lines.append(LogExporter._format_data_as_html(value))
                else:
                    html_lines.append(f"<strong>{key}:</strong> {value}<br>")
            return "".join(html_lines)
        elif isinstance(data, list):
            html_lines = []
            for i, item in enumerate(data):
                html_lines.append(f"<div>[{i}] {LogExporter._format_data_as_html(item)}</div>")
            return "".join(html_lines)
        else:
            return str(data).replace('\n', '<br>')
    
    @staticmethod
    def get_supported_formats() -> List[str]:
        """Get list of supported export formats."""
        return ["json", "txt", "html"]
    
    @staticmethod
    def get_format_description(format_name: str) -> str:
        """Get description of export format."""
        descriptions = {
            "json": "Structured JSON format with metadata",
            "txt": "Plain text format with headers",
            "html": "Styled HTML format for viewing in browsers"
        }
        return descriptions.get(format_name, "Unknown format")


if __name__ == "__main__":
    # Test LogExporter functionality
    test_data = {
        "session_info": {
            "start_time": "2025-06-01 12:00:00",
            "total_files": 42,
            "total_issues": 15
        },
        "stages": [
            {"name": "Ruff", "issues": 8, "duration": 1.2},
            {"name": "Flake8", "issues": 4, "duration": 0.8},
            {"name": "Pylint", "issues": 3, "duration": 2.1}
        ]
    }
    
    # Test exports
    print("Testing LogExporter...")
    
    success_json = LogExporter.export_to_json(test_data, "test_export.json")
    print(f"JSON export: {'SUCCESS' if success_json else 'FAILED'}")
    
    success_txt = LogExporter.export_to_txt(test_data, "test_export.txt")
    print(f"TXT export: {'SUCCESS' if success_txt else 'FAILED'}")
    
    success_html = LogExporter.export_to_html(test_data, "test_export.html")
    print(f"HTML export: {'SUCCESS' if success_html else 'FAILED'}")
    
    print(f"Supported formats: {LogExporter.get_supported_formats()}")
