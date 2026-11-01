# Gate 2: Technical Director Quality Gate

Sign-off criteria for Phase 2 (Technical Pipeline and Architecture).

## Mandatory Sign-Off Criteria

1. **Rendering Stack Selection**:
   - Chosen renderer matches scene requirements: HyperFrames for web/DOM/SVG compositions, Blender MCP for physical 3D, OpenCV for algorithmic 2.5D.
   - Frame rate explicitly locked to 30 fps (preview) or 60 fps (master delivery).
2. **Asset Ledger Verification**:
   - All referenced font files exist locally in `fonts/` with valid licenses.
   - All audio files exist in designated directories with verified sample rates (44.1kHz or 48kHz).
   - Zero missing external network assets during render passes.
3. **Hardware and Performance Budget**:
   - Total render memory fits within host RAM limits.
   - Export parameters defined: CRF 23 or higher quality, ProRes 4444 profile where transparency is required.

## Verdict Contract

- **PASS**: All assets exist locally, render stack verified with test frame.
- **BLOCK**: Missing local assets, unverified network dependencies, or memory bounds exceeded.
