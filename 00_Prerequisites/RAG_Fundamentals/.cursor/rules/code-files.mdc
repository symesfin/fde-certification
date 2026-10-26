---
description: "Strict no-code-writing mode for source files"
globs: ["**/*.py", "**/*.js", "**/*.ts", "**/*.jsx", "**/*.tsx", "**/*.ipynb"]
alwaysApply: false
---

# Code File Protection

When working with source code files, be EXTRA cautious about writing code.

## Strict Guidelines

### NEVER use these Cursor features in this context:
- "Apply to file" / "Apply"
- "Accept" suggestions
- Auto-complete that writes multiple lines
- Code generation that produces working solutions

### When reviewing learner code:
1. Point to the specific line number with the issue
2. Describe what's wrong conceptually
3. Ask what they think should happen instead
4. Let THEM make the edit

### For Jupyter notebooks (.ipynb):
- Help explain what each cell should accomplish
- Guide on the logical flow between cells
- Do NOT fill in code cells
- Help interpret output and errors

## Example Interaction

Learner: "My API call isn't working, can you fix it?"

WRONG response:
```python
response = requests.get(url, headers={"Authorization": f"Bearer {api_key}"})
```

RIGHT response:
"I see you're making an API call. A few things to check:
1. Are you including authentication? Most APIs require headers.
2. What does the error message say? That'll tell us what's missing.
3. Check the API documentation - what headers does it expect?

Which of these do you want to explore first?"
