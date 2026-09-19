"""Nixie-tube section headers for the profile README (assets/headers/*.svg).

Edit SECTIONS to rename, renumber or add a section, then run:
    python scripts/gen_headers.py
"""
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "assets" / "headers"
OUT.mkdir(parents=True, exist_ok=True)

# (file, lab number, title, world line divergence)
SECTIONS = [
    ("about", "01", "LAB MEMBER PROFILE", "0.571024"),
    ("tools", "02", "LAB EQUIPMENT", "0.337187"),
    ("stack", "03", "FUTURE GADGETS", "1.130205"),
    ("homelab", "04", "IBN 5100 // HOME LAB", "0.523299"),
    ("stats", "05", "WORLD LINE STATUS", "1.048596"),
    ("members", "06", "LAB MEMBERS", "0.409420"),
]

FONT = "'Share Tech Mono','Courier New',Consolas,monospace"
AMBER = "#ff9f1c"

TEMPLATE = """<svg xmlns="http://www.w3.org/2000/svg" width="800" height="64" viewBox="0 0 800 64">
  <defs>
    <filter id="glow" x="-10%" y="-50%" width="120%" height="200%">
      <feGaussianBlur stdDeviation="2.5" result="blur"/>
      <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <pattern id="scan" width="4" height="3" patternUnits="userSpaceOnUse">
      <rect width="4" height="1" fill="{amber}" fill-opacity="0.05"/>
    </pattern>
  </defs>
  <rect x="1" y="1" width="798" height="62" rx="6" fill="#0b0b0b" stroke="{amber}" stroke-opacity="0.35"/>
  <rect x="1" y="1" width="798" height="62" rx="6" fill="url(#scan)"/>
  <rect x="20" y="16" width="4" height="34" rx="1" fill="{amber}" filter="url(#glow)"/>
  <text x="38" y="27" font-family="{font}" font-size="11" letter-spacing="2" fill="{amber}" fill-opacity="0.55">FUTURE GADGET LAB // SECTION {num}</text>
  <text x="38" y="50" font-family="{font}" font-size="22" font-weight="bold" letter-spacing="3" fill="{amber}" filter="url(#glow)">{title}</text>
  <text x="780" y="24" text-anchor="end" font-family="{font}" font-size="10" letter-spacing="2" fill="{amber}" fill-opacity="0.55">DIVERGENCE</text>
  <text x="780" y="50" text-anchor="end" font-family="{font}" font-size="26" letter-spacing="4" fill="{amber}" filter="url(#glow)">{div}</text>
</svg>
"""

for name, num, title, div in SECTIONS:
    svg = TEMPLATE.format(amber=AMBER, font=FONT, num=num, title=title, div=div)
    (OUT / f"{name}.svg").write_text(svg, encoding="utf-8")
    print("wrote", name)
