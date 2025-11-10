# Design Document - Database Multi-Tenant

## Overview

Este documento descreve o design da camada de persistência multi-tenant usando PostgreSQL com Row-Level Security (RLS). A solução migra o sistema atual baseado em JSON para um banco relacional escalável, mantendo isolamento completo entre organizações.

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Application Layer                     │
│  (FastAPI / Scripts / Background Jobs)                  │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              Database Connection Layer                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │ Connection   │  │  SQLAlchemy  │  │   Context    │ │
│  │    Pool      │  │    Models    │  │   Manager    │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                  PostgreSQL 15+                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Row-Level Security (RLS) Policies               │  │
│  │  - Filter by org_id automatically                │  │
│  │  - Inject org_id on INSERT                       │  │
│  └──────────────────────────────────────────────────┘  │
│                                                          │
│  Tables: organizations, suppliers, products_unified,    │
│          users, audit_logs, schema_migrations           │
└─────────────────────────────────────────────────────────┘
```

## Components and Interfaces

### 1. Database Connection Manager

**File:** `src/database/connection.py`

```python
class DatabaseConnection:
    """Manages PostgreSQL connection pool and context."""
    
    def __init__(self, config: DatabaseConfig):
        self.engine = create_engine(
            config.connection_string,
            pool_size=5,
            max_overflow=15,
            pool_timeout=30,
            pool_recycle=300
        )
        self.SessionLocal = sessionmaker(bind=self.engine)
    
    def get_session(self) -> Session:
        """Returns a new database session."""
        
    def set_org_context(self, session: Session, org_id: int):
        """Sets current organization context for RLS."""
        session.execute(f"SET app.current_org_id = {org_id}")
    
    def health_check(self) -> HealthStatus:
        """Checks database connectivity and metrics."""
```

**Interface:**
- `get_session()` → Session object
- `set_org_context(session, org_id)` → void
- `health_check()` → HealthStatus dict

---

### 2. SQLAlchemy Models

**File:** `src/database/models.py`

```python
class Organization(Base):
    __tablename__ = "organizations"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    slug = Column(String(100), unique=True, nullable=False)
    plan = Column(Enum('free', 'basic', 'pro', 'enterprise'))
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    
    # Relationships
    suppliers = relationship("Supplier", back_populates="organization")
    products = relationship("Product", back_populates="organization")
    users = relationship("User", back_populates="organization")

class Supplier(Base):
    __tablename__ = "suppliers"
    __table_args__ = (
        Index('idx_suppliers_org_id', 'org_id'),
    )
    
    id = Column(Integer, primary_key=True)
    org_id = Column(Integer, ForeignKey('organizations.id'), nullable=False)
    supplier_id = Column(String(50), nullable=False)  # gramore, elmar, etc
    name = Column(String(255), nullable=False)
    data_type = Column(Enum('html', 'xml', 'csv', 'api'))
    url = Column(String(500))
    consent_obtained = Column(Boolean, default=False)
    consent_date = Column(Date)
    extraction_config = Column(JSON)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)
    
    # Relationships
    organization = relationship("Organization", back_populates="suppliers")
    products = relationship("Product", back_populates="supplier")

