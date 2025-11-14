# Streamlit Built-in OIDC Authentication

Complete guide for using Streamlit's native OIDC support (version 1.42+).

## Prerequisites

- Streamlit >= 1.42.0
- OAuth 2.0 client configured with identity provider

## Configuration

### secrets.toml Structure

Create `.streamlit/secrets.toml`:

```toml
[auth]
redirect_uri = "http://localhost:8501/oauth2callback"
cookie_secret = "your-random-secret-here-32-chars-minimum"

# Single provider example (Google)
[auth.google]
client_id = "your-client-id.apps.googleusercontent.com"
client_secret = "your-client-secret"
server_metadata_url = "https://accounts.google.com/.well-known/openid-configuration"

# Multiple providers
[auth.microsoft]
client_id = "your-microsoft-client-id"
client_secret = "your-microsoft-client-secret"
server_metadata_url = "https://login.microsoftonline.com/{tenant}/v2.0/.well-known/openid-configuration"

[auth.auth0]
client_id = "your-auth0-client-id"
client_secret = "your-auth0-client-secret"
server_metadata_url = "https://your-domain.auth0.com/.well-known/openid-configuration"
```

### Generate Cookie Secret

```python
import secrets
cookie_secret = secrets.token_urlsafe(32)
print(f"cookie_secret = \"{cookie_secret}\"")
```

## Basic Implementation

### Simple Login/Logout

```python
import streamlit as st

# Check if user is logged in
if not st.user.is_logged_in:
    st.write("Please log in to continue")
    
    if st.button("Log in with Google"):
        st.login("google")  # Provider name from secrets.toml
    
    st.stop()  # Stop execution if not logged in

# User is authenticated
st.write(f"Welcome, {st.user.name}!")
st.write(f"Email: {st.user.email}")

if st.button("Log out"):
    st.logout()
```

### Multiple Provider Support

```python
import streamlit as st

if not st.user.is_logged_in:
    st.write("## Choose your login method")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔵 Google", use_container_width=True):
            st.login("google")
    
    with col2:
        if st.button("🔷 Microsoft", use_container_width=True):
            st.login("microsoft")
    
    with col3:
        if st.button("🔶 Auth0", use_container_width=True):
            st.login("auth0")
    
    st.stop()

# Show user info
st.success(f"Logged in as {st.user.name}")

# Logout button in sidebar
with st.sidebar:
    if st.button("🚪 Log out"):
        st.logout()
```

## Accessing User Information

### Available User Attributes

```python
if st.user.is_logged_in:
    # Basic info
    st.write("User ID (sub):", st.user.id)
    st.write("Name:", st.user.name)
    st.write("Email:", st.user.email)
    st.write("Email Verified:", st.user.email_verified)
    
    # Picture/Avatar
    if st.user.picture:
        st.image(st.user.picture, width=100)
    
    # Raw token (for API calls)
    token = st.user.token
    st.write("Token available:", bool(token))
```

## Integration with FastAPI Backend

### Passing Token to Backend

```python
import streamlit as st
import requests

if st.user.is_logged_in:
    # Get JWT token
    token = st.user.token
    
    # Call protected FastAPI endpoint
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(
        "https://your-api.com/api/protected",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        st.json(data)
    else:
        st.error(f"API Error: {response.status_code}")
```

### Complete Integration Example

```python
import streamlit as st
import requests
from typing import Optional

# Configuration
API_BASE_URL = "https://your-api.com/api"

def call_api(endpoint: str, method: str = "GET", data: Optional[dict] = None):
    """Make authenticated API call"""
    if not st.user.is_logged_in:
        st.error("Please log in first")
        return None
    
    headers = {
        "Authorization": f"Bearer {st.user.token}",
        "Content-Type": "application/json"
    }
    
    url = f"{API_BASE_URL}/{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data)
        elif method == "PUT":
            response = requests.put(url, headers=headers, json=data)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers)
        
        response.raise_for_status()
        return response.json()
    
    except requests.exceptions.HTTPError as e:
        st.error(f"API Error: {e}")
        return None

# Main app
st.title("My Secure App")

if not st.user.is_logged_in:
    if st.button("Log in"):
        st.login("google")
    st.stop()

# Fetch user data from backend
user_data = call_api("users/me")
if user_data:
    st.json(user_data)

# Create new resource
with st.form("create_form"):
    name = st.text_input("Name")
    description = st.text_area("Description")
    
    if st.form_submit_button("Create"):
        result = call_api(
            "resources",
            method="POST",
            data={"name": name, "description": description}
        )
        if result:
            st.success("Created successfully!")
```

