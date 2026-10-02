# Runtime Reference — Video Style Cloner

## Required Tools

### Python 3.10+
```bash
# Check
python3 --version

# macOS
brew install python@3.12

# Linux
sudo apt install python3.12 python3.12-venv

# Install Python dependencies
pip install -r requirements.txt
# or from source repo:
# pip install yt-dlp faster-whisper opencv-python librosa numpy scipy pillow
```

### FFmpeg 6.0+
```bash
# Check
ffmpeg -version

# macOS
brew install ffmpeg

# Linux
sudo apt install ffmpeg

# Windows
winget install ffmpeg
```

### yt-dlp (YouTube download for analysis only)
```bash
pip install -U yt-dlp
# or
brew install yt-dlp
```

### Node.js 22.18+ (for HyperFrames renderer)
```bash
# Check
node --version

# macOS/Linux via nvm
nvm install 22
nvm use 22

# Or via package manager
brew install node
```

### faster-whisper (lyrics alignment)
```bash
pip install faster-whisper
```

---

## Doctor Check
Run this to verify all tools are available:
```bash
python3 -c "
import subprocess, sys
tools = {
  'python':  ('python3', '--version'),
  'ffmpeg':  ('ffmpeg',  '-version'),
  'yt-dlp':  ('yt-dlp',  '--version'),
  'node':    ('node',    '--version'),
}
for name, (cmd, flag) in tools.items():
    try:
        r = subprocess.run([cmd, flag], capture_output=True, text=True)
        print(f'✅ {name}: {r.stdout.strip() or r.stderr.strip()}')
    except FileNotFoundError:
        print(f'❌ {name}: NOT FOUND — install required')
"
```

---

## Project Workspace Layout

```
projects/<slug>/
├── analysis/
│   ├── report.json          # Shot details, BPM, beat times
│   ├── sheet_1fps.jpg       # 1 frame/second contact sheet
│   ├── sheet_scenes.jpg     # Scene-break contact sheet
│   ├── STYLE.md             # Agent-written style analysis
│   └── song/                # Audio analysis output
│       └── report.json
├── inputs/
│   ├── audio.*              # User-provided music file
│   ├── lyrics.txt           # User-provided lyrics text
│   └── character_*.png      # User-provided design sheets
├── assets/
│   ├── ASSETS.md            # Attribution log for all fetched assets
│   └── clip.m4a             # Processed audio clip
├── build/
│   ├── production.json      # Segment plan + shared assets
│   ├── frames/              # Rendered PNG frames per segment
│   └── character_sheets/    # Approved character definitions
├── out/
│   └── final.mp4            # Final output
├── STORYBOARD.md            # Shot plan (must be approved before production)
├── plan.json                # Machine-readable shot plan with ref_shot, camera
└── fixes.json               # Fix log with before/after evidence
```

---

## Key Environment Variables

```bash
# Optional: point to custom analyze.py location
export REELMIMIC_SCRIPTS=/path/to/.claude/skills/video-clone/scripts

# Optional: Pixabay API key for asset search
export PIXABAY_API_KEY=your_key

# Optional: Openverse API key
export OPENVERSE_API_KEY=your_key
```
