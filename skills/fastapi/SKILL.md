---
name: fastapi
description: Comprehensive guide for building production-ready REST APIs with FastAPI. Use when creating web APIs, implementing microservices, building backend services with Python type hints, working with async operations, requiring automatic API documentation, handling authentication/authorization (OAuth2, JWT), integrating databases (SQLAlchemy, async), implementing WebSockets, adding middleware, managing CORS, validating request/response data with Pydantic, or migrating from Flask/Django to FastAPI.
---

# FastAPI Implementation Guide

This skill provides comprehensive guidance for building robust, production-ready APIs with FastAPI, covering everything from basic setup to advanced patterns including async operations, security, database integration, and deployment.

## Core Concepts

### Why FastAPI

FastAPI is a modern, high-performance web framework for building APIs with Python 3.7+ based on standard Python type hints. Key advantages:

- **Performance**: One of the fastest Python frameworks (on par with NodeJS and Go)
- **Automatic documentation**: OpenAPI (Swagger) and ReDoc documentation generated automatically
- **Type safety**: Built on Pydantic for automatic data validation and serialization
- **Async support**: Native async/await support for concurrent operations
- **Developer experience**: Editor support with autocompletion and type checking reduces bugs by ~40%

## Quick Start

### Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install FastAPI with all standard dependencies
pip install "fastapi[standard]"

# Or minimal installation
pip install fastapi uvicorn
```

### Basic Application Structure

```python
from fastapi import FastAPI

app = FastAPI(
    title="My API",
    description="API description",
    version="1.0.0"
)

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/items/{item_id}")
async def read_item(item_id: int, q: str | None = None):
    return {"item_id": item_id, "q": q}
```

### Running the Application

```bash
# Development mode (auto-reload enabled)
fastapi dev main.py

# Production mode
fastapi run main.py

# Or with uvicorn directly
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Access documentation at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Request Handling

### Path Parameters

Path parameters capture dynamic values from the URL path:

```python
from fastapi import FastAPI, Path
from typing import Annotated

app = FastAPI()

# Basic path parameter
@app.get("/items/{item_id}")
async def read_item(item_id: int):
    return {"item_id": item_id}

# With validation
@app.get("/items/{item_id}")
async def read_item(
    item_id: Annotated[int, Path(title="Item ID", ge=1, le=1000)]
):
    return {"item_id": item_id}

# Multiple path parameters
@app.get("/users/{user_id}/items/{item_id}")
async def read_user_item(user_id: int, item_id: str):
    return {"user_id": user_id, "item_id": item_id}
```

### Query Parameters

Query parameters are optional URL parameters after `?`:

```python
from fastapi import Query

# Basic query parameters
@app.get("/items/")
async def read_items(skip: int = 0, limit: int = 10):
    return {"skip": skip, "limit": limit}

# With validation
@app.get("/items/")
async def read_items(
    q: Annotated[str | None, Query(
        min_length=3,
        max_length=50,
        pattern="^[a-zA-Z0-9]+$"
    )] = None
):
    return {"q": q}

# Multiple values for same parameter
@app.get("/items/")
async def read_items(tags: list[str] = Query(default=[])):
    return {"tags": tags}
```

### Request Body with Pydantic

Use Pydantic models for request body validation:

```python
from pydantic import BaseModel, Field, EmailStr
from datetime import datetime

class User(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: str | None = None
    age: int = Field(..., ge=0, le=150)
    created_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_schema_extra = {
            "example": {
                "username": "johndoe",
                "email": "john@example.com",
                "full_name": "John Doe",
                "age": 30
            }
        }

@app.post("/users/", response_model=User)
async def create_user(user: User):
    # FastAPI automatically validates and parses the JSON body
    return user

# Nested models
class Address(BaseModel):
    street: str
    city: str
    country: str

class UserWithAddress(BaseModel):
    username: str
    email: EmailStr
    address: Address

@app.post("/users-with-address/")
async def create_user_with_address(user: UserWithAddress):
    return user
```

### Custom Validation

```python
from pydantic import BaseModel, validator, root_validator

class Item(BaseModel):
    name: str
    price: float
    tax: float | None = None
    
    @validator('price')
    def price_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Price must be positive')
        return v
    
    @root_validator
    def check_tax_less_than_price(cls, values):
        price = values.get('price')
        tax = values.get('tax')
        if tax and price and tax >= price:
            raise ValueError('Tax must be less than price')
        return values
```

## Response Handling

### Response Models

```python
from fastapi import FastAPI, HTTPException, status

class UserOut(BaseModel):
    username: str
    email: EmailStr
    # Exclude sensitive fields like password

class UserIn(BaseModel):
    username: str
    email: EmailStr
    password: str

@app.post("/users/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserIn):
    # Process user, hash password, etc.
    return user  # Password automatically excluded from response
```

### Status Codes and Headers

```python
from fastapi import Response, status

@app.post("/items/", status_code=status.HTTP_201_CREATED)
async def create_item(item: Item, response: Response):
    # Add custom headers
    response.headers["X-Custom-Header"] = "value"
    return {"id": 1, **item.dict()}

@app.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(item_id: int):
    return None
```

### Error Handling

```python
from fastapi import HTTPException

@app.get("/items/{item_id}")
async def read_item(item_id: int):
    if item_id not in items:
        raise HTTPException(
            status_code=404,
            detail="Item not found",
            headers={"X-Error": "Custom error header"}
        )
    return items[item_id]

# Custom exception handlers
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=400,
        content={"detail": exc.errors(), "body": exc.body}
    )
```

## Dependency Injection

Dependency injection is FastAPI's most powerful feature for code reusability:

