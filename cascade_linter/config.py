#!/usr/bin/env python3
"""
Configuration Management for Cascade Linter
Handles settings, preferences, and persistent configuration for both CLI and GUI.
"""

import json
import os
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Optional
from enum import Enum

from .core import LinterStage


class ThemeMode(Enum):
    """Theme options"""

    SYSTEM = "system"
    LIGHT = "light"
    DARK = "dark"


@dataclass
class LinterConfig:
    """Configuration for individual linters"""

    enabled: bool = True
    max_line_length: int = 88
    custom_args: List[str] = None

    def __post_init__(self):
        if self.custom_args is None:
            self.custom_args = []


@dataclass
class UIConfig:
    """UI-specific configuration"""

    theme: ThemeMode = ThemeMode.SYSTEM
    window_width: int = 800
    window_height: int = 600
    window_maximized: bool = False
    log_font_size: int = 10
    show_line_numbers: bool = True
    auto_scroll_log: bool = True
    animation_enabled: bool = True


@dataclass
class GeneralConfig:
    """General application configuration"""

    default_stages: List[str] = None
    check_only_default: bool = False
    unsafe_fixes_default: bool = False
    auto_save_logs: bool = True
    log_retention_days: int = 30
    max_log_files: int = 100
    respect_gitignore: bool = True

    def __post_init__(self):
        if self.default_stages is None:
            self.default_stages = ["ruff", "flake8", "pylint", "bandit", "mypy"]


@dataclass
class CascadeLinterConfig:
    """Complete configuration for Cascade Linter"""

    general: GeneralConfig = None
    ui: UIConfig = None
    linters: Dict[str, LinterConfig] = None

    def __post_init__(self):
        if self.general is None:
            self.general = GeneralConfig()
        if self.ui is None:
            self.ui = UIConfig()
        if self.linters is None:
            self.linters = {
                "ruff": LinterConfig(),
                "flake8": LinterConfig(),
                "pylint": LinterConfig(),
                "bandit": LinterConfig(),
                "mypy": LinterConfig(),
            }


