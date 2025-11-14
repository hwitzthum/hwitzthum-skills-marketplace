# OAuth 2.0 Authentication Skill for FastAPI & Streamlit

## 🎉 Your Production-Ready Authentication Skill is Complete!

This comprehensive skill provides everything you need to implement secure, RFC 9700-compliant OAuth 2.0 and OpenID Connect authentication in your FastAPI and Streamlit applications.

## 📦 What's Included

### Core Documentation
- **SKILL.md** - Main guide with quick start workflows and security principles
- **FastAPI Patterns** - Complete implementation patterns including Auth0, custom JWT, RBAC
- **Streamlit Built-in OIDC** - Full guide for Streamlit 1.42+ native authentication
- **JWT Best Practices** - Comprehensive security guide compliant with RFC 9700

### Utility Scripts
- **generate_secret_key.py** - Generate cryptographically secure keys for JWT and sessions
- **generate_pkce.py** - Generate PKCE parameters (mandatory as of RFC 9700)
- **validate_jwt.py** - Test and debug JWT token validation

### Configuration Templates
- **auth0-config-template.json** - Auth0 application configuration
- **env-template.txt** - Environment variables template for all settings

## 🚀 Key Features

### RFC 9700 Compliant (January 2025)
- ✅ Mandatory PKCE for all OAuth clients
- ✅ Authorization Code Flow (Implicit Grant deprecated)
- ✅ Short-lived access tokens (15-60 minutes)
- ✅ Refresh token rotation
- ✅ Strict redirect URI validation
- ✅ Token replay prevention

### Production-Ready Patterns
- Complete FastAPI + Auth0 integration
- Custom JWT with PostgreSQL/SQLAlchemy
- Role-Based Access Control (RBAC)
- Refresh token implementation with rotation
- Security middleware (CORS, rate limiting, headers)
- Streamlit native OIDC support (v1.42+)
- Full-stack integration examples

### Security First
- HTTPS enforcement
- httpOnly cookies for token storage
- Token revocation and blacklisting
- JWT signature validation
- Comprehensive error handling
- Security headers middleware
- Rate limiting on authentication endpoints

## 📖 How to Use This Skill

### For New Projects

1. **Upload the skill** to Claude
2. **Tell Claude what you're building**:
   - "I'm building a FastAPI backend with Auth0 authentication"
   - "I need to add authentication to my Streamlit app"
   - "Help me implement secure login for my FastAPI + Streamlit application"

3. **Claude will automatically**:
   - Read the relevant parts of the skill
   - Provide code examples
   - Guide you through configuration
   - Help you avoid common security mistakes

### For Existing Projects

Tell Claude:
- "I need to add OAuth 2.0 authentication to my existing FastAPI app"
- "Help me secure my Streamlit app with Google login"
- "I want to implement RBAC in my FastAPI application"

Claude will use the skill to provide RFC 9700-compliant solutions.

## 🎯 Quick Start Examples

### Example 1: FastAPI with Auth0

```
You: "Help me add Auth0 authentication to my FastAPI app. 
     I need to protect my API endpoints."

Claude will:
1. Reference the FastAPI patterns from the skill
2. Show you how to set up Auth0 configuration
3. Provide complete working code
4. Explain security best practices
```

### Example 2: Streamlit Login

```
You: "I want to add Google login to my Streamlit app using 
     the built-in OIDC support."

Claude will:
1. Reference the Streamlit OIDC guide from the skill
2. Show you how to configure secrets.toml
3. Provide the login/logout flow code
4. Explain how to integrate with your FastAPI backend
```

### Example 3: Complete Full-Stack

```
You: "I'm building a FastAPI backend and Streamlit frontend. 
     Users should log in with Auth0 on Streamlit, then access 
     protected API endpoints. How do I implement this?"

Claude will:
1. Walk you through the complete integration
2. Show both FastAPI and Streamlit code
3. Explain token passing between frontend and backend
4. Provide security checklist
```

## 🔧 Using the Utility Scripts

### Generate Secure Keys

```bash
# Generate JWT secret key
python scripts/generate_secret_key.py --length 32 --format hex

# Generate cookie secret
python scripts/generate_secret_key.py --length 32 --format url
```

### Generate PKCE Parameters

```bash
# Generate PKCE code verifier and challenge
python scripts/generate_pkce.py

# Multiple pairs for testing
python scripts/generate_pkce.py --count 3
```

### Validate JWT Tokens

```bash
# Validate with secret key
python scripts/validate_jwt.py \
  --token YOUR_TOKEN \
  --secret YOUR_SECRET \
  --issuer https://your-domain.auth0.com/ \
  --audience your-api-identifier

# Decode without validation (inspect only)
python scripts/validate_jwt.py --token YOUR_TOKEN --no-verify
```

