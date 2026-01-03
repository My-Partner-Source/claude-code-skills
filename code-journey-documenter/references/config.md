# Book Project Configuration

## Book Repository Location

book_path: ~/dev/personal/books/code-with-claude

## Directory Mapping

When generating content for the book, use these paths:

| Content Type | Path |
|--------------|------|
| Part I Chapters | {book_path}/chapters/part-1-foundations/ |
| Part II Chapters | {book_path}/chapters/part-2-job-stories/ |
| Part III Chapters | {book_path}/chapters/part-3-beyond/ |
| Session Logs | {book_path}/session-logs/ |
| Code Examples | {book_path}/code-examples/ |
| Drafts | {book_path}/drafts/ |
| Diagrams | {book_path}/assets/diagrams/ |
| Screenshots | {book_path}/assets/screenshots/ |

## File Naming Conventions

- Chapters: `chapter-XX-kebab-case-title.md`
- Session logs: `YYYY-MM-DD-project-name.md`
- Code examples: `chapter-XX/descriptive-name.ext`

## Usage

When the user asks to save content for the book, expand `{book_path}` to the full path above and save to the appropriate directory based on content type.

If the book directory doesn't exist, prompt the user to create it or confirm the correct path.
