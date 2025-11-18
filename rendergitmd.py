#!/usr/bin/env python3
"""
rendergitmd - Aggregate a git codebase into a markdown file
Similar to karpathy's rendergit but outputs markdown with proper syntax highlighting
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path
from typing import List, Dict, Optional
import fnmatch


# Extension to markdown syntax highlighting mapping
EXTENSION_MAP = {
    '.py': 'python',
    '.js': 'javascript',
    '.jsx': 'jsx',
    '.ts': 'typescript',
    '.tsx': 'tsx',
    '.java': 'java',
    '.c': 'c',
    '.cpp': 'cpp',
    '.cc': 'cpp',
    '.cxx': 'cpp',
    '.h': 'c',
    '.hpp': 'cpp',
    '.cs': 'csharp',
    '.go': 'go',
    '.rs': 'rust',
    '.rb': 'ruby',
    '.php': 'php',
    '.swift': 'swift',
    '.kt': 'kotlin',
    '.scala': 'scala',
    '.sh': 'bash',
    '.bash': 'bash',
    '.zsh': 'zsh',
    '.fish': 'fish',
    '.ps1': 'powershell',
    '.r': 'r',
    '.R': 'r',
    '.m': 'matlab',
    '.sql': 'sql',
    '.html': 'html',
    '.htm': 'html',
    '.xml': 'xml',
    '.css': 'css',
    '.scss': 'scss',
    '.sass': 'sass',
    '.less': 'less',
    '.json': 'json',
    '.yaml': 'yaml',
    '.yml': 'yaml',
    '.toml': 'toml',
    '.ini': 'ini',
    '.cfg': 'ini',
    '.conf': 'conf',
    '.md': 'markdown',
    '.markdown': 'markdown',
    '.rst': 'rst',
    '.tex': 'latex',
    '.vim': 'vim',
    '.lua': 'lua',
    '.pl': 'perl',
    '.hs': 'haskell',
    '.ex': 'elixir',
    '.exs': 'elixir',
    '.erl': 'erlang',
    '.clj': 'clojure',
    '.elm': 'elm',
    '.ml': 'ocaml',
    '.fs': 'fsharp',
    '.dart': 'dart',
    '.vue': 'vue',
    '.svelte': 'svelte',
    '.sol': 'solidity',
    '.proto': 'protobuf',
    '.graphql': 'graphql',
    '.gql': 'graphql',
    '.dockerfile': 'dockerfile',
    '.tf': 'terraform',
    '.hcl': 'hcl',
    '.nix': 'nix',
    '.zig': 'zig',
    '.v': 'v',
}

# Default patterns to ignore
DEFAULT_IGNORE_PATTERNS = [
    '.git',
    '__pycache__',
    'node_modules',
    '.venv',
    'venv',
    '.env',
    '*.pyc',
    '*.pyo',
    '*.pyd',
    '.DS_Store',
    'Thumbs.db',
    '*.swp',
    '*.swo',
    '*~',
    '.idea',
    '.vscode',
    '*.min.js',
    '*.min.css',
    'dist',
    'build',
    'target',
    '*.lock',
    'package-lock.json',
    'yarn.lock',
    'poetry.lock',
    'Cargo.lock',
    'Pipfile.lock',
]


def get_git_info(repo_path: str) -> Dict[str, str]:
    """Extract git repository information"""
    info = {}

    try:
        # Get remote origin URL
        result = subprocess.run(
            ['git', 'config', '--get', 'remote.origin.url'],
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=True
        )
        info['origin_url'] = result.stdout.strip()
    except subprocess.CalledProcessError:
        info['origin_url'] = 'N/A'

    try:
        # Get current branch
        result = subprocess.run(
            ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=True
        )
        info['branch'] = result.stdout.strip()
    except subprocess.CalledProcessError:
        info['branch'] = 'N/A'

    try:
        # Get latest commit hash
        result = subprocess.run(
            ['git', 'rev-parse', 'HEAD'],
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=True
        )
        info['commit'] = result.stdout.strip()[:8]
    except subprocess.CalledProcessError:
        info['commit'] = 'N/A'

    try:
        # Get author of latest commit
        result = subprocess.run(
            ['git', 'log', '-1', '--format=%an <%ae>'],
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=True
        )
        info['author'] = result.stdout.strip()
    except subprocess.CalledProcessError:
        info['author'] = 'N/A'

    try:
        # Get commit date
        result = subprocess.run(
            ['git', 'log', '-1', '--format=%ai'],
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=True
        )
        info['date'] = result.stdout.strip()
    except subprocess.CalledProcessError:
        info['date'] = 'N/A'

    return info


def should_ignore(file_path: str, ignore_patterns: List[str]) -> bool:
    """Check if file should be ignored based on patterns"""
    path_parts = Path(file_path).parts

    for pattern in ignore_patterns:
        # Check if any part of the path matches the pattern
        for part in path_parts:
            if fnmatch.fnmatch(part, pattern):
                return True
        # Also check the full relative path
        if fnmatch.fnmatch(file_path, pattern):
            return True

    return False


def get_language_hint(file_path: str) -> str:
    """Get markdown language hint for code block based on file extension"""
    ext = Path(file_path).suffix.lower()

    # Special case for Dockerfile
    if Path(file_path).name.lower() in ['dockerfile', 'dockerfile.dev', 'dockerfile.prod']:
        return 'dockerfile'

    # Special case for Makefile
    if Path(file_path).name.lower() in ['makefile', 'gnumakefile']:
        return 'makefile'

    return EXTENSION_MAP.get(ext, '')


def collect_files(repo_path: str, ignore_patterns: List[str]) -> List[str]:
    """Collect all files in the repository that should be included"""
    files = []
    repo_path = Path(repo_path)

    for root, dirs, filenames in os.walk(repo_path):
        # Modify dirs in-place to skip ignored directories
        dirs[:] = [d for d in dirs if not should_ignore(d, ignore_patterns)]

        for filename in filenames:
            file_path = Path(root) / filename
            relative_path = file_path.relative_to(repo_path)

            if not should_ignore(str(relative_path), ignore_patterns):
                files.append(str(relative_path))

    return sorted(files)


def is_binary(file_path: str) -> bool:
    """Check if a file is binary"""
    try:
        with open(file_path, 'rb') as f:
            chunk = f.read(1024)
            return b'\0' in chunk
    except Exception:
        return True


def group_files_by_depth(files: List[str], depth: int) -> Dict[str, List[str]]:
    """
    Group files by directory at the specified depth level.

    depth=0: All files in one group
    depth=1: Group by top-level directory
    depth=2: Group by second-level directory, etc.

    Returns dict mapping group names to file lists.
    """
    if depth == 0:
        return {'': files}  # Empty string means all files in root output

    groups = {}

    for file_path in files:
        parts = Path(file_path).parts

        if len(parts) <= depth:
            # File is at a shallower level than depth
            # Put it in the group for its deepest directory, or root if it's at the root
            if len(parts) == 1:
                # Root level file
                group_name = ''
            else:
                # Use all parts up to the file as the group
                group_name = '/'.join(parts[:-1])
        else:
            # File is deeper than depth - group by path at depth level
            group_name = '/'.join(parts[:depth])

        if group_name not in groups:
            groups[group_name] = []
        groups[group_name].append(file_path)

    return groups


def sanitize_filename(name: str) -> str:
    """Convert a path/name into a safe filename"""
    if not name:
        return 'root'
    return name.replace('/', '-').replace('\\', '-')


def write_file_section(out, repo_path: Path, file_path: str, max_file_size: int,
                       include_separator: bool = True) -> None:
    """Write a single file section to the output"""
    full_path = repo_path / file_path

    # Create anchor
    anchor = file_path.replace('/', '-').replace('.', '-').replace('_', '-').lower()

    # Write file header
    out.write(f"## {file_path}\n\n")
    out.write(f'<a id="{anchor}"></a>\n\n')

    # Check if file is binary
    if is_binary(str(full_path)):
        out.write('*Binary file*\n\n')
    else:
        try:
            # Check file size
            file_size = full_path.stat().st_size
            if file_size > max_file_size:
                out.write(f'*File too large ({file_size / 1024 / 1024:.2f} MB), skipped*\n\n')
            else:
                # Read file content
                with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                # Get language hint
                lang_hint = get_language_hint(file_path)

                # Write code block
                out.write(f'```{lang_hint}\n')
                out.write(content)
                if not content.endswith('\n'):
                    out.write('\n')
                out.write('```\n\n')
        except Exception as e:
            out.write(f'*Error reading file: {e}*\n\n')

    # Add page separator
    if include_separator:
        out.write('---\n\n')


def generate_hierarchical_markdown(repo_path: str, output_base: str, ignore_patterns: List[str],
                                   max_file_size: int, depth: int) -> None:
    """Generate multiple markdown files organized by directory depth"""
    repo_path = Path(repo_path).resolve()

    # Get git info
    git_info = get_git_info(str(repo_path))

    # Collect files
    print(f"Scanning repository: {repo_path}")
    files = collect_files(repo_path, ignore_patterns)
    print(f"Found {len(files)} files to include")

    # Group files by depth
    groups = group_files_by_depth(files, depth)
    print(f"Grouped into {len(groups)} sections at depth {depth}")

    # Determine output directory and base name
    output_path = Path(output_base)
    if output_path.suffix == '.md':
        # User specified a file like 'repo.md', use its directory and stem
        output_dir = output_path.parent
        base_name = output_path.stem
    else:
        # User specified a directory or no extension
        output_dir = output_path
        base_name = 'repository'

    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate index file
    index_file = output_dir / f"{base_name}.md"
    subfiles = []

    with open(index_file, 'w', encoding='utf-8') as idx:
        # Write frontmatter
        idx.write('---\n')
        idx.write(f"title: {repo_path.name}\n")
        idx.write(f"repository: {git_info['origin_url']}\n")
        idx.write(f"branch: {git_info['branch']}\n")
        idx.write(f"commit: {git_info['commit']}\n")
        idx.write(f"author: {git_info['author']}\n")
        idx.write(f"date: {git_info['date']}\n")
        idx.write(f"files: {len(files)}\n")
        idx.write(f"depth: {depth}\n")
        idx.write('---\n\n')

        idx.write(f"# {repo_path.name}\n\n")
        idx.write("This repository has been split into multiple files for easier navigation.\n\n")

        # If depth > 0, write links to subfiles
        if depth > 0:
            idx.write("## Sections\n\n")

            for group_name in sorted(groups.keys()):
                group_files = groups[group_name]
                subfile_name = f"{base_name}-{sanitize_filename(group_name)}.md"
                subfiles.append((group_name, subfile_name, group_files))

                display_name = group_name if group_name else '(root files)'
                idx.write(f"- [{display_name}](./{subfile_name}) ({len(group_files)} files)\n")

            idx.write('\n')
        else:
            # depth == 0, write everything in index file
            idx.write("## Table of Contents\n\n")
            for file_path in files:
                anchor = file_path.replace('/', '-').replace('.', '-').replace('_', '-').lower()
                idx.write(f"- [{file_path}](#{anchor})\n")
            idx.write('\n')

            # Write all files
            for i, file_path in enumerate(files):
                write_file_section(idx, repo_path, file_path, max_file_size,
                                 include_separator=(i < len(files) - 1))

    print(f"Generated index: {index_file}")

    # Generate subfiles if depth > 0
    if depth > 0:
        for group_name, subfile_name, group_files in subfiles:
            subfile_path = output_dir / subfile_name

            with open(subfile_path, 'w', encoding='utf-8') as sub:
                # Write frontmatter
                sub.write('---\n')
                sub.write(f"title: {repo_path.name} - {group_name or 'root'}\n")
                sub.write(f"section: {group_name or 'root'}\n")
                sub.write(f"files: {len(group_files)}\n")
                sub.write('---\n\n')

                # Link back to index
                sub.write(f"[← Back to index](./{base_name}.md)\n\n")

                sub.write(f"# {group_name or '(root files)'}\n\n")

                # Table of contents
                sub.write("## Table of Contents\n\n")
                for file_path in group_files:
                    anchor = file_path.replace('/', '-').replace('.', '-').replace('_', '-').lower()
                    sub.write(f"- [{file_path}](#{anchor})\n")
                sub.write('\n')

                # Write files
                for i, file_path in enumerate(group_files):
                    write_file_section(sub, repo_path, file_path, max_file_size,
                                     include_separator=(i < len(group_files) - 1))

            print(f"Generated: {subfile_path}")


def generate_markdown(repo_path: str, output_file: str, ignore_patterns: List[str],
                     max_file_size: int = 1024 * 1024) -> None:
    """Generate markdown file from git repository"""
    repo_path = Path(repo_path).resolve()

    # Get git info
    git_info = get_git_info(str(repo_path))

    # Collect files
    print(f"Scanning repository: {repo_path}")
    files = collect_files(repo_path, ignore_patterns)
    print(f"Found {len(files)} files to include")

    # Generate markdown
    with open(output_file, 'w', encoding='utf-8') as out:
        # Write frontmatter
        out.write('---\n')
        out.write(f"title: {repo_path.name}\n")
        out.write(f"repository: {git_info['origin_url']}\n")
        out.write(f"branch: {git_info['branch']}\n")
        out.write(f"commit: {git_info['commit']}\n")
        out.write(f"author: {git_info['author']}\n")
        out.write(f"date: {git_info['date']}\n")
        out.write(f"files: {len(files)}\n")
        out.write('---\n\n')

        # Write table of contents
        out.write('# Table of Contents\n\n')
        for file_path in files:
            # Create anchor link (replace special chars with hyphens)
            anchor = file_path.replace('/', '-').replace('.', '-').replace('_', '-').lower()
            out.write(f"- [{file_path}](#{anchor})\n")
        out.write('\n')

        # Write each file
        for i, file_path in enumerate(files):
            full_path = repo_path / file_path

            # Create anchor
            anchor = file_path.replace('/', '-').replace('.', '-').replace('_', '-').lower()

            # Write file header
            out.write(f"## {file_path}\n\n")
            out.write(f'<a id="{anchor}"></a>\n\n')

            # Check if file is binary
            if is_binary(str(full_path)):
                out.write('*Binary file*\n\n')
            else:
                try:
                    # Check file size
                    file_size = full_path.stat().st_size
                    if file_size > max_file_size:
                        out.write(f'*File too large ({file_size / 1024 / 1024:.2f} MB), skipped*\n\n')
                    else:
                        # Read file content
                        with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()

                        # Get language hint
                        lang_hint = get_language_hint(file_path)

                        # Write code block
                        out.write(f'```{lang_hint}\n')
                        out.write(content)
                        if not content.endswith('\n'):
                            out.write('\n')
                        out.write('```\n\n')
                except Exception as e:
                    out.write(f'*Error reading file: {e}*\n\n')

            # Add page separator (except for last file)
            if i < len(files) - 1:
                out.write('---\n\n')

    print(f"Generated: {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description='Aggregate a git codebase into a markdown file with syntax highlighting'
    )
    parser.add_argument(
        'repo_path',
        nargs='?',
        default='.',
        help='Path to git repository (default: current directory)'
    )
    parser.add_argument(
        '-o', '--output',
        default='repository.md',
        help='Output markdown file (default: repository.md)'
    )
    parser.add_argument(
        '-i', '--ignore',
        action='append',
        default=[],
        help='Additional patterns to ignore (can be used multiple times)'
    )
    parser.add_argument(
        '--no-default-ignore',
        action='store_true',
        help='Do not use default ignore patterns'
    )
    parser.add_argument(
        '--max-size',
        type=int,
        default=1024,
        help='Maximum file size in KB to include (default: 1024)'
    )
    parser.add_argument(
        '--depth',
        type=int,
        default=0,
        help='Directory depth for splitting output (0=single file, 1=split by top-level dirs, etc.)'
    )

    args = parser.parse_args()

    # Prepare ignore patterns
    ignore_patterns = [] if args.no_default_ignore else DEFAULT_IGNORE_PATTERNS.copy()
    ignore_patterns.extend(args.ignore)

    # Check if repo path exists and is a git repo
    repo_path = Path(args.repo_path)
    if not repo_path.exists():
        print(f"Error: Path does not exist: {args.repo_path}", file=sys.stderr)
        sys.exit(1)

    if not (repo_path / '.git').exists():
        print(f"Error: Not a git repository: {args.repo_path}", file=sys.stderr)
        sys.exit(1)

    max_file_size = args.max_size * 1024

    # Generate markdown (hierarchical or flat based on depth)
    if args.depth > 0:
        generate_hierarchical_markdown(
            str(repo_path),
            args.output,
            ignore_patterns,
            max_file_size,
            args.depth
        )
    else:
        generate_markdown(
            str(repo_path),
            args.output,
            ignore_patterns,
            max_file_size
        )


if __name__ == '__main__':
    main()
