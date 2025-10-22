#!/bin/bash
# Safe cleanup script for hwitzthum-skills-marketplace
# This script safely removes old plugin structure AFTER verifying all files are copied

set -e  # Exit on error

echo "🔍 Safe Cleanup Script for hwitzthum-skills-marketplace"
echo "========================================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check if file exists
check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✅${NC} Found: $1"
        return 0
    else
        echo -e "${RED}❌${NC} Missing: $1"
        return 1
    fi
}

# Function to compare files
compare_files() {
    local old_file="$1"
    local new_file="$2"
    
    if [ ! -f "$old_file" ]; then
        echo -e "${YELLOW}⚠️${NC}  Old file doesn't exist: $old_file"
        return 0
    fi
    
    if [ ! -f "$new_file" ]; then
        echo -e "${RED}❌${NC} New file missing: $new_file"
        return 1
    fi
    
    # Check if files are identical
    if cmp -s "$old_file" "$new_file"; then
        echo -e "${GREEN}✅${NC} Identical: $new_file"
        return 0
    else
        echo -e "${YELLOW}⚠️${NC}  Different: $new_file (this is OK if you edited it)"
        return 0
    fi
}

echo "Step 1: Verifying all important files exist in skills/ directory"
echo "----------------------------------------------------------------"

# Check critical files
MISSING_FILES=0

check_file "skills/documentation-generator-pro/SKILL.md" || MISSING_FILES=$((MISSING_FILES + 1))
check_file "skills/documentation-generator-pro/README.md" || MISSING_FILES=$((MISSING_FILES + 1))
check_file "skills/documentation-generator-pro/scripts/extract_api.py" || MISSING_FILES=$((MISSING_FILES + 1))
check_file "skills/documentation-generator-pro/scripts/generate_diagram.py" || MISSING_FILES=$((MISSING_FILES + 1))
check_file "skills/documentation-generator-pro/scripts/generate_tutorial.py" || MISSING_FILES=$((MISSING_FILES + 1))
check_file "skills/documentation-generator-pro/templates/README_TEMPLATE.md" || MISSING_FILES=$((MISSING_FILES + 1))
check_file "skills/documentation-generator-pro/templates/ONBOARDING_TEMPLATE.md" || MISSING_FILES=$((MISSING_FILES + 1))
check_file "skills/documentation-generator-pro/references/documentation_standards.md" || MISSING_FILES=$((MISSING_FILES + 1))

echo ""

if [ $MISSING_FILES -gt 0 ]; then
    echo -e "${RED}❌ ERROR: $MISSING_FILES critical files are missing!${NC}"
    echo "Please run the restructure script first: ./restructure.sh"
    exit 1
fi

echo -e "${GREEN}✅ All critical files verified!${NC}"
echo ""

echo "Step 2: Comparing files (optional verification)"
echo "-----------------------------------------------"

# Compare files to ensure they match or are intentionally different
compare_files "documentation-generation-pro/scripts/extract_api.py" \
              "skills/documentation-generator-pro/scripts/extract_api.py"

compare_files "documentation-generation-pro/scripts/generate_diagram.py" \
              "skills/documentation-generator-pro/scripts/generate_diagram.py"

compare_files "documentation-generation-pro/scripts/generate_tutorial.py" \
              "skills/documentation-generator-pro/scripts/generate_tutorial.py"

echo ""
echo "Step 3: What will be removed"
echo "----------------------------"

if [ -d "documentation-generation-pro" ]; then
    echo -e "${YELLOW}📁 Will remove:${NC} documentation-generation-pro/"
    echo "   This contains:"
    find documentation-generation-pro -type f | sed 's/^/     - /'
else
    echo -e "${GREEN}✅ Already removed: documentation-generation-pro/${NC}"
fi

echo ""

if [ -d ".claude/skills" ]; then
    echo -e "${YELLOW}📁 Will remove:${NC} .claude/skills/ (local install cache)"
else
    echo -e "${GREEN}✅ Already removed: .claude/skills/${NC}"
fi

echo ""

if [ -d ".claude-plugin" ]; then
    echo -e "${YELLOW}📁 Will remove:${NC} .claude-plugin/ (plugin infrastructure)"
else
    echo -e "${GREEN}✅ Already removed: .claude-plugin/${NC}"
fi

echo ""
echo "Step 4: Confirmation"
echo "--------------------"

read -p "Do you want to proceed with cleanup? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo -e "${YELLOW}⚠️  Cleanup cancelled by user${NC}"
    exit 0
fi

echo ""
echo "Step 5: Performing cleanup"
echo "--------------------------"

# Remove old plugin directory
if [ -d "documentation-generation-pro" ]; then
    echo -e "${YELLOW}🗑️  Removing: documentation-generation-pro/${NC}"
    rm -rf documentation-generation-pro
    echo -e "${GREEN}✅ Removed: documentation-generation-pro/${NC}"
fi

# Remove local install cache
if [ -d ".claude/skills" ]; then
    echo -e "${YELLOW}🗑️  Removing: .claude/skills/${NC}"
    rm -rf .claude/skills
    echo -e "${GREEN}✅ Removed: .claude/skills/${NC}"
fi

# Remove .claude directory if empty
if [ -d ".claude" ] && [ -z "$(ls -A .claude)" ]; then
    echo -e "${YELLOW}🗑️  Removing empty: .claude/${NC}"
    rm -rf .claude
    echo -e "${GREEN}✅ Removed: .claude/${NC}"
fi

# Remove plugin infrastructure
if [ -d ".claude-plugin" ]; then
    echo -e "${YELLOW}🗑️  Removing: .claude-plugin/${NC}"
    rm -rf .claude-plugin
    echo -e "${GREEN}✅ Removed: .claude-plugin/${NC}"
fi

# Remove plugin-related files from old structure
if [ -d "documentation-generation-pro/.claude-plugin" ]; then
    echo -e "${YELLOW}🗑️  Removing: documentation-generation-pro/.claude-plugin${NC}"
    rm -rf documentation-generation-pro/.claude-plugin
    echo -e "${GREEN}✅ Removed: documentation-generation-pro/.claude-plugin${NC}"
fi

echo ""
echo "Step 6: Final verification"
echo "--------------------------"

# Verify the new structure
if [ -f "skills/documentation-generator-pro/SKILL.md" ]; then
    echo -e "${GREEN}✅ Verified: skills/documentation-generator-pro/SKILL.md exists${NC}"
else
    echo -e "${RED}❌ ERROR: skills/documentation-generator-pro/SKILL.md missing!${NC}"
    exit 1
fi

# Count files in skills directory
FILE_COUNT=$(find skills/documentation-generator-pro -type f | wc -l)
echo -e "${GREEN}✅ Skills directory contains $FILE_COUNT files${NC}"

# Run validation
if [ -f "scripts/validate_skills.py" ]; then
    echo ""
    echo "Running validation..."
    python3 scripts/validate_skills.py
fi

echo ""
echo -e "${GREEN}✅ Cleanup complete!${NC}"
echo ""
echo "Your repository now has:"
echo "  ✅ skills/ - All skills with scripts, templates, references"
echo "  ✅ templates/ - Skill creation templates"
echo "  ✅ docs/ - Documentation"
echo "  ✅ scripts/ - Automation tools"
echo ""
echo "Next steps:"
echo "  1. Review: ls -la skills/documentation-generator-pro/"
echo "  2. Test: cp -r skills/documentation-generator-pro ~/.claude/skills/"
echo "  3. Commit: git add . && git commit -m 'Convert to skills-only structure'"
echo ""
