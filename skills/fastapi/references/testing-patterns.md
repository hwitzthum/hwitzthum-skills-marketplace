# FastAPI Testing Patterns

Complete guide for testing FastAPI applications with pytest, covering unit tests, integration tests, async testing, database testing, and authentication testing.

## Overview

This reference provides patterns for:
- Unit testing endpoints
- Integration testing with databases
- Async testing
- Testing authentication and authorization
- Mocking dependencies
- Test fixtures and setup
- Coverage and continuous integration

## Dependencies

```bash
pip install pytest pytest-asyncio httpx
pip install pytest-cov  # For coverage
pip install faker       # For generating test data
```

## Basic Testing Setup

### Test Client

```python
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_read_main():
    """Test basic endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}
```

### Project Structure

```
tests/
├── __init__.py
├── conftest.py          # Shared fixtures
├── test_users.py        # User endpoint tests
├── test_items.py        # Item endpoint tests
├── test_auth.py         # Authentication tests
└── integration/
    └── test_workflows.py # Integration tests
```

## Testing with Database

### Test Database Setup

```python
# tests/conftest.py
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from typing import AsyncGenerator

from app.database import Base
from app.main import app, get_db

# Use in-memory SQLite for tests
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

@pytest_asyncio.fixture
async def test_engine():
    """Create test database engine."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()

@pytest_asyncio.fixture
async def test_db(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create test database session."""
    async_session = sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session

@pytest.fixture
def override_get_db(test_db):
    """Override database dependency."""
    async def _get_test_db():
        yield test_db
    
    app.dependency_overrides[get_db] = _get_test_db
    yield
    app.dependency_overrides.clear()

@pytest.fixture
def client(override_get_db):
    """Create test client with overridden dependencies."""
    return TestClient(app)
```

### Database Tests

```python
# tests/test_users.py
import pytest
from fastapi import status

def test_create_user(client):
    """Test user creation."""
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "password123"
    }
    
    response = client.post("/users/", json=user_data)
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["username"] == user_data["username"]
    assert data["email"] == user_data["email"]
    assert "id" in data
    assert "password" not in data  # Password should not be returned

def test_get_user(client):
    """Test getting user by ID."""
    # Create user first
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "password123"
    }
    create_response = client.post("/users/", json=user_data)
    user_id = create_response.json()["id"]
    
    # Get user
    response = client.get(f"/users/{user_id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == user_data["username"]

def test_get_nonexistent_user(client):
    """Test getting non-existent user returns 404."""
    response = client.get("/users/9999")
    assert response.status_code == 404

def test_list_users(client):
    """Test listing users with pagination."""
    # Create multiple users
    for i in range(5):
        client.post("/users/", json={
            "username": f"user{i}",
            "email": f"user{i}@example.com",
            "password": "password123"
        })
    
    # List users
    response = client.get("/users/?skip=0&limit=3")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3

def test_update_user(client):
    """Test updating user."""
    # Create user
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "password123"
    }
    create_response = client.post("/users/", json=user_data)
    user_id = create_response.json()["id"]
    
    # Update user
    update_data = {"full_name": "Test User"}
    response = client.patch(f"/users/{user_id}", json=update_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["full_name"] == update_data["full_name"]

def test_delete_user(client):
    """Test deleting user."""
    # Create user
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "password123"
    }
    create_response = client.post("/users/", json=user_data)
    user_id = create_response.json()["id"]
    
    # Delete user
    response = client.delete(f"/users/{user_id}")
    assert response.status_code == 204
    
    # Verify user is deleted
    get_response = client.get(f"/users/{user_id}")
    assert get_response.status_code == 404
```

## Testing Authentication

### Auth Fixtures

```python
# tests/conftest.py (continued)
from app.core.security import create_access_token

@pytest.fixture
def test_user_data():
    """Test user data."""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "password123"
    }

@pytest.fixture
def test_user(client, test_user_data):
    """Create test user and return user data."""
    response = client.post("/users/", json=test_user_data)
    return response.json()

@pytest.fixture
def test_user_token(test_user):
    """Generate access token for test user."""
    token = create_access_token(data={"sub": test_user["username"]})
    return token

@pytest.fixture
def auth_headers(test_user_token):
    """Authorization headers with test user token."""
    return {"Authorization": f"Bearer {test_user_token}"}
```

