"""
Settings Manager Module
Handles loading and saving configuration to JSON file.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any


class SettingsManager:
    """
    Manages application settings and persistence to JSON file.
    Follows XDG Base Directory Specification.
    """

    def __init__(self):
        """Initialize settings manager and create config directory if needed."""
        self.config_dir = Path.home() / ".config" / "clipguard"
        self.config_file = self.config_dir / "settings.json"
        self.settings: Dict[str, Any] = {}
        
        # Ensure config directory exists
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Load settings
        self.load()

    def load(self):
        """Load settings from JSON file."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    self.settings = json.load(f)
            except (json.JSONDecodeError, IOError):
                # If file is corrupted, start with defaults
                self.settings = self._get_default_settings()
        else:
            # First run, use defaults
            self.settings = self._get_default_settings()
            self.save()

    def save(self):
        """Save settings to JSON file."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
        except IOError as e:
            print(f"Error saving settings: {e}")

    def _get_default_settings(self) -> Dict[str, Any]:
        """
        Get default settings structure.
        
        Returns:
            Dictionary with default settings
        """
        from masking_engine import MaskingEngine
        
        return {
            "monitoring_active": True,
            "builtin_patterns": MaskingEngine.BUILTIN_PATTERNS.copy(),
            "custom_patterns": {}
        }

    def get(self, key: str, default=None) -> Any:
        """
        Get a setting value.
        
        Args:
            key: Setting key
            default: Default value if key doesn't exist
            
        Returns:
            Setting value or default
        """
        return self.settings.get(key, default)

    def set(self, key: str, value: Any):
        """
        Set a setting value.
        
        Args:
            key: Setting key
            value: Setting value
        """
        self.settings[key] = value

    def get_all_patterns(self) -> Dict[str, dict]:
        """
        Get all patterns (built-in and custom) merged.
        
        Returns:
            Dictionary of all patterns
        """
        builtin = self.get("builtin_patterns", {})
        custom = self.get("custom_patterns", {})
        return {**builtin, **custom}

    def update_pattern(self, name: str, pattern_data: dict, is_custom: bool = False):
        """
        Update a specific pattern.
        
        Args:
            name: Pattern name
            pattern_data: Pattern configuration
            is_custom: Whether this is a custom pattern
        """
        if is_custom:
            custom = self.get("custom_patterns", {})
            custom[name] = pattern_data
            self.set("custom_patterns", custom)
        else:
            builtin = self.get("builtin_patterns", {})
            builtin[name] = pattern_data
            self.set("builtin_patterns", builtin)
        
        self.save()

    def delete_pattern(self, name: str):
        """
        Delete a custom pattern.
        
        Args:
            name: Pattern name to delete
        """
        custom = self.get("custom_patterns", {})
        if name in custom:
            del custom[name]
            self.set("custom_patterns", custom)
            self.save()

    def add_custom_pattern(self, name: str, pattern: str, replacement: str):
        """
        Add a new custom pattern.
        
        Args:
            name: Pattern name
            pattern: Regex pattern
            replacement: Replacement text
        """
        custom = self.get("custom_patterns", {})
        custom[name] = {
            "pattern": pattern,
            "replacement": replacement,
            "enabled": True,
            "custom": True
        }
        self.set("custom_patterns", custom)
        self.save()


