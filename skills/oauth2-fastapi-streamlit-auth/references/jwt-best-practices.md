# JWT Best Practices (RFC 9700 Compliant)

Essential security practices for JWT implementation in OAuth 2.0 applications.

## Token Structure

### Standard Claims

**Required Claims:**
- `iss` (Issuer) - Who issued the token
- `sub` (Subject) - User identifier
- `aud` (Audience) - Intended recipient
- `exp` (Expiration) - When token expires
- `iat` (Issued At) - When token was issued

**Recommended Claims:**
- `nbf` (Not Before) - Token not valid before this time
- `jti` (JWT ID) - Unique identifier for token replay prevention

```python
{
    "iss": "https://your-auth-server.com",
    "sub": "user123",
    "aud": "your-api-identifier",
    "exp": 1699564800,
    "iat": 1699561200,
    "nbf": 1699561200,
    "jti": "unique-token-id-12345"
}
```

## Algorithm Selection

### Recommended: RS256 (RSA)

**Asymmetric - Best for Production**
- Public key for verification
- Private key for signing
- Keys can be rotated easily
- Compliant with RFC 9700

```python
from jose import jwt
from cryptography.hazmat.primitives import serialization

# Load keys
with open("private_key.pem", "rb") as key_file:
    private_key = key_file.read()

with open("public_key.pem", "rb") as key_file:
    public_key = key_file.read()

# Sign token
token = jwt.encode(
    claims,
    private_key,
    algorithm="RS256"
)

# Verify token
payload = jwt.decode(
    token,
    public_key,
    algorithms=["RS256"]
)
```

### Alternative: HS256 (HMAC)

**Symmetric - Simpler Setup**
- Single shared secret
- Suitable for internal services
- Must protect secret carefully

```python
SECRET_KEY = "your-256-bit-secret"

# Sign and verify with same key
token = jwt.encode(claims, SECRET_KEY, algorithm="HS256")
payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
```

### ❌ NEVER Use: "none" Algorithm

```python
# CRITICAL SECURITY VULNERABILITY
# Never accept tokens with alg="none"
algorithms = ["RS256", "HS256"]  # Never include "none"
```

## Token Expiration

### Access Tokens

**RFC 9700 Recommendation: 15-60 minutes**

```python
from datetime import datetime, timedelta, timezone

ACCESS_TOKEN_EXPIRE_MINUTES = 30  # Recommended

expire = datetime.now(timezone.utc) + timedelta(
    minutes=ACCESS_TOKEN_EXPIRE_MINUTES
)

claims = {
    "sub": user_id,
    "exp": expire,
    "iat": datetime.now(timezone.utc)
}
```

### Refresh Tokens

**Longer Lifetime: 7-90 days**

```python
REFRESH_TOKEN_EXPIRE_DAYS = 7

expire = datetime.now(timezone.utc) + timedelta(
    days=REFRESH_TOKEN_EXPIRE_DAYS
)
```

## Token Validation

### Complete Validation Flow

```python
from jose import jwt, JWTError
from datetime import datetime, timezone

def validate_token(token: str, secret: str, audience: str, issuer: str):
    """Comprehensive token validation"""
    try:
        payload = jwt.decode(
            token,
            secret,
            algorithms=["RS256"],
            audience=audience,
            issuer=issuer,
            options={
                "verify_signature": True,
                "verify_exp": True,
                "verify_nbf": True,
                "verify_iat": True,
                "verify_aud": True,
                "verify_iss": True
            }
        )
        
        # Additional custom validation
        if "jti" in payload:
            # Check if token is revoked (check against database/cache)
            if is_token_revoked(payload["jti"]):
                raise ValueError("Token has been revoked")
        
        return payload
        
    except jwt.ExpiredSignatureError:
        raise ValueError("Token has expired")
    except jwt.JWTClaimsError:
        raise ValueError("Invalid token claims")
    except JWTError as e:
        raise ValueError(f"Token validation failed: {str(e)}")
```

## Token Storage

### ❌ Don't Store in localStorage

```javascript
// VULNERABLE TO XSS ATTACKS
localStorage.setItem('token', token);  // ❌ DON'T DO THIS
```

### ✅ Use httpOnly Cookies (Recommended)

```python
from fastapi import Response

@app.post("/login")
async def login(response: Response):
    token = create_access_token(user_data)
    
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,      # Prevents JavaScript access
        secure=True,        # HTTPS only
        samesite="lax",     # CSRF protection
        max_age=1800        # 30 minutes
    )
    
    return {"message": "Logged in successfully"}
```

### Alternative: Session Storage (Better than localStorage)

```javascript
// Less persistent than localStorage
// Cleared when tab closes
sessionStorage.setItem('token', token);  // ⚠️ Use with caution
```

## Token Revocation

### Implement Token Blacklist

