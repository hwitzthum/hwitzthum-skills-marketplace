# Documentation Generator Pro

Comprehensive documentation generation skill for creating API docs, architecture diagrams, onboarding guides, and interactive tutorials from codebases.

## Installation

### Option 1: Project-Specific (Recommended for teams)
```bash
# In your project root
mkdir -p .claude/skills
cp -r /path/to/hwitzthum-skills-marketplace/skills/documentation-generator-pro .claude/skills/
```

### Option 2: Personal (Available across all projects)
```bash
# Install globally
cp -r /path/to/hwitzthum-skills-marketplace/skills/documentation-generator-pro ~/.claude/skills/
```

## Usage

Once installed, Claude will automatically detect and use this skill when you request:
- API documentation
- Architecture diagrams
- Onboarding guides
- README files
- Interactive tutorials

Example prompts:
- "Generate comprehensive API documentation for this project"
- "Create an architecture diagram showing the system components"
- "Write an onboarding guide for new developers"

## Structure

```
documentation-generator-pro/
├── SKILL.md              # Core skill definition
├── README.md             # This file
├── scripts/              # Helper scripts
├── templates/            # Documentation templates
└── references/           # Reference materials
```

## Requirements

- Claude Code or Claude.ai with Skills enabled
- Code execution enabled
- Python 3.8+ (for scripts)

## Version

1.0.0
