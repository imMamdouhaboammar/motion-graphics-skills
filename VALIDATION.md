# Skill Validation Rules

Every skill in `skills/` and prompt in `prompts/` must pass the validation checks enforced by `validate-skills.sh`.

Run the validator locally:
```bash
bash validate-skills.sh
```

## Rules Checked

### 1. Folder Structure & Naming
- **Directory naming**: Lowercase alphanumeric with single hyphens (`^[a-z0-9]+(-[a-z0-9]+)*$`).
- **Required file**: Each skill directory must contain a `SKILL.md`.
- **Optional subdirectories**: `references/`, `scripts/`, `assets/`, `evals/`.

### 2. YAML Frontmatter (`SKILL.md`)
- **Delimiters**: Must begin with `---` on line 1 and have a closing `---`.
- **`name` field**:
  - Required and non-empty.
  - Must exactly match the directory name.
  - Maximum length: 64 characters.
- **`description` field**:
  - Required and non-empty.
  - Maximum length: 1024 characters.
  - Must include trigger phrasing (such as `use`, `Use`, or `when`).
- **File size**:
  - Recommended <= 500 lines. Larger files should break details out into `references/`.

### 3. House Style Rules (Prose in Markdown)
Applied to `SKILL.md`, `references/*.md`, `evals/*.md`, and `prompts/*.md`:
- **No Em Dashes**: Use standard hyphens, colons, or clean phrasing in prose outside fenced code blocks.
- **No Semicolons**: Do not use semicolons in prose sentences outside fenced code blocks and inline code.
- **No Local Paths**: Never commit absolute user paths (such as `/Users/...`). Use relative paths (e.g. `.agents/skills`).
- **No Banned Words**: The word `steal` is prohibited across skill definitions.

### 4. Prompts Validation (`prompts/*.md`)
- Must obey the same house style rules.
- Fenced code blocks must always be matched and properly closed (even count of triple backticks).
