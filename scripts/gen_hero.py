"""
Generate hero images for 30 Posti via Gemini Nano Banana Pro.
Concept: Cinematic wine pour — dark moody, top-down, gourmet wine bar.
Aspect: 16:9 for full-screen hero.
"""
import os
import sys
from datetime import datetime
from pathlib import Path

# Load Gemini key from my_ai_project .env
ENV_PATH = Path("/Users/mac/my_ai_project/.env")
for line in ENV_PATH.read_text().splitlines():
    if line.startswith("GEMINI_API_KEY="):
        os.environ["GEMINI_API_KEY"] = line.split("=", 1)[1].strip()
        break

from google import genai
from google.genai import types

OUT_DIR = Path("/Users/mac/projects/30-posti/assets/photos")
OUT_DIR.mkdir(parents=True, exist_ok=True)

MODEL = "gemini-3-pro-image-preview"

BASE = """Editorial cinematic photograph for a luxury wine bar hero banner.
Subject: a single elegant hand pouring deep ruby red wine from a dark bottle into a fine crystal glass.
Camera: top-down 70-degree angle, shallow depth of field, anamorphic lens look, 35mm film grain.
Setting: a small, intimate gourmet wine bar in a coastal Italian village (Praia a Mare, Calabria) — old stone wall background, aged cream-colored marble bar top with natural veining, one beeswax candle in glass holder slightly out of focus creating warm bokeh, a sprig of fresh rosemary, a folded raw-edge linen napkin, scattered crystals of sea salt, an antique brass corkscrew.
Lighting: chiaroscuro — single warm tungsten light source from upper right, deep shadows on the left side of the frame, candle flame highlights catching the rim of the glass and the falling wine stream.
Mood: intimate, sophisticated, slow, hand-crafted, "storia di cibo e di vino", quiet luxury.
Color palette: deep burgundy and oxblood wine, warm amber candlelight, cream marble (paper-tone #F5F0E8), espresso brown shadows, with a single accent of fuchsia magenta from a tiny wild flower or pomegranate seed in the frame.
Composition: STRICT — leave the upper-left third of the frame as dark negative space (deep brown to black gradient) for overlaid white serif typography. Wine action is in the lower-right two-thirds.
No people faces visible. No logos. No text. No watermarks.
Style: David Loftus food editorial, Cinelli Colombini wine ad, FT Weekend magazine cover.
Aspect ratio 16:9, ultra high detail, hyperreal, professional food photography."""

VARIANTS = [
    ("a-pour", "Focus on the moment the wine stream hits the glass, splash droplets frozen mid-air, candle directly behind glass creating glow-through."),
    ("b-counter", "Wider crop showing more of the marble bar top, glass already 1/3 full, the bottle label hand-written and partially visible (no readable text), aged wooden serving board with one slice of aged pecorino visible at the right edge."),
    ("c-still", "Glass is already full and being set down by the hand, droplet running down the side, the bottle stands behind it, candle and rosemary in foreground bokeh, more cinematic stillness than action."),
]


def gen(name: str, extra: str):
    prompt = BASE + "\n\nVariant direction: " + extra
    print(f"[*] {name}: generating...")
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    resp = client.models.generate_content(
        model=MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_modalities=["IMAGE", "TEXT"],
            image_config=types.ImageConfig(aspect_ratio="16:9"),
        ),
    )
    image_data = None
    for part in resp.candidates[0].content.parts:
        if hasattr(part, "inline_data") and part.inline_data:
            if part.inline_data.mime_type.startswith("image/"):
                image_data = part.inline_data.data
                break
    if not image_data:
        print(f"[!] {name}: no image returned")
        return None
    out = OUT_DIR / f"hero-{name}.png"
    out.write_bytes(image_data)
    print(f"[+] {name}: {out}  ({len(image_data)/1024:.0f} KB)")
    return out


def main():
    only = sys.argv[1] if len(sys.argv) > 1 else None
    paths = []
    for name, extra in VARIANTS:
        if only and only != name:
            continue
        try:
            p = gen(name, extra)
            if p:
                paths.append(p)
        except Exception as e:
            print(f"[!] {name}: {e}")
    print()
    print(f"Done: {len(paths)} files")
    for p in paths:
        print(f"  {p}")


if __name__ == "__main__":
    main()
