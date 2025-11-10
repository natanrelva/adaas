"""Initialize database with migrations and default data."""

import sys
import logging
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database.connection import DatabaseConnection
from src.database.config import DatabaseConfig
from src.database.migration_runner import MigrationRunner
from src.database.models import Organization, User
from sqlalchemy import text
import hashlib

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_default_organization(db: DatabaseConnection) -> int:
    """
    Create default organization 'Made in Natural'.
    
    Args:
        db: DatabaseConnection instance.
    
    Returns:
        Organization ID.
    """
    session = db.get_session()
    
    try:
        # Check if organization already exists
        result = session.execute(
            text("SELECT id FROM organizations WHERE slug = 'made-in-natural'")
        )
        existing = result.fetchone()
        
        if existing:
            org_id = existing[0]
            logger.info(f"Organization 'Made in Natural' already exists (ID: {org_id})")
            return org_id
        
        # Create new organization
        org = Organization(
            name="Made in Natural",
            slug="made-in-natural",
            plan="free",
            active=True
        )
        
        session.add(org)
        session.commit()
        session.refresh(org)
        
        logger.info(f"✓ Created default organization: {org.name} (ID: {org.id})")
        return org.id
        
    except Exception as e:
        session.rollback()
        logger.error(f"Failed to create default organization: {e}")
        raise
    finally:
        session.close()


def create_admin_user(db: DatabaseConnection, org_id: int):
    """
    Create default admin user.
    
    Args:
        db: DatabaseConnection instance.
        org_id: Organization ID.
    """
    session = db.get_session()
    
    try:
        # Set org context for RLS
        db.set_org_context(session, org_id, user_role='platform_admin')
        
        # Check if admin user already exists
        result = session.execute(
            text("SELECT id FROM users WHERE email = 'admin@addas.com'")
        )
        existing = result.fetchone()
        
        if existing:
            logger.info("Admin user already exists")
            return
        
        # Create admin user with simple hash (in production, use bcrypt)
        password_hash = hashlib.sha256("admin123".encode()).hexdigest()
        
        user = User(
            org_id=org_id,
            email="admin@addas.com",
            password_hash=password_hash,
            role="platform_admin",
            active=True
        )
        
        session.add(user)
        session.commit()
        
        logger.info(f"✓ Created admin user: {user.email}")
        logger.warning("⚠️  Default password is 'admin123' - CHANGE IT IN PRODUCTION!")
        
    except Exception as e:
        session.rollback()
        logger.error(f"Failed to create admin user: {e}")
        raise
    finally:
        session.close()


def main():
    """Initialize database with migrations and default data."""
    print("=" * 60)
    print("DATABASE INITIALIZATION - Add'as Platform")
    print("=" * 60)
    
    try:
        # 1. Load configuration
        logger.info("Loading database configuration...")
        config = DatabaseConfig()
        logger.info(f"Environment: {config.env}")
        logger.info(f"Database: {config.config['database']}")
        
        # 2. Create connection
        logger.info("Connecting to database...")
        db = DatabaseConnection(config)
        
        # 3. Run migrations
        logger.info("\n[1/4] Running database migrations...")
        print("-" * 60)
        runner = MigrationRunner(db)
        count = runner.run_migrations()
        
        if count > 0:
            logger.info(f"✓ Applied {count} migration(s)")
        
        # 4. Validate schema
        logger.info("\n[2/4] Validating database schema...")
        print("-" * 60)
        session = db.get_session()
        is_valid = runner.validate_schema(session)
        session.close()
        
        if not is_valid:
            logger.error("Schema validation failed")
            sys.exit(1)
        
        # 5. Create default organization
        logger.info("\n[3/4] Creating default organization...")
        print("-" * 60)
        org_id = create_default_organization(db)
        
        # 6. Create admin user
        logger.info("\n[4/4] Creating admin user...")
        print("-" * 60)
        create_admin_user(db, org_id)
        
        # 7. Show migration status
        logger.info("\n" + "=" * 60)
        logger.info("MIGRATION STATUS")
        logger.info("=" * 60)
        status = runner.get_migration_status()
        logger.info(f"Applied migrations: {status['applied_count']}")
        logger.info(f"Latest version: {status['latest_version']}")
        logger.info(f"Pending migrations: {status['pending_count']}")
        
        # 8. Success
        print("\n" + "=" * 60)
        print("✅ DATABASE INITIALIZATION COMPLETE")
        print("=" * 60)
        print(f"\nOrganization ID: {org_id}")
        print(f"Admin Email: admin@addas.com")
        print(f"Admin Password: admin123 (CHANGE IN PRODUCTION!)")
        print("\nNext steps:")
        print("  1. Run data migration: python scripts/migrate_json_to_postgres.py")
        print("  2. Start the application")
        print("=" * 60)
        
    except Exception as e:
        logger.error(f"\n❌ INITIALIZATION FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
