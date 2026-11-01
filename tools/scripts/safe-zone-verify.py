#!/usr/bin/env python3
"""
Safe Zone Verifier for Mobile Video Platforms (9:16 - 1080x1920)
Generates or verifies safe zone overlays to prevent UI button collision.
"""

import sys
import os

def print_safe_zone_rules():
    print("==================================================")
    print(" MOBILE VIDEO SAFE ZONE SPECIFICATION (1080x1920) ")
    print("==================================================")
    print(" Top Margin    : 0px to 170px (10%)    -> Clear of headers and logos")
    print(" Bottom Margin : 1536px to 1920px (20%)-> Clear of subtitles and CTAs")
    print(" Right Margin  : 918px to 1080px (15%) -> Clear between Y=900 and Y=1500")
    print(" Safe Content  : X: [100px, 900px], Y: [170px, 1500px]")
    print("==================================================")

def generate_svg_overlay(out_path="renders/safe-zone-overlay.svg"):
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    svg_content = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1080 1920" width="1080" height="1920">
  <!-- Top Danger Margin (10% - 170px) -->
  <rect x="0" y="0" width="1080" height="170" fill="red" opacity="0.35"/>
  <text x="540" y="95" fill="white" font-family="sans-serif" font-size="28" font-weight="bold" text-anchor="middle">TOP SAFE MARGIN (STATUS &amp; SEARCH)</text>

  <!-- Bottom Danger Margin (20% - 384px) -->
  <rect x="0" y="1536" width="1080" height="384" fill="red" opacity="0.35"/>
  <text x="540" y="1740" fill="white" font-family="sans-serif" font-size="28" font-weight="bold" text-anchor="middle">BOTTOM SAFE MARGIN (CAPTION &amp; PROFILE)</text>

  <!-- Right Action Column Danger Zone (15% - 162px, Y: 900-1500) -->
  <rect x="918" y="900" width="162" height="600" fill="red" opacity="0.45"/>
  <text x="999" y="1210" fill="white" font-family="sans-serif" font-size="22" font-weight="bold" text-anchor="middle" transform="rotate(-90 999 1210)">BUTTON ZONE</text>

  <!-- Safe Center Outline -->
  <rect x="80" y="190" width="820" height="1320" fill="none" stroke="#00FF66" stroke-width="4" stroke-dasharray="12,12"/>
  <text x="490" y="240" fill="#00FF66" font-family="sans-serif" font-size="24" font-weight="bold" text-anchor="middle">PRIMARY SAFE CONTENT BOUNDARY</text>
</svg>"""
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(svg_content)
    print(f"Generated SVG safe-zone overlay at: {out_path}")

def main():
    print_safe_zone_rules()
    out = sys.argv[1] if len(sys.argv) > 1 else "renders/safe-zone-overlay.svg"
    generate_svg_overlay(out)

if __name__ == "__main__":
    main()
