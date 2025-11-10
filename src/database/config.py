"""Database configuration management."""

import os
import yaml
from pathlib import Path
from typing import Dict, Any


class DatabaseConfig:
    """Manages database configuration from YAML and environment variables."""
    
    def __init__(self, env: str = None):
        """
        Initialize database configuration.
        
        Args:
            env: Environment name (development, test, production).
                 If None, uses APP_ENV environment variable or defaults to 'development'.
        """
        self.env = env or os.getenv('APP_ENV', 'development')
        self.config = self._load_config()
        self._validate()
    
    def _load_config(self) -> Dict[str, Any]:
        """
        Load configuration from YAML file and override with environment variables.
        
        Returns:
            Configuration dictionary for the current environment.
        """
        config_file = Path(__file__).parent.parent.parent / 'config' / 'database.yml'
        
        if not config_file.exists():
            raise FileNotFoundError(f"Database config file not found: {config_file}")
        
        with open(config_file, 'r') as f:
            all_configs = yaml.safe_load(f)
        
        if self.env not in all_configs:
            raise ValueError(f"Environment '{self.env}' not found in database.yml")
        
        config = all_configs[self.env].copy()
        
        # Override with environment variables
        config['host'] = os.getenv('DB_HOST', config.get('host'))
        config['port'] = int(os.getenv('DB_PORT', config.get('port', 5432)))
        config['database'] = os.getenv('DB_NAME', config.get('database'))
        config['user'] = os.getenv('DB_USER', config.get('user'))
        
        # Handle password with default from YAML
        password = config.get('password', '')
        if password.startswith('${') and password.endswith('}'):
            # Extract env var name and default: ${DB_PASSWORD:-default}
            env_expr = password[2:-1]
            if ':-' in env_expr:
                env_var, default = env_expr.split(':-', 1)
                config['password'] = os.getenv(env_var, default)
            else:
                config['password'] = os.getenv(env_expr, '')
        else:
            config['password'] = password
        
        return config
    
    def _validate(self):
        """Validate that required configuration fields are present."""
        required_fields = ['host', 'port', 'database', 'user', 'password']
        
        missing_fields = [field for field in required_fields if not self.config.get(field)]
        
        if missing_fields:
            raise ValueError(
                f"Missing required database configuration fields: {', '.join(missing_fields)}\n"
                f"Please set them in config/database.yml or via environment variables."
            )
    
    @property
    def connection_string(self) -> str:
        """
        Generate SQLAlchemy connection string.
        
        Returns:
            PostgreSQL connection string in format:
            postgresql://user:password@host:port/database
        """
        return (
            f"postgresql://{self.config['user']}:{self.config['password']}"
            f"@{self.config['host']}:{self.config['port']}/{self.config['database']}"
        )
    
    @property
    def pool_size(self) -> int:
        """Get connection pool size."""
        return self.config.get('pool_size', 5)
    
    @property
    def max_overflow(self) -> int:
        """Get maximum overflow connections."""
        return self.config.get('max_overflow', 15)
    
    @property
    def pool_timeout(self) -> int:
        """Get pool timeout in seconds."""
        return self.config.get('pool_timeout', 30)
    
    @property
    def pool_recycle(self) -> int:
        """Get pool recycle time in seconds."""
        return self.config.get('pool_recycle', 300)
    
    @property
    def echo(self) -> bool:
        """Get SQL echo setting (log queries)."""
        return self.config.get('echo', False)
    
    @property
    def pool_pre_ping(self) -> bool:
        """Get pool pre-ping setting (verify connections)."""
        return self.config.get('pool_pre_ping', False)
    
    @property
    def connect_args(self) -> Dict[str, Any]:
        """Get additional connection arguments."""
        return self.config.get('connect_args', {})
    
    def __repr__(self) -> str:
        """String representation (without password)."""
        return (
            f"DatabaseConfig(env='{self.env}', "
            f"host='{self.config['host']}', "
            f"database='{self.config['database']}')"
        )
