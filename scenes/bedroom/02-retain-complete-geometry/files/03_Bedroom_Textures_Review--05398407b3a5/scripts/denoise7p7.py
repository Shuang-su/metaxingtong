import time,subprocess
from pathlib import Path
R=Path(__file__).resolve().parent;D=R/'final7p7/renders';script=R/'source/unpacked/scripts/denoise_images.py'
while True:
 files=[p for p in D.glob('*.png') if not any(s in p.stem for s in ['denoised','overlay'])]
 for p in files:
  if not p.with_name(p.stem+'_denoised.png').exists() and time.time()-p.stat().st_mtime>3:
   subprocess.run(['python3',str(script),str(p)],check=True)
 if len(files)==18 and all(p.with_name(p.stem+'_denoised.png').exists() for p in files):break
 time.sleep(5)
print('ALL_18_DENOISED')
