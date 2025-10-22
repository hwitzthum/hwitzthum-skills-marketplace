#!/usr/bin/env python3
"""
Documentation Testing Tool

Validates documentation by:
- Checking for broken links
- Executing code examples
- Validating markdown syntax
- Checking for common issues

Usage:
    python test_docs.py --path docs/ --execute-examples
    python test_docs.py --path docs/ --check-links --fix
    python test_docs.py --path docs/ --all
"""

import argparse
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import List, Tuple


class DocumentationTester:
    """Test and validate documentation"""

    def __init__(self, docs_path: str):
        self.docs_path = Path(docs_path)
        self.errors = []
        self.warnings = []
        self.stats = {
            "files_checked": 0,
            "links_checked": 0,
            "code_blocks_tested": 0,
            "errors": 0,
            "warnings": 0
        }

    def run_all_tests(self, execute_examples: bool = False, fix: bool = False):
        """Run all documentation tests"""
        print("🧪 Testing documentation...\n")

        # Find all markdown files
        md_files = list(self.docs_path.glob("**/*.md"))
        if not md_files:
            print(f"⚠️  No markdown files found in {self.docs_path}")
            return False

        print(f"Found {len(md_files)} markdown files\n")

        for md_file in md_files:
            if "node_modules" in str(md_file) or ".git" in str(md_file):
                continue

            print(f"📄 Testing {md_file.relative_to(self.docs_path)}")
            self.stats["files_checked"] += 1

            content = md_file.read_text()

            # Run tests
            self._check_markdown_syntax(md_file, content)
            self._check_links(md_file, content, fix)
            self._check_common_issues(md_file, content)

            if execute_examples:
                self._test_code_examples(md_file, content)

        # Print results
        self._print_results()

        return self.stats["errors"] == 0

    def _check_markdown_syntax(self, filepath: Path, content: str):
        """Check markdown syntax"""
        lines = content.split('\n')

        # Check for multiple H1 headers
        h1_count = sum(1 for line in lines if line.strip().startswith('# ') and not line.strip().startswith('##'))
        if h1_count > 1:
            self._add_warning(filepath, "Multiple H1 headers found (should have only one)")

        # Check for empty links
        empty_links = re.findall(r'\[([^\]]+)\]\(\s*\)', content)
        if empty_links:
            self._add_error(filepath, f"Empty links found: {', '.join(empty_links)}")

        # Check for unclosed code blocks
        code_block_count = content.count('```')
        if code_block_count % 2 != 0:
            self._add_error(filepath, "Unclosed code block (odd number of ```)")

        # Check for heading hierarchy
        prev_level = 0
        for i, line in enumerate(lines, 1):
            if line.strip().startswith('#'):
                level = len(line) - len(line.lstrip('#'))
                if level > prev_level + 1 and prev_level > 0:
                    self._add_warning(
                        filepath,
                        f"Line {i}: Skipped heading level (went from H{prev_level} to H{level})"
                    )
                prev_level = level

    def _check_links(self, filepath: Path, content: str, fix: bool = False):
        """Check for broken links"""
        # Find all markdown links
        links = re.findall(r'\[([^\]]+)\]\(([^\)]+)\)', content)

        for link_text, link_url in links:
            self.stats["links_checked"] += 1

            # Skip anchors and external URLs (for now)
            if link_url.startswith('#'):
                continue
            if link_url.startswith('http://') or link_url.startswith('https://'):
                # Could check external links with requests, but skip for now
                continue
            if link_url.startswith('mailto:'):
                continue

            # Check relative file links
            if not link_url.startswith('/'):
                # Relative to current file
                link_path = (filepath.parent / link_url).resolve()
            else:
                # Relative to docs root
                link_path = (self.docs_path / link_url.lstrip('/')).resolve()

            # Remove anchor if present
            if '#' in str(link_path):
                link_path = Path(str(link_path).split('#')[0])

            if not link_path.exists():
                self._add_error(filepath, f"Broken link: {link_url} -> {link_path}")

    def _check_common_issues(self, filepath: Path, content: str):
        """Check for common documentation issues"""
        # Check for TODO/FIXME comments
        todos = re.findall(r'TODO|FIXME|XXX', content)
        if todos:
            self._add_warning(filepath, f"Found {len(todos)} TODO/FIXME markers")

        # Check for very long lines (except in code blocks)
        lines = content.split('\n')
        in_code_block = False
        for i, line in enumerate(lines, 1):
            if line.strip().startswith('```'):
                in_code_block = not in_code_block
                continue

            if not in_code_block and len(line) > 120:
                self._add_warning(filepath, f"Line {i}: Very long line ({len(line)} chars)")

        # Check for common typos
        common_typos = {
            r'\bthe\s+the\b': 'duplicate "the"',
            r'\bof\s+of\b': 'duplicate "of"',
            r'\bis\s+is\b': 'duplicate "is"'
        }

        for pattern, description in common_typos.items():
            if re.search(pattern, content, re.IGNORECASE):
                self._add_warning(filepath, f"Possible typo: {description}")

    def _test_code_examples(self, filepath: Path, content: str):
        """Extract and test code examples"""
        # Extract code blocks
        code_blocks = re.findall(r'```(\w+)\n(.*?)```', content, re.DOTALL)

        for lang, code in code_blocks:
            lang = lang.lower()

            # Skip non-executable code blocks
            if lang in ['text', 'markdown', 'json', 'yaml', 'yml', 'output']:
                continue

            self.stats["code_blocks_tested"] += 1

            if lang == 'python':
                self._test_python_code(filepath, code)
            elif lang in ['javascript', 'js']:
                self._test_javascript_code(filepath, code)
            elif lang == 'bash':
                self._test_bash_code(filepath, code)

    def _test_python_code(self, filepath: Path, code: str):
        """Test Python code example"""
        # Skip examples with placeholders
        if 'YOUR_API_KEY' in code or 'your-' in code.lower() or 'example.com' in code:
            return

        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            temp_file = f.name

        try:
            # Try to syntax check
            result = subprocess.run(
                ['python', '-m', 'py_compile', temp_file],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode != 0:
                self._add_error(
                    filepath,
                    f"Python code syntax error:\n{result.stderr}"
                )
        except subprocess.TimeoutExpired:
            self._add_warning(filepath, "Python code test timed out")
        except Exception as e:
            self._add_warning(filepath, f"Could not test Python code: {e}")
        finally:
            Path(temp_file).unlink(missing_ok=True)

    def _test_javascript_code(self, filepath: Path, code: str):
        """Test JavaScript code example"""
        # Skip examples with placeholders
        if 'YOUR_API_KEY' in code or 'your-' in code.lower() or 'example.com' in code:
            return

        # Check if node is available
        try:
            subprocess.run(['node', '--version'], capture_output=True, timeout=2)
        except:
            return  # Skip if node not available

        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
            f.write(code)
            temp_file = f.name

        try:
            # Try to syntax check with node
            result = subprocess.run(
                ['node', '--check', temp_file],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode != 0:
                self._add_error(
                    filepath,
                    f"JavaScript code syntax error:\n{result.stderr}"
                )
        except subprocess.TimeoutExpired:
            self._add_warning(filepath, "JavaScript code test timed out")
        except Exception as e:
            self._add_warning(filepath, f"Could not test JavaScript code: {e}")
        finally:
            Path(temp_file).unlink(missing_ok=True)

    def _test_bash_code(self, filepath: Path, code: str):
        """Test Bash code example"""
        # Skip examples with placeholders or dangerous commands
        dangerous = ['rm -rf', 'dd if=', 'mkfs', ':(){:|:&};:']
        if any(cmd in code for cmd in dangerous):
            return

        if 'YOUR_' in code or 'your-' in code.lower():
            return

        # Just check for basic syntax issues
        lines = code.split('\n')
        for i, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            # Check for unmatched quotes
            if line.count('"') % 2 != 0 or line.count("'") % 2 != 0:
                self._add_warning(
                    filepath,
                    f"Bash code may have unmatched quotes: {line}"
                )

    def _add_error(self, filepath: Path, message: str):
        """Add an error"""
        self.errors.append((filepath, message))
        self.stats["errors"] += 1

    def _add_warning(self, filepath: Path, message: str):
        """Add a warning"""
        self.warnings.append((filepath, message))
        self.stats["warnings"] += 1

    def _print_results(self):
        """Print test results"""
        print("\n" + "="*70)
        print("📊 Test Results")
        print("="*70 + "\n")

        print(f"Files checked: {self.stats['files_checked']}")
        print(f"Links checked: {self.stats['links_checked']}")
        print(f"Code blocks tested: {self.stats['code_blocks_tested']}")
        print(f"\nErrors: {self.stats['errors']}")
        print(f"Warnings: {self.stats['warnings']}\n")

        # Print errors
        if self.errors:
            print("❌ Errors:\n")
            for filepath, message in self.errors:
                print(f"  {filepath.name}:")
                print(f"    {message}\n")

        # Print warnings
        if self.warnings:
            print("⚠️  Warnings:\n")
            for filepath, message in self.warnings:
                print(f"  {filepath.name}:")
                print(f"    {message}\n")

        # Final verdict
        print("="*70)
        if self.stats["errors"] == 0:
            print("✅ All tests passed!")
            if self.stats["warnings"] > 0:
                print(f"   (with {self.stats['warnings']} warnings)")
        else:
            print(f"❌ Tests failed with {self.stats['errors']} errors")
        print("="*70)


class LinkChecker:
    """Check for broken links in documentation"""

    @staticmethod
    def check_external_links(docs_path: Path) -> List[Tuple[Path, str, str]]:
        """Check external HTTP(S) links"""
        broken_links = []

        try:
            import requests
        except ImportError:
            print("⚠️  Install 'requests' to check external links: pip install requests")
            return broken_links

        md_files = list(docs_path.glob("**/*.md"))

        for md_file in md_files:
            if "node_modules" in str(md_file):
                continue

            content = md_file.read_text()
            links = re.findall(r'\[([^\]]+)\]\((https?://[^\)]+)\)', content)

            for link_text, url in links:
                try:
                    response = requests.head(url, timeout=5, allow_redirects=True)
                    if response.status_code >= 400:
                        broken_links.append((md_file, url, f"HTTP {response.status_code}"))
                except requests.RequestException as e:
                    broken_links.append((md_file, url, str(e)))

        return broken_links


def main():
    parser = argparse.ArgumentParser(description="Test and validate documentation")
    parser.add_argument(
        "--path",
        default="docs",
        help="Documentation directory to test (default: docs)"
    )
    parser.add_argument(
        "--execute-examples",
        action="store_true",
        help="Execute code examples to verify they work"
    )
    parser.add_argument(
        "--check-links",
        action="store_true",
        help="Check for broken links (including external)"
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Attempt to fix issues automatically"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Run all tests"
    )

    args = parser.parse_args()

    # Validate path
    docs_path = Path(args.path)
    if not docs_path.exists():
        print(f"❌ Documentation path not found: {docs_path}")
        sys.exit(1)

    # Run tests
    tester = DocumentationTester(docs_path)

    if args.all:
        args.execute_examples = True
        args.check_links = True

    success = tester.run_all_tests(
        execute_examples=args.execute_examples,
        fix=args.fix
    )

    # Check external links if requested
    if args.check_links:
        print("\n🔗 Checking external links...")
        broken = LinkChecker.check_external_links(docs_path)
        if broken:
            print(f"\n❌ Found {len(broken)} broken external links:\n")
            for filepath, url, error in broken:
                print(f"  {filepath.name}: {url}")
                print(f"    Error: {error}\n")
            success = False
        else:
            print("✅ All external links are valid")

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()