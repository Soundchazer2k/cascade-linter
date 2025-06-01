# cascade_linter/gui/tools/ThemeLoader.py
"""
Theme Loader for Cascade Linter GUI

Manages loading and applying QSS themes for the application.
Supports 9 built-in themes plus system default.

Usage:
    from cascade_linter.gui.tools.ThemeLoader import ThemeLoader
    from PySide6.QtWidgets import QApplication
    
    app = QApplication.instance()
    ThemeLoader.load_theme("dark", app)
"""

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QFile, QTextStream
import os
from pathlib import Path
from typing import Optional


class ThemeLoader:
    """
    Handles loading and applying QSS stylesheets for theming.
    
    Available themes:
    0. System default (no custom styling)
    1. Light
    2. Dark  
    3. Solarized Light
    4. Solarized Dark
    5. Dracula
    6. Dweeb (sepia)
    7. Retro Green (Game Boy)
    8. Corps (teal & yellow)
    """
    
    THEME_NAMES = [
        "system",
        "light", 
        "dark",
        "solarized-light",
        "solarized-dark", 
        "dracula",
        "dweeb",
        "retro-green",
        "corps"
    ]
    
    THEME_DISPLAY_NAMES = [
        "System Default",
        "Light",
        "Dark", 
        "Solarized Light",
        "Solarized Dark",
        "Dracula",
        "Dweeb",
        "Retro Green", 
        "Corps"
    ]
    
    @classmethod
    def get_theme_directory(cls) -> Path:
        """Get the path to the themes directory."""
        # Navigate from this file to the assets/themes directory
        current_file = Path(__file__)
        project_root = current_file.parent.parent.parent.parent
        themes_dir = project_root / "assets" / "themes"
        return themes_dir
    
    @classmethod
    def get_theme_file_path(cls, theme_name: str) -> Path:
        """Get the full path to a theme QSS file."""
        themes_dir = cls.get_theme_directory()
        return themes_dir / f"{theme_name}.qss"
    
    @classmethod
    def load_qss_file(cls, file_path: Path) -> str:
        """Load QSS content from a file."""
        if not file_path.exists():
            raise FileNotFoundError(f"Theme file not found: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            raise RuntimeError(f"Failed to read theme file {file_path}: {e}")
    
    @classmethod
    def apply_qss_to_app(cls, qss_content: str, app: QApplication) -> None:
        """Apply QSS stylesheet to the application."""
        if app is None:
            raise ValueError("QApplication instance is required")
        
        app.setStyleSheet(qss_content)
    
    @classmethod
    def load_theme(cls, theme_name: str, app: QApplication) -> bool:
        """
        Load and apply a theme to the application.
        
        Args:
            theme_name: Name of the theme (e.g., "dark", "light", "system")
            app: QApplication instance
            
        Returns:
            True if theme was loaded successfully, False otherwise
        """
        if theme_name not in cls.THEME_NAMES:
            print(f"Warning: Unknown theme '{theme_name}', falling back to system")
            theme_name = "system"
        
        # System theme means no custom styling
        if theme_name == "system":
            app.setStyleSheet("")
            return True
        
        try:
            theme_file = cls.get_theme_file_path(theme_name)
            qss_content = cls.load_qss_file(theme_file)
            cls.apply_qss_to_app(qss_content, app)
            print(f"Successfully loaded theme: {theme_name}")
            return True
            
        except (FileNotFoundError, RuntimeError) as e:
            print(f"Failed to load theme '{theme_name}': {e}")
            # Fall back to system theme
            app.setStyleSheet("")
            return False
    
    @classmethod
    def load_theme_by_index(cls, theme_index: int, app: QApplication) -> bool:
        """Load a theme by its numeric index."""
        if 0 <= theme_index < len(cls.THEME_NAMES):
            theme_name = cls.THEME_NAMES[theme_index]
            return cls.load_theme(theme_name, app)
        else:
            print(f"Invalid theme index: {theme_index}")
            return cls.load_theme("system", app)
    
    @classmethod
    def get_available_themes(cls) -> list[tuple[int, str, str]]:
        """
        Get a list of available themes.
        
        Returns:
            List of tuples: (index, internal_name, display_name)
        """
        return [
            (i, name, display_name)
            for i, (name, display_name) in enumerate(
                zip(cls.THEME_NAMES, cls.THEME_DISPLAY_NAMES)
            )
        ]
    
    @classmethod
    def get_theme_display_name(cls, theme_name: str) -> str:
        """Get the user-friendly display name for a theme."""
        try:
            index = cls.THEME_NAMES.index(theme_name)
            return cls.THEME_DISPLAY_NAMES[index]
        except ValueError:
            return theme_name.title()
    
    @classmethod
    def get_theme_name_by_index(cls, index: int) -> str:
        """Get the internal theme name by index."""
        if 0 <= index < len(cls.THEME_NAMES):
            return cls.THEME_NAMES[index]
        return "system"
    
    @classmethod
    def validate_themes_directory(cls) -> bool:
        """Check if the themes directory exists and contains expected files."""
        themes_dir = cls.get_theme_directory()
        
        if not themes_dir.exists():
            print(f"Themes directory not found: {themes_dir}")
            return False
        
        missing_themes = []
        for theme_name in cls.THEME_NAMES[1:]:  # Skip "system"
            theme_file = cls.get_theme_file_path(theme_name)
            if not theme_file.exists():
                missing_themes.append(theme_name)
        
        if missing_themes:
            print(f"Missing theme files: {missing_themes}")
            return False
        
        return True
    
    @classmethod
    def create_themes_directory(cls) -> bool:
        """Create the themes directory if it doesn't exist."""
        themes_dir = cls.get_theme_directory()
        try:
            themes_dir.mkdir(parents=True, exist_ok=True)
            return True
        except Exception as e:
            print(f"Failed to create themes directory: {e}")
            return False


if __name__ == "__main__":
    # Test the ThemeLoader
    print("Testing ThemeLoader...")
    
    themes_dir = ThemeLoader.get_theme_directory()
    print(f"Themes directory: {themes_dir}")
    
    # Check if themes directory exists
    if not ThemeLoader.validate_themes_directory():
        print("Creating themes directory...")
        ThemeLoader.create_themes_directory()
    
    # List available themes
    print("\nAvailable themes:")
    for index, name, display_name in ThemeLoader.get_available_themes():
        print(f"  {index}: {name} ({display_name})")
    
    # Test theme file paths
    print("\nTheme file paths:")
    for theme_name in ThemeLoader.THEME_NAMES[1:]:  # Skip system
        file_path = ThemeLoader.get_theme_file_path(theme_name)
        exists = "✓" if file_path.exists() else "✗"
        print(f"  {exists} {theme_name}: {file_path}")
    
    print("ThemeLoader test completed!")