class ConfigManager:
    """Manages configuration loading, saving, and validation"""

    def __init__(self, config_dir: Optional[Path] = None):
        """Initialize configuration manager

        Args:
            config_dir: Custom configuration directory, defaults to user config dir
        """
        if config_dir is None:
            config_dir = self._get_default_config_dir()

        self.config_dir = Path(config_dir)
        self.config_file = self.config_dir / "config.json"
        self.logs_dir = self.config_dir / "logs"

        # Ensure directories exist
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(exist_ok=True)

        self._config = self._load_config()

    def _get_default_config_dir(self) -> Path:
        """Get the default configuration directory for the current platform"""
        if os.name == "nt":  # Windows
            base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
        elif os.name == "posix":
            if "darwin" in os.uname().sysname.lower():  # macOS
                base = Path.home() / "Library" / "Application Support"
            else:  # Linux
                base = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
        else:
            base = Path.home() / ".config"

        return base / "cascade-linter"

    def _load_config(self) -> CascadeLinterConfig:
        """Load configuration from file or create default"""
        if self.config_file.exists():
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    data = json.load(f)

                # Convert data to config objects
                config = CascadeLinterConfig()

                if "general" in data:
                    config.general = GeneralConfig(**data["general"])

                if "ui" in data:
                    # Handle enum conversion
                    ui_data = data["ui"].copy()
                    if "theme" in ui_data:
                        ui_data["theme"] = ThemeMode(ui_data["theme"])
                    config.ui = UIConfig(**ui_data)

                if "linters" in data:
                    config.linters = {}
                    for linter_name, linter_data in data["linters"].items():
                        config.linters[linter_name] = LinterConfig(**linter_data)

                return config

            except (json.JSONDecodeError, TypeError, ValueError) as e:
                print(f"Warning: Could not load config file: {e}")
                print("Using default configuration")

        return CascadeLinterConfig()

    def save_config(self) -> bool:
        """Save current configuration to file"""
        try:
            # Convert config to serializable dict
            data = {
                "general": asdict(self._config.general),
                "ui": {
                    **asdict(self._config.ui),
                    "theme": self._config.ui.theme.value,  # Convert enum to string
                },
                "linters": {
                    name: asdict(config)
                    for name, config in self._config.linters.items()
                },
            }

            # Write to file with pretty formatting
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            return True

        except Exception as e:
            print(f"Error saving config: {e}")
            return False

    @property
    def config(self) -> CascadeLinterConfig:
        """Get the current configuration"""
        return self._config

    def update_general_config(self, **kwargs) -> None:
        """Update general configuration"""
        for key, value in kwargs.items():
            if hasattr(self._config.general, key):
                setattr(self._config.general, key, value)

    def update_ui_config(self, **kwargs) -> None:
        """Update UI configuration"""
        for key, value in kwargs.items():
            if hasattr(self._config.ui, key):
                setattr(self._config.ui, key, value)

    def update_linter_config(self, linter_name: str, **kwargs) -> None:
        """Update configuration for a specific linter"""
        if linter_name in self._config.linters:
            for key, value in kwargs.items():
                if hasattr(self._config.linters[linter_name], key):
                    setattr(self._config.linters[linter_name], key, value)

    def get_enabled_stages(self) -> List[LinterStage]:
        """Get list of enabled linter stages"""
        enabled_stages = []
        stage_mapping = {
            "ruff": LinterStage.RUFF,
            "flake8": LinterStage.FLAKE8,
            "pylint": LinterStage.PYLINT,
            "bandit": LinterStage.BANDIT,
            "mypy": LinterStage.MYPY,
        }

        for stage_name in self._config.general.default_stages:
            if (
                stage_name in self._config.linters
                and self._config.linters[stage_name].enabled
                and stage_name in stage_mapping
            ):
                enabled_stages.append(stage_mapping[stage_name])

        return enabled_stages

    def get_linter_args(self, linter_name: str) -> List[str]:
        """Get custom arguments for a linter"""
        if linter_name in self._config.linters:
            return self._config.linters[linter_name].custom_args.copy()
        return []

    def cleanup_old_logs(self) -> int:
        """Clean up old log files based on retention policy"""
        if not self.logs_dir.exists():
            return 0

        log_files = list(self.logs_dir.glob("*.log"))

        # Sort by modification time (newest first)
        log_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)

        removed_count = 0
        retention_days = self._config.general.log_retention_days
        max_files = self._config.general.max_log_files

        # Remove files beyond max count
        if len(log_files) > max_files:
            for log_file in log_files[max_files:]:
                try:
                    log_file.unlink()
                    removed_count += 1
                except OSError:
                    pass

        # Remove files older than retention period
        if retention_days > 0:
            import time

            cutoff_time = time.time() - (retention_days * 24 * 60 * 60)

            for log_file in log_files[:max_files]:  # Only check remaining files
                try:
                    if log_file.stat().st_mtime < cutoff_time:
                        log_file.unlink()
                        removed_count += 1
                except OSError:
                    pass

        return removed_count

    def get_log_file_path(self, prefix: str = "linting") -> Path:
        """Get path for a new log file"""
        from datetime import datetime

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return self.logs_dir / f"{prefix}_{timestamp}.log"

    def list_recent_logs(self, limit: int = 10) -> List[Path]:
        """Get list of recent log files"""
        if not self.logs_dir.exists():
            return []

        log_files = list(self.logs_dir.glob("*.log"))
        log_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)

        return log_files[:limit]

    def export_config(self, export_path: Path) -> bool:
        """Export configuration to a file"""
        try:
            # Create a copy of the current config file
            with open(self.config_file, "r", encoding="utf-8") as src:
                with open(export_path, "w", encoding="utf-8") as dst:
                    dst.write(src.read())
            return True
        except Exception as e:
            print(f"Error exporting config: {e}")
            return False

    def import_config(self, import_path: Path) -> bool:
        """Import configuration from a file"""
        try:
            # Backup current config
            backup_path = self.config_file.with_suffix(".json.backup")
            if self.config_file.exists():
                with open(self.config_file, "r", encoding="utf-8") as src:
                    with open(backup_path, "w", encoding="utf-8") as dst:
                        dst.write(src.read())

            # Import new config
            with open(import_path, "r", encoding="utf-8") as src:
                with open(self.config_file, "w", encoding="utf-8") as dst:
                    dst.write(src.read())

            # Reload configuration
            self._config = self._load_config()
            return True

        except Exception as e:
            print(f"Error importing config: {e}")
            # Try to restore backup
            try:
                if backup_path.exists():
                    with open(backup_path, "r", encoding="utf-8") as src:
                        with open(self.config_file, "w", encoding="utf-8") as dst:
                            dst.write(src.read())
                    self._config = self._load_config()
            except:
                pass
            return False

    def reset_to_defaults(self) -> None:
        """Reset configuration to defaults"""
        self._config = CascadeLinterConfig()
        self.save_config()


# Global configuration manager instance
_config_manager = None


def get_config_manager() -> ConfigManager:
    """Get the global configuration manager instance"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager


def get_config() -> CascadeLinterConfig:
    """Get the current configuration"""
    return get_config_manager().config
