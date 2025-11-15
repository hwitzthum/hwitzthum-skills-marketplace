---
name: oauth2-fastapi-streamlit-auth
description: Production-ready OAuth 2.0 and OIDC authentication implementation guide compliant with RFC 9700 (January 2025) Best Current Practice. Use when implementing secure authentication in FastAPI backends and Streamlit frontends, requiring JWT tokens, PKCE flows, token validation, or setting up OAuth 2.0 providers (Auth0, Google, Azure). Covers authorization code flow with PKCE, token security, session management, API protection, and modern security patterns for Python web applications.
---

# OAuth 2.0 Authentication for FastAPI & Streamlit

Production-ready authentication implementation guide compliant with **RFC 9700 (January 2025)** - OAuth 2.0 Security Best Current Practice.

## Quick Start

This skill provides three implementation paths:

1. **FastAPI Backend** - Secure API authentication with JWT
2. **Streamlit Frontend** - User authentication and session management
3. **Full Stack** - Integrated FastAPI + Streamlit with OAuth 2.0/OIDC

## Core Security Principles (RFC 9700)

### Mandatory Requirements

1. **ALWAYS use Authorization Code Flow with PKCE** - Mandatory for all clients (public and confidential)
2. **NEVER use Implicit Grant or Password Grant** - Deprecated in RFC 9700
3. **ALWAYS validate redirect URIs** - Prevent authorization code injection attacks
4. **ALWAYS use HTTPS in production** - TLS 1.2+ required
5. **ALWAYS implement token expiration** - Short-lived access tokens (15-60 minutes)
6. **ALWAYS validate JWT signatures** - Use proper key management
7. **ALWAYS implement CSRF protection** - Use state parameter or PKCE

### Key Security Updates from RFC 9700

- **PKCE is mandatory** for all OAuth clients, including confidential clients
- **Sender-constrained tokens** (DPoP) recommended for enhanced security
- **Strict redirect URI validation** to prevent code injection attacks
- **Token replay prevention** through proper validation and expiration
- **Authorization code single-use** enforcement
- **Refresh token rotation** for enhanced security

## Implementation Workflows

### Workflow 1: FastAPI Backend with OAuth 2.0

Follow these steps for FastAPI backend authentication:

1. **Choose authentication provider** → Auth0, Google, Azure AD, or custom
2. **Configure OAuth 2.0 client** → Set up client ID, secret, redirect URIs
3. **Implement Authorization Code Flow with PKCE** → See `references/fastapi-patterns.md`
4. **Set up JWT validation** → Use proper libraries and key management
5. **Protect API endpoints** → Implement dependency injection for auth
6. **Add token refresh logic** → Handle token expiration gracefully

### Workflow 2: Streamlit Frontend with OIDC

Follow these steps for Streamlit authentication:

1. **Choose authentication method**:
   - **Built-in OIDC** (Streamlit 1.42+) → See `references/streamlit-builtin-oidc.md`
   - **Custom OAuth component** → See `references/streamlit-custom-auth.md`
2. **Configure identity provider** → Set up OAuth2 client in secrets.toml
3. **Implement login/logout flow** → Use st.login()/st.logout() or custom component
4. **Manage user sessions** → Handle cookies and session state
5. **Integrate with backend** → Pass JWT tokens to FastAPI backend

### Workflow 3: Full Stack Integration

For complete FastAPI + Streamlit integration:

1. **Set up FastAPI backend** → Follow Workflow 1
2. **Set up Streamlit frontend** → Follow Workflow 2
3. **Configure shared OAuth provider** → Same client for both or separate clients
4. **Implement token passing** → Streamlit passes JWT to FastAPI headers
5. **Add security middleware** → CORS, rate limiting, security headers
6. **Test end-to-end flow** → Login → API call → Token validation → Response

## FastAPI Implementation

### Basic JWT Authentication

