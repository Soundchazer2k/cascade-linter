# cascade_linter/gui/tools/ConfigManager.py
"""
Configuration Manager for Cascade Linter GUI

Provides a clean interface to QSettings for persistent configuration storage.
All GUI settings are organized into logical groups (General, Linters, Interface).

Usage:
    from cascade_linter.gui.tools.ConfigManager import ConfigManager

    # Set values
    ConfigManager.set_bool("General/CheckOnly", True)
    ConfigManager.set_int("Interface/Theme", 2)

    # Get values with defaults
    check_only = ConfigManager.get_bool("General/CheckOnly", False)
    theme_index = ConfigManager.get_int("Interface/Theme", 0)
"""

from PySide6.QtCore import QSettings
from typing import Any, Union
import os


class ConfigManager:
    """
    Centralized configuration management using QSettings.

    Configuration Groups:
    - General: Basic linting options (CheckOnly, UnsafeFixes, etc.)
    - Linters: Individual linter settings (RuffEnabled, MaxLineLength, etc.)
    - Interface: GUI preferences (Theme, AnimationsEnabled, LogFontSize, etc.)
    """

    _settings = None
    _organization = "VibeCodeLabs"
    _application = "CascadeLinter"

    @classmethod
    def _get_settings(cls) -> QSettings:
        """Get or create the QSettings instance."""
        if cls._settings is None:
            cls._settings = QSettings(cls._organization, cls._application)
        return cls._settings

    @classmethod
    def set_value(cls, key: str, value: Any) -> None:
        """Set a configuration value."""
        settings = cls._get_settings()
        settings.setValue(key, value)
        settings.sync()

    @classmethod
    def get_value(cls, key: str, default: Any = None) -> Any:
        """Get a configuration value with optional default."""
        settings = cls._get_settings()
        return settings.value(key, default)

    @classmethod
    def set_bool(cls, key: str, value: bool) -> None:
        """Set a boolean configuration value."""
        cls.set_value(key, value)

    @classmethod
    def get_bool(cls, key: str, default: bool = False) -> bool:
        """Get a boolean configuration value."""
        value = cls.get_value(key, default)
        # QSettings may return strings, so convert properly
        if isinstance(value, str):
            return value.lower() in ("true", "1", "yes", "on")
        return bool(value)

    @classmethod
    def set_int(cls, key: str, value: int) -> None:
        """Set an integer configuration value."""
        cls.set_value(key, value)

    @classmethod
    def get_int(cls, key: str, default: int = 0) -> int:
        """Get an integer configuration value."""
        value = cls.get_value(key, default)
        try:
            return int(value)
        except (ValueError, TypeError):
            return default

    @classmethod
    def set_string(cls, key: str, value: str) -> None:
        """Set a string configuration value."""
        cls.set_value(key, value)

    @classmethod
    def get_string(cls, key: str, default: str = "") -> str:
        """Get a string configuration value."""
        value = cls.get_value(key, default)
        return str(value) if value is not None else default

    @classmethod
    def remove(cls, key: str) -> None:
        """Remove a configuration key."""
        settings = cls._get_settings()
        settings.remove(key)
        settings.sync()

    @classmethod
    def contains(cls, key: str) -> bool:
        """Check if a configuration key exists."""
        settings = cls._get_settings()
        return settings.contains(key)

    @classmethod
    def get_all_keys(cls) -> list[str]:
        """Get all configuration keys."""
        settings = cls._get_settings()
        return settings.allKeys()

    @classmethod
    def clear_all(cls) -> None:
        """Clear all configuration (use with caution!)."""
        settings = cls._get_settings()
        settings.clear()
        settings.sync()

    @classmethod
    def export_settings(cls) -> dict[str, Any]:
        """Export all settings to a dictionary."""
        settings = cls._get_settings()
        result = {}
        for key in settings.allKeys():
            result[key] = settings.value(key)
        return result

    @classmethod
    def import_settings(cls, settings_dict: dict[str, Any]) -> None:
        """Import settings from a dictionary."""
        for key, value in settings_dict.items():
            cls.set_value(key, value)

    @classmethod
    def get_config_file_path(cls) -> str:
        """Get the path to the QSettings configuration file."""
        settings = cls._get_settings()
        return settings.fileName()


# Configuration defaults for easy access
class ConfigDefaults:
    """Default configuration values organized by group."""

    # General settings
    GENERAL = {
        "CheckOnly": False,
        "UnsafeFixes": False,
        "RespectGitignore": True,
        "KeepLogsDays": 30,
        "MaxLogFiles": 100,
        "VerboseLogging": False,
        "CustomLogDirectory": "",
    }

    # Linter settings
    LINTERS = {
        "RuffEnabled": True,
        "Flake8Enabled": True,
        "PylintEnabled": True,
        "BanditEnabled": True,
        "MyPyEnabled": True,
        "MaxLineLength": 88,
    }

    # Interface settings
    INTERFACE = {
        "Theme": 0,  # 0=System, 1=Light, 2=Dark, etc.
        "AnimationsEnabled": True,
        "LogFontSize": 10,
        "ShowLineNumbers": True,
        "AutoScrollLog": True,
        "MainWindowGeometry": "",
        "MainWindowState": "",
        "SplitterSizes": "",
    }

    @classmethod
    def apply_defaults(cls) -> None:
        """Apply default values for any missing configuration keys."""
        for group_name, defaults in [
            ("General", cls.GENERAL),
            ("Linters", cls.LINTERS),
            ("Interface", cls.INTERFACE),
        ]:
            for key, default_value in defaults.items():
                full_key = f"{group_name}/{key}"
                if not ConfigManager.contains(full_key):
                    ConfigManager.set_value(full_key, default_value)


if __name__ == "__main__":
    # Test the ConfigManager
    print("Testing ConfigManager...")

    # Apply defaults
    ConfigDefaults.apply_defaults()

    # Test setting and getting values
    ConfigManager.set_bool("General/CheckOnly", True)
    ConfigManager.set_int("Interface/Theme", 2)
    ConfigManager.set_string("Test/StringValue", "Hello World")

    # Test getting values
    check_only = ConfigManager.get_bool("General/CheckOnly")
    theme = ConfigManager.get_int("Interface/Theme")
    test_string = ConfigManager.get_string("Test/StringValue")

    print(f"CheckOnly: {check_only}")
    print(f"Theme: {theme}")
    print(f"TestString: {test_string}")

    # Test export/import
    exported = ConfigManager.export_settings()
    print(f"Exported {len(exported)} settings")

    # Show config file location
    print(f"Config file: {ConfigManager.get_config_file_path()}")

    # Clean up test value
    ConfigManager.remove("Test/StringValue")

    print("ConfigManager test completed successfully!")
