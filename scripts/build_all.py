"""Local convenience orchestrator: regenerate every SVG in the profile README.

Always runs the heatmap + info-card pipelines. Runs the photo/ASCII pipeline
only if assets/photo.jpg (or .png/.jpeg) is present, so this is safe to run
before the photo has been supplied.
"""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
PHOTO_CANDIDATES = ["photo.jpg", "photo.jpeg", "photo.png"]


def run(script_name: str, *args: str):
    cmd = [sys.executable, str(SCRIPTS / script_name), *args]
    print(f"$ {' '.join(cmd)}")
    subprocess.run(cmd, check=True)


def find_photo():
    for name in PHOTO_CANDIDATES:
        candidate = ROOT / "assets" / name
        if candidate.exists():
            return candidate
    return None


def main():
    run("fetch_contributions.py")
    run("render_heatmap_svg.py")
    run("generate_info_card_svg.py")
    run("generate_tagline_svg.py")

    photo = find_photo()
    if photo is None:
        print(
            "No assets/photo.jpg (or .png/.jpeg) found — skipping ASCII portrait "
            "generation. Drop a photo there and re-run this script to build it."
        )
    else:
        processed = ROOT / "assets" / "photo_processed.png"
        run("preprocess_photo.py", "--input", str(photo), "--output", str(processed))
        run("ascii_convert.py")
        run("render_ascii_svg.py")

    if (ROOT / "data" / "ascii_art.json").exists():
        run("render_combined_svg.py")
    else:
        print(
            "No data/ascii_art.json yet — skipping the combined synced hero SVG "
            "(needs the ASCII pipeline to have run at least once)."
        )


if __name__ == "__main__":
    main()