```python
from fastapi import Depends, HTTPException, status
from typing import Annotated

# Simple dependency
async def get_query_param(q: str | None = None):
    return q

@app.get("/items/")
async def read_items(query: Annotated[str | None, Depends(get_query_param)]):
    return {"q": query}

# Database session dependency
from sqlalchemy.orm import Session

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/users/")
async def read_users(db: Annotated[Session, Depends(get_db)]):
    users = db.query(User).all()
    return users

# Authentication dependency
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    user = verify_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    return user

@app.get("/users/me")
async def read_users_me(current_user: Annotated[User, Depends(get_current_user)]):
    return current_user

# Class-based dependencies
class Pagination:
    def __init__(self, skip: int = 0, limit: int = 100):
        self.skip = skip
        self.limit = limit

@app.get("/items/")
async def read_items(pagination: Annotated[Pagination, Depends()]):
    return items[pagination.skip : pagination.skip + pagination.limit]
```

## Security and Authentication

See `references/security-oauth2-jwt.md` for comprehensive security implementation patterns.

### Basic Authentication Setup

```python
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# JWT token creation
SECRET_KEY = "your-secret-key-here"  # Use environment variable in production
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# Authentication endpoint
@app.post("/token")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect credentials")
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}
```

## Database Integration

See `references/database-async-sqlalchemy.md` for complete async database patterns.

### Async SQLAlchemy Setup

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String

# Database URL (use asyncpg for PostgreSQL, aiosqlite for SQLite)
DATABASE_URL = "postgresql+asyncpg://user:password@localhost/dbname"

# Create async engine
engine = create_async_engine(DATABASE_URL, echo=True)

# Create async session factory
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

Base = declarative_base()

# Define models
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)

# Initialize database
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Dependency for getting async session
async def get_db():
    async with async_session_maker() as session:
        yield session

# CRUD operations
@app.post("/users/", response_model=UserOut)
async def create_user(
    user: UserIn,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    db_user = User(
        email=user.email,
        username=user.username,
        hashed_password=get_password_hash(user.password)
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user
```

## Async Operations

FastAPI fully supports async/await for concurrent operations:

```python
import asyncio
import httpx

# When to use async def vs def:
# - Use async def when using await, async libraries, or I/O operations
# - Use def for CPU-bound operations or when not using async operations

# Async endpoint with external API call
@app.get("/external-data")
async def get_external_data():
    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.example.com/data")
        return response.json()

# Multiple concurrent operations
@app.get("/combined-data")
async def get_combined_data():
    async with httpx.AsyncClient() as client:
        # Run multiple requests concurrently
        results = await asyncio.gather(
            client.get("https://api.example.com/users"),
            client.get("https://api.example.com/posts"),
            client.get("https://api.example.com/comments")
        )
        return {
            "users": results[0].json(),
            "posts": results[1].json(),
            "comments": results[2].json()
        }

# Background tasks (non-blocking)
from fastapi import BackgroundTasks

def send_notification(email: str, message: str):
    # Simulate sending email
    print(f"Sending notification to {email}: {message}")

@app.post("/send-notification/")
async def create_notification(
    email: str,
    background_tasks: BackgroundTasks
):
    background_tasks.add_task(send_notification, email, "Welcome!")
    return {"message": "Notification scheduled"}
```

## Middleware

```python
from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import time

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Specify origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Trusted host middleware (security)
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["example.com", "*.example.com"]
)

# Custom middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response
```

## WebSockets

```python
from fastapi import WebSocket, WebSocketDisconnect
from typing import List

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    
    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(f"Message: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast("A client disconnected")
```

## Testing

```python
from fastapi.testclient import TestClient
import pytest

client = TestClient(app)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}

def test_create_user():
    response = client.post(
        "/users/",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "secret"
        }
    )
    assert response.status_code == 201
    assert response.json()["username"] == "testuser"
```

## Project Structure

Recommended structure for production applications:

```
project/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app instance
│   ├── config.py            # Configuration and settings
│   ├── models/              # SQLAlchemy models
│   ├── schemas/             # Pydantic schemas
│   ├── api/                 # API routes
│   ├── crud/                # CRUD operations
│   ├── db/                  # Database
│   └── core/                # Core functionality
├── tests/
├── alembic/                 # Database migrations
├── .env                     # Environment variables
├── requirements.txt
└── README.md
```

## Common Patterns

### Router Organization

```python
from fastapi import APIRouter

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}}
)

@router.get("/")
async def read_users():
    return [{"username": "user1"}]

# Include router in main app
app.include_router(router)
```

### Environment Configuration

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    secret_key: str
    
    class Config:
        env_file = ".env"

settings = Settings()
```

## Troubleshooting

**CORS errors**: Configure CORSMiddleware with specific origins in production

**Validation errors**: Check Pydantic model definitions and type hints

**Async database errors**: Use async database drivers (asyncpg, aiosqlite)

**Background tasks not executing**: Ensure tasks are added before returning response

## Additional Resources

- `references/security-oauth2-jwt.md` - Complete authentication implementation
- `references/database-async-sqlalchemy.md` - Async database patterns
- `references/testing-patterns.md` - Comprehensive testing strategies
- Official docs: https://fastapi.tiangolo.com/

## Key Decision Points

**Use `async def` when**: Using `await`, async libraries, or I/O operations  
**Use `def` when**: CPU-bound operations or simple synchronous code

**Use background tasks for**: Non-critical operations like notifications, logging  
**Avoid background tasks for**: Critical operations that must complete

**Database choice**: PostgreSQL+asyncpg (production), SQLite+aiosqlite (development)
