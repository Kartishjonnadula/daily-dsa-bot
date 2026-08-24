# Contributing to Daily DSA

Thanks for contributing!

## Development Setup

1. Fork the repository.
2. Clone your fork.
3. Create a Python virtual environment.
4. Install dependencies:

```bash
python -m pip install -r requirements.txt
```

5. Create `.env` from `.env.example`.
6. Add your Discord bot token.
7. Run:

```bash
python bot.py
```

## Problem Data

Problems are stored in:

```text
neet_code/problems.json
```

Every problem must have a unique stable `id`.

Recommended IDs are the LeetCode slugs:

```text
two-sum
valid-anagram
binary-tree-level-order-traversal
```

Avoid changing an existing problem's ID unless the problem itself is being replaced. Rotation history depends on these IDs.

## Pull Requests

Keep changes focused and explain:

- What changed
- Why it changed
- How it was tested

Never commit:

- `.env`
- Discord tokens
- `neet_code/neetcode.db`
- Hosting credentials
