"""Database migration runner for Add'as Platform."""

import logging
from pathlib import Path
from typing import List, Tuple
from sqlalchemy import text
from sqlalchemy.orm import Session

from src.database.connection import DatabaseConnection

logger = logging.getLogger(__name__)


class MigrationRunner:
    """Manages database schema migrations."""
    
    def __init__(self, db: DatabaseConnection):
        """
        Initialize migration runner.
        
        Args:
            db: DatabaseConnection instance.
        """
        self.db = db
        self.migrations_dir = Path(__file__).parent / 'migrations'
    
    def get_applied_migrations(self, session: Session) -> List[int]:
        """
        Get list of already applied migration versions.
        
        Args:
            session: Database session.
        
        Returns:
            List of applied migration version numbers.
        """
        try:
            result = session.execute(
                text("SELECT version FROM schema_migrations ORDER BY version")
            )
            return [row[0] for row in result]
        except Exception as e:
            # Table doesn't exist yet, no migrations applied
            logger.debug(f"schema_migrations table not found: {e}")
            return []
    
    def get_available_migrations(self) -> List[Tuple[int, Path]]:
        """
        Get list of available migration files.
        
        Returns:
            List of tuples (version, file_path) sorted by version.
        """
        migrations = []
        
        for file_path in sorted(self.migrations_dir.glob('*.sql')):
            # Extract version from filename (e.g., 001_initial_schema.sql -> 1)
            try:
                version = int(file_path.stem.split('_')[0])
                migrations.append((version, file_path))
            except (ValueError, IndexError):
                logger.warning(f"Skipping invalid migration file: {file_path.name}")
        
        return sorted(migrations, key=lambda x: x[0])
    
    def get_pending_migrations(self, session: Session) -> List[Tuple[int, Path]]:
        """
        Get list of migrations that haven't been applied yet.
        
        Args:
            session: Database session.
        
        Returns:
            List of tuples (version, file_path) for pending migrations.
        """
        applied = set(self.get_applied_migrations(session))
        available = self.get_available_migrations()
        
        return [(v, p) for v, p in available if v not in applied]
    
    def run_migration(self, session: Session, version: int, file_path: Path) -> bool:
        """
        Run a single migration file.
        
        Args:
            session: Database session.
            version: Migration version number.
            file_path: Path to migration SQL file.
        
        Returns:
            True if successful, False otherwise.
        """
        try:
            logger.info(f"Running migration {version}: {file_path.name}")
            
            # Read SQL file
            with open(file_path, 'r', encoding='utf-8') as f:
                sql_content = f.read()
            
            # Execute SQL (split by semicolon for multiple statements)
            # Note: This is a simple approach. For complex migrations, consider using Alembic
            session.execute(text(sql_content))
            session.commit()
            
            logger.info(f"✓ Migration {version} completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"✗ Migration {version} failed: {e}")
            session.rollback()
            raise
    
    def run_migrations(self) -> int:
        """
        Run all pending migrations.
        
        Returns:
            Number of migrations applied.
        """
        session = self.db.get_session()
        count = 0
        
        try:
            pending = self.get_pending_migrations(session)
            
            if not pending:
                logger.info("No pending migrations")
                return 0
            
            logger.info(f"Found {len(pending)} pending migration(s)")
            
            for version, file_path in pending:
                self.run_migration(session, version, file_path)
                count += 1
            
            logger.info(f"✓ Applied {count} migration(s) successfully")
            return count
            
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            raise
        finally:
            session.close()
    
    def validate_schema(self, session: Session) -> bool:
        """
        Validate that all expected tables exist.
        
        Args:
            session: Database session.
        
        Returns:
            True if schema is valid, False otherwise.
        """
        expected_tables = [
            'organizations',
            'suppliers',
            'products_unified',
            'users',
            'audit_logs',
            'schema_migrations'
        ]
        
        try:
            result = session.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """))
            
            existing_tables = {row[0] for row in result}
            missing_tables = set(expected_tables) - existing_tables
            
            if missing_tables:
                logger.error(f"Missing tables: {', '.join(missing_tables)}")
                return False
            
            logger.info("✓ Schema validation passed")
            return True
            
        except Exception as e:
            logger.error(f"Schema validation failed: {e}")
            return False
    
    def get_migration_status(self) -> dict:
        """
        Get current migration status.
        
        Returns:
            Dictionary with migration status information.
        """
        session = self.db.get_session()
        
        try:
            applied = self.get_applied_migrations(session)
            available = self.get_available_migrations()
            pending = self.get_pending_migrations(session)
            
            return {
                'applied_count': len(applied),
                'available_count': len(available),
                'pending_count': len(pending),
                'latest_version': max(applied) if applied else 0,
                'applied_versions': applied,
                'pending_versions': [v for v, _ in pending]
            }
        finally:
            session.close()
