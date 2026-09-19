"""Wrap Simple Icons logos in skillicons-style dark tiles (plus a bare Intel logo
for the home lab row). Writes assets/icons/*.svg:
    python scripts/gen_icons.py

To add a tile, find the logo's slug at https://simpleicons.org and add it to TILES.
"""
import re
import urllib.request
from pathlib import Path

# pinned so re-running gives the same shapes; bump deliberately
SIMPLE_ICONS = "https://cdn.jsdelivr.net/npm/simple-icons@16.31.0/icons/{slug}.svg"
OUT = Path(__file__).resolve().parent.parent / "assets" / "icons"
OUT.mkdir(parents=True, exist_ok=True)

TILE_BG = "#242938"  # skillicons dark tile colour

# slug -> logo colour on the dark tile (black/near-black brands switched to white)
TILES = {
    "appium": "#EE376D",
    "tailscale": "#FFFFFF",
    "rclone": "#3F79AD",
    "kdeplasma": "#1D99F3",
    "jsonwebtokens": "#FFFFFF",
}


def path_of(slug):
    with urllib.request.urlopen(SIMPLE_ICONS.format(slug=slug)) as resp:
        svg = resp.read().decode("utf-8")
    return re.search(r'<path d="([^"]+)"', svg).group(1)


for slug, color in TILES.items():
    tile = f"""<svg xmlns="http://www.w3.org/2000/svg" width="256" height="256" viewBox="0 0 256 256">
  <rect width="256" height="256" rx="60" fill="{TILE_BG}"/>
  <path transform="translate(53 53) scale(6.25)" fill="{color}" d="{path_of(slug)}"/>
</svg>
"""
    (OUT / f"{slug}.svg").write_text(tile, encoding="utf-8")
    print("tile", slug)

# bare logo in brand blue, same as the other home lab icons
(OUT / "intel.svg").write_text(
    f'<svg xmlns="http://www.w3.org/2000/svg" width="24" height="12" viewBox="0 6 24 12"><path fill="#0071C5" d="{path_of("intel")}"/></svg>\n',
    encoding="utf-8",
)
print("bare intel")
