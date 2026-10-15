from pathlib import Path
from PIL import Image
import shutil, hashlib, json, html
root=Path('/workspace/scratch/fa58bfcf0425')
out=root/'hospital_bed_context_review_20261015/independent_visual'
(out/'sources').mkdir(exist_ok=True)
base=root/'hospital_cloud_capture_20261015/long82_105'
refs=root/'hospital_anchor_preparation_20261014/restored'
items=[
('L1',base/'obs_5476.600449.jpg','VIEWPORT 1180×757 JPEG · 5476.600449 s','低机位仅见单端板局部、一个完整孔、中央凹槽疑似局部；床垫外侧、托架/斜撑、单处轮脚有新增信息。不是患者眼位标定图。',[(760,95,420,500,'A'),(790,265,390,190,'B'),(815,408,365,238,'C'),(908,618,87,76,'D')]),
('L2',base/'obs_5477.528817.jpg','VIEWPORT 1180×757 JPEG · 5477.528817 s','紧邻渐暗帧仍呈相同局部床构成。曝光更差，未补出第二端板或完整长侧。',[]),
('B1',base/'obs_5663.912151.jpg','VIEWPORT 1180×757 JPEG · 5663.912151 s','双孔、中央长圆角凹槽与浅拱轮廓清楚；床端—电视—左窗—双杆的共现关系可与 F/G 对照。',[(430,495,596,160,'E'),(620,348,340,170,'F'),(126,27,678,69,'G')]),
('B2',base/'obs_5668.329653.jpg','VIEWPORT 1180×757 JPEG · 5668.329653 s','近邻视角重复双孔与凹槽；床端遮住电视下缘。只支持此视角的投影遮挡，不等于电视/床端实体等高。',[]),
('B3',base/'obs_5693.628433.jpg','VIEWPORT 1180×757 JPEG · 5693.628433 s','相同床端特征与电视/左窗/上方双杆共现，右缘有门局部。镜头姿态不同，不能直接与前帧做刚性像素差。',[]),
('T1',base/'obs_6063.423552.jpg','VIEWPORT 1180×757 JPEG · 6063.423552 s','前景是有木纹的桌面，放着通话屏设备；左侧绿椅，后方棕色双坐垫沙发。此图没有可确认的病床几何。',[(350,360,830,300,'H')]),
('F',refs/'hospital-F-tv-BV1GqXMByE1s-t1823.678156-native.png','NATIVE 1920×1080 PNG · 原生参考 F','原生 F 底部截去大部分端板；保留孔上部、中央凹槽上缘及同组电视/左窗/双杆。心率叠字不是几何。',[]),
('G',refs/'hospital-G-bed-edge-BV1GqXMByE1s-t1116.180816-native.png','NATIVE 1920×1080 PNG · 原生参考 G','原生 G 右缘只有单孔与中央凹槽局部；床面在右下，与窗前沙发/绿椅同处构图。此图也不提供完整床侧。',[]),
('N665',root/'hospital_expanded_video_20261014_0315/native_frames/BV1GqXMByE1s_665.501733_downward_native.png','NATIVE 1920×1080 PNG · 665.501733 s','前景可直接见浅木纹、平整板面与较硬直的远侧边缘，判为木桌面高置信。条状暗带为落在板面的阴影，不是阶梯体块。',[(1160,790,760,290,'J')]),
('N640',root/'hospital_empty_frame_annotation_20261014/source_views/BV1GqXMByE1s_640.406589_empty_hospital_native.png','NATIVE 1920×1080 PNG · 640.406589 s','底部仅露窄浅色前景面。右侧上边略不规则，表面有暗条；可确认平面及遮挡边界，身份待定，不强制改为桌或床。',[]),
('H',refs/'hospital-H-window-BV1GqXMByE1s-t1101.728114-native.png','NATIVE 1920×1080 PNG · 原生参考 H','底部前景更窄；标注点只表示可见浅色表面，不能从窄条恢复厚度、床阶梯或桌腿。',[]),
('CUTS',base/'review_5473_5482.jpg','CONTACT SHEET · 原采集 viewport 的缩略图汇总','独立目视确认：棕墙前人物正面 → 5476 低机位床 → 5477–5479 变暗 → 5480–5481 帘前演出；不是低机位床直接切电视。此页为已有缩略汇总，不能做细节或像素测量。',[])
]
manifest=[]
cards=[]
point_data={
 'N665': {'identity':'wood_table_surface','confidence':'high','points':[(1260,1020),(1780,1040)]},
 'N640': {'identity':'visible_foreground_surface_identity_unresolved','confidence':'unresolved','points':[(1530,1030),(1770,1000),(1850,1060)]},
 'H': {'identity':'visible_foreground_surface_identity_unresolved','confidence':'unresolved','points':[(1740,1035),(1840,1025)]},
 'G': {'identity':'visible_foreground_surface_identity_unresolved','confidence':'unresolved','points':[(1570,985),(1805,1055)]},
 'T1': {'identity':'wood_table_surface','confidence':'high','points':[(995,540),(560,615)]}
}
point_manifest=[]
for sid,src,label,cap,boxes in items:
    dst=out/'sources'/src.name
    shutil.copyfile(src,dst)
    with Image.open(src) as im: w,h=im.size;fmt=im.format
    digest=hashlib.sha256(src.read_bytes()).hexdigest()
    assert hashlib.sha256(dst.read_bytes()).hexdigest()==digest
    native=sid in ['F','G','H','N665','N640']
    if sid=='G': cap='原生 G 右缘只有单孔与中央凹槽局部；右下可见浅色前景面与条状投影，但床垫/桌面身份仍待定。紧邻端板不足以证明同一实体，此图也不提供完整床侧。'
    manifest.append({'id':sid,'source_path':str(src),'copied_relative_path':str(dst.relative_to(out)),'width':w,'height':h,'format':fmt,'sha256':digest,'native_reference':native,'viewport_not_native':not native and sid!='CUTS','role':cap,'annotation_boxes_image_px': [{'x':x,'y':y,'width':bw,'height':bh,'label':tag} for x,y,bw,bh,tag in boxes]})
    svg=''.join(f'<rect x="{x}" y="{y}" width="{bw}" height="{bh}"/><text x="{x+8}" y="{y+24}">{tag}</text>' for x,y,bw,bh,tag in boxes)
    if sid in point_data:
        d=point_data[sid]
        for i,(x,y) in enumerate(d['points'],1):
            pid=f'{sid}-P{i}'
            point_manifest.append({'id':pid,'source_id':sid,'source_path':str(src),'image_width':w,'image_height':h,'coordinate_origin':'top_left','x':x,'y':y,'coordinate_space':'native_1920x1080' if native else 'viewport_1180x757_not_native','point_kind':'visible_surface_interior','source_surface_identity':d['identity'],'identity_confidence':d['confidence'],'allowed_use':'native point may be used to compare existing model first-hit identity; viewport point is visual evidence only','not_allowed':'Do not infer thickness, object identity, or physical stepped geometry solely from brightness/shadow. Do not convert viewport point to native coordinates by scaling.'})
            svg+=f'<circle cx="{x}" cy="{y}" r="7" fill="#25e8ff" stroke="#07232a" stroke-width="2"/><text x="{x-100}" y="{y-14}" style="fill:#25e8ff;font-size:19px">{pid}</text>'
    cards.append(f'<section id="{sid}"><h2>{sid} · {html.escape(label)}</h2><p>{html.escape(cap)}</p><div class="evidence"><img src="sources/{src.name}" width="{w}" height="{h}" alt="{html.escape(label)}"><svg viewBox="0 0 {w} {h}" aria-hidden="true">{svg}</svg></div><p class="file">原图：{src.name}；保留原文件字节，未调光、锐化、补画或重采样。</p></section>')
