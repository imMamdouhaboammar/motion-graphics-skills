# Gate 5: Platform QA Quality Gate

Sign-off criteria for Phase 5 (Safe Zones, Aspect Ratios, and Delivery).

## Mandatory Sign-Off Criteria

1. **Vertical Safe Zone Compliance (1080 x 1920)**:
   - Top 170px (10%) completely clear of essential headlines and focal points.
   - Bottom 384px (20%) completely clear of subtitles and primary text.
   - Right 162px (15%) completely clear of buttons and interactive elements.
2. **True Responsive Re-Layout**:
   - 9:16 layout rescattered and reframed rather than center-cropped from 16:9.
   - Hero subjects scale up to dominate vertical orientation.
3. **Delivery Master Verification**:
   - Master MP4 rendered with clean CRF 23 or higher encoding.
   - Transparent overlays delivered as ProRes 4444 MOV with alpha channel.
   - Automated safe zone overlay image produced and inspected.

## Verdict Contract

- **PASS**: Safe zone test frame confirms zero button collision, master formats verified.
- **BLOCK**: Text covered by platform icons or captions, distorted aspect ratio, or missing alpha channel.
