"""Database connection management with pooling and RLS context."""

from sqlalchemy import create_engine, text, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from typing import Optional, Dict, Any
from contextlib import contextmanager
import logging

from src.database.config import DatabaseConfig

logger = logging.getLogger(__name__)


class DatabaseConnection:
    """Manages PostgreSQL connection pool and organization context for RLS."""
    
    def __init__(self, config: Optional[DatabaseConfig] = None):
        """
        Initialize database connection with pooling.
        
        Args:
            config: DatabaseConfig instance. If None, creates default config.
        """
        self.config = config or DatabaseConfig()
        self.engine = self._create_engine()
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )
        
        logger.info(f"Database connection initialized: {self.config}")
    
    def _create_engine(self):
        """Create SQLAlchemy engine with connection pooling."""
        engine = create_engine(
            self.config.connection_string,
            poolclass=QueuePool,
            pool_size=self.config.pool_size,
            max_overflow=self.config.max_overflow,
            pool_timeout=self.config.pool_timeout,
            pool_recycle=self.config.pool_recycle,
            pool_pre_ping=self.config.pool_pre_ping,
            echo=self.config.echo,
            connect_args=self.config.connect_args
        )
        
        # Log pool statistics
        @event.listens_for(engine, "connect")
        def receive_connect(dbapi_conn, connection_record):
            logger.debug("Database connection established")
        
        @event.listens_for(engine, "checkout")
        def receive_checkout(dbapi_conn, connection_record, connection_proxy):
            logger.debug("Connection checked out from pool")
        
        return engine
    
    def get_session(self) -> Session:
        """
        Get a new database session.
        
        Returns:
            SQLAlchemy Session instance.
        """
        return self.SessionLocal()
    
    def set_org_context(self, session: Session, org_id: int, user_role: Optional[str] = None):
        """
        Set organization context for Row-Level Security.
        
        This sets PostgreSQL session variables that RLS policies use to filter data.
        
        Args:
            session: SQLAlchemy session.
            org_id: Organization ID to set as context.
            user_role: Optional user role (e.g., 'platform_admin' for bypass).
        """
        try:
            session.execute(text(f"SET app.current_org_id = {org_id}"))
            
            if user_role:
                session.execute(text(f"SET app.user_role = '{user_role}'"))
            
            logger.debug(f"Organization context set: org_id={org_id}, role={user_role}")
        except Exception as e:
            logger.error(f"Failed to set organization context: {e}")
            raise
    
    @contextmanager
    def with_org_context(self, org_id: int, user_role: Optional[str] = None):
        """
        Context manager for automatic organization context management.
        
        Usage:
            with db.with_org_context(org_id=1):
                products = session.query(Product).all()  # Filtered by org_id=1
        
        Args:
            org_id: Organization ID.
            user_role: Optional user role.
        
        Yields:
            SQLAlchemy Session with org context set.
        """
        session = self.get_session()
        try:
            self.set_org_context(session, org_id, user_role)
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Error in org context: {e}")
            raise
        finally:
            session.close()
    
    def get_pool_status(self) -> Dict[str, Any]:
        """
        Get current connection pool statistics.
        
        Returns:
            Dictionary with pool metrics:
            - size: Current pool size
            - checked_in: Connections in pool
            - checked_out: Connections in use
            - overflow: Overflow connections
            - total: Total connections
        """
        pool = self.engine.pool
        
        return {
            "size": pool.size(),
            "checked_in": pool.checkedin(),
            "checked_out": pool.checkedout(),
            "overflow": pool.overflow(),
            "total": pool.size() + pool.overflow()
        }
    
    def close(self):
        """Close all connections and dispose of the engine."""
        logger.info("Closing database connections")
        self.engine.dispose()
    
    def __repr__(self) -> str:
        """String representation."""
        return f"DatabaseConnection(config={self.config})"


# Global database connection instance
_db_connection: Optional[DatabaseConnection] = None


def get_db() -> DatabaseConnection:
    """
    Get global database connection instance (singleton pattern).
    
    Returns:
        DatabaseConnection instance.
    """
    global _db_connection
    
    if _db_connection is None:
        _db_connection = DatabaseConnection()
    
    return _db_connection


def init_db(config: Optional[DatabaseConfig] = None):
    """
    Initialize global database connection.
    
    Args:
        config: Optional DatabaseConfig. If None, uses default.
    """
    global _db_connection
    _db_connection = DatabaseConnection(config)
    logger.info("Global database connection initialized")


def close_db():
    """Close global database connection."""
    global _db_connection
    
    if _db_connection:
        _db_connection.close()
        _db_connection = None
