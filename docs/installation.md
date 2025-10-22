# Installation Guide

## Prerequisites

- Claude Code or Claude.ai Pro/Team/Enterprise plan
- Code execution enabled
- Skills feature enabled

## Installation Methods

### Method 1: Project-Specific Installation (Recommended for Teams)

Install skills that are specific to a single project:

```bash
# Navigate to your project root
cd /path/to/your-project

# Create project skills directory
mkdir -p .claude/skills

# Copy the skill
cp -r /path/to/hwitzthum-skills-marketplace/skills/documentation-generator-pro .claude/skills/
```

**Benefits:**
- Skills are version-controlled with your project
- Team members automatically get the skills when they clone
- Different projects can have different skill versions

### Method 2: Personal Installation (Global)

Install skills available across all your projects:

```bash
# Copy to your global skills directory
cp -r /path/to/hwitzthum-skills-marketplace/skills/documentation-generator-pro ~/.claude/skills/
```

**Benefits:**
- Available in all projects immediately
- No need to install per-project
- Personal customizations

### Method 3: Clone Entire Marketplace

Get all skills at once:

```bash
# Clone the repository
git clone https://github.com/hwitzthum/hwitzthum-skills-marketplace.git

# Install all skills globally
cp -r hwitzthum-skills-marketplace/skills/* ~/.claude/skills/

# Or install to project
mkdir -p .claude/skills
cp -r hwitzthum-skills-marketplace/skills/* .claude/skills/
```

## Verification

### For Claude Code

```bash
# List installed skills
ls ~/.claude/skills/

# Or for project skills
ls .claude/skills/

# View a specific skill
cat ~/.claude/skills/documentation-generator-pro/SKILL.md
```

### For Claude.ai

1. Go to Settings → Capabilities
2. Scroll to Skills section
3. You should see your installed skills listed

## Updating Skills

To update an existing skill:

```bash
# Remove old version
rm -rf ~/.claude/skills/documentation-generator-pro

# Copy new version
cp -r /path/to/hwitzthum-skills-marketplace/skills/documentation-generator-pro ~/.claude/skills/
```

## Uninstalling Skills

```bash
# Remove from global
rm -rf ~/.claude/skills/skill-name

# Remove from project
rm -rf .claude/skills/skill-name

# Restart Claude Code to apply changes
```

## Troubleshooting

### Skills not showing up

1. **Check directory location:**
   ```bash
   # Should be one of these:
   ls ~/.claude/skills/skill-name/SKILL.md
   ls .claude/skills/skill-name/SKILL.md
   ```

2. **Verify SKILL.md format:**
   - File must start with `---`
   - Must have `name:` and `description:` fields
   - YAML must be valid

3. **Restart Claude Code:**
   ```bash
   # Exit and restart Claude Code
   ```

### Permission issues

```bash
# Fix permissions
chmod -R 755 ~/.claude/skills/

# Or for project
chmod -R 755 .claude/skills/
```

## Next Steps

- [Creating Your Own Skills](creating-skills.md)
- [Skill Guidelines](skill-guidelines.md)
- [Troubleshooting](troubleshooting.md)
