"""Hand-drawn style home lab doodle, amber line-art on a transparent background.

Animated with SMIL: good traffic rides through the bouncer and tunnel to the
house, bots bounce off the bouncer and fall. Writes assets/homelab-route.svg
(dark mode) and assets/homelab-route-light.svg (light mode):
    python scripts/gen_homelab_doodle.py

The embedded Patrick Hand font (fonts/patrick-hand.woff2, SIL OFL, see
fonts/OFL.txt) is a subset covering only: a-z A-Z 0-9 space ~ ( ) " ' . , : ! ? - ·
If you add text with other characters, re-download the subset from
https://fonts.googleapis.com/css2?family=Patrick+Hand&text=<characters>
(the woff2 URL is in the returned CSS; request it with a browser User-Agent).
"""
import base64
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
ASSETS = HERE.parent / "assets"
# (ink, bot red, page background) for dark mode and light mode
OUTS = {
    ASSETS / "homelab-route.svg": ("#ff9f1c", "#ff5a5a", "#0d1117"),
    ASSETS / "homelab-route-light.svg": ("#b35900", "#c62828", "#ffffff"),
}
font_b64 = base64.b64encode((HERE / "fonts" / "patrick-hand.woff2").read_bytes()).decode()

CYCLE = 6  # seconds per packet loop


