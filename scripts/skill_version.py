#!/usr/bin/env python3
"""Read or replace the repository's canonical metadata.version line."""

import re
import sys
from pathlib import Path


def version_span(text):
    header = re.match(r'\A---\n(.*?)\n---(?:\n|$)', text, re.DOTALL)
    if not header:
        raise ValueError('Missing YAML frontmatter')
    blocks = list(re.finditer(r'^metadata:\n((?:[ \t]+[^\n]*\n|\n)*)',
                              header.group(1) + '\n', re.MULTILINE))
    if len(blocks) != 1 or len(re.findall(r"^metadata\s*:", header.group(1), re.MULTILINE)) != 1:
        raise ValueError('Expected one block-style metadata mapping')
    block = blocks[0]
    versions = list(re.finditer(r'^  version: "([^"\n]+)"[ \t]*$',
                                block.group(1), re.MULTILINE))
    if len(versions) != 1:
        raise ValueError('Expected one metadata.version with two-space indentation and a quoted string')
    # Reject duplicate version keys even if the extra one uses another YAML style.
    if len(re.findall(r'^\s*version\s*:', block.group(1), re.MULTILINE)) != 1:
        raise ValueError('Duplicate metadata.version')
    match = versions[0]
    offset = header.start(1) + block.start(1)
    return offset + match.start(1), offset + match.end(1)


def main():
    if len(sys.argv) not in (2, 3):
        raise ValueError('Usage: skill_version.py SKILL.md [new-version]')
    path = Path(sys.argv[1])
    text = path.read_text(encoding='utf-8')
    start, end = version_span(text)
    if len(sys.argv) == 3:
        path.write_text(text[:start] + sys.argv[2] + text[end:], encoding='utf-8')
    else:
        print(text[start:end])


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError) as error:
        sys.exit(f'Error: {error}')
