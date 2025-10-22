# Skill Description Guidelines

## Character Limit

**Maximum:** 200 characters  
**Recommended:** 150-180 characters

## Why This Matters

The description field is **critical** for skill discovery. Claude reads all skill descriptions at startup to determine which skills are relevant to the current task. A clear, concise description ensures your skill gets loaded when needed.

## Good Description Formula

```
[What it does] + [When to use it]
```

### Examples of Good Descriptions

✅ **Good (162 chars):**
```yaml
description: Generate API docs, architecture diagrams, onboarding guides, and tutorials from codebases. Use for documentation, README files, or architectural docs.
```

✅ **Good (178 chars):**
```yaml
description: Apply brand guidelines to presentations and documents including official colors, fonts, and logo usage. Use when creating external-facing materials.
```

✅ **Good (145 chars):**
```yaml
description: Analyze code for best practices, security issues, and performance. Use when reviewing PRs, auditing code, or checking quality.
```

### Examples of Bad Descriptions

❌ **Too Vague (58 chars):**
```yaml
description: Helps with documentation tasks for various projects.
```
*Problem: Not specific enough - when should this be used?*

❌ **Too Long (285 chars):**
```yaml
description: This is a comprehensive documentation generation skill that helps you create high-quality API documentation, system architecture diagrams, detailed onboarding guides for new team members, and interactive tutorials. It works with multiple programming languages and frameworks.
```
*Problem: Exceeds 200 character limit*

❌ **Too Generic (42 chars):**
```yaml
description: Documentation skill for Claude.
```
*Problem: What kind of documentation? When to use?*

## Writing Tips

### 1. Be Specific About "What"

Instead of:
- "Helps with coding" ❌
- "Documentation tool" ❌
- "Data processing" ❌

Use:
- "Generates TypeScript type definitions from JSON schemas" ✅
- "Creates API reference docs with examples and authentication details" ✅
- "Transforms CSV files into interactive charts and dashboards" ✅

### 2. Be Clear About "When"

Include trigger words:
- "Use when..."
- "Use for..."
- "Apply to..."

Examples:
- "Use when working with Excel files" ✅
- "Use for REST API development" ✅
- "Apply to external-facing materials" ✅

### 3. Include Key Technologies/Formats

Mention specific:
- File formats: `.xlsx`, `.pdf`, `.json`
- Technologies: `React`, `FastAPI`, `SQL`
- Domains: `API`, `database`, `frontend`

Example:
```yaml
description: Extract and transform data from Excel (.xlsx) files using pandas. Use for data analysis, reporting, and ETL pipelines.
```

### 4. Avoid Filler Words

Remove unnecessary words:
- "comprehensive" - rarely needed
- "high-quality" - implied
- "powerful" - subjective
- "amazing" - not useful

Before (192 chars):
```yaml
description: A comprehensive and powerful skill for generating high-quality documentation including amazing API docs, beautiful diagrams, and detailed guides for your projects.
```

After (158 chars):
```yaml
description: Generate API docs, architecture diagrams, and onboarding guides from codebases. Use for technical documentation, README files, or project wikis.
```

## Character Count Trick

Use this one-liner to check your description length:

```bash
echo "Your description here" | wc -c
```

Or in Python:

```python
desc = "Your description here"
print(f"Length: {len(desc)} chars")
```

## Testing Your Description

Ask yourself:
1. ✅ Does it clearly state WHAT the skill does?
2. ✅ Does it indicate WHEN to use it?
3. ✅ Would someone reading this know if it's relevant?
4. ✅ Is it under 200 characters?
5. ✅ Does it include key technologies/formats?

If you answer "no" to any of these, revise!

## Common Patterns

### For Document Skills
```
Create/edit/analyze [format] with [key features]. Use when working with [files/tasks].
```

Example:
```yaml
description: Create and edit PowerPoint presentations with charts, tables, and templates. Use when building slide decks or presentation materials.
```

### For Code Skills
```
[Action] [language/framework] code for [purpose]. Use when [scenario].
```

Example:
```yaml
description: Generate Python unit tests with pytest fixtures and mocks. Use when adding test coverage or practicing TDD.
```

### For Analysis Skills
```
Analyze [data type] to [outcome]. Use for [use case].
```

Example:
```yaml
description: Analyze log files to identify errors, performance issues, and anomalies. Use for debugging and system monitoring.
```

### For Workflow Skills
```
[Workflow name] following [standards/process]. Use when [trigger].
```

Example:
```yaml
description: Generate commit messages following Conventional Commits standard. Use when staging changes or writing commit history.
```

## Quick Reference Table

| Element | Example | Character Budget |
|---------|---------|------------------|
| Core action | "Generate API documentation" | 20-40 chars |
| Key features | "with examples and auth details" | 30-50 chars |
| Trigger | "Use when building REST APIs" | 25-40 chars |
| Technologies | "for FastAPI and Flask projects" | 20-40 chars |
| **Total** | | **150-180 chars** |

## Your Fixed Description

**Before (278 chars):**
```yaml
description: Comprehensive documentation generation skill for creating API docs, architecture diagrams, onboarding guides, and interactive tutorials from codebases. Use when users request documentation, guides, README files, API references, or architectural documentation for their projects.
```

**After (162 chars):**
```yaml
description: Generate API docs, architecture diagrams, onboarding guides, and tutorials from codebases. Use for documentation, README files, or architectural docs.
```

**Improvements:**
- ✅ Removed "comprehensive" and "skill for creating" (redundant)
- ✅ Shortened "interactive tutorials" to "tutorials"
- ✅ Condensed trigger conditions
- ✅ Kept all key information
- ✅ Under 200 character limit

---

**Remember:** The description is Claude's first encounter with your skill. Make it count! 🎯
