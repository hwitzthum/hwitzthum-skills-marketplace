# FastAPI Security and Authentication

Complete guide for implementing OAuth2 with JWT authentication in FastAPI.

## Overview

This reference provides production-ready patterns for securing FastAPI applications using:
- Password hashing with Argon2/Bcrypt
- JWT (JSON Web Tokens) for stateless authentication
- OAuth2 password flow
- Role-based access control (RBAC)
- Refresh tokens
- Security best practices

## Dependencies

```bash
pip install python-jose[cryptography]  # JWT handling
pip install passlib[argon2]            # Password hashing
pip install python-multipart           # Form data support
```

## Password Hashing

Always hash passwords before storing them:

```python
from passlib.context import CryptContext

# Use Argon2 (recommended) or Bcrypt
pwd_context = CryptContext(
    schemes=["argon2", "bcrypt"],
    deprecated="auto"
)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against hashed password."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Generate hash from plain password."""
    return pwd_context.hash(password)

# Example usage
hashed = get_password_hash("mysecretpassword")
is_valid = verify_password("mysecretpassword", hashed)  # True
```

## JWT Token Implementation

### Token Creation and Validation

```python
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt

# Configuration (use environment variables in production)
SECRET_KEY = "your-secret-key-here-should-be-32-bytes-or-more"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict) -> str:
    """Create JWT refresh token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str, token_type: str = "access") -> Optional[dict]:
    """Verify and decode JWT token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != token_type:
            return None
        return payload
    except JWTError:
        return None
```

### Complete Authentication System

```python
from fastapi import Depends, HTTPException, status, FastAPI
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from typing import Annotated, Optional
from sqlalchemy.orm import Session

# Pydantic models
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    username: Optional[str] = None

class User(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    disabled: bool = False

class UserInDB(User):
    hashed_password: str

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Database functions (adapt to your database)
def get_user(db: Session, username: str) -> Optional[UserInDB]:
    """Retrieve user from database."""
    # Replace with actual database query
    user = db.query(UserModel).filter(UserModel.username == username).first()
    if user:
        return UserInDB(**user.__dict__)
    return None

def authenticate_user(db: Session, username: str, password: str) -> Optional[UserInDB]:
    """Authenticate user credentials."""
    user = get_user(db, username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

# Dependency for getting current user
async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(get_db)]
) -> User:
    """Extract and validate current user from JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = verify_token(token, "access")
    if payload is None:
        raise credentials_exception
    
    username: str = payload.get("sub")
    if username is None:
        raise credentials_exception
    
    user = get_user(db, username=username)
    if user is None:
        raise credentials_exception
    
    return user

async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
) -> User:
    """Ensure user is active (not disabled)."""
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

# Authentication endpoints
app = FastAPI()

@app.post("/token", response_model=Token)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[Session, Depends(get_db)]
):
    """Login endpoint - returns access and refresh tokens."""
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user.username})
    refresh_token = create_refresh_token(data={"sub": user.username})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@app.post("/token/refresh", response_model=Token)
async def refresh_token_endpoint(
    refresh_token: str,
    db: Annotated[Session, Depends(get_db)]
):
    """Refresh access token using refresh token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid refresh token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = verify_token(refresh_token, "refresh")
    if payload is None:
        raise credentials_exception
    
    username: str = payload.get("sub")
    if username is None:
        raise credentials_exception
    
    # Optionally verify user still exists and is active
    user = get_user(db, username)
    if user is None or user.disabled:
        raise credentials_exception
    
    new_access_token = create_access_token(data={"sub": username})
    new_refresh_token = create_refresh_token(data={"sub": username})
    
    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer"
    }

# Protected endpoints
@app.get("/users/me", response_model=User)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    """Get current authenticated user."""
    return current_user

@app.get("/users/me/items")
async def read_own_items(
    current_user: Annotated[User, Depends(get_current_active_user)]
):
    """Get items for current authenticated user."""
    return [{"item_id": "Foo", "owner": current_user.username}]
```

## Role-Based Access Control (RBAC)