def quad_len(p0, c, p1, n=200):
    pts = [
        ((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * c[0] + t ** 2 * p1[0],
         (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * c[1] + t ** 2 * p1[1])
        for t in (i / n for i in range(n + 1))
    ]
    return sum(math.dist(a, b) for a, b in zip(pts, pts[1:]))


# good packet: in along the dotted path, hidden through the cloud, out along the tunnel
GOOD_PATH = "M160 96 Q235 52 312 88 L470 128 Q560 190 628 124"
_seg = [quad_len((160, 96), (235, 52), (312, 88)), math.dist((312, 88), (470, 128)),
        quad_len((470, 128), (560, 190), (628, 124))]
F1 = _seg[0] / sum(_seg)
F2 = (_seg[0] + _seg[1]) / sum(_seg)

# bot: in along the dotted path, bonks the cloud, bounces back and drops
BAD_PATH = "M160 96 Q235 52 306 86 Q296 66 282 82 Q272 104 268 170"
H = quad_len((160, 96), (235, 52), (306, 86))
H /= H + quad_len((306, 86), (296, 66), (282, 82)) + quad_len((282, 82), (272, 104), (268, 170))


def good_packet(A, begin, window):
    return f"""
  <circle r="5.5" fill="{A}" opacity="0">
    <animateMotion path="{GOOD_PATH}" dur="{CYCLE}s" begin="{begin}s" repeatCount="indefinite"
      calcMode="linear" keyTimes="0;0.35;0.5;0.9;1" keyPoints="0;{F1:.3f};{F2:.3f};1;1"/>
    <animate attributeName="opacity" dur="{CYCLE}s" begin="{begin}s" repeatCount="indefinite"
      keyTimes="0;0.03;0.34;0.36;0.49;0.51;0.89;0.91;1" values="0;1;1;0;0;1;1;0;0"/>
  </circle>
  <rect x="{window[0]}" y="{window[1]}" width="18" height="16" fill="{A}" opacity="0">
    <animate attributeName="opacity" dur="{CYCLE}s" begin="{begin}s" repeatCount="indefinite"
      keyTimes="0;0.9;0.93;1" values="0;0;0.7;0"/>
  </rect>"""


def bot(R, BG, begin, word, wx, wy):
    return f"""
  <g opacity="0">
    <circle r="7" fill="{R}"/>
    <path d="M-3 -3 L3 3 M3 -3 L-3 3" stroke="{BG}" stroke-width="2" stroke-linecap="round"/>
    <animateMotion path="{BAD_PATH}" dur="{CYCLE}s" begin="{begin}s" repeatCount="indefinite"
      calcMode="linear" keyTimes="0;0.3;0.45;1" keyPoints="0;{H:.3f};1;1"/>
    <animate attributeName="opacity" dur="{CYCLE}s" begin="{begin}s" repeatCount="indefinite"
      keyTimes="0;0.03;0.4;0.46;1" values="0;1;1;0;0"/>
  </g>
  <text class="nope" x="{wx}" y="{wy}" opacity="0">{word}
    <animate attributeName="opacity" dur="{CYCLE}s" begin="{begin}s" repeatCount="indefinite"
      keyTimes="0;0.29;0.31;0.42;0.46;1" values="0;0;1;1;0;0"/>
  </text>"""


def render(A, R, BG):
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="800" height="270" viewBox="0 0 800 270">
  <defs>
    <style>
      @font-face {{ font-family: 'Patrick Hand'; src: url(data:font/woff2;base64,{font_b64}) format('woff2'); }}
      text {{ font-family: 'Patrick Hand', 'Comic Sans MS', cursive; fill: {A}; text-anchor: middle; }}
      .label {{ font-size: 24px; }}
      .sub {{ font-size: 17px; fill-opacity: 0.7; }}
      .note {{ font-size: 16px; fill-opacity: 0.6; }}
      .ink {{ fill: none; stroke: {A}; stroke-width: 2.4; stroke-linecap: round; stroke-linejoin: round; }}
      .faint {{ stroke-opacity: 0.55; }}
      .dots {{ stroke-dasharray: 2 8; stroke-width: 3; }}
      .dash {{ stroke-dasharray: 10 8; }}
      .nope {{ font-size: 20px; fill: {R}; }}
    </style>
    <filter id="rough" x="-5%" y="-5%" width="110%" height="110%">
      <feTurbulence type="fractalNoise" baseFrequency="0.035" numOctaves="2" seed="7"/>
      <feDisplacementMap in="SourceGraphic" scale="3.5"/>
    </filter>
  </defs>

  <g filter="url(#rough)">
    <!-- you: a little globe -->
    <circle class="ink" cx="110" cy="100" r="40"/>
    <ellipse class="ink faint" cx="110" cy="100" rx="17" ry="40"/>
    <path class="ink faint" d="M72 88 Q110 78 148 88 M72 112 Q110 122 148 112"/>
    <line class="ink faint" x1="70" y1="100" x2="150" y2="100"/>

    <!-- path: globe to cloud -->
    <path class="ink dots" d="M160 96 Q235 52 312 88"/>
    <path class="ink" d="M298 78 L314 89 L297 96"/>

    <!-- the bouncer: a cloud wearing sunglasses, flinches when a bot hits it -->
    <g>
      <path class="ink" d="M338 126 Q312 126 314 106 Q316 86 340 88 Q344 60 374 62 Q396 44 420 62 Q448 56 456 82 Q484 86 482 108 Q480 128 456 126 Z"/>
      <path class="ink" d="M372 96 h20 q-2 12 -10 12 q-8 0 -10 -12 z M404 96 h20 q-2 12 -10 12 q-8 0 -10 -12 z M392 98 h12"/>
      <path class="ink faint" d="M386 116 q12 5 24 0"/>
      <animateTransform attributeName="transform" type="translate" dur="{CYCLE / 2}s" begin="{1.5 + 0.3 * CYCLE}s"
        repeatCount="indefinite" keyTimes="0;0.04;0.08;0.12;1" values="0 0;4 -1;-2 0;0 0;0 0"/>
    </g>

    <!-- secret tunnel: cloud swoops down and back up to the house -->
    <path class="ink dash" d="M470 128 Q560 190 628 124"/>
    <path class="ink" d="M612 122 L630 122 L627 140"/>

    <!-- my house -->
    <path class="ink" d="M640 96 L700 48 L760 96"/>
    <rect class="ink" x="652" y="92" width="96" height="70"/>
    <rect class="ink" x="690" y="124" width="22" height="38"/>
    <rect class="ink faint" x="664" y="104" width="18" height="16"/>
    <rect class="ink faint" x="720" y="104" width="18" height="16"/>
    <path class="ink faint" d="M735 62 v-16 h10 v24"/>
    <path class="ink faint" d="M740 38 q6 -6 0 -12 q-6 -6 0 -12"/>
  </g>
{good_packet(A, 0, (664, 104))}
{good_packet(A, CYCLE / 2, (720, 104))}
{bot(R, BG, 1.5, "nope!", 292, 56)}
{bot(R, BG, 1.5 + CYCLE / 2, "not today", 280, 50)}

  <circle cx="24" cy="18" r="5" fill="{A}"/>
  <text class="note" x="50" y="23">legit</text>
  <circle cx="86" cy="18" r="6" fill="{R}"/>
  <path d="M83 15 L89 21 M89 15 L83 21" stroke="{BG}" stroke-width="1.8" stroke-linecap="round"/>
  <text class="note" x="110" y="23">bots</text>

  <text class="label" x="110" y="176">you</text>
  <text class="sub" x="110" y="198">(anywhere)</text>

  <text class="label" x="398" y="176">my VPS bouncer</text>
  <text class="sub" x="398" y="198">"no bots allowed"</text>
  <text class="note" x="556" y="140">secret tunnel</text>

  <text class="label" x="700" y="190">my house</text>
  <text class="sub" x="700" y="212">~20 apps live here</text>

  <text class="note" x="400" y="258">psst: the admin stuff never leaves the house · a GPU does the AI chores</text>
</svg>
"""
for out, colors in OUTS.items():
    svg = render(*colors)
    out.write_text(svg, encoding="utf-8")
    print("wrote", out.relative_to(HERE.parent), len(svg) // 1024, "KB")