```python
from datetime import datetime, timedelta, timezone
from typing import Annotated
import jwt
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from pydantic import BaseModel

# Configuration
SECRET_KEY = "your-secret-key-here"  # Use environment variables!
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# IMPORTANT: Use bcrypt 4.0.1 for compatibility with passlib 1.7.4
# See "Password Hashing Best Practices" section below for details

# Models
class Token(BaseModel):
    access_token: str
    token_type: str

class User(BaseModel):
    username: str
    email: str | None = None
    disabled: bool | None = False

# Create access token
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Verify token and get current user
async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        # Fetch user from database here
        return User(username=username)
    except jwt.InvalidTokenError:
        raise credentials_exception

# Protected endpoint
@app.get("/protected")
async def protected_route(current_user: Annotated[User, Depends(get_current_user)]):
    return {"message": f"Hello {current_user.username}"}
```

### OAuth 2.0 with Auth0 (Recommended)

```python
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2AuthorizationCodeBearer
from jose import jwt, JWTError
import httpx

app = FastAPI()

# Auth0 configuration
AUTH0_DOMAIN = "your-domain.auth0.com"
API_AUDIENCE = "your-api-identifier"
ALGORITHMS = ["RS256"]

# OAuth2 scheme
oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl=f"https://{AUTH0_DOMAIN}/authorize",
    tokenUrl=f"https://{AUTH0_DOMAIN}/oauth/token",
)

# Get Auth0 public keys
async def get_auth0_public_key():
    async with httpx.AsyncClient() as client:
        response = await client.get(f"https://{AUTH0_DOMAIN}/.well-known/jwks.json")
        return response.json()

# Validate token
async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        # Get signing key
        jwks = await get_auth0_public_key()
        unverified_header = jwt.get_unverified_header(token)
        
        # Find the right key
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
        
        # Validate token
        payload = jwt.decode(
            token,
            rsa_key,
            algorithms=ALGORITHMS,
            audience=API_AUDIENCE,
            issuer=f"https://{AUTH0_DOMAIN}/"
        )
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.get("/api/protected")
async def protected_resource(current_user: dict = Depends(get_current_user)):
    return {"message": "Access granted", "user": current_user}
```

## Streamlit Implementation

### Built-in OIDC (Streamlit 1.42+)

Configure in `.streamlit/secrets.toml`:

```toml
[auth]
redirect_uri = "http://localhost:8501/oauth2callback"
cookie_secret = "your-random-secret-here"

[auth.google]
client_id = "your-google-client-id"
client_secret = "your-google-client-secret"
server_metadata_url = "https://accounts.google.com/.well-known/openid-configuration"
```

Implement in your Streamlit app:

```python
import streamlit as st

# Check authentication status
if not st.user.is_logged_in:
    if st.button("Log in with Google"):
        st.login("google")
    st.stop()

# User is logged in
if st.button("Log out"):
    st.logout()

st.write(f"Welcome, {st.user.name}!")
st.write(f"Email: {st.user.email}")

# Access JWT token for API calls
token = st.user.token
```

### Integration with FastAPI Backend

```python
import streamlit as st
import httpx

# Get token from logged-in user
if st.user.is_logged_in:
    token = st.user.token
    
    # Call protected FastAPI endpoint
    headers = {"Authorization": f"Bearer {token}"}
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://your-api.com/protected",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            st.write(data)
        else:
            st.error("Authentication failed")
```

## PKCE Implementation

PKCE (Proof Key for Code Exchange) is **mandatory** as of RFC 9700.

### Generate PKCE Parameters (Python)

```python
import secrets
import hashlib
import base64

def generate_pkce_pair():
    """Generate PKCE code verifier and challenge"""
    # Generate code verifier (43-128 characters)
    code_verifier = base64.urlsafe_b64encode(
        secrets.token_bytes(32)
    ).decode('utf-8').rstrip('=')
    
    # Generate code challenge (SHA256 hash)
    code_challenge = base64.urlsafe_b64encode(
        hashlib.sha256(code_verifier.encode('utf-8')).digest()
    ).decode('utf-8').rstrip('=')
    
    return code_verifier, code_challenge

# Usage
verifier, challenge = generate_pkce_pair()
print(f"Code Verifier: {verifier}")
print(f"Code Challenge: {challenge}")
```

