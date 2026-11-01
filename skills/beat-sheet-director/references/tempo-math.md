# Tempo to Frame Rate Math

Reference calculations for synchronizing visual animation frames with musical tempo.

## Tempo to Duration Formula

For a track in 4/4 time signature:
- Seconds per beat = 60 / BPM
- Seconds per measure (bar) = 240 / BPM
- Frames per beat (at 30 fps) = 1800 / BPM
- Frames per beat (at 60 fps) = 3600 / BPM

## Common Tempo Conversions

| BPM | Seconds per Beat | Seconds per Bar | Frames per Beat (30 fps) | Frames per Beat (60 fps) |
|---|---|---|---|---|
| 90 | 0.667s | 2.667s | 20.0 | 40.0 |
| 100 | 0.600s | 2.400s | 18.0 | 36.0 |
| 110 | 0.545s | 2.182s | 16.4 | 32.7 |
| 120 | 0.500s | 2.000s | 15.0 | 30.0 |
| 128 | 0.469s | 1.875s | 14.1 | 28.1 |
| 140 | 0.429s | 1.714s | 12.9 | 25.7 |
