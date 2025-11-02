# FastAPI Async Database with SQLAlchemy

Complete guide for integrating async SQLAlchemy with FastAPI for high-performance database operations.

## Overview

This reference covers:
- Async SQLAlchemy setup with PostgreSQL, MySQL, and SQLite
- Database session management
- CRUD operations with async/await
- Relationships and joins
- Database migrations with Alembic
- Connection pooling and optimization

## Why Async Database Operations

Async database operations allow FastAPI to handle multiple requests concurrently without blocking:
- Non-blocking I/O improves throughput
- Better resource utilization
- Handles high concurrency efficiently
- Maintains FastAPI's async benefits end-to-end

## Dependencies

```bash
# Core dependencies
pip install sqlalchemy[asyncio]

# Database drivers (choose one or more)
pip install asyncpg      # PostgreSQL (recommended)
pip install aiomysql     # MySQL
pip install aiosqlite    # SQLite

# Migrations
pip install alembic

# Optional: ORM alternative
pip install sqlmodel
```

## Database Setup

### Configuration

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import AsyncAdaptedQueuePool
from typing import AsyncGenerator

# Database URLs for different databases
# PostgreSQL: "postgresql+asyncpg://user:password@localhost/dbname"
# MySQL: "mysql+aiomysql://user:password@localhost/dbname"
# SQLite: "sqlite+aiosqlite:///./test.db"

DATABASE_URL = "postgresql+asyncpg://user:password@localhost/dbname"

# Create async engine with connection pooling
engine = create_async_engine(
    DATABASE_URL,
    echo=True,  # Set to False in production
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,  # Verify connections before using
    pool_recycle=3600,   # Recycle connections after 1 hour
    poolclass=AsyncAdaptedQueuePool
)

# Create async session factory
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

# Declarative base for models
Base = declarative_base()
```

### Dependency for Database Sessions

```python
from fastapi import Depends
from typing import Annotated

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for getting async database sessions."""
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

# Use in endpoints
DatabaseDep = Annotated[AsyncSession, Depends(get_db)]
```

## Database Models

### Basic Models

```python
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100))
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    items = relationship("Item", back_populates="owner", cascade="all, delete-orphan")

class Item(Base):
    __tablename__ = "items"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), index=True, nullable=False)
    description = Column(Text)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    owner = relationship("User", back_populates="items")
```

### Many-to-Many Relationships

```python
from sqlalchemy import Table

# Association table
user_roles = Table(
    'user_roles',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('role_id', Integer, ForeignKey('roles.id'), primary_key=True)
)

class Role(Base):
    __tablename__ = "roles"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(255))
    
    # Many-to-many relationship
    users = relationship("User", secondary=user_roles, back_populates="roles")

# Update User model
class User(Base):
    # ... existing columns ...
    roles = relationship("Role", secondary=user_roles, back_populates="users")
```

## Database Initialization

```python
from fastapi import FastAPI

app = FastAPI()

async def init_db():
    """Initialize database - create all tables."""
    async with engine.begin() as conn:
        # Drop all tables (use with caution!)
        # await conn.run_sync(Base.metadata.drop_all)
        
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)

@app.on_event("startup")
async def startup_event():
    """Run on application startup."""
    await init_db()

@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown."""
    await engine.dispose()
```

## CRUD Operations

### Create Operations

```python
from sqlalchemy import select, insert
from pydantic import BaseModel

class UserCreate(BaseModel):
    email: str
    username: str
    password: str
    full_name: str | None = None

