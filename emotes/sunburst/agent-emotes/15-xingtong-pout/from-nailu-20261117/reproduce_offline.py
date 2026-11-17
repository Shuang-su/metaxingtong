"""Rebuild delivered files from cached new artwork without making API requests."""
from pathlib import Path
import hashlib, json, subprocess, sys
HERE = Path(__file__).resolve().parent

def hashes():
    return {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((HERE/'delivery').glob('*.gif'))}

def main():
    before = hashes()
    subprocess.run([sys.executable, 'build.py'], cwd=HERE, check=True)
    subprocess.run([sys.executable, 'verify.py'], cwd=HERE, check=True, stdout=subprocess.DEVNULL)
    after = hashes(); different = [name for name in before if before[name] != after.get(name)]
    result = {'status': 'passed' if not different else 'mismatch', 'API_calls': 0,
              'compared_gif_files': len(before), 'byte_identical': not different,
              'different_files': different, 'before': before, 'after': after}
    (HERE/'offline-reproduction.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2))
    if different:
        raise SystemExit(1)

if __name__ == '__main__':
    main()