### Authentication Tests

```python
# tests/test_auth.py
def test_login_success(client, test_user_data):
    """Test successful login."""
    # Create user first
    client.post("/users/", json=test_user_data)
    
    # Login
    response = client.post(
        "/token",
        data={
            "username": test_user_data["username"],
            "password": test_user_data["password"]
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_invalid_credentials(client):
    """Test login with invalid credentials."""
    response = client.post(
        "/token",
        data={
            "username": "nonexistent",
            "password": "wrongpassword"
        }
    )
    
    assert response.status_code == 401

def test_access_protected_endpoint(client, auth_headers):
    """Test accessing protected endpoint with valid token."""
    response = client.get("/users/me", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert "username" in data

def test_access_protected_endpoint_no_token(client):
    """Test accessing protected endpoint without token."""
    response = client.get("/users/me")
    
    assert response.status_code == 401

def test_access_protected_endpoint_invalid_token(client):
    """Test accessing protected endpoint with invalid token."""
    response = client.get(
        "/users/me",
        headers={"Authorization": "Bearer invalidtoken"}
    )
    
    assert response.status_code == 401
```

## Async Testing

### Async Test Setup

```python
import pytest
import pytest_asyncio
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_async_endpoint():
    """Test async endpoint."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/async-endpoint")
    
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_create_user_async(test_db):
    """Test async database operation."""
    from app.crud import create_user
    from app.schemas import UserCreate
    
    user_in = UserCreate(
        username="testuser",
        email="test@example.com",
        password="password123"
    )
    
    user = await create_user(test_db, user_in)
    
    assert user.username == user_in.username
    assert user.email == user_in.email
```

## Mocking Dependencies

### Mocking External Services

```python
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_external_api_call():
    """Test endpoint that calls external API."""
    mock_response = {"data": "mocked"}
    
    with patch('httpx.AsyncClient.get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value.json.return_value = mock_response
        
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get("/external-data")
        
        assert response.json() == mock_response

def test_with_mocked_dependency(client):
    """Test with mocked dependency."""
    # Mock a dependency
    def mock_get_current_user():
        return {"username": "mockuser", "id": 1}
    
    app.dependency_overrides[get_current_user] = mock_get_current_user
    
    response = client.get("/users/me")
    
    assert response.status_code == 200
    assert response.json()["username"] == "mockuser"
    
    # Clean up
    app.dependency_overrides.clear()
```

## Test Data Generation

### Using Faker

```python
from faker import Faker

fake = Faker()

@pytest.fixture
def random_user_data():
    """Generate random user data."""
    return {
        "username": fake.user_name(),
        "email": fake.email(),
        "password": fake.password(),
        "full_name": fake.name()
    }

def test_create_multiple_users(client):
    """Test creating multiple users with random data."""
    for _ in range(10):
        user_data = {
            "username": fake.user_name(),
            "email": fake.email(),
            "password": fake.password()
        }
        response = client.post("/users/", json=user_data)
        assert response.status_code == 201
```

### Factory Pattern

```python
# tests/factories.py
from app.models import User
from app.core.security import get_password_hash

class UserFactory:
    @staticmethod
    def create(db, **kwargs):
        """Create user with default or custom values."""
        defaults = {
            "username": "testuser",
            "email": "test@example.com",
            "hashed_password": get_password_hash("password123"),
            "is_active": True
        }
        defaults.update(kwargs)
        
        user = User(**defaults)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    
    @staticmethod
    async def create_async(db, **kwargs):
        """Create user asynchronously."""
        defaults = {
            "username": "testuser",
            "email": "test@example.com",
            "hashed_password": get_password_hash("password123"),
            "is_active": True
        }
        defaults.update(kwargs)
        
        user = User(**defaults)
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

# Usage
@pytest.mark.asyncio
async def test_with_factory(test_db):
    user = await UserFactory.create_async(
        test_db,
        username="customuser",
        email="custom@example.com"
    )
    assert user.username == "customuser"
```

