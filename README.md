# hwitzthum Skills Marketplace

A collection of custom skills for Claude Code to enhance specific workflows.

## Installation

### Step 1: Add the Marketplace

From your Claude Code interface, run:

```bash
/plugin marketplace add /Users/hwitzthum/hwitzthum-skills-marketplace
```

Or if you clone this repository elsewhere:

```bash
/plugin marketplace add /path/to/hwitzthum-skills-marketplace
```

### Step 2: Install the Plugin

```bash
/plugin install documentation-generation-pro@hwitzthum-skills-marketplace
```

### Step 3: Restart Claude Code

Restart Claude Code to activate the new plugin and skills.

### Step 4: Verify Installation

Run `/help` in Claude Code to see the newly available skills and commands.

## Available Plugins

### documentation-generation-pro

**Version:** 1.0.0
**Category:** Documentation

Comprehensive documentation generation skill for creating API docs, architecture diagrams, onboarding guides, and interactive tutorials from codebases.

**Use this when you need:**
- API documentation or references
- Architecture diagrams or system overviews
- Onboarding guides for new developers
- README files with comprehensive project information
- Interactive tutorials or getting-started guides
- Code documentation (inline comments, docstrings)
- Migration guides or upgrade documentation

## Directory Structure

```
hwitzthum-skills-marketplace/
├── .claude-plugin/
│   └── marketplace.json          # Marketplace configuration
└── documentation-generation-pro/  # Plugin directory
    ├── .claude-plugin/
    │   └── plugin.json           # Plugin metadata
    ├── skills/
    │   └── documentation-generator-pro/  # Skill folder
    │       └── SKILL.md          # Skill definition
    ├── assets/
    │   └── templates/            # Documentation templates
    ├── references/               # Reference materials
    └── scripts/                  # Utility scripts
```

## Development

### Adding New Plugins

1. Create a new directory for your plugin
2. Add `.claude-plugin/plugin.json` with plugin metadata
3. Add skills to `skills/` subdirectory (each as `SKILL.md`)
4. Update `.claude-plugin/marketplace.json` to include the new plugin

### Plugin Structure

Each plugin should follow this structure:

```
plugin-name/
├── .claude-plugin/
│   └── plugin.json          # Required: Plugin metadata
├── skills/                   # Skills directory
│   └── my-skill/            # Each skill in its own folder
│       └── SKILL.md         # Skill definition
├── commands/                 # Optional: Custom slash commands
├── agents/                   # Optional: Custom agents
└── hooks/                    # Optional: Event handlers
```

### Skill Definition Format

Skills are defined in `SKILL.md` files with frontmatter:

```markdown
---
name: skill-name
description: Brief description of what the skill does
---

# Skill Name

Detailed documentation about the skill...
```

## Troubleshooting

### Plugin Not Showing Up

1. Verify the marketplace was added correctly: `/plugin marketplace list`
2. Check that the plugin structure matches the expected format
3. Restart Claude Code
4. Check for errors in the plugin.json files

### Skills Not Available

1. Ensure the SKILL.md file is in a subdirectory within `skills/` (e.g., `skills/my-skill/SKILL.md`)
2. Each skill must have its own folder inside the `skills/` directory
3. Verify the frontmatter in SKILL.md is properly formatted
4. Restart Claude Code after making changes

## Contributing

To contribute new skills or improvements:

1. Follow the plugin structure guidelines
2. Test your plugin locally before committing
3. Update this README with new plugin information
4. Submit a pull request

## License

MIT License - See LICENSE file for details

## Author

Harry Witzthum
Email: hwitzthum@caritas.ch
GitHub: https://github.com/hwitzthum/hwitzthum-skills-marketplace.git