### PKCE Authorization Flow

```python
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
import httpx

app = FastAPI()

# Step 1: Initiate authorization
@app.get("/login")
async def login(request: Request):
    # Generate PKCE parameters
    code_verifier, code_challenge = generate_pkce_pair()
    
    # Store code_verifier in session (use secure session management)
    request.session["code_verifier"] = code_verifier
    
    # Build authorization URL
    auth_url = (
        f"https://{AUTH0_DOMAIN}/authorize?"
        f"response_type=code&"
        f"client_id={CLIENT_ID}&"
        f"redirect_uri={REDIRECT_URI}&"
        f"scope=openid profile email&"
        f"code_challenge={code_challenge}&"
        f"code_challenge_method=S256&"
        f"state={generate_state()}"
    )
    
    return RedirectResponse(auth_url)

# Step 2: Handle callback
@app.get("/callback")
async def callback(code: str, state: str, request: Request):
    # Retrieve code_verifier from session
    code_verifier = request.session.get("code_verifier")
    
    # Exchange code for tokens
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"https://{AUTH0_DOMAIN}/oauth/token",
            data={
                "grant_type": "authorization_code",
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "code": code,
                "code_verifier": code_verifier,
                "redirect_uri": REDIRECT_URI
            }
        )
        
        tokens = response.json()
        return {"access_token": tokens["access_token"]}
```

## Security Checklists

### Pre-Deployment Security Checklist

- [ ] HTTPS enabled in production
- [ ] Environment variables for all secrets
- [ ] PKCE implemented for all OAuth flows
- [ ] JWT signature validation enabled
- [ ] Token expiration properly configured (15-60 min for access tokens)
- [ ] Refresh token rotation enabled
- [ ] Redirect URI validation strict and comprehensive
- [ ] CORS configured properly (not using *)
- [ ] Rate limiting enabled on authentication endpoints
- [ ] Security headers configured (HSTS, CSP, X-Frame-Options)
- [ ] Logging enabled for authentication events
- [ ] Error messages don't leak sensitive information
- [ ] Session timeout configured
- [ ] Authorization code single-use enforced

### Common Vulnerabilities to Avoid

1. **Hardcoded secrets** - Use environment variables
2. **Weak token expiration** - Access tokens should expire in 15-60 minutes
3. **Missing PKCE** - Required for all clients as of RFC 9700
4. **Loose redirect URI validation** - Use exact matching
5. **Storing tokens in localStorage** - Use httpOnly cookies when possible
6. **Not validating JWT signatures** - Always verify with proper keys
7. **Using implicit grant** - Deprecated, use authorization code flow
8. **Exposing detailed error messages** - Generic messages for auth failures
9. **Missing CSRF protection** - Use state parameter or PKCE
10. **Not implementing rate limiting** - Prevent brute force attacks

## Password Hashing Best Practices

### Bcrypt Version Compatibility (CRITICAL)

**Issue**: bcrypt version 5.0+ has stricter validation that causes compatibility issues with passlib 1.7.4.

**Solution**: Pin bcrypt to version 4.0.1 in your requirements.txt

```txt
# requirements.txt
fastapi>=0.115.0
uvicorn[standard]>=0.32.0
python-jose[cryptography]>=3.3.0
passlib>=1.7.4
bcrypt==4.0.1  # CRITICAL: Pin to 4.0.1 for passlib compatibility
python-multipart>=0.0.12
pydantic[email]>=2.11.0
python-dotenv>=1.1.0
```

### Handling Bcrypt 72-Byte Limit

Bcrypt has a maximum password length of 72 bytes. Always truncate passwords before hashing:

```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash a password using bcrypt

        Note: Bcrypt has a maximum password length of 72 bytes.
        Passwords are truncated to 72 bytes if longer.
        """
        # Truncate password to 72 bytes (bcrypt limitation)
        password_bytes = password.encode('utf-8')[:72]
        return pwd_context.hash(password_bytes.decode('utf-8'))

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        Verify a password against its hash

        Note: Password is truncated to 72 bytes to match bcrypt behavior
        """
        # Truncate password to 72 bytes (bcrypt limitation)
        password_bytes = plain_password.encode('utf-8')[:72]
        return pwd_context.verify(password_bytes.decode('utf-8'), hashed_password)
```