## Integration Testing

### Testing Complete Workflows

```python
# tests/integration/test_workflows.py
def test_complete_user_workflow(client):
    """Test complete user lifecycle."""
    # 1. Register user
    user_data = {
        "username": "workflowuser",
        "email": "workflow@example.com",
        "password": "password123"
    }
    register_response = client.post("/users/", json=user_data)
    assert register_response.status_code == 201
    user = register_response.json()
    
    # 2. Login
    login_response = client.post(
        "/token",
        data={"username": user_data["username"], "password": user_data["password"]}
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 3. Access protected resource
    me_response = client.get("/users/me", headers=headers)
    assert me_response.status_code == 200
    assert me_response.json()["username"] == user_data["username"]
    
    # 4. Create item
    item_data = {"title": "Test Item", "description": "Test Description"}
    item_response = client.post("/items/", json=item_data, headers=headers)
    assert item_response.status_code == 201
    
    # 5. Get user's items
    items_response = client.get("/users/me/items", headers=headers)
    assert items_response.status_code == 200
    assert len(items_response.json()) == 1
    
    # 6. Update profile
    update_data = {"full_name": "Workflow User"}
    update_response = client.patch(
        f"/users/{user['id']}",
        json=update_data,
        headers=headers
    )
    assert update_response.status_code == 200
    
    # 7. Delete account
    delete_response = client.delete(f"/users/{user['id']}", headers=headers)
    assert delete_response.status_code == 204
```

## Performance Testing

### Load Testing Setup

```python
# tests/test_performance.py
import time

def test_endpoint_performance(client):
    """Test endpoint response time."""
    start_time = time.time()
    response = client.get("/users/")
    end_time = time.time()
    
    assert response.status_code == 200
    assert end_time - start_time < 1.0  # Should respond in less than 1 second

def test_bulk_operations(client):
    """Test bulk user creation performance."""
    users = [
        {
            "username": f"user{i}",
            "email": f"user{i}@example.com",
            "password": "password123"
        }
        for i in range(100)
    ]
    
    start_time = time.time()
    for user in users:
        client.post("/users/", json=user)
    end_time = time.time()
    
    assert end_time - start_time < 10.0  # Should complete in less than 10 seconds
```

## Test Coverage

### Running Tests with Coverage

```bash
# Run all tests with coverage
pytest --cov=app --cov-report=html --cov-report=term

# Run specific test file
pytest tests/test_users.py -v

# Run tests matching pattern
pytest -k "test_create" -v

# Run with markers
pytest -m "slow" -v
```

### Coverage Configuration

```ini
# setup.cfg or pytest.ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
markers =
    slow: marks tests as slow
    integration: marks tests as integration tests

[coverage:run]
source = app
omit =
    */tests/*
    */migrations/*
    */__init__.py

[coverage:report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
    if __name__ == .__main__.:
```

## CI/CD Integration

### GitHub Actions Example

```yaml
# .github/workflows/tests.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_USER: testuser
          POSTGRES_PASSWORD: testpass
          POSTGRES_DB: testdb
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install pytest pytest-asyncio pytest-cov
      
      - name: Run tests
        env:
          DATABASE_URL: postgresql://testuser:testpass@localhost:5432/testdb
        run: |
          pytest --cov=app --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
```

## Best Practices

1. **Isolate Tests**: Each test should be independent and not rely on others
2. **Use Fixtures**: Share setup code with fixtures
3. **Mock External Services**: Don't make real API calls in tests
4. **Test Edge Cases**: Test error conditions and boundary values
5. **Fast Tests**: Keep unit tests fast, separate slow integration tests
6. **Clear Assertions**: Use descriptive assertion messages
7. **Arrange-Act-Assert**: Follow AAA pattern for test structure
8. **Clean Database**: Reset database state between tests
9. **Coverage Goals**: Aim for >80% code coverage
10. **Continuous Testing**: Run tests automatically on every commit

This reference provides comprehensive testing patterns for FastAPI applications. Always maintain high test coverage and run tests in CI/CD pipelines before deployment.