async def create_user(db: AsyncSession, user_in: UserCreate) -> User:
    """Create a new user."""
    # Method 1: Using ORM
    db_user = User(
        email=user_in.email,
        username=user_in.username,
        hashed_password=get_password_hash(user_in.password),
        full_name=user_in.full_name
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

async def create_user_core(db: AsyncSession, user_in: UserCreate) -> User:
    """Create user using SQLAlchemy Core (faster for bulk operations)."""
    stmt = insert(User).values(
        email=user_in.email,
        username=user_in.username,
        hashed_password=get_password_hash(user_in.password),
        full_name=user_in.full_name
    ).returning(User)
    
    result = await db.execute(stmt)
    await db.commit()
    return result.scalar_one()

# Endpoint
@app.post("/users/", response_model=UserOut)
async def create_user_endpoint(user: UserCreate, db: DatabaseDep):
    return await create_user(db, user)
```

### Read Operations

```python
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import selectinload

async def get_user(db: AsyncSession, user_id: int) -> User | None:
    """Get user by ID."""
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    return result.scalar_one_or_none()

async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    """Get user by email."""
    result = await db.execute(
        select(User).where(User.email == email)
    )
    return result.scalar_one_or_none()

async def get_users(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    is_active: bool | None = None
) -> list[User]:
    """Get users with pagination and filtering."""
    query = select(User)
    
    if is_active is not None:
        query = query.where(User.is_active == is_active)
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

async def get_user_with_items(db: AsyncSession, user_id: int) -> User | None:
    """Get user with related items (eager loading)."""
    result = await db.execute(
        select(User)
        .options(selectinload(User.items))
        .where(User.id == user_id)
    )
    return result.scalar_one_or_none()

# Complex queries
async def search_users(
    db: AsyncSession,
    search: str,
    skip: int = 0,
    limit: int = 100
) -> list[User]:
    """Search users by email or username."""
    query = select(User).where(
        or_(
            User.email.ilike(f"%{search}%"),
            User.username.ilike(f"%{search}%")
        )
    ).offset(skip).limit(limit)
    
    result = await db.execute(query)
    return result.scalars().all()

# Endpoints
@app.get("/users/{user_id}", response_model=UserOut)
async def read_user(user_id: int, db: DatabaseDep):
    user = await get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.get("/users/", response_model=list[UserOut])
async def list_users(
    db: DatabaseDep,
    skip: int = 0,
    limit: int = 100,
    is_active: bool | None = None
):
    return await get_users(db, skip, limit, is_active)
```

### Update Operations

```python
from sqlalchemy import update

class UserUpdate(BaseModel):
    email: str | None = None
    full_name: str | None = None
    is_active: bool | None = None

async def update_user(
    db: AsyncSession,
    user_id: int,
    user_update: UserUpdate
) -> User | None:
    """Update user."""
    # Method 1: Fetch, modify, commit
    user = await get_user(db, user_id)
    if not user:
        return None
    
    update_data = user_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)
    
    user.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(user)
    return user

async def update_user_core(
    db: AsyncSession,
    user_id: int,
    user_update: UserUpdate
) -> User | None:
    """Update user using SQLAlchemy Core."""
    update_data = user_update.dict(exclude_unset=True)
    update_data['updated_at'] = datetime.utcnow()
    
    stmt = (
        update(User)
        .where(User.id == user_id)
        .values(**update_data)
        .returning(User)
    )
    
    result = await db.execute(stmt)
    await db.commit()
    return result.scalar_one_or_none()

# Endpoint
@app.patch("/users/{user_id}", response_model=UserOut)
async def update_user_endpoint(
    user_id: int,
    user: UserUpdate,
    db: DatabaseDep
):
    updated_user = await update_user(db, user_id, user)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    return updated_user
```

### Delete Operations

```python
from sqlalchemy import delete

async def delete_user(db: AsyncSession, user_id: int) -> bool:
    """Delete user."""
    result = await db.execute(
        delete(User).where(User.id == user_id)
    )
    await db.commit()
    return result.rowcount > 0

# Endpoint
@app.delete("/users/{user_id}", status_code=204)
async def delete_user_endpoint(user_id: int, db: DatabaseDep):
    deleted = await delete_user(db, user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="User not found")
    return None
```

## Advanced Queries

### Aggregations and Grouping

```python
from sqlalchemy import func, desc

async def get_user_item_counts(db: AsyncSession) -> list[dict]:
    """Get users with their item counts."""
    result = await db.execute(
        select(
            User.username,
            func.count(Item.id).label('item_count')
        )
        .outerjoin(Item)
        .group_by(User.id, User.username)
        .order_by(desc('item_count'))
    )
    return [{"username": row[0], "item_count": row[1]} for row in result.all()]
