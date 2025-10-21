#!/usr/bin/env python3
"""
Interactive Tutorial Generator

Creates step-by-step tutorials with code examples and exercises.

Usage:
    python generate_tutorial.py --topic "Getting Started" --language python
    python generate_tutorial.py --topic "Authentication" --language javascript --output tutorials/
"""

import argparse
from pathlib import Path
from typing import Dict


class TutorialGenerator:
    """Generate interactive tutorials"""

    TUTORIAL_TEMPLATES = {
        "getting_started": {
            "title": "Getting Started",
            "sections": [
                "Prerequisites",
                "Installation",
                "Your First Application",
                "Understanding the Basics",
                "Next Steps"
            ]
        },
        "authentication": {
            "title": "Authentication Guide",
            "sections": [
                "Authentication Overview",
                "Setting Up Auth",
                "Implementing Login",
                "Protected Routes",
                "Best Practices"
            ]
        },
        "api_usage": {
            "title": "API Usage Guide",
            "sections": [
                "API Overview",
                "Making Your First Request",
                "Handling Responses",
                "Error Handling",
                "Advanced Usage"
            ]
        }
    }

    def __init__(self, topic: str, language: str):
        self.topic = topic
        self.language = language
        self.template = self._select_template(topic)

    def _select_template(self, topic: str) -> Dict:
        """Select appropriate template based on topic"""
        topic_key = topic.lower().replace(" ", "_")
        return self.TUTORIAL_TEMPLATES.get(
            topic_key,
            self.TUTORIAL_TEMPLATES["getting_started"]
        )

    def generate(self) -> str:
        """Generate complete tutorial"""
        # Title and introduction
        sections = [
            f"# {self.template['title']}\n",
            self._generate_introduction()
        ]

        # Generate each section
        for i, section_title in enumerate(self.template['sections'], 1):
            sections.append(f"## {i}. {section_title}\n")
            sections.append(self._generate_section(section_title))

        # Add conclusion
        sections.append(self._generate_conclusion())

        return "\n".join(sections)

    def _generate_introduction(self) -> str:
        """Generate tutorial introduction"""
        return f"""
Welcome to this interactive tutorial! In this guide, you'll learn about {self.topic.lower()}.

**What you'll learn:**
- Core concepts and terminology
- Practical, hands-on examples
- Best practices and common patterns
- How to avoid common pitfalls

**Estimated time:** 15-20 minutes

Let's get started! 🚀
"""

    def _generate_section(self, section_title: str) -> str:
        """Generate content for a specific section"""
        content = []

        if "Prerequisites" in section_title:
            content.append(self._generate_prerequisites())

        elif "Installation" in section_title:
            content.append(self._generate_installation())

        elif "First" in section_title or "Basics" in section_title:
            content.append(self._generate_first_example())

        elif "Understanding" in section_title:
            content.append(self._generate_explanation())

        elif "Next Steps" in section_title or "Advanced" in section_title:
            content.append(self._generate_next_steps())

        else:
            content.append(self._generate_generic_section(section_title))

        return "\n".join(content)

    def _generate_prerequisites(self) -> str:
        """Generate prerequisites section"""
        if self.language == "python":
            return """
Before starting, make sure you have:

- Python 3.8 or higher installed
- pip package manager
- A code editor (VS Code, PyCharm, etc.)
- Basic Python knowledge

**Check your Python version:**
```bash
python --version
```

Expected output: `Python 3.8.0` or higher
"""
        elif self.language == "javascript":
            return """
Before starting, make sure you have:

- Node.js 14 or higher installed
- npm or yarn package manager
- A code editor (VS Code, WebStorm, etc.)
- Basic JavaScript knowledge

**Check your Node.js version:**
```bash
node --version
```

Expected output: `v14.0.0` or higher
"""
        else:
            return "Prerequisites for this tutorial will be covered in the setup section.\n"

    def _generate_installation(self) -> str:
        """Generate installation instructions"""
        if self.language == "python":
            return """
### Install Required Packages

Create a new project directory and install dependencies:

```bash
mkdir my-project
cd my-project
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate
pip install -r requirements.txt
```

**Create requirements.txt:**
```text
flask==2.3.0
requests==2.31.0
```

**Verify installation:**
```bash
pip list
```

You should see Flask and requests in the output.
"""
        elif self.language == "javascript":
            return """
### Install Required Packages

Create a new project and install dependencies:

```bash
mkdir my-project
cd my-project
npm init -y
npm install express axios
```

**Verify installation:**
```bash
npm list --depth=0
```

You should see express and axios in the output.
"""
        else:
            return "Installation instructions will vary based on your environment.\n"

    def _generate_first_example(self) -> str:
        """Generate first working example"""
        if self.language == "python":
            return """
### Your First Application

Let's create a simple "Hello World" application:

**Create `app.py`:**
```python
from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return {'message': 'Hello, World!'}

if __name__ == '__main__':
    app.run(debug=True)
```

**Run the application:**
```bash
python app.py
```

**Test it:**
Open your browser and navigate to `http://localhost:5000`

You should see: `{"message": "Hello, World!"}`

✅ **Success!** You've created your first application!

**What's happening here?**
1. We import Flask and create an app instance
2. We define a route `/` that returns JSON
3. We run the app in debug mode
"""
        elif self.language == "javascript":
            return """
### Your First Application

Let's create a simple "Hello World" server:

**Create `server.js`:**
```javascript
const express = require('express');
const app = express();
const PORT = 3000;

app.get('/', (req, res) => {
  res.json({ message: 'Hello, World!' });
});

app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
});
```

**Run the server:**
```bash
node server.js
```

**Test it:**
Open your browser and navigate to `http://localhost:3000`

You should see: `{"message":"Hello, World!"}`

✅ **Success!** You've created your first server!

**What's happening here?**
1. We import Express and create an app instance
2. We define a GET route `/` that returns JSON
3. We start the server on port 3000
"""
        else:
            return "Example code will be provided for your specific language.\n"

    @staticmethod
    def _generate_explanation() -> str:
        """Generate explanation of concepts"""
        return """
### Key Concepts

Let's break down the important concepts:

**1. Routes**
Routes define how your application responds to client requests. Each route has:
- A path (e.g., `/`, `/users`, `/api/data`)
- An HTTP method (GET, POST, PUT, DELETE)
- A handler function that processes the request

**2. Request and Response**
- **Request**: Contains data sent by the client (params, query, body)
- **Response**: What you send back to the client (JSON, HTML, etc.)

**3. Middleware** (if applicable)
Functions that process requests before they reach your route handlers.

**💡 Pro Tip:** Start simple and add complexity gradually!
"""

    @staticmethod
    def _generate_next_steps() -> str:
        """Generate next steps section"""
        return """
### Where to Go From Here

Congratulations! You've completed this tutorial. Here's what to explore next:

**Recommended Next Steps:**
1. 📚 **Read the full documentation** - Dive deeper into advanced features
2. 🔨 **Build a project** - Apply what you've learned in a real application
3. 🤝 **Join the community** - Connect with other developers
4. 📖 **Explore tutorials** - Check out advanced tutorials

**Additional Resources:**
- Official documentation: [link]
- Community forum: [link]
- GitHub examples: [link]
- Video tutorials: [link]

**Challenge yourself:**
Try modifying the example to add new features!

Happy coding! 🎉
"""

    @staticmethod
    def _generate_generic_section(section_title: str) -> str:
        """Generate generic section content"""
        return f"""
This section covers {section_title.lower()}.

[Content for {section_title} would be generated based on the specific topic]

"""

    @staticmethod
    def _generate_conclusion() -> str:
        """Generate tutorial conclusion"""
        return """
## Summary

In this tutorial, you learned:

- ✅ How to set up your development environment
- ✅ Creating your first application
- ✅ Understanding core concepts
- ✅ Best practices and next steps

**Remember:** Practice is key! The more you build, the better you'll become.

**Need help?** Don't hesitate to:
- Check the documentation
- Ask in the community forum
- Review example projects

Good luck with your projects! 🚀
"""


def main():
    parser = argparse.ArgumentParser(description="Generate interactive tutorials")
    parser.add_argument("--topic", required=True, help="Tutorial topic")
    parser.add_argument("--language", choices=["python", "javascript", "typescript", "java"],
                        default="python", help="Programming language")
    parser.add_argument("--output", default="tutorials", help="Output directory")

    args = parser.parse_args()

    # Create output directory
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate tutorial
    generator = TutorialGenerator(args.topic, args.language)
    tutorial_content = generator.generate()

    # Save to file
    filename = args.topic.lower().replace(" ", "_")
    output_file = output_dir / f"{filename}_{args.language}.md"
    output_file.write_text(tutorial_content)

    print(f"✅ Tutorial generated: {output_file}")
    print(f"   Topic: {args.topic}")
    print(f"   Language: {args.language}")


if __name__ == "__main__":
    main()
