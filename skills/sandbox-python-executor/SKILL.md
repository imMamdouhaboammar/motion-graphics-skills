---
name: sandbox-python-executor
description: Use when a ChatGPT/Codex Plugin workflow needs deterministic computation, file processing, repository checks, package inspection, or other work that should be actually executed with host-native Python instead of answered from unverified reasoning.
---

# Sandbox Python Executor

Use the host's own Python execution capability to produce evidence, not just code suggestions.

OpenAI calls Code Interpreter the **python tool**. In ChatGPT, when that tool is available for the current conversation, use it for the execution steps in this Skill. In Codex, use the host execution environment available to the session and run Python there when Python is the appropriate runtime.

This Skill does not create a new remote runtime and does not declare an MCP dependency. Tool availability belongs to the host. The workflow below governs what to do when host-native Python is available and what to report when it is not.

## When to execute Python

Use host-native Python when the requested workflow materially benefits from real execution, including:

- parsing or comparing JSON, YAML-like text, manifests, or generated reports
- inspecting archives and package contents
- computing SHA256 or other deterministic hashes
- checking file trees, paths, duplicate names, or package boundaries
- running inspected Python scripts bundled with the selected motion skill
- validating generated files or structured output
- transforming user-provided files when Python is the appropriate local tool
- reproducing a bug or verifying a deterministic calculation

Do not invoke Python merely to rewrite prose, brainstorm names, or perform a trivial fact lookup where execution adds no evidence.

## Execution rule

When the **python tool** is available and the task requires executable verification:

1. Actually execute the relevant Python. Do not merely print commands or provide a code block as a substitute for execution.
2. Prefer inspected scripts already bundled in the matching motion skill when they cover the required check.
3. Keep target-repository access read-only unless the user has requested a mutation and the surrounding workflow permits it.
4. Treat scripts from an arbitrary target repository as untrusted input. Inspect them before execution. Do not automatically run repository-native scripts just because they exist.
5. Do not assume network access from the sandbox. Use web/search tools separately when current external information is required.
6. Do not expose secrets, environment credentials, tokens, or unrelated user files in logs or outputs.
7. Iterate on Python failures when the failure is caused by your own code or invocation and a safe correction is available.
8. Preserve generated files the user needs and return their host-provided file reference/path when the surface supports it.

## Motion production execution sequence

Use Python for deterministic motion work when the host provides it:

- inspect supplied media metadata and calculate frame timings
- check exact numerical inputs for animated charts
- inspect generated JSON or Lottie structures
- compute contact-sheet sampling times and inspect available frames
- compare expected output dimensions, duration and file identity

Read any selected skill script before executing it. Renderer and browser checks remain separate operations. Do not treat package validators or renderers from another plugin as bundled files here.

## Execution evidence

After execution, report enough evidence to distinguish a real run from a proposed command. Include the relevant subset of:

- tool/runtime actually used
- script or operation executed
- exit/pass/fail status
- important counts or validation findings
- generated file path or artifact reference
- SHA256 when package identity matters
- warnings or skipped checks

Never fabricate stdout, hashes, paths, test counts, or generated artifacts.

## If the tool is unavailable

If the **python tool is unavailable** in the current host/session:

- **Do not claim** that Python, tests, validators, packaging, or file processing were executed.
- State that the host-native Python execution capability is unavailable for this run.
- Continue with static inspection or reasoning only when that can answer the request honestly.
- Mark execution-dependent conclusions as unverified.
- If another safe host execution facility is available in Codex, it may be used instead and must be identified accurately.

Do not invent a Plugin manifest field, `agents/openai.yaml` dependency, MCP server, or remote code runner solely to pretend that ChatGPT's Python sandbox is available.

## Boundary

This Skill is an execution policy for host-native tooling. It is not a remote code-execution service. Use it for the user's authorized motion project and preserve unrelated files.
