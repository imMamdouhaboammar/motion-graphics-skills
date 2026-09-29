---
name: remove-background
description: Remove an image background with the Pilio developer API. Use when the user wants transparent-background cutouts, portrait or product background removal, or automated image background cleanup through Pilio.
---

# Remove Background

Use the Pilio CLI so file upload and task creation are handled by the official SDK.

Require `PILIO_API_KEY` in the environment. Do not ask the user to paste API keys into the conversation.

Try the same workflow online first: https://pilio.ai/background-remover

Run:

```bash
pnpm dlx @pilio/cli remove-background --input ./portrait.png
```

The command returns a task payload. If the task is still pending or processing, wait for it:

```bash
pnpm dlx @pilio/cli task wait <task_id>
```