### Common Bcrypt Errors and Solutions

**Error**: `ValueError: password cannot be longer than 72 bytes`
```python
# ❌ WRONG - Will fail with long passwords
pwd_context.hash(password)

# ✅ CORRECT - Truncate to 72 bytes
password_bytes = password.encode('utf-8')[:72]
pwd_context.hash(password_bytes.decode('utf-8'))
```

**Error**: `AttributeError: module 'bcrypt' has no attribute '__about__'`
```bash
# Solution: Downgrade bcrypt to 4.0.1
pip uninstall -y bcrypt
pip install bcrypt==4.0.1
```

### Alternative: Argon2 (Recommended for New Projects)

For new projects, consider Argon2 instead of bcrypt (no 72-byte limit):

```python
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

# Argon2 doesn't have the 72-byte limitation
def hash_password(password: str) -> str:
    return pwd_context.hash(password)  # No truncation needed
```

**Dependencies for Argon2**:
```txt
passlib[argon2]>=1.7.4
argon2-cffi>=21.3.0
```

### Password Strength Validation

Always validate password strength before hashing:

```python
from pydantic import BaseModel, field_validator
import re

class UserRegistration(BaseModel):
    username: str
    password: str

    @field_validator('password')
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character')
        return v
```

## Configuration Examples

### Auth0 Configuration

See `assets/auth0-config-template.json` for complete Auth0 application configuration.

### Google OAuth Configuration

See `assets/google-oauth-config.md` for setting up Google Cloud Console.

### Azure AD Configuration

See `assets/azure-ad-config.md` for Azure Active Directory setup.

## Detailed References

For detailed implementation patterns and examples:

- **FastAPI patterns**: `references/fastapi-patterns.md`
- **Streamlit built-in OIDC**: `references/streamlit-builtin-oidc.md`
- **Streamlit custom auth**: `references/streamlit-custom-auth.md`
- **JWT best practices**: `references/jwt-best-practices.md`
- **Production deployment**: `references/production-deployment.md`
- **Testing strategies**: `references/testing-auth.md`

## Utility Scripts

Available in `scripts/` directory:

- `generate_secret_key.py` - Generate cryptographically secure secret keys
- `generate_pkce.py` - Generate PKCE code verifier and challenge
- `validate_jwt.py` - Test JWT token validation
- `test_auth_flow.py` - End-to-end authentication flow testing

## Troubleshooting

### Common Issues

**Token validation fails**
- Check JWT signature algorithm matches configuration
- Verify issuer and audience claims
- Ensure proper key management (RS256 vs HS256)

**Redirect URI mismatch**
- Verify exact URI matching in OAuth provider
- Check for trailing slashes
- Ensure HTTPS in production

**PKCE validation fails**
- Verify code_verifier is stored securely between requests
- Check code_challenge_method is S256
- Ensure proper base64url encoding

**Session not persisting**
- Check cookie configuration (httpOnly, secure, SameSite)
- Verify session middleware is enabled
- Check cookie domain and path settings

**Password hashing errors (bcrypt)**
- `ValueError: password cannot be longer than 72 bytes` → Truncate password to 72 bytes before hashing
- `AttributeError: module 'bcrypt' has no attribute '__about__'` → Downgrade to bcrypt==4.0.1
- Always use consistent truncation in both hash_password() and verify_password()
- See "Password Hashing Best Practices" section for complete solution

## Additional Resources

- [RFC 9700: OAuth 2.0 Security Best Current Practice](https://www.rfc-editor.org/rfc/rfc9700.html)
- [RFC 7636: PKCE Specification](https://www.rfc-editor.org/rfc/rfc7636.html)
- [FastAPI Security Documentation](https://fastapi.tiangolo.com/tutorial/security/)
- [Streamlit Authentication Documentation](https://docs.streamlit.io/develop/concepts/connections/authentication)
