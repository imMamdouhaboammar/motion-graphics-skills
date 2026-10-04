from pathlib import Path
from PIL import Image
import numpy as np
p=Path(__file__).resolve().parents[1]
N='#172B46';T='#8BAFBB';O='#D97335';I='#F3F0E8';W='#FAF9F5'
def save(n,body):
 (p/f'assets/backgrounds/scene-{n:02}.svg').write_text(f'<svg xmlns="http://www.w3.org/2000/svg" width="1920" height="1080" viewBox="0 0 1920 1080"><title>Original editable scene {n} background</title><rect width="1920" height="1080" fill="{I}"/>{body}</svg>')
def line(x,y,w,h,color=N,a=.15):return f'<path d="M{x} {y}h{w}v{h}" fill="none" stroke="{color}" stroke-opacity="{a}" stroke-width="2"/>'
# 1: question's broken archive edges: large spatial shape, negative space at right
save(1,f'<g id="archive-plane"><path d="M70 210L910 135 970 840 180 920 70 720Z" fill="{T}" opacity=".24"/><path d="M140 770L940 660 960 850 180 965Z" fill="{N}"/></g><g id="registration-lines">'+line(1000,170,800,700)+line(122,120,800,800)+f'<path d="M1080 880h690M1690 210h80" stroke="{O}" stroke-width="4"/></g>')
# 2: domestic architectural setting; actual window light, horizontal bench plane
save(2,f'<g id="domestic-window"><path d="M90 140h800v740H90Z" fill="{T}" opacity=".2"/><path d="M120 160h580v610H120Z" fill="{N}"/><path d="M155 195h510v540H155Z" fill="{T}"/><path d="M325 195v540M495 195v540M155 460h510" stroke="{I}" stroke-width="12"/><path d="M155 220L620 735H155Z" fill="{W}" opacity=".3"/></g><g id="floor-plane"><path d="M0 940L1050 865 1920 985V1080H0Z" fill="{N}" opacity=".09"/></g><path d="M990 185h780M1760 185v680" fill="none" stroke="{N}" stroke-opacity=".22" stroke-width="2"/>')
# 3 scientific observation field not vague molecules
cells=''.join(f'<path d="M{1170+i*55} 180v670" stroke="{N}" stroke-opacity=".08"/>' for i in range(12))
save(3,f'<g id="lab-mask"><path d="M85 800L110 180 880 225 910 900Z" fill="{N}"/><path d="M135 280L810 340 840 810 165 750Z" fill="{T}" opacity=".38"/></g><g id="cell-coordinate-grid">{cells}<path d="M1100 280h680M1100 430h680M1100 580h680M1100 730h680" stroke="{N}" stroke-opacity=".08"/></g><path d="M1070 835H1790" stroke="{O}" stroke-width="4"/>')
#4 diagram path background, continuity to folded evidence leaves
save(4,f'<g id="evidence-axis"><path d="M1700 280L1400 390 1040 560 660 700 225 810" fill="none" stroke="{T}" stroke-width="100" stroke-opacity=".25"/><path d="M1700 280L1400 390 1040 560 660 700 225 810" fill="none" stroke="{N}" stroke-width="2" stroke-dasharray="5 9"/></g><path d="M100 200h1720M100 940h1720" stroke="{N}" stroke-opacity=".15"/>')
#5 open-journal quiet field with binding registration
save(5,f'<g id="publication-field"><path d="M65 140H1855V975H65Z" fill="{W}"/><path d="M130 180h1660M130 935h1660" stroke="{N}" stroke-opacity=".15"/><path d="M960 210v690" stroke="{N}" stroke-opacity=".08" stroke-width="60"/></g>')
#6 terminal still paper shelf / book slot
save(6,f'<g id="book-structure"><path d="M120 990L850 850 1780 940 1650 1020Z" fill="{N}" opacity=".07"/><path d="M180 190L935 130 985 930 250 950Z" fill="{T}" opacity=".17"/><path d="M1090 860h650" stroke="{O}" stroke-width="4"/></g><path d="M1110 220h670M1760 220v540" fill="none" stroke="{N}" stroke-opacity=".17"/>')
rng=np.random.default_rng(4727);a=np.ones((540,960,4),dtype=np.uint8)*255;a[:,:,:3]=95;a[:,:,3]=rng.integers(0,10,(540,960),dtype=np.uint8);Image.fromarray(a).save(p/'assets/textures/print-grain.png')
