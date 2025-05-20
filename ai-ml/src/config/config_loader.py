"""
Configuration Loader with Dynamic Updates
"""
from typing import Dict, Any, Optional, Type, cast
import os
import yaml
import logging
from pathlib import Path

class ConfigLoader:
    _instance: Optional['ConfigLoader'] = None
    _config: Dict[str, Dict[str, Any]] = {}
    
    def __new__(cls: Type['ConfigLoader']) -> 'ConfigLoader':
        if cls._instance is None:
            cls._instance = super(ConfigLoader, cls).__new__(cls)
        return cast(ConfigLoader, cls._instance)
    
    def __init__(self):
        self.base_dir = Path(os.path.dirname(os.path.dirname(__file__)))
        self.config_dir = self.base_dir / 'config'
        self.env_prefix = 'SCOPE3_'
        
    def load_config(self, config_name: str) -> Dict[str, Any]:
        """Load configuration with environment overrides"""
        config_path = self.config_dir / f"{config_name}.yaml"
        
        try:
            # Load base config
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
                
            # Apply environment overrides
            config = self._apply_env_overrides(config)
            
            # Cache config
            self._config[config_name] = config
            
            return config
            
        except Exception as e:
            logging.error(f"Error loading config {config_name}: {e}")
            return {}
            
    def get_config(
        self,
        config_name: str,
        section: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get configuration, optionally for specific section"""
        if config_name not in self._config:
            self.load_config(config_name)
            
        config = self._config.get(config_name, {})
        
        if section:
            return config.get(section, {})
        return config
        
    def _apply_env_overrides(
        self,
        config: Dict[str, Any],
        prefix: str = ''
    ) -> Dict[str, Any]:
        """Apply environment variable overrides to config"""
        for key, value in config.items():
            env_key = f"{self.env_prefix}{prefix}{key}".upper()
            
            if isinstance(value, dict):
                # Recurse into nested dicts
                config[key] = self._apply_env_overrides(
                    value,
                    f"{prefix}{key}_"
                )
            else:
                # Override with environment variable if exists
                env_value = os.getenv(env_key)
                if env_value is not None:
                    # Convert to appropriate type
                    if isinstance(value, bool):
                        config[key] = env_value.lower() == 'true'
                    elif isinstance(value, int):
                        config[key] = int(env_value)
                    elif isinstance(value, float):
                        config[key] = float(env_value)
                    else:
                        config[key] = env_value
                        
        return config
        
    def reload_config(self, config_name: str) -> Dict[str, Any]:
        """Reload configuration from disk"""
        if config_name in self._config:
            del self._config[config_name]
        return self.load_config(config_name)
        
    def update_config(
        self,
        config_name: str,
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update configuration with new values"""
        config = self.get_config(config_name)
        
        def deep_update(d: Dict[str, Any], u: Dict[str, Any]) -> Dict[str, Any]:
            for k, v in u.items():
                if isinstance(v, dict):
                    d[k] = deep_update(d.get(k, {}), v)
                else:
                    d[k] = v
            return d
            
        config = deep_update(config, updates)
        self._config[config_name] = config
        
        return config
        
    @staticmethod
    def get_instance() -> 'ConfigLoader':
        """Get singleton instance"""
        if ConfigLoader._instance is None:
            ConfigLoader()
        return cast(ConfigLoader, ConfigLoader._instance)