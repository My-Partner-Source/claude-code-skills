#!/usr/bin/env python3
"""
validate_post.py - Validate social media posts before publishing

Usage:
    python scripts/validate_post.py <post_file>
    
Example:
    python scripts/validate_post.py ~/social-posts/x/drafts/2025-01-02-bug-discovery.md
"""

import argparse
import re
import sys
from pathlib import Path


def extract_frontmatter(content: str) -> dict:
    """Extract YAML frontmatter from post."""
    frontmatter = {}
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            for line in parts[1].strip().split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    frontmatter[key.strip()] = value.strip()
    return frontmatter


def extract_post_content(content: str) -> str:
    """Extract the actual post content from markdown."""
    # Look for content between triple backticks after "## The Post"
    match = re.search(r'## The Post\s*```\s*(.*?)\s*```', content, re.DOTALL)
    if match:
        return match.group(1).strip()
    return ""


def extract_thread_tweets(content: str) -> list:
    """Extract individual tweets from a thread."""
    tweets = []
    # Match patterns like "### 1/" followed by code block
    pattern = r'### \d+/\s*```\s*(.*?)\s*```'
    matches = re.findall(pattern, content, re.DOTALL)
    return [m.strip() for m in matches]


def validate_x_post(content: str, post_text: str) -> list:
    """Validate a single X post."""
    issues = []
    
    # Character count
    char_count = len(post_text)
    if char_count > 280:
        issues.append(f"❌ Over character limit: {char_count}/280")
    elif char_count > 260:
        issues.append(f"⚠️  Close to limit: {char_count}/280")
    else:
        issues.append(f"✓ Character count OK: {char_count}/280")
    
    # Check for hashtags
    if '#' in post_text:
        issues.append("❌ Contains hashtags (discouraged on X)")
    
    # Check if starts with "I"
    if post_text.strip().startswith('I ') or post_text.strip().startswith('I\''):
        issues.append("⚠️  Starts with 'I' (consider pattern interrupt)")
    
    # Check for engagement bait
    bait_phrases = ['like if', 'retweet if', 'rt if', 'share if']
    if any(phrase in post_text.lower() for phrase in bait_phrases):
        issues.append("❌ Contains engagement bait")
    
    # Check for clichés
    cliches = ['game-changer', 'game changer', '10x', 'crushing it', 'let\'s go']
    found_cliches = [c for c in cliches if c in post_text.lower()]
    if found_cliches:
        issues.append(f"⚠️  Contains clichés: {', '.join(found_cliches)}")
    
    return issues


def validate_x_thread(content: str) -> list:
    """Validate an X thread."""
    issues = []
    tweets = extract_thread_tweets(content)
    
    if not tweets:
        issues.append("❌ No tweets found in thread")
        return issues
    
    issues.append(f"Thread length: {len(tweets)} tweets")
    
    for i, tweet in enumerate(tweets, 1):
        char_count = len(tweet)
        prefix = f"Tweet {i}:"
        
        if char_count > 280:
            issues.append(f"❌ {prefix} Over limit ({char_count}/280)")
        elif char_count > 260:
            issues.append(f"⚠️  {prefix} Close to limit ({char_count}/280)")
        
        if '#' in tweet:
            issues.append(f"❌ {prefix} Contains hashtags")
    
    # Check first tweet hooks well
    if tweets and len(tweets[0]) < 50:
        issues.append("⚠️  First tweet may be too short for a good hook")
    
    return issues


def validate_linkedin_post(content: str, post_text: str) -> list:
    """Validate a LinkedIn post."""
    issues = []
    
    # Character count
    char_count = len(post_text)
    if char_count > 3000:
        issues.append(f"❌ Over character limit: {char_count}/3000")
    else:
        issues.append(f"✓ Character count OK: {char_count}/3000")
    
    # Check hook length (before "See more")
    first_line = post_text.split('\n')[0] if post_text else ""
    if len(first_line) > 210:
        issues.append(f"⚠️  Hook may be cut off: {len(first_line)}/210 chars")
    
    # Check for hashtags (should have them on LinkedIn)
    hashtag_count = len(re.findall(r'#\w+', post_text))
    if hashtag_count == 0:
        issues.append("⚠️  No hashtags (LinkedIn posts should have 3-5)")
    elif hashtag_count > 5:
        issues.append(f"⚠️  Too many hashtags: {hashtag_count} (aim for 3-5)")
    else:
        issues.append(f"✓ Hashtag count OK: {hashtag_count}")
    
    # Check if starts with "I"
    if post_text.strip().startswith('I ') or post_text.strip().startswith('I\''):
        issues.append("⚠️  Starts with 'I' (consider pattern interrupt)")
    
    # Check for links in body
    if 'http://' in post_text or 'https://' in post_text:
        issues.append("⚠️  Contains link in body (may reduce reach, consider comments)")
    
    # Check paragraph length (should have line breaks)
    paragraphs = [p for p in post_text.split('\n\n') if p.strip()]
    long_paragraphs = [p for p in paragraphs if len(p) > 300]
    if long_paragraphs:
        issues.append("⚠️  Some paragraphs may be too long (add line breaks)")
    
    return issues


def main():
    parser = argparse.ArgumentParser(description='Validate social media posts')
    parser.add_argument('file', help='Post file to validate')
    args = parser.parse_args()
    
    path = Path(args.file).expanduser()
    if not path.exists():
        print(f"Error: File not found: {args.file}")
        return 1
    
    content = path.read_text()
    frontmatter = extract_frontmatter(content)
    platform = frontmatter.get('platform', 'unknown')
    
    print(f"\n📝 Validating: {path.name}")
    print(f"📱 Platform: {platform}")
    print("-" * 40)
    
    if platform == 'x':
        post_text = extract_post_content(content)
        issues = validate_x_post(content, post_text)
    elif platform == 'x-thread':
        issues = validate_x_thread(content)
    elif platform == 'linkedin':
        post_text = extract_post_content(content)
        issues = validate_linkedin_post(content, post_text)
    else:
        print(f"Unknown platform: {platform}")
        return 1
    
    for issue in issues:
        print(issue)
    
    print("-" * 40)
    
    has_errors = any('❌' in issue for issue in issues)
    if has_errors:
        print("Status: ❌ Has issues to fix")
        return 1
    else:
        print("Status: ✓ Ready for review")
        return 0


if __name__ == '__main__':
    sys.exit(main())