## 🎨 What Makes This Skill Special

### 1. RFC 9700 Compliant
This skill implements the latest OAuth 2.0 security standards published in January 2025, including:
- Mandatory PKCE for all clients
- Deprecated Implicit Grant
- Strict security requirements
- Token rotation best practices

### 2. Production-Ready Code
All examples are:
- Fully functional and tested
- Include error handling
- Follow security best practices
- Production deployment ready

### 3. Comprehensive Coverage
From basic JWT to complex:
- Multi-provider OAuth
- Role-based access control
- Token refresh and rotation
- Full-stack integration

### 4. Security Focused
Every pattern includes:
- Security checklists
- Common vulnerabilities to avoid
- Best practices from RFC 9700
- Production deployment guides

## 📚 Reference Documentation Structure

The skill uses progressive disclosure:

**Level 1: SKILL.md (Always loaded)**
- Quick start workflows
- Core security principles
- Basic implementation examples
- References to detailed docs

**Level 2: Reference Files (Loaded when needed)**
- `fastapi-patterns.md` - Detailed FastAPI implementations
- `streamlit-builtin-oidc.md` - Streamlit OIDC complete guide
- `jwt-best-practices.md` - JWT security deep dive

**Level 3: Assets (Used as templates)**
- Configuration templates
- Environment variable examples
- Provider-specific setup

## 🔐 Security Standards Implemented

### MUST Requirements (RFC 9700)
- ✅ PKCE for all OAuth clients
- ✅ Authorization Code Flow only
- ✅ Strict redirect URI validation
- ✅ HTTPS in production
- ✅ Short-lived access tokens
- ✅ Token signature validation

### SHOULD Requirements
- ✅ Refresh token rotation
- ✅ Token revocation support
- ✅ Audience validation
- ✅ Issuer validation
- ✅ Rate limiting
- ✅ Security headers

### Best Practices
- ✅ httpOnly cookies
- ✅ CSRF protection
- ✅ Error handling without leaks
- ✅ Comprehensive logging
- ✅ Environment variable secrets
- ✅ Database-backed user management

## 🆘 Common Questions

**Q: Do I need to read all the documentation?**
A: No! Just tell Claude what you're trying to do. Claude will read the relevant parts of the skill automatically.

**Q: Can I use this with providers other than Auth0?**
A: Yes! The skill includes patterns for Auth0, Google, Microsoft Azure AD, and custom JWT implementations.

**Q: Is this suitable for production?**
A: Yes! All code follows RFC 9700 best practices and includes security checklists for production deployment.

**Q: What if I have an existing authentication system?**
A: Claude can help you migrate to RFC 9700-compliant patterns while maintaining your existing user database.

**Q: Do I need both FastAPI and Streamlit?**
A: No! Use just the parts you need. The skill covers:
- FastAPI only (API authentication)
- Streamlit only (Web app authentication)  
- FastAPI + Streamlit (Full-stack)

## 🎓 Learning Resources

The skill references these authoritative sources:
- RFC 9700: OAuth 2.0 Security Best Current Practice (January 2025)
- RFC 7636: Proof Key for Code Exchange (PKCE)
- RFC 6749: OAuth 2.0 Authorization Framework
- OpenID Connect Core Specification

## 💡 Pro Tips

1. **Start Simple**: Begin with basic JWT or single-provider OAuth
2. **Use Scripts**: The utility scripts save time and prevent errors
3. **Test Locally**: Use localhost URLs during development
4. **Check Security**: Run through security checklists before deployment
5. **Monitor Tokens**: Implement logging for authentication events
6. **Rotate Keys**: Regularly rotate JWT secret keys in production

## 📞 Getting Help

When asking Claude for help:

**Good:**
- "Help me implement Auth0 login for my Streamlit app"
- "I'm getting a 'redirect URI mismatch' error with Google OAuth"
- "Show me how to add RBAC to my FastAPI endpoints"

**Better:**
- Include error messages
- Specify your provider (Auth0, Google, etc.)
- Mention if you're using FastAPI, Streamlit, or both
- Say if you're in development or production

## 🎉 You're All Set!

This skill contains everything you need for production-ready authentication. Claude will automatically use it when you discuss authentication, OAuth, JWT, or security topics.

Just upload the skill file and start building secure applications!

---

**Questions or Issues?**
The skill includes troubleshooting guides and common solutions. Just ask Claude:
- "I'm having trouble with [specific issue]"
- "How do I configure [specific provider]?"
- "What's the best practice for [specific scenario]?"

**Happy Building! 🚀**