```python
from enum import Enum

class Role(str, Enum):
    ADMIN = "admin"
    USER = "user"
    MODERATOR = "moderator"

class UserWithRole(User):
    role: Role

def require_role(required_role: Role):
    """Dependency to check user has required role."""
    async def role_checker(
        current_user: Annotated[UserWithRole, Depends(get_current_active_user)]
    ) -> UserWithRole:
        if current_user.role != required_role and current_user.role != Role.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        return current_user
    return role_checker

# Usage
@app.delete("/items/{item_id}")
async def delete_item(
    item_id: int,
    current_user: Annotated[UserWithRole, Depends(require_role(Role.ADMIN))]
):
    """Only admins can delete items."""
    return {"message": f"Item {item_id} deleted by {current_user.username}"}

# Multiple roles allowed
def require_any_role(*allowed_roles: Role):
    """Dependency to check user has any of the allowed roles."""
    async def role_checker(
        current_user: Annotated[UserWithRole, Depends(get_current_active_user)]
    ) -> UserWithRole:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role must be one of: {', '.join(allowed_roles)}"
            )
        return current_user
    return role_checker

@app.post("/moderate/")
async def moderate_content(
    current_user: Annotated[
        UserWithRole,
        Depends(require_any_role(Role.ADMIN, Role.MODERATOR))
    ]
):
    """Admins and moderators can moderate content."""
    return {"message": "Content moderated"}
```

## Security Best Practices

### 1. Secret Key Management

Never hardcode secrets:

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    class Config:
        env_file = ".env"

settings = Settings()

# Use settings.secret_key instead of hardcoded value
```

### 2. HTTPS in Production

Always use HTTPS in production:

```python
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

# Redirect HTTP to HTTPS
app.add_middleware(HTTPSRedirectMiddleware)
```

### 3. Secure Cookie Settings

For cookie-based authentication:

```python
from fastapi import Response

@app.post("/login")
async def login(response: Response, ...):
    # Set secure cookie
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,  # Prevent JavaScript access
        secure=True,    # HTTPS only
        samesite="lax", # CSRF protection
        max_age=1800    # 30 minutes
    )
    return {"message": "Logged in"}
```

### 4. Rate Limiting

Implement rate limiting to prevent brute force attacks:

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/token")
@limiter.limit("5/minute")  # 5 attempts per minute
async def login(request: Request, ...):
    # Login logic
    pass
```

### 5. Input Validation

Always validate input thoroughly:

```python
from pydantic import BaseModel, Field, validator

class UserRegistration(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, pattern="^[a-zA-Z0-9_]+$")
    email: EmailStr
    password: str = Field(..., min_length=8)
    
    @validator('password')
    def password_strength(cls, v):
        # Check password complexity
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain digit')
        return v
```

## OAuth2 Scopes

For fine-grained permissions:

```python
from fastapi.security import OAuth2PasswordBearer, SecurityScopes

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="token",
    scopes={
        "items:read": "Read items",
        "items:write": "Write items",
        "users:read": "Read users"
    }
)

def get_current_user_with_scopes(
    security_scopes: SecurityScopes,
    token: Annotated[str, Depends(oauth2_scheme)]
):
    """Verify user has required scopes."""
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = "Bearer"
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": authenticate_value},
    )
    
    payload = verify_token(token)
    if payload is None:
        raise credentials_exception
    
    token_scopes = payload.get("scopes", [])
    for scope in security_scopes.scopes:
        if scope not in token_scopes:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
    
    return payload

@app.get("/items/")
async def read_items(
    current_user: Annotated[dict, Security(get_current_user_with_scopes, scopes=["items:read"])]
):
    """Requires items:read scope."""
    return [{"item_id": "Foo"}]
```

## Complete Example: User Registration

```python
@app.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserRegistration,
    db: Annotated[Session, Depends(get_db)]
):
    """Register new user."""
    # Check if user exists
    existing_user = db.query(UserModel).filter(
        (UserModel.username == user_data.username) |
        (UserModel.email == user_data.email)
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered"
        )
    
    # Create user
    hashed_password = get_password_hash(user_data.password)
    db_user = UserModel(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return User(**db_user.__dict__)
```

## Testing Authentication

```python
from fastapi.testclient import TestClient

def test_login():
    client = TestClient(app)
    response = client.post(
        "/token",
        data={"username": "testuser", "password": "testpass"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_protected_endpoint():
    client = TestClient(app)
    # Login first
    login_response = client.post(
        "/token",
        data={"username": "testuser", "password": "testpass"}
    )
    token = login_response.json()["access_token"]
    
    # Access protected endpoint
    response = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
```

This reference provides production-ready authentication patterns. Always use HTTPS in production, store secrets securely, and implement rate limiting to prevent abuse.
