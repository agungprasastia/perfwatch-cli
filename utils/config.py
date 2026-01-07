"""
Config Loader - Load settings from YAML configuration file.
"""

import os
from pathlib import Path
from typing import Any, Optional
import yaml


class Config:
    """Configuration manager for Perfwatch."""
    
    _instance = None
    _config = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._config is None:
            self._load_config()
    
    def _load_config(self):
        """Load configuration from YAML file."""
        config_paths = [
            Path("config/settings.yaml"),
            Path("settings.yaml"),
            Path.home() / ".perfwatch" / "settings.yaml",
        ]
        
        for path in config_paths:
            if path.exists():
                with open(path, "r", encoding="utf-8") as f:
                    self._config = yaml.safe_load(f) or {}
                return
        
        # Default config if no file found
        self._config = {}
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a config value using dot notation.
        
        Example: config.get("loadtest.requests", 100)
        """
        keys = key.split(".")
        value = self._config
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
            
            if value is None:
                return default
        
        return value
    
    def get_ai_model(self) -> str:
        """Get AI model name."""
        return self.get("ai.model", "gemini-2.5-flash")
    
    def get_ai_temperature(self) -> float:
        """Get AI temperature."""
        return self.get("ai.temperature", 0.3)
    
    def get_loadtest_requests(self) -> int:
        """Get default load test requests."""
        return self.get("loadtest.requests", 100)
    
    def get_loadtest_concurrent(self) -> int:
        """Get default load test concurrent connections."""
        return self.get("loadtest.concurrent", 10)
    
    def get_loadtest_timeout(self) -> int:
        """Get default load test timeout."""
        return self.get("loadtest.timeout", 30)
    
    def get_pagespeed_strategy(self) -> str:
        """Get PageSpeed strategy (mobile/desktop)."""
        return self.get("pagespeed.strategy", "mobile")
    
    def get_pagespeed_categories(self) -> list:
        """Get PageSpeed categories."""
        return self.get("pagespeed.categories", [
            "performance", "accessibility", "best-practices", "seo"
        ])
    
    def get_reports_dir(self) -> str:
        """Get reports output directory."""
        return self.get("reports.output_dir", "reports")
    
    def get_reports_format(self) -> str:
        """Get default report format."""
        return self.get("reports.default_format", "html")


# Global config instance
config = Config()
