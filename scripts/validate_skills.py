#!/usr/bin/env python3
"""
Validate Skills in the marketplace for proper structure and format.
"""

import os
import sys
import yaml
from pathlib import Path

def validate_skill(skill_path):
    """Validate a single skill directory."""
    errors = []
    warnings = []
    
    skill_name = skill_path.name
    skill_md = skill_path / "SKILL.md"
    
    # Check SKILL.md exists
    if not skill_md.exists():
        errors.append(f"{skill_name}: Missing SKILL.md file")
        return errors, warnings
    
    # Read and validate SKILL.md
    content = skill_md.read_text(encoding='utf-8')
    
    # Check for YAML frontmatter
    if not content.startswith('---'):
        errors.append(f"{skill_name}: SKILL.md must start with YAML frontmatter (---)")
        return errors, warnings
    
    # Extract YAML frontmatter
    try:
        parts = content.split('---', 2)
        if len(parts) < 3:
            errors.append(f"{skill_name}: Invalid YAML frontmatter format")
            return errors, warnings
        
        frontmatter = yaml.safe_load(parts[1])
        
        # Validate required fields
        if 'name' not in frontmatter:
            errors.append(f"{skill_name}: Missing required field 'name' in frontmatter")
        
        if 'description' not in frontmatter:
            errors.append(f"{skill_name}: Missing required field 'description' in frontmatter")
        else:
            # Check description length
            desc_len = len(frontmatter['description'])
            if desc_len > 200:
                errors.append(f"{skill_name}: Description too long ({desc_len} chars, max 200)")
            elif desc_len < 20:
                warnings.append(f"{skill_name}: Description quite short ({desc_len} chars), consider adding more detail")
        
        # Check for name length
        if 'name' in frontmatter and len(frontmatter['name']) > 64:
            errors.append(f"{skill_name}: Name too long ({len(frontmatter['name'])} chars, max 64)")
        
    except yaml.YAMLError as e:
        errors.append(f"{skill_name}: Invalid YAML frontmatter: {e}")
        return errors, warnings
    
    # Check markdown body exists
    markdown_body = parts[2].strip()
    if not markdown_body:
        errors.append(f"{skill_name}: SKILL.md has no content after frontmatter")
    elif len(markdown_body) < 100:
        warnings.append(f"{skill_name}: SKILL.md content is quite short")
    
    # Check for README (optional but recommended)
    if not (skill_path / "README.md").exists():
        warnings.append(f"{skill_name}: No README.md found (optional but recommended)")
    
    return errors, warnings

def main():
    """Main validation function."""
    skills_dir = Path(__file__).parent.parent / "skills"
    
    if not skills_dir.exists():
        print(f"❌ Skills directory not found: {skills_dir}")
        return 1
    
    all_errors = []
    all_warnings = []
    skills_count = 0
    
    print("🔍 Validating skills in marketplace...\n")
    
    # Validate each skill
    for skill_path in sorted(skills_dir.iterdir()):
        if skill_path.is_dir() and not skill_path.name.startswith('.'):
            skills_count += 1
            errors, warnings = validate_skill(skill_path)
            all_errors.extend(errors)
            all_warnings.extend(warnings)
            
            if not errors and not warnings:
                print(f"✅ {skill_path.name}")
            elif not errors:
                print(f"⚠️  {skill_path.name} (warnings)")
            else:
                print(f"❌ {skill_path.name} (errors)")
    
    # Print detailed results
    if all_warnings:
        print("\n⚠️  Warnings:")
        for warning in all_warnings:
            print(f"  - {warning}")
    
    if all_errors:
        print("\n❌ Errors:")
        for error in all_errors:
            print(f"  - {error}")
    
    # Summary
    print(f"\n📊 Summary:")
    print(f"  Skills validated: {skills_count}")
    print(f"  Errors: {len(all_errors)}")
    print(f"  Warnings: {len(all_warnings)}")
    
    return 1 if all_errors else 0


if __name__ == "__main__":
    sys.exit(main())
