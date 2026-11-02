"""Explicitly derived, labeled review sheets. Never overwrite native sources or renders."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import hashlib, json

R = Path(__file__).resolve().parents[1]
O = R / 'stages/r06-review-candidate'
D = O / 'delivery-previews'
D.mkdir(exist_ok=True)
FONT = R / 'presentation/fonts/NotoSansCJK-Regular.ttc'
font = lambda n: ImageFont.truetype(str(FONT), n, index=2)
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
navy, amber, pale = '#142938', '#ffc366', '#ecf2f6'
records = []

def panel(canvas, path, xy, wh):
    original = Image.open(path).convert('RGB')
    assert original.width * wh[1] == original.height * wh[0], 'No crop or aspect change'
    canvas.paste(original.resize(wh, Image.Resampling.LANCZOS), xy)
    return {'path': str(path.relative_to(R)), 'sha256': sha(path),
            'original_dimensions': list(original.size), 'display_dimensions': list(wh),
            'scale': wh[0] / original.width, 'operation': 'uniform Lanczos display downsample only; no crop/warp/retouch'}

def finish(canvas, filename, role, panels):
    out = D / filename
    canvas.save(out)
    records.append({'path': str(out.relative_to(R)), 'role': role, 'bytes': out.stat().st_size,
                    'dimensions': list(canvas.size), 'sha256': sha(out), 'panels': panels,
                    'source_acceptance': 'NOT_PASSED', 'new_source_angle': False})

for state, label in [('material', '材质'), ('white', '白模')]:
    im = Image.new('RGB', (1920, 850), pale)
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, 1920, 116), fill=navy)
    d.text((24, 12), f'海港 R06｜8 个有效检查方位 · {label}', font=font(32), fill='white')
    d.text((24, 62), '派生联系表：原图 960×600 → 每格 480×300（50%）｜内部诊断，不是新增来源角度', font=font(23), fill=amber)
    inputs = []
    for i in range(1, 9):
        col, row = (i - 1) % 4, (i - 1) // 4
        x, y = col * 480, 116 + row * 342
        text = f'{i:02d}  共享几何 / 不隐藏物件'
        if i in (3, 7):
            text = f'{i:02d}  叶片遮局部边缘，核心可见'
        d.text((x + 10, y + 6), text, font=font(20), fill=navy)
        inputs.append(panel(im, O / f'checks/{state}/check-{i:02d}.png', (x, y + 38), (480, 300)))
    d.text((20, 808), '高角会自遮下方脚部；另有低接触机位与环境总览。源轮廓、环境、后续独立回放均未验收。', font=font(22), fill=navy)
    finish(im, f'eight-angle-{state}-derived.png', f'eight-angle {state} derived contact sheet', inputs)

titles = {'aug24-front': '实演正面局部', 'preview-front': '预告正宽', 'preview-high': '预告高俯局部',
          'preview-wide': '预告斜宽', 'preview-low': '预告低仰', 'companion-120': '同场节目侧部 120 秒',
          'companion-126': '同场节目侧部 126 秒'}
notes = {
    'aug24-front': '曲带宽度与弧线、箭框投影及后景不合；人物、节目图层与镜面反射不建作固定实体。',
    'preview-front': '核心前视外包络较近，但箭框位置、曲带剖面、外裙/侧阶与环境仍有明显残差。',
    'preview-high': '下碟与曲带脚部投影错位，箭框透视不合；粉色源灯态不通过按机位调色来掩盖。',
    'preview-wide': '斜宽的冠环/下碟与台盘严重错位，条件相机尚未标定；金色源灯态并非几何变化。',
    'preview-low': '下碟底形、内环及曲带轮廓不合；中央 V 形细节与精确灯具尚缺，后腿数仍未知。',
    'companion-120': '箭框/圆环与脚部有明显双边；此帧菜单曾选 4K，但实际原图仅 1920×1080。',
    'companion-126': '真 4K 侧部进一步显示脚面、箭框、边灯与背景位置不合；不能据局部推定完整棚顶。'}
cfgs = json.loads((O / 'source-cameras.json').read_text())
for i, cfg in enumerate(cfgs, 1):
    id = cfg['id']; w, h = cfg['size']
    im = Image.new('RGB', (1440, 430), pale)
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, 1440, 104), fill=navy)
    d.text((18, 8), f'海港 R06｜{i}/7 {titles[id]}｜训练输入 · 对齐未通过', font=font(28), fill='white')
    d.text((18, 49), f'派生展示：原生 {w}×{h} → 每格 480×270（{480/w:.1%}）｜条件机位；未作局部对齐', font=font(21), fill=amber)
    panels = [R / cfg['file'], O / f'source-renders/{id}/material.png', O / f'source-renders/{id}/material-direct50.png']
    labels = ['原生来源（仅整体缩小展示）', 'R06 同一全局青色材质状态', '原生源/材直接 50% 混合后缩小']
    inputs = []
    for col, (p, label) in enumerate(zip(panels, labels)):
        d.text((col * 480 + 8, 77), label, font=font(19), fill='white')
        inputs.append(panel(im, p, (col * 480, 104), (480, 270)))
    d.text((16, 384), notes[id], font=font(20), fill=navy)
    finish(im, f'comparison-{i:02d}-{id}-derived.png', 'source/material/direct50 derived comparison; training failure retained', inputs)

im = Image.new('RGB', (1440, 1120), pale)
d = ImageDraw.Draw(im)
d.rectangle((0, 0, 1440, 100), fill=navy)
d.text((18, 10), '海港 R06｜三组来源对照概览 · FAILED', font=font(31), fill='white')
d.text((18, 57), '全部为训练输入；条件机位未标定；共享同一材质状态；失败残差保留，仅等比缩小展示。', font=font(21), fill=amber)
inputs = []
for row, (id, bv, time) in enumerate([
        ('preview-front', 'BV1uqYvzDEZK', '5.051975'),
        ('preview-wide', 'BV1uqYvzDEZK', '13.767175'),
        ('companion-126', 'BV1gseHzLEuf', '126.768777')]):
    cfg = next(c for c in cfgs if c['id'] == id)
    w, h = cfg['size']; y = 100 + row * 340
    d.text((15, y + 3), f'{titles[id]}  {bv}  t={time}s｜{w}×{h} → 480×270（{480/w:.1%}）｜FAILED', font=font(20), fill=navy)
    paths = [R / cfg['file'], O / f'source-renders/{id}/material.png', O / f'source-renders/{id}/material-direct50.png']
    for col, (p, label) in enumerate(zip(paths, ['原生来源，仅缩小', 'R06 条件机位材质渲染', '原生源/材直接 50% 混合后缩小'])):
        d.text((col * 480 + 8, y + 30), label, font=font(18), fill=navy)
        rec = panel(im, p, (col * 480, y + 60), (480, 270))
        rec.update({'source_id': id, 'BV': bv, 'player_currentTime': time, 'fit_status': 'FAILED / conditional'})
        inputs.append(rec)
finish(im, 'three-source-failed-overview-derived.png', 'three selected training-source failure comparisons; explicitly derived overview', inputs)

main = O / 'source-renders/preview-front/material.png'
manifest = {'main_image_is_original_native_render': {'path': str(main.relative_to(R)), 'sha256': sha(main),
             'dimensions': [1920, 1080], 'derivative': False}, 'derived_previews': records,
            'font': {'path': str(FONT.relative_to(R)), 'sha256': sha(FONT), 'collection_index': 2,
                     'license': 'presentation/fonts/Noto-CJK-license.txt'},
            'scope': 'Small labeled delivery previews only. Native files retained unchanged. '
                     'Not a new source/holdout, not source acceptance, not proof of Issue image visibility.'}
(D / 'preview-manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2))
print('DERIVED_DELIVERY_PREVIEWS_READY', len(records))