```python
from datetime import datetime
import redis

# Redis for fast lookups
redis_client = redis.Redis(host='localhost', port=6379, db=0)

def revoke_token(jti: str, exp: int):
    """Add token to blacklist"""
    ttl = exp - int(datetime.now().timestamp())
    redis_client.setex(f"revoked:{jti}", ttl, "1")

def is_token_revoked(jti: str) -> bool:
    """Check if token is revoked"""
    return redis_client.exists(f"revoked:{jti}") > 0
```

### Validate Against Blacklist

```python
async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Check revocation
        if "jti" in payload and is_token_revoked(payload["jti"]):
            raise HTTPException(
                status_code=401,
                detail="Token has been revoked"
            )
        
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

## Refresh Token Rotation

### Implement Token Rotation (RFC 9700)

```python
@app.post("/token/refresh")
async def refresh_token(
    old_refresh_token: str,
    db: Session = Depends(get_db)
):
    # Validate old token
    user_id = validate_refresh_token(old_refresh_token)
    
    # Revoke old refresh token
    revoke_refresh_token(old_refresh_token)
    
    # Create new tokens
    new_access_token = create_access_token({"sub": user_id})
    new_refresh_token = create_refresh_token({"sub": user_id})
    
    # Store new refresh token
    store_refresh_token(new_refresh_token, user_id)
    
    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token
    }
```

## Security Headers

### Extract Token from Header

```python
from fastapi import Header, HTTPException

async def get_token_from_header(authorization: str = Header(None)):
    """Extract Bearer token from Authorization header"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")
    
    scheme, _, token = authorization.partition(" ")
    
    if scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid authentication scheme")
    
    if not token:
        raise HTTPException(status_code=401, detail="Missing token")
    
    return token
```

## Common Vulnerabilities

### 1. Algorithm Confusion Attack

**Vulnerability:**
```python
# ❌ Accepts any algorithm
payload = jwt.decode(token, secret)  # DON'T DO THIS
```

**Fix:**
```python
# ✅ Explicitly specify allowed algorithms
payload = jwt.decode(token, secret, algorithms=["RS256"])
```

### 2. Missing Expiration Check

**Vulnerability:**
```python
# ❌ Ignores expiration
payload = jwt.decode(token, secret, options={"verify_exp": False})
```

**Fix:**
```python
# ✅ Always verify expiration
payload = jwt.decode(token, secret, options={"verify_exp": True})
```

### 3. Weak Secret Key

**Vulnerability:**
```python
# ❌ Weak secret
SECRET_KEY = "secret"
```

**Fix:**
```python
# ✅ Strong, random secret (32+ bytes)
import secrets
SECRET_KEY = secrets.token_urlsafe(32)
```

### 4. No Audience Validation

**Vulnerability:**
```python
# ❌ Accepts token for any audience
payload = jwt.decode(token, secret)
```

**Fix:**
```python
# ✅ Validate audience
payload = jwt.decode(token, secret, audience="your-api-identifier")
```

## Testing

### Unit Test Example

```python
import pytest
from datetime import datetime, timedelta, timezone
import jwt

def test_token_expiration():
    # Create expired token
    expired_payload = {
        "sub": "user123",
        "exp": datetime.now(timezone.utc) - timedelta(minutes=1)
    }
    expired_token = jwt.encode(expired_payload, SECRET_KEY, algorithm="HS256")
    
    # Should raise ExpiredSignatureError
    with pytest.raises(jwt.ExpiredSignatureError):
        jwt.decode(expired_token, SECRET_KEY, algorithms=["HS256"])

def test_invalid_signature():
    valid_token = create_access_token({"sub": "user123"})
    
    # Modify token
    tampered_token = valid_token[:-10] + "tampered123"
    
    # Should raise InvalidSignatureError
    with pytest.raises(jwt.InvalidSignatureError):
        jwt.decode(tampered_token, SECRET_KEY, algorithms=["HS256"])
```

## Monitoring

### Log Token Events

```python
import logging

logger = logging.getLogger(__name__)

def validate_token_with_logging(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        logger.info(f"Token validated for user: {payload.get('sub')}")
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning(f"Expired token attempted")
        raise
    except jwt.InvalidTokenError as e:
        logger.error(f"Invalid token: {str(e)}")
        raise
```

## Production Checklist

- [ ] Using RS256 or strong HS256 (32+ byte secret)
- [ ] Access token expiration ≤ 60 minutes
- [ ] All required claims present (iss, sub, aud, exp, iat)
- [ ] Audience validation enabled
- [ ] Issuer validation enabled
- [ ] Signature verification enabled
- [ ] Tokens stored in httpOnly cookies
- [ ] Refresh token rotation implemented
- [ ] Token revocation system in place
- [ ] Logging for authentication events
- [ ] Rate limiting on token endpoints
- [ ] HTTPS enforced in production
