"""Read all three private GIF streams and compare the decoded timelines."""
from pathlib import Path
import hashlib
import json
from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
EXPECTED = json.loads((HERE / "inputs.json").read_text())

def inspect(path):
    pixels = hashlib.sha256()
    durations = []
    with Image.open(path) as im:
        assert im.format == "GIF" and im.size == (768, 768) and im.info.get("loop") == 0
        for i in range(im.n_frames):
            im.seek(i)
            pixels.update(im.convert("RGB").tobytes())
            durations.append(im.info["duration"])
    assert len(durations) == 54 and sum(durations) == 4560
    return dict(file_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                decoded_rgb_sha256=pixels.hexdigest(), frames=len(durations),
                duration_ms=sum(durations), delays_ms=durations)

if __name__ == "__main__":
    results = {name:inspect(ROOT / item["path"]) for name,item in EXPECTED.items()}
    for name, result in results.items():
        assert result["file_sha256"] == EXPECTED[name]["sha256"], name
    assert all(result["delays_ms"] == results["nailu"]["delays_ms"] for result in results.values())
    print(json.dumps(results, indent=2))