```

### Joins

```python
async def get_items_with_owners(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100
) -> list[Item]:
    """Get items with owner information."""
    result = await db.execute(
        select(Item)
        .join(User)
        .options(selectinload(Item.owner))
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()
```

### Transactions

```python
async def transfer_items(
    db: AsyncSession,
    from_user_id: int,
    to_user_id: int,
    item_ids: list[int]
) -> None:
    """Transfer items between users (atomic operation)."""
    try:
        # Verify users exist
        from_user = await get_user(db, from_user_id)
        to_user = await get_user(db, to_user_id)
        
        if not from_user or not to_user:
            raise ValueError("User not found")
        
        # Update items
        await db.execute(
            update(Item)
            .where(
                and_(
                    Item.id.in_(item_ids),
                    Item.owner_id == from_user_id
                )
            )
            .values(owner_id=to_user_id)
        )
        
        await db.commit()
    except Exception:
        await db.rollback()
        raise
```

## Database Migrations with Alembic

### Setup

```bash
# Initialize Alembic
alembic init -t async alembic

# Edit alembic.ini - set database URL
# sqlalchemy.url = postgresql+asyncpg://user:pass@localhost/dbname
```

### Configuration

```python
# alembic/env.py
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context

# Import your models
from app.models import Base
target_metadata = Base.metadata

# Get URL from your config
from app.config import settings
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

async def run_async_migrations():
    """Run migrations in 'online' mode."""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()

def do_run_migrations(connection: Connection):
    context.configure(
        connection=connection,
        target_metadata=target_metadata
    )

    with context.begin_transaction():
        context.run_migrations()
```

### Creating and Running Migrations

```bash
# Create migration
alembic revision --autogenerate -m "Add users table"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1

# Show current revision
alembic current

# Show migration history
alembic history
```

## Performance Optimization

### Connection Pooling

```python
# Optimized engine configuration
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_size=20,              # Number of connections to maintain
    max_overflow=10,           # Additional connections when pool is full
    pool_pre_ping=True,        # Test connections before use
    pool_recycle=3600,         # Recycle connections after 1 hour
    pool_timeout=30,           # Wait up to 30 seconds for connection
    connect_args={
        "server_settings": {
            "application_name": "fastapi_app",
            "jit": "on"
        }
    }
)
```

### Bulk Operations

```python
async def create_users_bulk(db: AsyncSession, users: list[UserCreate]) -> list[User]:
    """Create multiple users efficiently."""
    db_users = [
        User(
            email=user.email,
            username=user.username,
            hashed_password=get_password_hash(user.password)
        )
        for user in users
    ]
    
    db.add_all(db_users)
    await db.commit()
    
    # Refresh all objects
    for user in db_users:
        await db.refresh(user)
    
    return db_users
```

### Lazy vs Eager Loading

```python
# Lazy loading (N+1 problem)
users = await get_users(db)
for user in users:
    # This triggers a new query for each user!
    print(user.items)

# Eager loading (efficient)
from sqlalchemy.orm import selectinload

result = await db.execute(
    select(User).options(selectinload(User.items))
)
users = result.scalars().all()
for user in users:
    # No additional queries!
    print(user.items)
```

## Testing

```python
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

@pytest_asyncio.fixture
async def test_db():
    """Create test database."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session
    
    await engine.dispose()

@pytest.mark.asyncio
async def test_create_user(test_db):
    """Test user creation."""
    user_in = UserCreate(
        email="test@example.com",
        username="testuser",
        password="password123"
    )
    
    user = await create_user(test_db, user_in)
    
    assert user.email == "test@example.com"
    assert user.username == "testuser"
    assert user.id is not None
```

## Common Patterns

### Repository Pattern

```python
from abc import ABC, abstractmethod

class BaseRepository(ABC):
    def __init__(self, db: AsyncSession):
        self.db = db
    
    @abstractmethod
    async def get(self, id: int):
        pass
    
    @abstractmethod
    async def list(self, skip: int = 0, limit: int = 100):
        pass
    
    @abstractmethod
    async def create(self, data):
        pass
    
    @abstractmethod
    async def update(self, id: int, data):
        pass
    
    @abstractmethod
    async def delete(self, id: int):
        pass

class UserRepository(BaseRepository):
    async def get(self, user_id: int) -> User | None:
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def list(self, skip: int = 0, limit: int = 100) -> list[User]:
        result = await self.db.execute(
            select(User).offset(skip).limit(limit)
        )
        return result.scalars().all()
    
    # Implement other methods...

# Usage
@app.get("/users/{user_id}")
async def get_user(user_id: int, db: DatabaseDep):
    repo = UserRepository(db)
    user = await repo.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
```

This reference provides comprehensive patterns for async database operations with FastAPI and SQLAlchemy. Always use connection pooling, eager loading for relationships, and proper transaction management for production applications.
