# Director Gates Evaluation Rubric

Detailed verification criteria for studio stage sign-offs.

## Gate Verdicts

- **PASS**: All mandatory criteria satisfied with verifiable on-disk evidence.
- **WARN**: Minor non-blocking aesthetic observations that do not violate platform constraints.
- **BLOCK**: Critical blocker such as text clipping in 9:16 safe zones, master loudness exceeding -1 dBTP, or ungrounded floating geometry without contact shadows.

## Verification Checklist

1. Does the first 2 seconds contain a high-impact hook?
2. Are font assets licensed and locally cached in the `fonts/` directory?
3. Does `ffmpeg` report integrated loudness within 0.5 LUFS of target -14.0 LUFS?
4. Is the safe-zone overlay check image clean of text collisions?
