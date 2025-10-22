#!/usr/bin/env python3
"""
Multi-Language Documentation Generator

Generates documentation in multiple languages from a source documentation set.
Supports translation and localization of documentation content.

Usage:
    python generate_docs.py --languages en,es,fr --output docs/i18n/
    python generate_docs.py --languages en,ja --source docs/ --output docs/i18n/
"""

import argparse
import json
import shutil
from pathlib import Path
from typing import List


class DocumentationGenerator:
    """Generate documentation in multiple languages"""

    # Language configurations
    LANGUAGES = {
        "en": {"name": "English", "dir": "ltr", "default": True},
        "es": {"name": "Español", "dir": "ltr"},
        "fr": {"name": "Français", "dir": "ltr"},
        "de": {"name": "Deutsch", "dir": "ltr"},
        "ja": {"name": "日本語", "dir": "ltr"},
        "zh": {"name": "中文", "dir": "ltr"},
        "ar": {"name": "العربية", "dir": "rtl"},
        "pt": {"name": "Português", "dir": "ltr"},
        "ru": {"name": "Русский", "dir": "ltr"},
        "ko": {"name": "한국어", "dir": "ltr"}
    }

    def __init__(self, source_dir: str, output_dir: str, languages: List[str]):
        self.source_dir = Path(source_dir)
        self.output_dir = Path(output_dir)
        self.languages = languages

        # Validate languages
        for lang in languages:
            if lang not in self.LANGUAGES:
                raise ValueError(f"Unsupported language: {lang}")

    def generate(self):
        """Generate documentation for all languages"""
        print(f"📚 Generating documentation for {len(self.languages)} languages...")

        for lang in self.languages:
            print(f"\n🌐 Processing language: {self.LANGUAGES[lang]['name']} ({lang})")
            self._generate_language(lang)

        self._generate_index()
        print(f"\n✅ Documentation generated successfully!")
        print(f"   Output directory: {self.output_dir}")

    def _generate_language(self, lang: str):
        """Generate documentation for a specific language"""
        lang_dir = self.output_dir / lang
        lang_dir.mkdir(parents=True, exist_ok=True)

        # Copy source files (English) or generate translated versions
        if lang == "en":
            # Copy English files
            self._copy_docs(self.source_dir, lang_dir)
        else:
            # Generate translated files
            self._generate_translated_docs(lang_dir, lang)

        # Generate language-specific index
        self._generate_language_index(lang_dir, lang)

        print(f"   ✓ Generated {lang} documentation at {lang_dir}")

    def _copy_docs(self, source: Path, dest: Path):
        """Copy documentation files from source to destination"""
        if not source.exists():
            print(f"   ⚠ Source directory not found: {source}")
            print(f"   Creating sample documentation...")
            self._create_sample_docs(dest)
            return

        # Copy markdown files
        for md_file in source.glob("**/*.md"):
            if "node_modules" in str(md_file) or ".git" in str(md_file):
                continue

            relative_path = md_file.relative_to(source)
            dest_file = dest / relative_path
            dest_file.parent.mkdir(parents=True, exist_ok=True)

            shutil.copy2(md_file, dest_file)

    def _create_sample_docs(self, dest: Path):
        """Create sample documentation structure"""
        sample_readme = dest / "README.md"
        sample_readme.write_text("""# Documentation

Welcome to the documentation!

## Table of Contents

- [Getting Started](getting-started.md)
- [API Reference](api/reference.md)
- [Guides](guides/index.md)

## Quick Start

Get started with this project in 5 minutes!

## Support

For help, visit our [support page](support.md).
""")

        # Create getting started
        getting_started = dest / "getting-started.md"
        getting_started.write_text("""# Getting Started

## Installation

```bash
npm install your-package
```

## Basic Usage

```javascript
const client = new Client();
const result = client.doSomething();
```

## Next Steps

- Read the [API Reference](api/reference.md)
- Check out [examples](examples.md)
""")

        # Create API directory
        api_dir = dest / "api"
        api_dir.mkdir(exist_ok=True)

        api_ref = api_dir / "reference.md"
        api_ref.write_text("""# API Reference

## Client

### Constructor

```javascript
new Client(options)
```

### Methods

#### doSomething()

Does something useful.

**Returns:** Result object
""")

    def _generate_translated_docs(self, lang_dir: Path, lang: str):
        """Generate translated documentation using translation backend"""
        lang_name = self.LANGUAGES[lang]["name"]

        # Check if source docs exist
        if not self.source_dir.exists():
            print(f"   ⚠ Source directory not found: {self.source_dir}")
            self._create_translation_placeholder(lang_dir, lang)
            return

        # Try to translate markdown files
        translated_count = 0
        for md_file in self.source_dir.glob("**/*.md"):
            if "node_modules" in str(md_file) or ".git" in str(md_file):
                continue

            try:
                content = md_file.read_text()
                relative_path = md_file.relative_to(self.source_dir)
                dest_file = lang_dir / relative_path
                dest_file.parent.mkdir(parents=True, exist_ok=True)

                # Translate the content
                translated_content = self._translate_markdown(content, lang)
                dest_file.write_text(translated_content)
                translated_count += 1

            except Exception as e:
                print(f"   ⚠ Failed to translate {md_file.name}: {e}")
                continue

        if translated_count > 0:
            print(f"   ✓ Translated {translated_count} files")
        else:
            print(f"   ⚠ No files could be translated, creating placeholder")
            self._create_translation_placeholder(lang_dir, lang)

    def _create_translation_placeholder(self, lang_dir: Path, lang: str):
        """Create placeholder when translation is not available"""
        lang_name = self.LANGUAGES[lang]["name"]

        readme = lang_dir / "README.md"
        readme.write_text(f"""# Documentation ({lang_name})

⚠️ **Translation in progress**

This documentation is being translated to {lang_name}.

English version is available in the [en](../en/) directory.

## Table of Contents

- Getting Started
- API Reference
- Guides

---

To contribute to translations, please see [Translation Guide](../TRANSLATION.md)
""")

    def _translate_markdown(self, content: str, target_lang: str) -> str:
        """Translate markdown content preserving structure and code blocks"""
        # Try different translation backends in order of preference
        try:
            return self._translate_with_deepl(content, target_lang)
        except Exception as e:
            print(f"   ⚠ DeepL translation failed: {e}")

        try:
            return self._translate_with_google(content, target_lang)
        except Exception as e:
            print(f"   ⚠ Google Translate failed: {e}")

        try:
            return self._translate_with_openai(content, target_lang)
        except Exception as e:
            print(f"   ⚠ OpenAI translation failed: {e}")

        # If all backends fail, return content with translation note
        return self._add_translation_note(content, target_lang)

    def _translate_with_deepl(self, content: str, target_lang: str) -> str:
        """Translate using DeepL API"""
        try:
            import deepl
            import os

            auth_key = os.environ.get("DEEPL_AUTH_KEY")
            if not auth_key:
                raise ValueError("DEEPL_AUTH_KEY environment variable not set")

            translator = deepl.Translator(auth_key)

            # Extract and preserve code blocks
            preserved_blocks, clean_content = self._extract_code_blocks(content)

            # Translate the clean content
            result = translator.translate_text(
                clean_content,
                target_lang=target_lang.upper()
            )

            # Restore code blocks
            translated = self._restore_code_blocks(str(result), preserved_blocks)
            return translated

        except ImportError:
            raise ValueError("deepl package not installed. Install with: pip install deepl")

    def _translate_with_google(self, content: str, target_lang: str) -> str:
        """Translate using Google Translate API"""
        try:
            from google.cloud import translate_v2 as translate
            import os

            if not os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"):
                raise ValueError("GOOGLE_APPLICATION_CREDENTIALS environment variable not set")

            client = translate.Client()

            # Extract and preserve code blocks
            preserved_blocks, clean_content = self._extract_code_blocks(content)

            # Translate in chunks to avoid size limits
            result = client.translate(
                clean_content,
                target_language=target_lang,
                format_="text"
            )

            translated = result["translatedText"]

            # Restore code blocks
            translated = self._restore_code_blocks(translated, preserved_blocks)
            return translated

        except ImportError:
            raise ValueError("google-cloud-translate package not installed. Install with: pip install google-cloud-translate")

    def _translate_with_openai(self, content: str, target_lang: str) -> str:
        """Translate using OpenAI API"""
        try:
            import openai
            import os

            api_key = os.environ.get("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY environment variable not set")

            openai.api_key = api_key

            lang_name = self.LANGUAGES[target_lang]["name"]

            # Extract and preserve code blocks
            preserved_blocks, clean_content = self._extract_code_blocks(content)

            # Use OpenAI to translate
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": f"You are a technical documentation translator. Translate the following markdown documentation to {lang_name}. Preserve all markdown formatting, technical terms, and code placeholders exactly as they appear."
                    },
                    {
                        "role": "user",
                        "content": clean_content
                    }
                ],
                temperature=0.3
            )

            translated = response.choices[0].message.content

            # Restore code blocks
            translated = self._restore_code_blocks(translated, preserved_blocks)
            return translated

        except ImportError:
            raise ValueError("openai package not installed. Install with: pip install openai")

    def _extract_code_blocks(self, content: str) -> tuple:
        """Extract code blocks and other non-translatable content"""
        import re

        preserved = []
        placeholder_pattern = "<<<CODE_BLOCK_{}>>>"

        # Find all code blocks
        code_pattern = r'```[\s\S]*?```'
        matches = list(re.finditer(code_pattern, content))

        clean_content = content
        for i, match in enumerate(reversed(matches)):
            preserved.insert(0, match.group(0))
            placeholder = placeholder_pattern.format(len(matches) - 1 - i)
            clean_content = clean_content[:match.start()] + placeholder + clean_content[match.end():]

        # Also preserve inline code
        inline_pattern = r'`[^`]+`'
        matches = list(re.finditer(inline_pattern, clean_content))

        for i, match in enumerate(reversed(matches)):
            preserved.insert(0, match.group(0))
            placeholder = f"<<<INLINE_CODE_{len(matches) - 1 - i}>>>"
            clean_content = clean_content[:match.start()] + placeholder + clean_content[match.end():]

        return preserved, clean_content

    def _restore_code_blocks(self, content: str, preserved: list) -> str:
        """Restore preserved code blocks"""
        import re

        result = content

        # Restore code blocks
        for i, block in enumerate(preserved):
            if block.startswith('```'):
                placeholder = f"<<<CODE_BLOCK_{i}>>>"
                result = result.replace(placeholder, block)
            elif block.startswith('`'):
                placeholder = f"<<<INLINE_CODE_{i}>>>"
                result = result.replace(placeholder, block)

        return result

    def _add_translation_note(self, content: str, target_lang: str) -> str:
        """Add translation note when automatic translation fails"""
        lang_name = self.LANGUAGES[target_lang]["name"]

        note = f"""---
**⚠️ Translation Note**

This content is not yet translated to {lang_name}.
To enable automatic translation, set up one of:
- DeepL: Set DEEPL_AUTH_KEY environment variable
- Google Translate: Set GOOGLE_APPLICATION_CREDENTIALS
- OpenAI: Set OPENAI_API_KEY environment variable

---

"""
        return note + content

    def _generate_language_index(self, lang_dir: Path, lang: str):
        """Generate index file for a language"""
        index_file = lang_dir / "index.md"

        lang_name = self.LANGUAGES[lang]["name"]
        direction = self.LANGUAGES[lang]["dir"]

        # Find all markdown files
        md_files = sorted(lang_dir.glob("**/*.md"))
        md_files = [f for f in md_files if f.name != "index.md"]

        content = [
            f"# Documentation Index - {lang_name}\n",
            f"Language: {lang_name} ({lang})\n",
            f"Text Direction: {direction}\n",
            "\n## Available Documents\n"
        ]

        for md_file in md_files:
            relative_path = md_file.relative_to(lang_dir)
            title = relative_path.stem.replace("_", " ").replace("-", " ").title()
            content.append(f"- [{title}]({relative_path})")

        index_file.write_text("\n".join(content))

    def _generate_index(self):
        """Generate main index with language selector"""
        index_file = self.output_dir / "index.md"

        content = [
            "# Documentation - Language Selection\n",
            "Select your language:\n"
        ]

        for lang in self.languages:
            lang_name = self.LANGUAGES[lang]["name"]
            content.append(f"- [{lang_name}]({lang}/README.md) ({lang})")

        content.append("\n---\n")
        content.append("*Documentation available in multiple languages*")

        index_file.write_text("\n".join(content))

        # Also create a metadata file
        metadata = {
            "languages": [
                {
                    "code": lang,
                    "name": self.LANGUAGES[lang]["name"],
                    "direction": self.LANGUAGES[lang]["dir"],
                    "default": self.LANGUAGES[lang].get("default", False)
                }
                for lang in self.languages
            ],
            "generated_at": "auto-generated"
        }

        metadata_file = self.output_dir / "languages.json"
        metadata_file.write_text(json.dumps(metadata, indent=2))


