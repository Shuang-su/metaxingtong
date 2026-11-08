"""Validate decoded deliverables, timing, protected eyes, and neck continuity."""
from pathlib import Path
import sys,json,hashlib,subprocess,shutil
import numpy as np
import cv2 as cv
from PIL import Image
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE));import generate as build
f=build.f

def read(path):
    frames=[];delays=[]
    with Image.open(path) as g:
        size=g.size;loop=g.info.get('loop')
        for i in range(g.n_frames):g.seek(i);frames.append(np.array(g.convert('RGB')));delays.append(g.info['duration'])
    return frames,delays,size,loop

def main():
    current,ds,_,_=read(HERE.parent/'master.gif');orig,ods,_,_=read(f.ORIGINAL/'master.gif')
    motion=json.loads((HERE/'motion.json').read_text());results={};fixed=None
    for name,size in [('master.gif',(768,768)),('chat.gif',(320,320)),('paired.gif',(640,320)),('review-112.gif',(112,112))]:
        frames,delays,actual,loop=read(HERE/name)
        assert len(frames)==54 and delays==ds==ods and sum(ds)==4560 and actual==size and loop==0
        results[name]=dict(size=size,frames=len(frames),duration_ms=sum(delays),delays_ms=delays,decoded_rgb_sha256=hashlib.sha256(b''.join(a.tobytes() for a in frames)).hexdigest(),file_sha256=hashlib.sha256((HERE/name).read_bytes()).hexdigest())
        if name=='master.gif':fixed=frames
    assert np.array_equal(current[0],fixed[0])
    eyes=[];neck=[]
    eye_region=np.zeros((512,512),np.float32);eye_region[267:343,149:367]=1
    for i,(a,b,row) in enumerate(zip(current,fixed,motion)):
        mask=f.warp(eye_region,f.mapping(f.TRACK['frames'][i]['nailu_eyes']),768)>.99
        changed=int(np.any(a!=b,axis=2)[mask].sum());assert changed==0,(i+1,changed)
        eyes.append(dict(frame=i+1,protected_pixels=int(mask.sum()),changed_pixels=changed))
        if i:
            matrix=np.array(row['final_body_matrix']);cx=int(round((matrix@np.array([400,680,1]))[0]));y=int(row['jaw_y'])
            white=b[y:y+24,cx-2:cx+3].min(2)>248
            gap=int(white.sum());neck.append(dict(frame=i+1,white_pixels_under_jaw=gap,full_width_white_rows=int(white.all(axis=1).sum())))
    assert not any(r['full_width_white_rows'] for r in neck),neck
    report=dict(inputs_commit='4ef01476009277a97aa1823ffee1262b6f53a688',decoder='Pillow '+Image.__version__,outputs=results,first_frame_exactly_matches_current=True,protected_eyes=eyes,neck_center_checks=neck,pose_comparison_size=Image.open(HERE/'pose-comparison.jpg').size)
    if shutil.which('ffmpeg'):
        proc=subprocess.Popen(['ffmpeg','-v','fatal','-i',str(HERE/'master.gif'),'-fps_mode','passthrough','-f','rawvideo','-pix_fmt','rgb24','-'],stdout=subprocess.PIPE)
        digest=hashlib.sha256();count=0
        while True:
            data=proc.stdout.read(1024*1024)
            if not data:break
            digest.update(data);count+=len(data)
        assert proc.wait()==0 and count==54*768*768*3
        assert digest.hexdigest()==results['master.gif']['decoded_rgb_sha256']
        report['independent_ffmpeg_decode']=dict(frames=54,decoded_rgb_sha256=digest.hexdigest())
    (HERE/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(first_frame_exact=True,all_54_eye_regions_exact=True,all_neck_center_samples_without_full_width_white_gap=True,outputs={n:{k:v for k,v in r.items() if k!='delays_ms'} for n,r in results.items()}),indent=2))
if __name__=='__main__':main()
