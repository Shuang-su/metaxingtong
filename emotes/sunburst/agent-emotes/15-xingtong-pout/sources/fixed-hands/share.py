"""Refresh the side-by-side GIF and replace the corrected entry in the existing ZIP."""
from pathlib import Path
from zipfile import ZipFile

from PIL import Image

from render import SHOT, digest, index_colors, read, save


def refresh():
    root = SHOT.parent
    manifest = read(SHOT / "manifest.json")
    delays = manifest["frame_durations_ms"]
    pairs = []
    with Image.open(SHOT / "chat.gif") as left, Image.open(root / "10-pout/chat.gif") as right:
        assert left.n_frames == right.n_frames == len(delays)
        for i, duration in enumerate(delays):
            left.seek(i)
            right.seek(i)
            assert left.info["duration"] == right.info["duration"] == duration
            pair = Image.new("RGB", (640, 320))
            pair.paste(left.convert("RGB"))
            pair.paste(right.convert("RGB"), (320, 0))
            pairs.append(pair)
    indexed = index_colors(pairs)
    path = SHOT / "paired.gif"
    indexed[0].save(path, save_all=True, append_images=indexed[1:], duration=delays,
                    loop=0, disposal=1, optimize=False)
    delivery = read(root / "delivery.json")
    delivery["comparison"].update(sha256=digest(path.read_bytes()), durations_ms=delays)
    archive = root / delivery["zip"]["filename"]
    replacement = (SHOT / "chat.gif").read_bytes()
    target = next(row for row in delivery["gifs"] if row["filename"].startswith("15 "))
    updated = archive.with_suffix(".zip.partial")
    with ZipFile(archive) as previous, ZipFile(updated, "w") as result:
        for item in previous.infolist():
            data = replacement if item.filename == target["filename"] else previous.read(item)
            result.writestr(item, data)
    with ZipFile(updated) as result:
        assert result.testzip() is None and len(result.namelist()) == len(delivery["gifs"])
        for row in delivery["gifs"]:
            expected = digest(replacement) if row == target else row["sha256"]
            assert digest(result.read(row["filename"])) == expected
    updated.replace(archive)
    target["sha256"] = digest(replacement)
    delivery["zip"].update(bytes=archive.stat().st_size, sha256=digest(archive.read_bytes()))
    save(root / "delivery.json", delivery)


if __name__ == "__main__":
    refresh()
