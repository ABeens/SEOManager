---
title: "Complete Markdown Guide"
description: "Everything you need to know about writing in Markdown - from basic syntax to advanced features."
pubDate: "2024-01-25"
author: "Blog Author"
tags: ["markdown", "writing", "documentation", "tutorial"]
---

# Complete Markdown Guide

Markdown is a lightweight markup language that's perfect for writing content. This blog uses Markdown for all posts, so let's explore everything you can do!

## Basic Syntax

### Headers

```markdown
# H1 Header
## H2 Header
### H3 Header
#### H4 Header
##### H5 Header
###### H6 Header
```

### Text Formatting

**Bold text** using `**bold**` or `__bold__`

*Italic text* using `*italic*` or `_italic_`

***Bold and italic*** using `***text***`

~~Strikethrough~~ using `~~text~~`

### Lists

#### Unordered Lists

- Item 1
- Item 2
  - Nested item
  - Another nested item
- Item 3

#### Ordered Lists

1. First item
2. Second item
   1. Nested numbered item
   2. Another nested item
3. Third item

### Links and Images

[Link to Astro](https://astro.build)

[Link with title](https://astro.build "Astro - Build fast websites")

## Code

### Inline Code

Use `backticks` for inline code.

### Code Blocks

```javascript
// JavaScript example
function calculateSum(a, b) {
  return a + b;
}

const result = calculateSum(5, 3);
console.log(`The sum is: ${result}`);
```

```python
# Python example
def greet_user(name):
    return f"Hello, {name}!"

message = greet_user("World")
print(message)
```

```css
/* CSS example */
.blog-post {
  max-width: 800px;
  margin: 0 auto;
  padding: 2rem;
  font-family: system-ui, sans-serif;
}

.blog-post h1 {
  color: #2c3e50;
  margin-bottom: 1rem;
}
```

## Blockquotes

> This is a blockquote. You can use it for highlighting important information or quotes.

> Multi-line blockquotes
> can span several lines
> and still look great!

Nested blockquotes:

> This is the first level of quoting.
>
> > This is nested blockquote.
>
> Back to the first level.

## Tables

| Feature | Supported | Notes |
|---------|-----------|--------|
| Headers | ✅ | H1-H6 supported |
| Lists | ✅ | Ordered and unordered |
| Code | ✅ | Inline and blocks |
| Tables | ✅ | Like this one! |
| Images | ✅ | With alt text |

## Advanced Features

### Task Lists

- [x] Learn Markdown basics
- [x] Set up Astro blog
- [ ] Write more content
- [ ] Add comments system

### Horizontal Rules

You can create horizontal rules with three or more hyphens:

---

### Line Breaks

To create a line break, end a line with two spaces
and then start a new line.

## Tips for Better Markdown

1. **Use consistent formatting** - Stick to one style for headers, lists, etc.
2. **Add alt text to images** - Helps with accessibility
3. **Preview your content** - Always check how it looks rendered
4. **Keep it simple** - Markdown works best when kept clean

## Markdown in This Blog

This Astro blog processes Markdown files and:

- Converts them to HTML automatically
- Applies syntax highlighting to code blocks
- Generates a table of contents from headers
- Optimizes images and links

## Resources

Want to learn more about Markdown?

- [Markdown Guide](https://www.markdownguide.org/)
- [GitHub Flavored Markdown](https://github.github.com/gfm/)
- [CommonMark Spec](https://commonmark.org/)

Happy writing! ✍️