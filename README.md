# rendergitmd

Aggregate a git codebase into a single markdown file with syntax highlighting, similar to [karpathy's rendergit](https://github.com/karpathy/rendergit).

## Features

- 📝 Converts entire git repositories into a single markdown file
- 🎨 Automatic syntax highlighting based on file extensions (supports 50+ languages)
- 📋 YAML frontmatter with repository metadata (origin URL, branch, commit, author)
- 📄 Page separators (`---`) between files
- 🔗 Table of contents with anchor links
- 🚫 Smart ignore patterns (node_modules, .git, build artifacts, etc.)
- 📦 Handles binary files gracefully
- ⚡ Configurable file size limits

## Installation

Simply clone this repository and make the script executable:

```bash
git clone <repository-url>
cd rendergitmd
chmod +x rendergitmd.py
```

Or use it directly with Python:

```bash
python3 rendergitmd.py
```

## Usage

### Basic usage

Generate markdown from current directory:

```bash
python3 rendergitmd.py
```

This creates `repository.md` in the current directory.

### Specify repository path

```bash
python3 rendergitmd.py /path/to/repo
```

### Custom output file

```bash
python3 rendergitmd.py -o output.md
```

### Additional ignore patterns

```bash
python3 rendergitmd.py -i "*.log" -i "temp/*"
```

### Disable default ignore patterns

```bash
python3 rendergitmd.py --no-default-ignore
```

### Set maximum file size (in KB)

```bash
python3 rendergitmd.py --max-size 2048
```

## Output Format

The generated markdown file includes:

1. **YAML Frontmatter** with repository metadata:
   ```yaml
   ---
   title: repository-name
   repository: https://github.com/user/repo
   branch: main
   commit: abc12345
   author: John Doe <john@example.com>
   date: 2025-01-15 10:30:00 +0000
   files: 42
   ---
   ```

2. **Table of Contents** with clickable links to each file

3. **File Contents** with proper syntax highlighting:
   ````markdown
   ## src/index.ts

   ```typescript
   const greeting: string = "Hello, World!";
   console.log(greeting);
   ```

   ---

   ## README.md

   ```markdown
   # My Project
   ...
   ```
   ````

## Supported Languages

The tool automatically detects and applies syntax highlighting for 50+ languages including:

- **Web**: JavaScript, TypeScript, JSX, TSX, HTML, CSS, SCSS, Vue, Svelte
- **Backend**: Python, Java, Go, Rust, C, C++, C#, PHP, Ruby
- **Config**: JSON, YAML, TOML, XML, Dockerfile, Terraform
- **And many more!**

## Default Ignore Patterns

The tool ignores common development artifacts by default:

- `.git`, `__pycache__`, `node_modules`
- `.venv`, `venv`, `dist`, `build`, `target`
- Lock files (`package-lock.json`, `yarn.lock`, etc.)
- IDE folders (`.idea`, `.vscode`)
- Binary artifacts (`*.pyc`, `*.min.js`, etc.)

## Example

```bash
# Generate markdown for the current repository
python3 rendergitmd.py -o my-codebase.md

# With custom ignore patterns
python3 rendergitmd.py -o output.md -i "*.test.js" -i "docs/*"
```

## Use Cases

- 📤 Sharing codebases with AI assistants (Claude, GPT, etc.)
- 📚 Creating documentation snapshots
- 👀 Code reviews in markdown-friendly platforms
- 📖 Archiving project states
- 🎓 Educational purposes (sharing code examples)

## License

MIT

## Credits

Inspired by [karpathy/rendergit](https://github.com/karpathy/rendergit)
