# R06b sidecar图像沿革勘误

基于真实冻结07ddd671517ef17f303c68c9d2513caca3fd7c15新增文本勘误。原models/roof-r06b-recovery.json字节保持不变。

原render_products字段整句“R03 pixels reused: mesh/material/light/source cameras unchanged. Inspection cameras materialized from exact render-cameras.json Euler/location/lens.”是从R04继承的错误描述，现明确废止。它不能用于R06b：中央CLOUD_2几何已经变化，R06b来源/近景像素是实际新渲，不是R03图像复用。

新描述入口为models/roof-r06b-recovery-description-corrected.json，仅替换render_products并新增render_products_addendum指向机器清单。全部其他恢复参数经深层相等核对，与旧JSON完全相同。旧GLB/材白BLEND/灯/相机/恢复参数和图像均未修改；原restore_r06b_glb.py从不读取render_products，既有独立实际双fresh恢复核验仍有效。本勘误不需要新模型或重渲。

实际新渲18张：R05基线4张、R06初失败4张、R06b材白8张（两SOURCE与front/oblique-close，各8samples）、R06b材白front-close64两张。R05基线也是本次脚本实际重渲，不与继承旧PNG混称。R06b新增两个原尺寸direct50由新R06b材图派生，独立逐像素核过。

renders/内全部继承PNG仅作R05或更早历史：旧CHECK01..08、DIAG09及其有效八角联系表不代表R06b新渲或重新通过检查，main-candidate-r04也是旧alias。逐文件SHA/尺寸/角色与脚本对应见render-products-correction.json；来源裁图、手工描线、before-after拼图属于派生比较，不增加实际渲染数量或源基线。

SOURCE仍FAILED，云实例未证、非native/时刻未知、背厚/内纹推断等限制不变。此提交只纠正文字沿革，不推广实验为CURRENT。

独立小复核补充：18张是整个R06实验过程实际新渲总数，其中当前R06b仅10张（8张8samples＋2张64samples），R05基线4张和R06初失败4张不能计入当前R06b。18新渲、41历史PNG、2direct50共61文件的SHA/字节/尺寸均已独立核对。此轮未重跑Blender，未改前次QA或原五件；附录在metadata-correction-independent-qa。
