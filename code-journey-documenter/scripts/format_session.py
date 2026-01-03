#!/usr/bin/env python3
"""
format_session.py - Transform raw session logs into structured chapter content

Usage:
    python scripts/format_session.py <input_log> [--output <output_file>]
    
Example:
    python scripts/format_session.py session_2024_01_15.md --output chapter_5_draft.md
"""

import argparse
import re
from datetime import datetime
from pathlib import Path


def extract_tagged_moments(content: str) -> dict:
    """Extract [INSIGHT], [FAILURE], [PATTERN], [META] tagged content."""
    tags = {
        'insights': [],
        'failures': [],
        'patterns': [],
        'meta': []
    }
    
    tag_patterns = {
        'insights': r'\[INSIGHT\]\s*(.+?)(?=\n\n|\n\[|\Z)',
        'failures': r'\[FAILURE\]\s*(.+?)(?=\n\n|\n\[|\Z)',
        'patterns': r'\[PATTERN\]\s*(.+?)(?=\n\n|\n\[|\Z)',
        'meta': r'\[META\]\s*(.+?)(?=\n\n|\n\[|\Z)'
    }
    
    for tag_type, pattern in tag_patterns.items():
        matches = re.findall(pattern, content, re.DOTALL)
        tags[tag_type] = [m.strip() for m in matches]
    
    return tags


def extract_prompts(content: str) -> list:
    """Extract prompt/response pairs from session log."""
    prompts = []
    
    # Look for prompt sections
    prompt_pattern = r'(?:Prompt \d+|Given to Claude Code:)\s*```(.*?)```'
    matches = re.findall(prompt_pattern, content, re.DOTALL)
    
    for i, match in enumerate(matches, 1):
        prompts.append({
            'number': i,
            'text': match.strip()
        })
    
    return prompts


def extract_metadata(content: str) -> dict:
    """Extract session metadata from header."""
    metadata = {
        'date': None,
        'project': None,
        'chapter': None,
        'challenge': None
    }
    
    # Extract date from session header
    date_match = re.search(r'Session:\s*(\d{4}-\d{2}-\d{2})', content)
    if date_match:
        metadata['date'] = date_match.group(1)
    
    # Extract project name
    project_match = re.search(r'Session:.*?-\s*(.+?)(?:\n|$)', content)
    if project_match:
        metadata['project'] = project_match.group(1).strip()
    
    # Extract target chapter
    chapter_match = re.search(r'(?:Target Chapter|Chapter target):\s*(.+?)(?:\n|$)', content)
    if chapter_match:
        metadata['chapter'] = chapter_match.group(1).strip()
    
    # Extract challenge
    challenge_match = re.search(r'Challenge:\s*(.+?)(?:\n|$)', content)
    if challenge_match:
        metadata['challenge'] = challenge_match.group(1).strip()
    
    return metadata


def generate_chapter_draft(metadata: dict, prompts: list, tags: dict) -> str:
    """Generate a chapter draft from extracted content."""
    
    output = []
    
    # Header
    output.append(f"# {metadata.get('chapter', 'Chapter Draft')}")
    output.append("")
    output.append(f"*Based on session: {metadata.get('date', 'Unknown')} - {metadata.get('project', 'Unknown')}*")
    output.append("")
    
    # Opening Hook
    output.append("## The Problem")
    output.append("")
    if metadata.get('challenge'):
        output.append(f"[EXPAND THIS: {metadata['challenge']}]")
    else:
        output.append("[Write the opening hook - describe the real-world problem]")
    output.append("")
    
    # The Attempt
    output.append("## The Approach")
    output.append("")
    if prompts:
        output.append("My first instinct was to ask Claude Code:")
        output.append("")
        output.append("```")
        output.append(prompts[0]['text'])
        output.append("```")
        output.append("")
        output.append("[Describe what happened with this initial approach]")
    else:
        output.append("[Describe your initial approach with Claude Code]")
    output.append("")
    
    # The Struggle (Iterations)
    if len(prompts) > 1:
        output.append("## The Iterations")
        output.append("")
        for prompt in prompts[1:]:
            output.append(f"### Attempt {prompt['number']}")
            output.append("")
            output.append("```")
            output.append(prompt['text'])
            output.append("```")
            output.append("")
            output.append("[Describe what changed and why]")
            output.append("")
    
    # Failures section
    if tags['failures']:
        output.append("## What Went Wrong")
        output.append("")
        for failure in tags['failures']:
            output.append(f"- {failure}")
        output.append("")
        output.append("[Expand on these failures - they're the teaching moments]")
        output.append("")
    
    # Insights section
    if tags['insights']:
        output.append("## The Breakthrough")
        output.append("")
        for insight in tags['insights']:
            output.append(f"- {insight}")
        output.append("")
        output.append("[Expand on these insights - what clicked?]")
        output.append("")
    
    # Patterns section
    if tags['patterns']:
        output.append("## The Pattern")
        output.append("")
        output.append("From this session, I extracted a transferable pattern:")
        output.append("")
        for pattern in tags['patterns']:
            output.append(f"**{pattern}**")
            output.append("")
            output.append("[Explain how readers can apply this]")
            output.append("")
    
    # Meta observations
    if tags['meta']:
        output.append("## Meta Observation")
        output.append("")
        output.append("*For the 'Beyond' section:*")
        output.append("")
        for meta in tags['meta']:
            output.append(f"- {meta}")
        output.append("")
    
    # Reader exercise
    output.append("## Try It Yourself")
    output.append("")
    output.append("[Suggest a prompt for readers to practice this pattern]")
    output.append("")
    output.append("```")
    output.append("[Example prompt]")
    output.append("```")
    output.append("")
    output.append("**Expected outcome:** [What should happen]")
    output.append("")
    output.append("**Watch out for:** [Common pitfalls]")
    
    return "\n".join(output)


def main():
    parser = argparse.ArgumentParser(
        description='Transform raw session logs into chapter drafts'
    )
    parser.add_argument('input', help='Input session log file')
    parser.add_argument('--output', '-o', help='Output file (default: stdout)')
    parser.add_argument('--tags-only', action='store_true', 
                        help='Only extract and display tagged moments')
    
    args = parser.parse_args()
    
    # Read input
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: File not found: {args.input}")
        return 1
    
    content = input_path.read_text()
    
    # Extract components
    metadata = extract_metadata(content)
    prompts = extract_prompts(content)
    tags = extract_tagged_moments(content)
    
    if args.tags_only:
        # Just print tagged moments
        print("=== Tagged Moments ===\n")
        for tag_type, items in tags.items():
            if items:
                print(f"[{tag_type.upper()}]")
                for item in items:
                    print(f"  - {item}")
                print()
        return 0
    
    # Generate chapter draft
    draft = generate_chapter_draft(metadata, prompts, tags)
    
    if args.output:
        output_path = Path(args.output)
        output_path.write_text(draft)
        print(f"Chapter draft written to: {args.output}")
    else:
        print(draft)
    
    return 0


if __name__ == '__main__':
    exit(main())