class Product(Base):
    __tablename__ = "products_unified"
    __table_args__ = (
        Index('idx_products_org_id_name', 'org_id', 'name'),
        Index('idx_products_org_id_category', 'org_id', 'category'),
        Index('idx_products_org_id_supplier', 'org_id', 'supplier_id'),
    )
    
    id = Column(String(16), primary_key=True)  # Hash-based ID
    org_id = Column(Integer, ForeignKey('organizations.id'), nullable=False)
    supplier_id = Column(Integer, ForeignKey('suppliers.id'), nullable=False)
    supplier_product_id = Column(String(100))
    name = Column(String(500), nullable=False)
    brand = Column(String(255))
    category = Column(String(100))
    weight = Column(Float)
    unit = Column(Enum('kg', 'g', 'l', 'ml', 'un'))
    price_base = Column(Numeric(10, 2))
    price_margin = Column(Numeric(5, 2))
    price_shipping = Column(Numeric(10, 2))
    price_final = Column(Numeric(10, 2))
    stock_available = Column(Boolean, default=True)
    stock_quantity = Column(Integer)
    metadata = Column(JSON)  # extraction_date, source_url, hash
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)
    
    # Relationships
    organization = relationship("Organization", back_populates="products")
    supplier = relationship("Supplier", back_populates="products")

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    org_id = Column(Integer, ForeignKey('organizations.id'), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum('admin', 'supplier', 'retailer', 'viewer'))
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    
    organization = relationship("Organization", back_populates="users")

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True)
    org_id = Column(Integer, ForeignKey('organizations.id'), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    operation = Column(String(50))  # extraction, transformation, etc
    entity_type = Column(String(50))  # product, supplier, etc
    entity_id = Column(String(100))
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    data_hash = Column(String(64))
    status = Column(String(20))
    metadata = Column(JSON)
```

---

### 3. Migration System

**File:** `src/database/migrations/001_initial_schema.sql`

```sql
-- Create organizations table
CREATE TABLE organizations (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    plan VARCHAR(20) DEFAULT 'free',
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create suppliers table
CREATE TABLE suppliers (
    id SERIAL PRIMARY KEY,
    org_id INTEGER NOT NULL REFERENCES organizations(id),
    supplier_id VARCHAR(50) NOT NULL,
    name VARCHAR(255) NOT NULL,
    data_type VARCHAR(20),
    url VARCHAR(500),
    consent_obtained BOOLEAN DEFAULT false,
    consent_date DATE,
    extraction_config JSONB,
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP,
    UNIQUE(org_id, supplier_id)
);

-- Create products_unified table
CREATE TABLE products_unified (
    id VARCHAR(16) PRIMARY KEY,
    org_id INTEGER NOT NULL REFERENCES organizations(id),
    supplier_id INTEGER NOT NULL REFERENCES suppliers(id),
    supplier_product_id VARCHAR(100),
    name VARCHAR(500) NOT NULL,
    brand VARCHAR(255),
    category VARCHAR(100),
    weight NUMERIC(10, 2),
    unit VARCHAR(10),
    price_base NUMERIC(10, 2),
    price_margin NUMERIC(5, 2),
    price_shipping NUMERIC(10, 2),
    price_final NUMERIC(10, 2),
    stock_available BOOLEAN DEFAULT true,
    stock_quantity INTEGER,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP
);

-- Create indexes
CREATE INDEX idx_suppliers_org_id ON suppliers(org_id);
CREATE INDEX idx_products_org_id_name ON products_unified(org_id, name);
CREATE INDEX idx_products_org_id_category ON products_unified(org_id, category);
CREATE INDEX idx_products_org_id_supplier ON products_unified(org_id, supplier_id);

-- Create users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    org_id INTEGER NOT NULL REFERENCES organizations(id),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'viewer',
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create audit_logs table
CREATE TABLE audit_logs (
    id SERIAL PRIMARY KEY,
    org_id INTEGER NOT NULL REFERENCES organizations(id),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    operation VARCHAR(50),
    entity_type VARCHAR(50),
    entity_id VARCHAR(100),
    user_id INTEGER REFERENCES users(id),
    data_hash VARCHAR(64),
    status VARCHAR(20),
    metadata JSONB
);

-- Create schema_migrations table
CREATE TABLE schema_migrations (
    version INTEGER PRIMARY KEY,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    description TEXT
);

INSERT INTO schema_migrations (version, description) 
VALUES (1, 'Initial schema with multi-tenant tables');
```

**File:** `src/database/migrations/002_rls_policies.sql`

```sql
-- Enable RLS on multi-tenant tables
ALTER TABLE suppliers ENABLE ROW LEVEL SECURITY;
ALTER TABLE products_unified ENABLE ROW LEVEL SECURITY;
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;

-- Create RLS policies for suppliers
CREATE POLICY suppliers_isolation_policy ON suppliers
    USING (org_id = current_setting('app.current_org_id')::int);

CREATE POLICY suppliers_insert_policy ON suppliers
    FOR INSERT
    WITH CHECK (org_id = current_setting('app.current_org_id')::int);

-- Create RLS policies for products
CREATE POLICY products_isolation_policy ON products_unified
    USING (org_id = current_setting('app.current_org_id')::int);

CREATE POLICY products_insert_policy ON products_unified
    FOR INSERT
    WITH CHECK (org_id = current_setting('app.current_org_id')::int);

-- Create RLS policies for users
CREATE POLICY users_isolation_policy ON users
    USING (org_id = current_setting('app.current_org_id')::int);

-- Create RLS policies for audit_logs
CREATE POLICY audit_logs_isolation_policy ON audit_logs
    USING (org_id = current_setting('app.current_org_id')::int);

-- Admin bypass policy (for platform admins)
CREATE POLICY admin_bypass_policy ON suppliers
    USING (current_setting('app.user_role', true) = 'platform_admin');

CREATE POLICY admin_bypass_policy ON products_unified
    USING (current_setting('app.user_role', true) = 'platform_admin');

INSERT INTO schema_migrations (version, description) 
VALUES (2, 'Row-Level Security policies for multi-tenancy');
```

---

### 4. Data Migration Script

**File:** `scripts/migrate_json_to_postgres.py`

```python
def migrate_suppliers(session: Session, org_id: int):
    """Migrates suppliers from JSON to PostgreSQL."""
    with open('data/suppliers.json') as f:
        suppliers_data = json.load(f)
    
    for supplier_data in suppliers_data:
        supplier = Supplier(
            org_id=org_id,
            supplier_id=supplier_data['id'],
            name=supplier_data['name'],
            data_type=supplier_data['data_type'],
            url=supplier_data['url'],
            consent_obtained=supplier_data['consent_obtained'],
            consent_date=supplier_data.get('consent_date'),
            extraction_config=supplier_data.get('extraction_config'),
            active=supplier_data.get('active', True)
        )
        session.add(supplier)
    
    session.commit()

def migrate_products(session: Session, org_id: int):
    """Migrates products from JSON to PostgreSQL."""
    with open('data/catalog/catalog_repository.json') as f:
        catalog_data = json.load(f)
    
    products_data = catalog_data.get('products', [])
    
    for product_data in products_data:
        # Get supplier_id from database
        supplier = session.query(Supplier).filter_by(
            org_id=org_id,
            supplier_id=product_data['supplier']
        ).first()
        
        product = Product(
            id=product_data['id'],
            org_id=org_id,
            supplier_id=supplier.id,
            supplier_product_id=product_data['supplier_product_id'],
            name=product_data['name'],
            brand=product_data.get('brand'),
            category=product_data.get('category'),
            weight=product_data.get('weight'),
            unit=product_data.get('unit'),
            price_base=product_data['price']['base'],
            price_margin=product_data['price']['margin'],
            price_shipping=product_data['price']['shipping'],
            price_final=product_data['price']['final'],
            stock_available=product_data['stock']['available'],
            stock_quantity=product_data['stock'].get('quantity'),
            metadata=product_data.get('metadata')
        )
        session.add(product)
    
    session.commit()
```

---

### 5. Configuration Management

**File:** `config/database.yml`

```yaml
development:
  host: localhost
  port: 5432
  database: addas_dev
  user: addas_user
  password: ${DB_PASSWORD}
  pool_size: 5
  max_overflow: 15
  pool_timeout: 30
  pool_recycle: 300

test:
  host: localhost
  port: 5432
  database: addas_test
  user: addas_test_user
  password: ${DB_PASSWORD}
  pool_size: 2
  max_overflow: 5

production:
  host: ${DB_HOST}
  port: ${DB_PORT}
  database: ${DB_NAME}
  user: ${DB_USER}
  password: ${DB_PASSWORD}
  pool_size: 10
  max_overflow: 20
  pool_timeout: 30
  pool_recycle: 300
  ssl_mode: require
```

**File:** `src/database/config.py`

```python
class DatabaseConfig:
    def __init__(self, env: str = 'development'):
        self.env = env
        self.config = self._load_config()
        self._validate()
    
    def _load_config(self) -> dict:
        """Loads config from YAML and env vars."""
        with open('config/database.yml') as f:
            all_configs = yaml.safe_load(f)
        
        config = all_configs[self.env]
        
        # Override with env vars
        config['host'] = os.getenv('DB_HOST', config['host'])
        config['port'] = int(os.getenv('DB_PORT', config['port']))
        config['database'] = os.getenv('DB_NAME', config['database'])
        config['user'] = os.getenv('DB_USER', config['user'])
        config['password'] = os.getenv('DB_PASSWORD', config['password'])
        
        return config
    
    @property
    def connection_string(self) -> str:
        """Returns SQLAlchemy connection string."""
        return (
            f"postgresql://{self.config['user']}:{self.config['password']}"
            f"@{self.config['host']}:{self.config['port']}/{self.config['database']}"
        )
```

## Data Models

### Entity-Relationship Diagram

```
┌─────────────────┐
│  organizations  │
│  - id (PK)      │
│  - name         │
│  - slug         │
│  - plan         │
└────────┬────────┘
         │ 1
         │
         │ N
    ┌────┴────┐
    │         │
    ▼         ▼
┌─────────┐ ┌──────────────┐
│ users   │ │  suppliers   │
│ - id    │ │  - id (PK)   │
│ - email │ │  - org_id    │
│ - role  │ │  - name      │
└─────────┘ └──────┬───────┘
                   │ 1
                   │
                   │ N
            ┌──────▼──────────┐
            │ products_unified│
            │ - id (PK)       │
            │ - org_id        │
            │ - supplier_id   │
            │ - name          │
            │ - price_*       │
            └─────────────────┘
```

## Error Handling

### Connection Errors
- **Timeout:** Retry 3x com backoff exponencial
- **Connection refused:** Log erro e retornar 503
- **Pool exhausted:** Aguardar até timeout ou retornar erro

### RLS Violations
- **Missing org_id:** Retornar 403 Forbidden
- **Invalid org_id:** Retornar 404 Not Found
- **Cross-tenant access:** Log security event e retornar 403

### Migration Errors
- **Duplicate data:** Skip com warning
- **Invalid foreign key:** Log erro e continuar
- **Transaction failure:** Rollback completo

## Testing Strategy

### Unit Tests
- Connection pool behavior
- Model validations
- RLS policy enforcement
- Configuration loading

### Integration Tests
- Full migration JSON → PostgreSQL
- Multi-tenant data isolation
- Query performance with indexes
- Backup and restore

### Performance Tests
- 10k products: queries < 100ms
- 100 concurrent connections
- Connection pool under load

## Security Considerations

1. **RLS Enforcement:** Todas as queries filtradas automaticamente
2. **SQL Injection:** Uso de parameterized queries via SQLAlchemy
3. **Password Storage:** Nunca em plaintext, sempre hashed
4. **Connection String:** Nunca em código, sempre em env vars
5. **Audit Trail:** Todas as operações logadas em audit_logs
