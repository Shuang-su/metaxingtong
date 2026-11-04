# R05最小差分核验

实际只读读取R04/R05材白，R05材BLEND和GLB均与R04对应原件逐字节相同，SHA见R05-glb-byte-diff.json。不是新渲染或新几何版本。

R05白仅WHITE_clay的Principled Base Color RGB由.7改.35，alpha1保持；其余所核节点输入/连接不变。187mesh世界几何与UV、12相机、灯光参数/节点、world及隐藏状态与R04完全同，R05材白上述内容亦同。文字非流形修复保持。详见R05-diff-check.json。

白GLB解析全部JSON与BIN比较：BIN块逐字节同；JSON仅BaseColorFactor的RGB三项及新增说明purpose的extras改变，其它字段同。因此不是严格‘只有base factor字段’，另有无渲染效应的元信息。未重复完整GLB回导，依据R04真实回导和此差分复用限定技术结论。地面合成纹理材版也因原件字节相同继续适用。

实际看R05-preview/white_MAIN_preview.png：门边、墙竖条、近灯和顶格现可辨，仍有明显低样本噪点及远灯细节不清。初稿仅看过R04三源预览而未看其MAIN，故将可比性描述过强；已记下此错误。经producer指出，现补看R04-preview/white_MAIN_preview.png并核preview_r04.py/preview_r05.py，确认两MAIN均同相机、16samples、60%和6CPU。实看R05墙竖条和顶格相对更易辨，不量化提升，不将其作为来源吻合证据。该预览不是正式24张套图、不是来源直接叠图、不是8角完成证据。原23-S3/灯身份与几何假设失败仍全部保留；来源未验收。
