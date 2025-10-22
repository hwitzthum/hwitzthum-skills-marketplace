#!/usr/bin/env python3
"""
Versioned Documentation Manager

Maintains documentation for multiple versions of your project.
Creates version-specific documentation directories and manages version switching.

Usage:
    python version_docs.py --version 2.0.0 --previous 1.5.0
    python version_docs.py --version 3.0.0 --copy-from 2.5.0 --output docs/versions/
    python version_docs.py --list
"""

import argparse
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class VersionedDocsManager:
    """Manage versioned documentation"""

    def __init__(self, docs_root: str = "docs"):
        self.docs_root = Path(docs_root)
        self.versions_dir = self.docs_root / "versions"
        self.versions_file = self.docs_root / "versions.json"
        self.versions_dir.mkdir(parents=True, exist_ok=True)

    def create_version(
        self,
        version: str,
        previous_version: Optional[str] = None,
        copy_from: Optional[str] = None
    ):
        """Create a new documentation version"""
        print(f"📚 Creating documentation for version {version}")

        version_dir = self.versions_dir / version
        if version_dir.exists():
            print(f"⚠️  Version {version} already exists!")
            response = input("Overwrite? (y/N): ")
            if response.lower() != 'y':
                print("Cancelled.")
                return
            shutil.rmtree(version_dir)

        version_dir.mkdir(parents=True)

        # Copy from specified version or previous version
        source_version = copy_from or previous_version
        if source_version:
            source_dir = self.versions_dir / source_version
            if source_dir.exists():
                print(f"📋 Copying from version {source_version}")
                self._copy_version_docs(source_dir, version_dir)
            else:
                print(f"⚠️  Source version {source_version} not found")
                print(f"   Creating new documentation from main docs")
                self._copy_main_docs(version_dir)
        else:
            print("📋 Creating from main documentation")
            self._copy_main_docs(version_dir)

        # Add version banner
        self._add_version_banner(version_dir, version, previous_version)

        # Update versions metadata
        self._update_versions_metadata(version, previous_version)

        # Generate version selector
        self._generate_version_selector()

        print(f"✅ Version {version} documentation created at {version_dir}")

    def _copy_version_docs(self, source: Path, dest: Path):
        """Copy documentation from one version to another"""
        for item in source.iterdir():
            if item.name.startswith('.'):
                continue

            if item.is_file():
                shutil.copy2(item, dest / item.name)
            elif item.is_dir():
                shutil.copytree(item, dest / item.name, dirs_exist_ok=True)

    def _copy_main_docs(self, dest: Path):
        """Copy from main documentation directory"""
        main_docs = self.docs_root

        for item in main_docs.iterdir():
            # Skip versions directory and metadata
            if item.name in ['versions', 'versions.json', 'version-selector.md']:
                continue
            if item.name.startswith('.'):
                continue

            if item.is_file() and item.suffix == '.md':
                shutil.copy2(item, dest / item.name)
            elif item.is_dir() and item.name not in ['versions']:
                shutil.copytree(item, dest / item.name, dirs_exist_ok=True)

    def _add_version_banner(
        self,
        version_dir: Path,
        version: str,
        previous_version: Optional[str]
    ):
        """Add version banner to README"""
        readme = version_dir / "README.md"

        if not readme.exists():
            # Create a basic README if it doesn't exist
            readme.write_text(f"# Documentation - Version {version}\n\n")

        content = readme.read_text()

        # Add version banner at the top
        banner = f"""---
**📌 Version {version} Documentation**

"""

        if previous_version:
            banner += f"Previous version: [{previous_version}](../{previous_version}/README.md) | "

        banner += "[All versions](../version-selector.md)\n\n"
        banner += "---\n\n"

        # Insert banner after the title
        lines = content.split('\n')
        if lines and lines[0].startswith('#'):
            # Insert after first title
            new_content = lines[0] + '\n\n' + banner + '\n'.join(lines[1:])
        else:
            new_content = banner + content

        readme.write_text(new_content)

    def _update_versions_metadata(self, version: str, previous_version: Optional[str]):
        """Update versions.json metadata file"""
        if self.versions_file.exists():
            versions_data = json.loads(self.versions_file.read_text())
        else:
            versions_data = {
                "versions": [],
                "latest": None
            }

        # Check if version already exists
        existing = [v for v in versions_data["versions"] if v["version"] == version]
        if existing:
            # Update existing version
            for v in versions_data["versions"]:
                if v["version"] == version:
                    v["updated_at"] = datetime.now().isoformat()
        else:
            # Add new version
            version_info = {
                "version": version,
                "created_at": datetime.now().isoformat(),
                "previous_version": previous_version,
                "status": "current"  # current, deprecated, archived
            }
            versions_data["versions"].append(version_info)

        # Sort versions (newest first) using semantic versioning
        def version_key(version_info):
            """Convert version string to tuple for proper sorting"""
            version = version_info["version"]
            try:
                # Try to parse as semantic version (e.g., "2.1.0")
                parts = version.split('.')
                return tuple(int(p) if p.isdigit() else p for p in parts)
            except (ValueError, AttributeError):
                # Fallback to string comparison if parsing fails
                return (version,)

        versions_data["versions"].sort(
            key=version_key,
            reverse=True
        )

        # Update latest version
        if versions_data["versions"]:
            versions_data["latest"] = versions_data["versions"][0]["version"]

        self.versions_file.write_text(json.dumps(versions_data, indent=2))

    def _generate_version_selector(self):
        """Generate version selector page"""
        if not self.versions_file.exists():
            return

        versions_data = json.loads(self.versions_file.read_text())

        content = [
            "# Documentation Versions\n",
            "Select the version that matches your installation:\n"
        ]

        latest_version = versions_data.get("latest")

        for version_info in versions_data["versions"]:
            version = version_info["version"]
            status = version_info.get("status", "current")
            created = version_info.get("created_at", "")

            # Format date
            if created:
                try:
                    dt = datetime.fromisoformat(created)
                    created_str = dt.strftime("%Y-%m-%d")
                except:
                    created_str = created

            badges = []
            if version == latest_version:
                badges.append("**Latest**")
            if status == "deprecated":
                badges.append("*Deprecated*")
            if status == "archived":
                badges.append("*Archived*")

            badge_str = " ".join(badges)
            if badge_str:
                badge_str = f" - {badge_str}"

            content.append(
                f"## [Version {version}](versions/{version}/README.md){badge_str}\n"
            )

            if created_str:
                content.append(f"*Released: {created_str}*\n")

            # Add migration notes if previous version exists
            prev_version = version_info.get("previous_version")
            if prev_version:
                content.append(
                    f"\n**Upgrading from {prev_version}?** "
                    f"See the [migration guide](versions/{version}/MIGRATION.md)\n"
                )

        content.append("\n---\n")
        content.append("\n**Can't find your version?** Check the [archive](versions/) directory.\n")

        selector_file = self.docs_root / "version-selector.md"
        selector_file.write_text("\n".join(content))

        print(f"✅ Version selector updated: {selector_file}")

    def list_versions(self):
        """List all available versions"""
        if not self.versions_file.exists():
            print("No versions found.")
            return

        versions_data = json.loads(self.versions_file.read_text())

        print("\n📚 Available Documentation Versions:\n")

        latest = versions_data.get("latest")

        for version_info in versions_data["versions"]:
            version = version_info["version"]
            status = version_info.get("status", "current")
            created = version_info.get("created_at", "Unknown")

            marker = "→" if version == latest else " "
            print(f"{marker} {version:15} {status:12} (created: {created})")

        print(f"\nLatest version: {latest}")
        print(f"Total versions: {len(versions_data['versions'])}")

    def deprecate_version(self, version: str):
        """Mark a version as deprecated"""
        if not self.versions_file.exists():
            print("No versions found.")
            return

        versions_data = json.loads(self.versions_file.read_text())

        for v in versions_data["versions"]:
            if v["version"] == version:
                v["status"] = "deprecated"
                v["deprecated_at"] = datetime.now().isoformat()
                break
        else:
            print(f"Version {version} not found.")
            return

        self.versions_file.write_text(json.dumps(versions_data, indent=2))
        self._generate_version_selector()

        print(f"✅ Version {version} marked as deprecated")

    def create_migration_guide(self, version: str, previous_version: str):
        """Create a migration guide template"""
        version_dir = self.versions_dir / version
        if not version_dir.exists():
            print(f"Version {version} not found.")
            return

        migration_file = version_dir / "MIGRATION.md"

        content = f"""# Migration Guide: {previous_version} → {version}

This guide will help you upgrade from version {previous_version} to {version}.

## Overview

Summary of major changes in version {version}.

## Breaking Changes

### 1. API Changes

**Changed:** Description of what changed

**Before ({previous_version}):**
```python
# Old API usage
old_function(param1, param2)
```

**After ({version}):**
```python
# New API usage
new_function(param1, param2, new_param)
```

**Migration steps:**
1. Update function calls
2. Add new parameter
3. Test your code

### 2. Configuration Changes

**Changed:** Configuration format updated

**Before:**
```yaml
old_config:
  setting: value
```

**After:**
```yaml
new_config:
  setting: value
  new_setting: default
```

### 3. Deprecated Features

The following features are deprecated and will be removed in the next major version:

- `old_feature()` - Use `new_feature()` instead
- `legacy_option` - Use `modern_option` instead

## New Features

### Feature 1: Description

New feature available in version {version}.

**Usage:**
```python
# Example usage
use_new_feature()
```

### Feature 2: Description

Another new feature.

## Step-by-Step Migration

### Step 1: Backup

Create a backup of your current installation:

```bash
# Backup command
cp -r project project-backup
```

### Step 2: Update Dependencies

Update to version {version}:

```bash
# Update command (example)
npm install package@{version}
# or
pip install package=={version}
```

### Step 3: Update Configuration

Update your configuration files according to the breaking changes above.

### Step 4: Update Code

Update your code to use the new API:

1. Replace deprecated function calls
2. Add new required parameters
3. Update configuration references

### Step 5: Test

Run your test suite:

```bash
npm test
# or
pytest
```

### Step 6: Deploy

After thorough testing, deploy to production.

## Troubleshooting

### Issue: Error message

**Cause:** Explanation

**Solution:** How to fix

### Issue: Another error

**Cause:** Explanation

**Solution:** How to fix

## Rollback Procedure

If you need to rollback to {previous_version}:

```bash
# Rollback command
npm install package@{previous_version}
```

## Support

Need help with migration?

- Check [GitHub Issues](https://github.com/user/repo/issues)
- Ask in [Community Forum](https://forum.example.com)
- Email support@example.com

## Timeline

Recommended migration timeline:

- **Week 1:** Review changes and plan migration
- **Week 2:** Test in development environment
- **Week 3:** Test in staging environment
- **Week 4:** Deploy to production

---

**Next:** [Version {version} Documentation](README.md)
"""

        migration_file.write_text(content)
        print(f"✅ Migration guide created: {migration_file}")


def main():
    parser = argparse.ArgumentParser(
        description="Manage versioned documentation"
    )
    parser.add_argument(
        "--version",
        help="Version to create (e.g., 2.0.0)"
    )
    parser.add_argument(
        "--previous",
        help="Previous version (for migration guides)"
    )
    parser.add_argument(
        "--copy-from",
        help="Version to copy from (instead of previous)"
    )
    parser.add_argument(
        "--docs-root",
        default="docs",
        help="Root documentation directory (default: docs)"
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List all versions"
    )
    parser.add_argument(
        "--deprecate",
        help="Mark a version as deprecated"
    )
    parser.add_argument(
        "--migration-guide",
        action="store_true",
        help="Create migration guide template"
    )

    args = parser.parse_args()

    manager = VersionedDocsManager(args.docs_root)

    if args.list:
        manager.list_versions()
    elif args.deprecate:
        manager.deprecate_version(args.deprecate)
    elif args.migration_guide:
        if not args.version or not args.previous:
            print("Error: --version and --previous required for migration guide")
            return
        manager.create_migration_guide(args.version, args.previous)
    elif args.version:
        manager.create_version(
            args.version,
            args.previous,
            args.copy_from
        )
    else:
        parser.print_help()


if __name__ == "__main__":
    main()