(out/'source_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
(out/'foreground_identity_points.json').write_text(json.dumps({'status':'manual visual observations; not calibrated residual targets','coordinate_rules':'All points use original file pixels, top-left origin. Native and viewport points must remain separate.','points':point_manifest},ensure_ascii=False,indent=2)+'\n')
page='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>病床新观察：独立视觉图证</title><style>body{font:16px/1.6 system-ui,sans-serif;background:#f5f3ee;color:#202627;max-width:1320px;margin:32px auto;padding:0 20px}h1{font-size:28px}h2{font-size:20px;margin-bottom:8px}.notice{border-left:5px solid #b96c1b;background:#fff4e2;padding:16px}section{background:#fff;padding:18px;margin:26px 0;border:1px solid #d4d4cc}.evidence{position:relative}.evidence img{display:block;width:100%;height:auto}.evidence svg{position:absolute;inset:0;width:100%;height:100%;pointer-events:none}.evidence rect{fill:none;stroke:#ffbf38;stroke-width:3}.evidence text{fill:#ffbf38;stroke:#111;stroke-width:1;font:bold 24px sans-serif;paint-order:stroke}.file{font-size:13px;color:#666}nav a{margin-right:16px}</style><h1>病床新观察：独立视觉图证</h1><p class="notice">新截图是 1180×757 播放器 viewport JPEG，含标题栏与播放器叠层；标注框仅定位观察区域，不是几何量测。禁止用于 1920 原生像素残差或相机验收。原生 F/G 单独标识。所有图片均逐字节复制，框线由网页矢量层绘制。</p><nav>'''+''.join(f'<a href="#{sid}">{sid}</a>' for sid,*_ in items)+'''</nav><p>A：单端板与一完整孔；B：床垫外侧/窄托边；C：下方托架、斜撑和圆形连接局部；D：单处轮脚且部分受 UI 遮挡；E：双孔＋中央凹槽＋浅拱端板；F：后方电视；G：顶上两平行杆及短连接件；H：木桌与通话设备。框线重叠不表示构件连接。</p>'''+''.join(cards)+'''<p>结论详见 independent_visual_review.md；源文件身份与尺寸详见 source_manifest.json。</p></html>'''
(out/'evidence.html').write_text(page)
print('Wrote',out/'evidence.html')
print('Verified unchanged source copies:',len(manifest))
