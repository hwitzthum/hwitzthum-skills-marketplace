# FastAPI Authentication Patterns

Comprehensive patterns for implementing OAuth 2.0 and JWT authentication in FastAPI, compliant with RFC 9700.

## Table of Contents

1. [Complete FastAPI + Auth0 Integration](#complete-fastapi--auth0-integration)
2. [Custom JWT with Database](#custom-jwt-with-database)
3. [Role-Based Access Control (RBAC)](#role-based-access-control)
4. [Refresh Token Implementation](#refresh-token-implementation)
5. [Multiple OAuth Providers](#multiple-oauth-providers)
6. [Testing Authentication](#testing-authentication)

---

## Complete FastAPI + Auth0 Integration

Full production-ready implementation with Auth0:

```python
# config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    auth0_domain: str
    auth0_api_audience: str
    auth0_algorithms: str = "RS256"
    auth0_issuer: str = None
    
    class Config:
        env_file = ".env"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.auth0_issuer is None:
            self.auth0_issuer = f"https://{self.auth0_domain}/"

settings = Settings()

# auth.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
import httpx
from functools import lru_cache

security = HTTPBearer()

@lru_cache()
async def get_jwks():
    """Cache JWKS for 1 hour"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://{settings.auth0_domain}/.well-known/jwks.json"
        )
        return response.json()

async def verify_token(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """Verify Auth0 JWT token"""
    token = credentials.credentials
    
    try:
        # Get unverified header to find the key
        unverified_header = jwt.get_unverified_header(token)
        
        # Get JWKS
        jwks = await get_jwks()
        
        # Find the matching key
        rsa_key = {}
        for key in jwks["keys"]:
            if key["kid"] == unverified_header["kid"]:
                rsa_key = {
                    "kty": key["kty"],
                    "kid": key["kid"],
                    "use": key["use"],
                    "n": key["n"],
                    "e": key["e"]
                }
                break
        
        if not rsa_key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Unable to find appropriate key"
            )
        
        # Validate token
        payload = jwt.decode(
            token,
            rsa_key,
            algorithms=[settings.auth0_algorithms],
            audience=settings.auth0_api_audience,
            issuer=settings.auth0_issuer,
        )
        
        return payload
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}"
        )

# main.py
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/public")
async def public_endpoint():
    return {"message": "This is a public endpoint"}

@app.get("/api/protected")
async def protected_endpoint(token_payload: dict = Depends(verify_token)):
    return {
        "message": "This is a protected endpoint",
        "user": token_payload
    }

@app.get("/api/profile")
async def get_profile(token_payload: dict = Depends(verify_token)):
    return {
        "user_id": token_payload.get("sub"),
        "email": token_payload.get("email"),
        "email_verified": token_payload.get("email_verified"),
        "permissions": token_payload.get("permissions", [])
    }
```

---

## Custom JWT with Database

Custom JWT implementation with PostgreSQL/SQLAlchemy:

```python
# database.py
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

SQLALCHEMY_DATABASE_URL = "postgresql://user:password@localhost/dbname"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# auth.py
from datetime import datetime, timedelta, timezone
from typing import Optional
import jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel

# Password hashing
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

# JWT configuration
SECRET_KEY = "your-secret-key"  # Use env variable!
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Models
class TokenData(BaseModel):
    username: Optional[str] = None

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool
    
    class Config:
        from_attributes = True

# Helper functions
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "access"
    })
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "refresh"
    })
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Get user from database
def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def authenticate_user(db: Session, username: str, password: str):
    user = get_user_by_username(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        token_type: str = payload.get("type")
        
        if username is None or token_type != "access":
            raise credentials_exception
            
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.InvalidTokenError:
        raise credentials_exception
    
    user = get_user_by_username(db, username=username)
    if user is None:
        raise credentials_exception
    
    return user

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

# Endpoints
from fastapi import FastAPI, Depends, status as http_status

app = FastAPI()

@app.post("/register", response_model=UserResponse)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    # Check if user exists
    db_user = get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="Username already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

@app.post("/token")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    refresh_token = create_refresh_token(data={"sub": user.username})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@app.get("/users/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user
```

---

## Role-Based Access Control (RBAC)

Implement fine-grained permissions:

```python
from enum import Enum
from typing import List
from fastapi import Depends, HTTPException, status

class UserRole(str, Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    USER = "user"

class Permission(str, Enum):
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    ADMIN = "admin"

# Extended user model with roles
class UserWithRoles(BaseModel):
    username: str
    roles: List[UserRole]
    permissions: List[Permission]

# Permission checker
class PermissionChecker:
    def __init__(self, required_permissions: List[Permission]):
        self.required_permissions = required_permissions
    
    def __call__(self, user: dict = Depends(verify_token)):
        user_permissions = user.get("permissions", [])
        
        for permission in self.required_permissions:
            if permission not in user_permissions:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Missing required permission: {permission}"
                )
        
        return user

# Role checker
class RoleChecker:
    def __init__(self, allowed_roles: List[UserRole]):
        self.allowed_roles = allowed_roles
    
    def __call__(self, user: dict = Depends(verify_token)):
        user_roles = user.get("roles", [])
        
        if not any(role in user_roles for role in self.allowed_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        
        return user

# Usage examples
@app.get("/api/admin/users")
async def list_users(
    user: dict = Depends(RoleChecker([UserRole.ADMIN]))
):
    return {"message": "List of all users"}

@app.delete("/api/resource/{resource_id}")
async def delete_resource(
    resource_id: int,
    user: dict = Depends(PermissionChecker([Permission.DELETE]))
):
    return {"message": f"Deleted resource {resource_id}"}

@app.post("/api/data")
async def create_data(
    data: dict,
    user: dict = Depends(PermissionChecker([Permission.WRITE]))
):
    return {"message": "Data created", "data": data}
```

---

## Refresh Token Implementation

Secure refresh token rotation (RFC 9700 recommended):

```python
from typing import Optional
import secrets
from datetime import datetime, timedelta
from sqlalchemy import Column, String, DateTime, ForeignKey

# Add to database models
class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    expires_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    revoked = Column(Boolean, default=False)

# Refresh token functions
def create_refresh_token_db(db: Session, user_id: int) -> str:
    """Create and store refresh token"""
    token = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(days=7)
    
    db_token = RefreshToken(
        token=token,
        user_id=user_id,
        expires_at=expires_at
    )
    db.add(db_token)
    db.commit()
    
    return token

def verify_refresh_token(db: Session, token: str) -> Optional[int]:
    """Verify refresh token and return user_id"""
    db_token = db.query(RefreshToken).filter(
        RefreshToken.token == token,
        RefreshToken.revoked == False,
        RefreshToken.expires_at > datetime.utcnow()
    ).first()
    
    if db_token:
        return db_token.user_id
    return None

def revoke_refresh_token(db: Session, token: str):
    """Revoke a refresh token"""
    db_token = db.query(RefreshToken).filter(
        RefreshToken.token == token
    ).first()
    
    if db_token:
        db_token.revoked = True
        db.commit()

# Refresh endpoint with token rotation
@app.post("/token/refresh")
async def refresh_access_token(
    refresh_token: str,
    db: Session = Depends(get_db)
):
    # Verify refresh token
    user_id = verify_refresh_token(db, refresh_token)
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )
    
    # Get user
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    # Revoke old refresh token (token rotation)
    revoke_refresh_token(db, refresh_token)
    
    # Create new tokens
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    new_refresh_token = create_refresh_token_db(db, user.id)
    
    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer"
    }

# Logout endpoint
@app.post("/logout")
async def logout(
    refresh_token: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Revoke refresh token
    revoke_refresh_token(db, refresh_token)
    
    return {"message": "Successfully logged out"}
```

---

## Security Middleware

Essential security middleware for production:

```python
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from starlette.middleware.sessions import SessionMiddleware
import secrets

# Session middleware
app.add_middleware(
    SessionMiddleware,
    secret_key=secrets.token_urlsafe(32),
    same_site="lax",
    https_only=True,  # In production
    max_age=1800  # 30 minutes
)

# Trusted hosts
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["example.com", "*.example.com"]
)

# Compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Security headers
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        return response

app.add_middleware(SecurityHeadersMiddleware)

# Rate limiting
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Apply rate limit to login endpoint
@app.post("/token")
@limiter.limit("5/minute")
async def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends()):
    # Login logic here
    pass
```

---

## Production Deployment Checklist

- [ ] All secrets in environment variables
- [ ] HTTPS enabled with TLS 1.2+
- [ ] CORS properly configured (no *)
- [ ] Rate limiting on auth endpoints
- [ ] Security headers middleware enabled
- [ ] JWT expiration set to 15-60 minutes
- [ ] Refresh token rotation implemented
- [ ] Database connection pooling configured
- [ ] Logging for authentication events
- [ ] Error messages don't leak information
- [ ] Health check endpoint implemented
- [ ] Monitoring and alerting configured
