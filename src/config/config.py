"""
Configuration module for the Life To Do application.

Manages application configuration and settings.
"""
import os
from typing import Dict, Any, Optional
from pathlib import Path
import json


class ConfigError(Exception):
    """Custom exception for configuration-related errors."""
    pass


class Config:
    """
    Configuration manager for the Life To Do application.
    """
    
    def __init__(self, config_file: str = "config.json"):
        """
        Initialize the configuration manager.
        
        Args:
            config_file: Path to the configuration file
        """
        self.config_file = Path(config_file)
        self._config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """
        Load configuration from file or create default configuration.
        
        Returns:
            Dictionary containing configuration values
        """
        default_config = {
            "user_data_dir": "User_Data",
            "chat_log_file": "chat_log.txt",
            "goals_file": "goals.json",
            "default_model": "llama2",
            "window_size": "1200x800",
            "logging_level": "INFO"
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    # Merge with defaults to ensure all keys exist
                    default_config.update(user_config)
                    return default_config
            except (json.JSONDecodeError, IOError) as e:
                raise ConfigError(f"Error loading config file: {e}")
        else:
            # Create default config file
            self._save_config(default_config)
            return default_config
    
    def _save_config(self, config: Dict[str, Any]) -> None:
        """
        Save configuration to file.
        
        Args:
            config: Configuration dictionary to save
        """
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4)
        except IOError as e:
            raise ConfigError(f"Error saving config file: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.
        
        Args:
            key: Configuration key
            default: Default value if key doesn't exist
            
        Returns:
            Configuration value or default
        """
        return self._config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """
        Set a configuration value and save to file.
        
        Args:
            key: Configuration key
            value: Value to set
        """
        self._config[key] = value
        self._save_config(self._config)
    
    @property
    def user_data_dir(self) -> str:
        """Get the user data directory."""
        return self._config.get("user_data_dir", "User_Data")
    
    @property
    def chat_log_file(self) -> str:
        """Get the chat log file path."""
        return self._config.get("chat_log_file", "chat_log.txt")
    
    @property
    def goals_file(self) -> str:
        """Get the goals file path."""
        return self._config.get("goals_file", "goals.json")
    
    @property
    def default_model(self) -> str:
        """Get the default model name."""
        return self._config.get("default_model", "llama2")

    @property
    def window_size(self) -> str:
        """Get the window size."""
        return self._config.get("window_size", "1200x800")
    
    @property
    def logging_level(self) -> str:
        """Get the logging level."""
        return self._config.get("logging_level", "INFO")