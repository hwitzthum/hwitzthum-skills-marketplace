# hwitzthum Skills Marketplace

A curated collection of high-quality Skills for Claude Code and Claude.ai to enhance your workflows.

## What are Skills?

Skills are folders containing instructions, scripts, and resources that Claude loads dynamically to improve performance on specialized tasks. Each skill teaches Claude how to complete specific tasks in a repeatable, consistent way.

## Available Skills

### 📚 Documentation Generator Pro
**Category:** Documentation  
**Version:** 1.0.0

Comprehensive documentation generation for codebases including API references, architecture diagrams, onboarding guides, and interactive tutorials.

**Use when you need:**
- API documentation or references
- Architecture diagrams
- Onboarding guides
- README files
- Code documentation

[View Details](skills/documentation-generator-pro/)

## Installation

### Quick Start

**Option 1: Install a specific skill to your project**
```bash
# Navigate to your project
cd your-project

# Create skills directory
mkdir -p .claude/skills

# Copy the skill you want
cp -r /path/to/hwitzthum-skills-marketplace/skills/documentation-generator-pro .claude/skills/
```

**Option 2: Install globally (available in all projects)**
```bash
# Copy to your global skills directory
cp -r /path/to/hwitzthum-skills-marketplace/skills/documentation-generator-pro ~/.claude/skills/
```

**Option 3: Clone entire marketplace**
```bash
# Clone the repository
git clone https://github.com/hwitzthum/hwitzthum-skills-marketplace.git

# Install all skills globally
cp -r hwitzthum-skills-marketplace/skills/* ~/.claude/skills/
```

### Verification

After installation, verify the skill is available:

**In Claude Code:**
```bash
# List all available skills
ls ~/.claude/skills/
# or for project skills
ls .claude/skills/
```

**In Claude.ai:**
Navigate to Settings → Capabilities → Skills to see installed skills.

## Usage

Skills are automatically invoked by Claude when relevant to your task. You don't need to explicitly call them.

**Example:**
```
You: "Generate comprehensive API documentation for this FastAPI project"
Claude: [Automatically loads and uses documentation-generator-pro skill]
```

## Directory Structure

```
hwitzthum-skills-marketplace/
├── skills/                    # All skills
│   ├── documentation-generator-pro/
│   │   ├── SKILL.md          # Skill definition
│   │   ├── README.md         # Documentation
│   │   ├── scripts/          # Executable code
│   │   ├── templates/        # Templates
│   │   └── references/       # Reference materials
│   └── template-skill/       # Template for new skills
├── templates/                 # Skill creation templates
├── docs/                      # Guides and documentation
├── scripts/                   # Automation scripts
└── README.md                  # This file
```

## Creating Your Own Skills

Want to create a custom skill? See our [Skill Creation Guide](docs/creating-skills.md).

**Quick Template:**
```bash
cp -r skills/template-skill skills/my-new-skill
cd skills/my-new-skill
# Edit SKILL.md with your skill definition
```

## Skill Structure

Each skill must have this minimum structure:

```
my-skill/
├── SKILL.md              # Required: Core skill file with YAML frontmatter
├── README.md             # Optional: Human-readable documentation
├── scripts/              # Optional: Executable code
├── templates/            # Optional: Template files
└── references/           # Optional: Reference documents
```

### SKILL.md Format

```markdown
---
name: my-skill-name
description: Clear description of what this skill does and when to use it (max 200 chars)
---

# My Skill Name

## Overview
Brief overview of the skill

## Instructions
Step-by-step instructions for Claude

## Examples
Concrete usage examples

## Guidelines
Best practices and guidelines
```

## Best Practices

✅ **Do:**
- Write clear, specific skill descriptions (critical for discovery)
- Include concrete examples
- Test skills incrementally
- Keep skills focused on specific tasks
- Document all dependencies

❌ **Don't:**
- Hardcode API keys or secrets
- Create overly broad skills
- Skip the description field
- Include unnecessary files

## Contributing

We welcome contributions! To add a new skill:

1. Fork this repository
2. Create your skill in `skills/your-skill-name/`
3. Follow the skill structure guidelines
4. Test your skill thoroughly
5. Update this README with your skill info
6. Submit a pull request

## Requirements

- Claude Code or Claude.ai Pro/Team/Enterprise
- Code execution enabled
- Skills feature enabled

## Troubleshooting

### Skill not being detected
1. Verify SKILL.md exists and has proper YAML frontmatter
2. Check that description is clear and specific
3. Restart Claude Code if needed
4. Ensure skills are in correct directory (`.claude/skills/` or `~/.claude/skills/`)

### Skill not activating
1. Make your prompt more explicit
2. Check that the skill description matches your use case
3. Verify code execution is enabled

For more help, see [Troubleshooting Guide](docs/troubleshooting.md).

## Resources

- [Official Skills Documentation](https://docs.claude.com/en/docs/claude-code/skills)
- [Anthropic Skills Repository](https://github.com/anthropics/skills)
- [Skills Engineering Blog](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)

## License

MIT License - See LICENSE file for details

## Author

**Harry Witzthum**  
Email: hwitzthum@caritas.ch  
GitHub: https://github.com/hwitzthum
