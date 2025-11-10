"""SQLAlchemy models for Add'as Platform - Multi-tenant schema."""

from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, Date, Float, Numeric,
    ForeignKey, Index, Enum as SQLEnum, JSON, Text
)
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func
import enum

Base = declarative_base()


# Enums
class PlanType(str, enum.Enum):
    """Subscription plan types."""
    FREE = "free"
    BASIC = "basic"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class UserRole(str, enum.Enum):
    """User roles in the system."""
    ADMIN = "admin"
    SUPPLIER = "supplier"
    RETAILER = "retailer"
    VIEWER = "viewer"
    PLATFORM_ADMIN = "platform_admin"


class DataType(str, enum.Enum):
    """Supplier data source types."""
    HTML = "html"
    XML = "xml"
    CSV = "csv"
    JSON = "json"
    API = "api"
    GOOGLE_SHEETS = "google_sheets"


class UnitType(str, enum.Enum):
    """Product unit types."""
    KG = "kg"
    G = "g"
    L = "l"
    ML = "ml"
    UN = "un"


# Models
class Organization(Base):
    """Organization (tenant) model."""
    __tablename__ = "organizations"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    plan = Column(SQLEnum(PlanType), default=PlanType.FREE, nullable=False)
    active = Column(Boolean, default=True, nullable=False)
    
    # Metadata
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    suppliers = relationship("Supplier", back_populates="organization", cascade="all, delete-orphan")
    products = relationship("Product", back_populates="organization", cascade="all, delete-orphan")
    users = relationship("User", back_populates="organization", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="organization", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Organization(id={self.id}, name='{self.name}', plan='{self.plan.value}')>"


class Supplier(Base):
    """Supplier model with multi-tenant support."""
    __tablename__ = "suppliers"
    __table_args__ = (
        Index('idx_suppliers_org_id', 'org_id'),
        Index('idx_suppliers_org_supplier', 'org_id', 'supplier_id', unique=True),
    )
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    org_id = Column(Integer, ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False)
    
    # Supplier identification
    supplier_id = Column(String(50), nullable=False)  # gramore, elmar, rmoura, etc
    name = Column(String(255), nullable=False)
    
    # Data source configuration
    data_type = Column(SQLEnum(DataType), nullable=False)
    url = Column(String(500))
    
    # Consent and compliance
    consent_obtained = Column(Boolean, default=False, nullable=False)
    consent_date = Column(Date)
    
    # Extraction configuration (JSON)
    extraction_config = Column(JSON)
    
    # Status
    active = Column(Boolean, default=True, nullable=False)
    
    # Metadata
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at = Column(DateTime, nullable=True)  # Soft delete
    
    # Relationships
    organization = relationship("Organization", back_populates="suppliers")
    products = relationship("Product", back_populates="supplier", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Supplier(id={self.id}, supplier_id='{self.supplier_id}', name='{self.name}')>"


class Product(Base):
    """Unified product model with multi-tenant support."""
    __tablename__ = "products_unified"
    __table_args__ = (
        Index('idx_products_org_id_name', 'org_id', 'name'),
        Index('idx_products_org_id_category', 'org_id', 'category'),
        Index('idx_products_org_id_supplier', 'org_id', 'supplier_id'),
        Index('idx_products_org_id_active', 'org_id', 'deleted_at'),
    )
    
    # Primary key (hash-based ID from original system)
    id = Column(String(16), primary_key=True)
    
    # Multi-tenant
    org_id = Column(Integer, ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False)
    supplier_id = Column(Integer, ForeignKey('suppliers.id', ondelete='CASCADE'), nullable=False)
    
    # Product identification
    supplier_product_id = Column(String(100))  # Original ID from supplier
    
    # Product details
    name = Column(String(500), nullable=False)
    brand = Column(String(255))
    category = Column(String(100))
    
    # Measurements
    weight = Column(Float)
    unit = Column(SQLEnum(UnitType))
    
    # Pricing (stored as Numeric for precision)
    price_base = Column(Numeric(10, 2))
    price_margin = Column(Numeric(5, 2))  # Percentage
    price_shipping = Column(Numeric(10, 2))
    price_final = Column(Numeric(10, 2))
    
    # Stock
    stock_available = Column(Boolean, default=True, nullable=False)
    stock_quantity = Column(Integer)
    
    # Metadata (JSON for flexibility)
    # Contains: extraction_date, source_url, hash, etc
    metadata = Column(JSON)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at = Column(DateTime, nullable=True)  # Soft delete
    
    # Relationships
    organization = relationship("Organization", back_populates="products")
    supplier = relationship("Supplier", back_populates="products")
    
    def __repr__(self) -> str:
        return f"<Product(id='{self.id}', name='{self.name}', supplier_id={self.supplier_id})>"
    
    @property
    def is_active(self) -> bool:
        """Check if product is active (not soft-deleted)."""
        return self.deleted_at is None


class User(Base):
    """User model with multi-tenant support."""
    __tablename__ = "users"
    __table_args__ = (
        Index('idx_users_org_id', 'org_id'),
        Index('idx_users_email', 'email', unique=True),
    )
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    org_id = Column(Integer, ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False)
    
    # Authentication
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    
    # Authorization
    role = Column(SQLEnum(UserRole), default=UserRole.VIEWER, nullable=False)
    
    # Status
    active = Column(Boolean, default=True, nullable=False)
    
    # Metadata
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at = Column(DateTime, nullable=True)  # Soft delete
    
    # Relationships
    organization = relationship("Organization", back_populates="users")
    audit_logs = relationship("AuditLog", back_populates="user")
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, email='{self.email}', role='{self.role.value}')>"
    
    @property
    def is_active(self) -> bool:
        """Check if user is active (not soft-deleted)."""
        return self.active and self.deleted_at is None


class AuditLog(Base):
    """Audit log model for compliance and traceability."""
    __tablename__ = "audit_logs"
    __table_args__ = (
        Index('idx_audit_logs_org_id', 'org_id'),
        Index('idx_audit_logs_timestamp', 'timestamp'),
        Index('idx_audit_logs_entity', 'entity_type', 'entity_id'),
    )
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    org_id = Column(Integer, ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False)
    
    # Timestamp
    timestamp = Column(DateTime, default=func.now(), nullable=False, index=True)
    
    # Operation details
    operation = Column(String(50))  # extraction, transformation, validation, etc
    entity_type = Column(String(50))  # product, supplier, user, etc
    entity_id = Column(String(100))
    
    # User who performed the operation (optional for system operations)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    
    # Data integrity
    data_hash = Column(String(64))  # SHA-256 hash
    
    # Status
    status = Column(String(20))  # success, error, warning
    
    # Additional metadata (JSON for flexibility)
    metadata = Column(JSON)
    
    # Relationships
    organization = relationship("Organization", back_populates="audit_logs")
    user = relationship("User", back_populates="audit_logs")
    
    def __repr__(self) -> str:
        return (
            f"<AuditLog(id={self.id}, operation='{self.operation}', "
            f"entity='{self.entity_type}:{self.entity_id}', status='{self.status}')>"
        )


class SchemaMigration(Base):
    """Schema migration tracking."""
    __tablename__ = "schema_migrations"
    
    version = Column(Integer, primary_key=True)
    description = Column(Text)
    applied_at = Column(DateTime, default=func.now(), nullable=False)
    
    def __repr__(self) -> str:
        return f"<SchemaMigration(version={self.version}, description='{self.description}')>"