## Session Management

### Session Persistence

```python
import streamlit as st
from datetime import datetime

# Initialize session state
if "login_time" not in st.session_state:
    st.session_state.login_time = None

if st.user.is_logged_in:
    # Record login time
    if st.session_state.login_time is None:
        st.session_state.login_time = datetime.now()
    
    # Show session duration
    duration = datetime.now() - st.session_state.login_time
    st.sidebar.write(f"Session: {duration.seconds // 60} minutes")
else:
    st.session_state.login_time = None
```

### Auto-Logout on Inactivity

```python
import streamlit as st
from datetime import datetime, timedelta

# Session timeout (30 minutes)
SESSION_TIMEOUT = timedelta(minutes=30)

if "last_activity" not in st.session_state:
    st.session_state.last_activity = datetime.now()

if st.user.is_logged_in:
    # Check for timeout
    if datetime.now() - st.session_state.last_activity > SESSION_TIMEOUT:
        st.warning("Session expired due to inactivity")
        st.logout()
        st.stop()
    
    # Update last activity
    st.session_state.last_activity = datetime.now()
```

## Role-Based Access

### Using Roles from Token

```python
import streamlit as st

def get_user_roles():
    """Extract roles from JWT token"""
    if not st.user.is_logged_in:
        return []
    
    # Roles might be in different claims depending on provider
    # Auth0: permissions or roles
    # Google: groups (if configured)
    # Custom: check your token structure
    
    # This is a placeholder - adjust based on your token structure
    return []  # Extract from token claims

def require_role(role: str):
    """Decorator-like function to require specific role"""
    user_roles = get_user_roles()
    if role not in user_roles:
        st.error(f"This feature requires {role} role")
        st.stop()

# Usage
if st.user.is_logged_in:
    require_role("admin")
    st.write("Admin-only content")
```

## Production Configuration

### HTTPS Requirements

```toml
# Production secrets.toml
[auth]
redirect_uri = "https://your-app.com/oauth2callback"  # HTTPS!
cookie_secret = "production-secret-min-32-chars"

[auth.google]
client_id = "prod-client-id.apps.googleusercontent.com"
client_secret = "prod-client-secret"
server_metadata_url = "https://accounts.google.com/.well-known/openid-configuration"
```

### Deployment Considerations

1. **Environment Variables**: Use Streamlit Cloud secrets or env vars
2. **HTTPS**: Required in production
3. **Cookie Security**: Streamlit handles httpOnly, secure, SameSite automatically
4. **Token Refresh**: Handled automatically by Streamlit
5. **Multiple Instances**: Shared secret required for session persistence

## Troubleshooting

### Common Issues

**"Redirect URI mismatch"**
- Ensure redirect_uri in secrets.toml matches OAuth provider exactly
- Include port for local development
- Use HTTPS in production

**"Cookie not persisting"**
- Check browser allows cookies
- Verify cookie_secret is set
- Ensure consistent secret across deployments

**"Token not available"**
- Check st.user.is_logged_in before accessing st.user.token
- Verify provider returns access token (some only return ID token)

**"Multi-page apps lose authentication"**
- Streamlit automatically manages sessions across pages
- Ensure secrets.toml is in correct location (.streamlit/)
- Check all pages use same cookie_secret

## Provider-Specific Setup

### Google Cloud Console

1. Create OAuth 2.0 Client ID
2. Add authorized redirect URI: `http://localhost:8501/oauth2callback`
3. Production: `https://your-app.com/oauth2callback`
4. Copy client ID and secret to secrets.toml

### Auth0

1. Create Application (Regular Web Application)
2. Add Allowed Callback URLs: `http://localhost:8501/oauth2callback`
3. Add Allowed Logout URLs: `http://localhost:8501`
4. Copy Domain, Client ID, and Client Secret
5. Use `https://YOUR-DOMAIN.auth0.com/.well-known/openid-configuration`

### Azure AD

1. Register Application
2. Add Redirect URI: `http://localhost:8501/oauth2callback`
3. Create Client Secret
4. Note Tenant ID
5. Use: `https://login.microsoftonline.com/{tenant}/v2.0/.well-known/openid-configuration`

## Resources

- [Streamlit Auth Docs](https://docs.streamlit.io/develop/concepts/connections/authentication)
- [OpenID Connect Discovery](https://openid.net/specs/openid-connect-discovery-1_0.html)
- [OAuth 2.0 RFC 6749](https://datatracker.ietf.org/doc/html/rfc6749)
