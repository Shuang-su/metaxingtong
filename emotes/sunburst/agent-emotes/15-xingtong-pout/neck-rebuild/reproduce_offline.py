"""Rebuild from stored PNG/API receipts only and compare delivery bytes; no API calls."""
from pathlib import Path
import hashlib, json, subprocess, sys

HERE = Path(__file__).resolve().parent

def hashes():
    return {str(p.relative_to(HERE)): hashlib.sha256(p.read_bytes()).hexdigest()
            for folder in ['short-review', 'full-review'] for p in sorted((HERE / folder).glob('*.gif'))}

def main():
    before = hashes()
    commands = [['compose_keys.py', '1', '11', '17', '25'], ['build_short.py'], ['build_full.py'],
                ['verify_short.py'], ['verify_full.py']]
    for args in commands:
        print('Running ' + ' '.join(args), flush=True)
        subprocess.run([sys.executable, *args], cwd=HERE, check=True, stdout=subprocess.DEVNULL)
    after = hashes()
    mismatches = [name for name in before if before[name] != after.get(name)]
    report = {'status': 'passed' if not mismatches else 'mismatch', 'api_calls': 0,
              'compared_gif_files': len(before), 'byte_identical': not mismatches,
              'mismatches': mismatches, 'before': before, 'after': after}
    (HERE / 'offline-reproduction.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))
    if mismatches:
        raise SystemExit(1)

if __name__ == '__main__':
    main()