class TranslationHelper:
    """Helper for managing translations"""

    @staticmethod
    def extract_translatable_strings(md_content: str) -> List[str]:
        """Extract strings that need translation from markdown"""
        # This is a simplified version
        # In practice, you'd want to:
        # - Skip code blocks
        # - Handle inline code differently
        # - Preserve markdown formatting
        # - Extract only prose content

        lines = md_content.split("\n")
        translatable = []
        in_code_block = False

        for line in lines:
            # Toggle code block state
            if line.strip().startswith("```"):
                in_code_block = not in_code_block
                continue

            # Skip code blocks
            if in_code_block:
                continue

            # Skip empty lines
            if not line.strip():
                continue

            # Skip pure markdown syntax lines
            if line.strip().startswith("#") or line.strip().startswith("-"):
                translatable.append(line)
            elif line.strip():
                translatable.append(line)

        return translatable

    @staticmethod
    def create_translation_template(source_dir: Path, output_file: Path):
        """Create a translation template file"""
        translations = {}

        for md_file in source_dir.glob("**/*.md"):
            if "node_modules" in str(md_file):
                continue

            content = md_file.read_text()
            strings = TranslationHelper.extract_translatable_strings(content)

            relative_path = str(md_file.relative_to(source_dir))
            translations[relative_path] = {
                "source": strings,
                "translated": [""] * len(strings)  # Empty translations
            }

        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(json.dumps(translations, indent=2, ensure_ascii=False))

        print(f"✅ Translation template created: {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate documentation in multiple languages"
    )
    parser.add_argument(
        "--languages",
        required=True,
        help="Comma-separated list of language codes (e.g., en,es,fr)"
    )
    parser.add_argument(
        "--source",
        default="docs",
        help="Source documentation directory (default: docs)"
    )
    parser.add_argument(
        "--output",
        default="docs/i18n",
        help="Output directory (default: docs/i18n)"
    )
    parser.add_argument(
        "--create-template",
        action="store_true",
        help="Create translation template instead of generating docs"
    )

    args = parser.parse_args()

    # Parse languages
    languages = [lang.strip() for lang in args.languages.split(",")]

    if args.create_template:
        # Create translation template
        output_file = Path(args.output) / "translation_template.json"
        TranslationHelper.create_translation_template(
            Path(args.source),
            output_file
        )
    else:
        # Generate documentation
        generator = DocumentationGenerator(
            args.source,
            args.output,
            languages
        )
        generator.generate()


if __name__ == "__main__":
    main()