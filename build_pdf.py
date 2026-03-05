#!/usr/bin/env python3
"""
Generates DM-DE-Refutation-of-the-Fundamental-Models.pdf from the repository markdown files.
Uses pandoc with XeLaTeX for high-quality typesetting.
"""

import os
import re
import subprocess
import tempfile

REPO_DIR = os.path.dirname(os.path.abspath(__file__))

CHAPTERS = [
    "File 02: Local_vs_Global_c.md",
    "File 03: Derivation_Errors.md",
    "File 04: Void_3.3c_Example.md",
    "File 05: Hubble_Error_Analysis.md",
    "File 06: Friedmann_Error_Analysis.md",
    "File 07: Euler_Model_Errors.md",
    "File 08: New_Interpretation.md",
]

ABSTRACT_FILE = "File 01: Abstract.md"
DIAGRAM_FILE = "Diagram v1.2.png"
OUTPUT_PDF = "DM-DE-Refutation-of-the-Fundamental-Models.pdf"

# Insert diagram after this chapter (0-based index into CHAPTERS list)
# 0 = File 02, 1 = File 03, 2 = File 04: Void_3.3c_Example.md
DIAGRAM_AFTER_CHAPTER = 2


def read_file(filename):
    path = os.path.join(REPO_DIR, filename)
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def clean_content(content):
    """Remove navigation links and trailing whitespace."""
    content = re.sub(r'\[←\s*Back to README\]\(README\.md\)\s*', "", content)
    content = re.sub(r'\n{3,}', "\n\n", content)
    return content.rstrip()


def extract_abstract():
    """Return the abstract body (without the '# Abstract' heading)."""
    content = read_file(ABSTRACT_FILE)
    content = clean_content(content)
    # Remove the top-level heading line
    content = re.sub(r'^# Abstract\s*\n+', "", content)
    # Remove trailing horizontal rule
    content = re.sub(r'\n+---\s*$', "", content)
    return content.strip()


def build_yaml_front_matter(abstract_text):
    """Build the YAML front matter block for pandoc."""
    # Indent each line of the abstract by two spaces for the YAML literal block
    indented = "\n".join("  " + line for line in abstract_text.splitlines())
    return f"""\
---
title: "DM-DE-Refutation of the Fundamental Models – A Structural Reinterpretation of Cosmology"
author: "Raiko Pulvermacher"
date: "2025"
lang: en
abstract: |
{indented}
documentclass: article
classoption:
  - a4paper
geometry: "margin=2.5cm"
linestretch: 1.2
fontsize: 11pt
numbersections: true
toc: true
toc-depth: 3
colorlinks: true
urlcolor: NavyBlue
linkcolor: black
---
"""


def main():
    abstract_text = extract_abstract()
    yaml_header = build_yaml_front_matter(abstract_text)

    diagram_path = os.path.join(REPO_DIR, DIAGRAM_FILE)
    diagram_md = (
        "\n\n"
        "!["
        "Diagram v1.2: Effective speed of light $c_{\\text{eff}}/c$ "
        "as a function of relative distance – Void vs. Cluster"
        f"]({diagram_path})"
        "\n"
    )

    parts = [yaml_header]

    for i, chapter_file in enumerate(CHAPTERS):
        content = clean_content(read_file(chapter_file))
        parts.append(content)
        if i == DIAGRAM_AFTER_CHAPTER:
            parts.append(diagram_md)

    combined = "\n\n\\newpage\n\n".join(parts)

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".md", encoding="utf-8", delete=False
    ) as tmp:
        tmp.write(combined)
        tmpfile = tmp.name

    output_path = os.path.join(REPO_DIR, OUTPUT_PDF)

    cmd = [
        "pandoc",
        tmpfile,
        "--output", output_path,
        "--pdf-engine=xelatex",
        "--highlight-style=tango",
        "--variable", "block-headings",
    ]

    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"PDF successfully generated: {output_path}")
        if result.stdout:
            print(result.stdout)
    except subprocess.CalledProcessError as exc:
        print("pandoc/XeLaTeX error:")
        print(exc.stderr)
        raise
    finally:
        os.unlink(tmpfile)


if __name__ == "__main__":
    main()
