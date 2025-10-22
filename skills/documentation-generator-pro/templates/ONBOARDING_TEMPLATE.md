# Developer Onboarding Guide

Welcome to the team! This guide will help you get set up and productive.

## 📋 Prerequisites

Before you begin, ensure you have:

- [ ] Access to GitHub repository
- [ ] Development machine setup (Mac/Linux/Windows)
- [ ] Required accounts (Slack, Email, etc.)
- [ ] Development tools installed (see below)

## 🛠️ Required Tools

### Essential

- **Git** (version 2.30+)
  ```bash
  git --version
  ```
  
- **Node.js** (version 14+) or **Python** (version 3.8+)
  ```bash
  node --version
  python --version
  ```

- **Code Editor** - Recommended: VS Code
  - [Download VS Code](https://code.visualstudio.com/)
  - Install recommended extensions (see `.vscode/extensions.json`)

### Optional but Recommended

- **Docker** - For containerized development
- **Postman** - For API testing
- **Terminal** - iTerm2 (Mac), Windows Terminal (Windows)

## ⚙️ Environment Setup

### 1. Clone the Repository

```bash
git clone https://github.com/organization/project.git
cd project
```

### 2. Install Dependencies

**For Node.js projects:**
```bash
npm install
```

**For Python projects:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure Environment

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` and add your credentials:

```bash
# Database
DATABASE_URL=postgresql://localhost:5432/mydb

# API Keys
API_KEY=your-api-key-here
SECRET_KEY=your-secret-key-here

# Feature Flags
FEATURE_NEW_UI=true
```

**Where to get credentials:**
- Database URL: Ask DevOps team or use local PostgreSQL
- API Keys: Generate in [Admin Panel](https://admin.example.com)
- Secret Key: Generate with `openssl rand -hex 32`

### 4. Set Up Database

```bash
# Create database
npm run db:create

# Run migrations
npm run db:migrate

# Seed with sample data
npm run db:seed
```

### 5. Verify Setup

Run the test suite to verify everything works:

```bash
npm test
```

Expected output: All tests passing ✅

## 🚀 Running the Application

### Development Mode

```bash
npm run dev
```

The application will start at `http://localhost:3000`

**Available endpoints:**
- Main app: http://localhost:3000
- API docs: http://localhost:3000/api/docs
- Health check: http://localhost:3000/health

### Production Build

```bash
npm run build
npm start
```

## 🏗️ Project Structure

```
project/
├── src/                    # Source code
│   ├── api/               # API routes
│   ├── models/            # Data models
│   ├── services/          # Business logic
│   ├── utils/             # Utility functions
│   └── tests/             # Test files
├── docs/                  # Documentation
├── scripts/               # Build and deployment scripts
├── .env.example           # Environment template
├── package.json           # Dependencies
└── README.md              # Project overview
```

### Key Directories

- **`src/api/`** - REST API endpoints
- **`src/services/`** - Core business logic (where most work happens)
- **`src/models/`** - Database schemas and ORM models
- **`src/tests/`** - Unit and integration tests

## 💼 Development Workflow

### 1. Pick a Task

- Check the [Project Board](https://github.com/organization/project/projects)
- Assign yourself to an issue
- Move it to "In Progress"

### 2. Create a Branch

```bash
git checkout -b feature/your-feature-name
```

**Branch naming convention:**
- `feature/` - New features
- `bugfix/` - Bug fixes
- `hotfix/` - Urgent production fixes
- `refactor/` - Code refactoring

### 3. Make Changes

- Write code
- Add tests
- Run linter: `npm run lint`
- Run tests: `npm test`

### 4. Commit Your Work

```bash
git add .
git commit -m "feat: add user authentication"
```

**Commit message format:**
```
type(scope): description

[optional body]

[optional footer]
```

**Types:** feat, fix, docs, style, refactor, test, chore

### 5. Push and Create PR

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub:

- Use the PR template
- Add description and screenshots
- Request reviewers
- Link related issues

### 6. Code Review

- Address review comments
- Push updates
- Get approval
- Merge when ready

## 🧪 Testing

### Running Tests

```bash
# All tests
npm test

# Specific test file
npm test -- path/to/test.js

# With coverage
npm run test:coverage

# Watch mode
npm run test:watch
```

### Writing Tests

Place test files next to the code they test:

```
src/
  services/
    userService.js
    userService.test.js
```

Example test:

```javascript
describe('UserService', () => {
  it('should create a new user', async () => {
    const user = await userService.create({
      email: 'test@example.com',
      name: 'Test User'
    });
    
    expect(user).toBeDefined();
    expect(user.email).toBe('test@example.com');
  });
});
```

## 📝 Code Style

We use ESLint and Prettier for code formatting.

### Auto-format on Save

VS Code settings:

```json
{
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": true
  }
}
```

### Manual Formatting

```bash
# Check for issues
npm run lint

# Auto-fix issues
npm run lint:fix

# Format code
npm run format
```

## 🐛 Debugging

### VS Code Debugging

Launch configuration is in `.vscode/launch.json`

**To debug:**
1. Set breakpoints in code
2. Press F5 or click "Start Debugging"
3. Use debug console to inspect variables

### Console Debugging

Add logging:

```javascript
console.log('Debug:', variable);
console.error('Error:', error);
```

Use the debug logger:

```javascript
const debug = require('debug')('app:service');
debug('Processing request', { id: 123 });
```

Enable debug logs:

```bash
DEBUG=app:* npm run dev
```

## 📚 Additional Resources

### Documentation

- [Architecture Overview](docs/architecture.md)
- [API Reference](docs/api/reference.md)
- [Database Schema](docs/database.md)
- [Deployment Guide](docs/deployment.md)

### Team Resources

- [Team Wiki](https://wiki.company.com)
- [Slack Channels](https://company.slack.com):
  - #dev-general - General development
  - #dev-backend - Backend discussions
  - #dev-frontend - Frontend discussions
  - #dev-help - Ask for help
- [Jira Board](https://company.atlassian.net)

### Learning Materials

- [Company Engineering Blog](https://blog.company.com)
- [Recommended Courses](docs/learning.md)
- [Best Practices](docs/best-practices.md)

## ❓ Common Issues

### Issue: Port already in use

**Error:** `EADDRINUSE: address already in use :::3000`

**Solution:**
```bash
# Find process using port 3000
lsof -ti:3000

# Kill the process
kill -9 $(lsof -ti:3000)
```

### Issue: Database connection failed

**Error:** `Connection refused`

**Solution:**
1. Check if database is running: `pg_isready` (PostgreSQL)
2. Verify DATABASE_URL in `.env`
3. Restart database: `npm run db:restart`

### Issue: Module not found

**Error:** `Cannot find module 'xyz'`

**Solution:**
```bash
# Clean install
rm -rf node_modules package-lock.json
npm install
```

### Issue: Tests failing

**Solution:**
1. Ensure test database is seeded: `npm run db:seed:test`
2. Clear test cache: `npm run test:clear-cache`
3. Run tests individually to isolate issue

## 🎯 Your First Task

Ready to contribute? Here's a good first issue:

1. Go to [GitHub Issues](https://github.com/organization/project/issues)
2. Filter by label: `good-first-issue`
3. Pick one and assign yourself
4. Follow the development workflow above

**Suggested first tasks:**
- Add a new API endpoint
- Write tests for existing code
- Fix a bug
- Improve documentation

## 🤝 Getting Help

Don't hesitate to ask for help!

- **Quick questions:** #dev-help on Slack
- **Code review:** Tag `@team` in PR
- **Bugs:** Create GitHub issue
- **Onboarding questions:** Ask your mentor

**Your mentor:** [Mentor Name] (@mentor on Slack)

## ✅ Onboarding Checklist

Complete these tasks in your first week:

- [ ] Set up development environment
- [ ] Run the application locally
- [ ] Read the architecture documentation
- [ ] Complete a good-first-issue
- [ ] Submit your first PR
- [ ] Attend team standup
- [ ] Introduce yourself in #dev-general

## 🎉 Welcome!

You're all set! Don't worry if it feels overwhelming at first - everyone goes through this. The team is here to help you succeed.

**Tips for success:**
- Ask questions early and often
- Document what you learn
- Share knowledge with the team
- Take breaks and maintain work-life balance

Happy coding! 🚀

---

**Questions?** Contact your mentor or ask in #dev-help on Slack.
