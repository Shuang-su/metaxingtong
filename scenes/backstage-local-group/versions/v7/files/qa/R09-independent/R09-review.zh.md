# 后台R09箱柄有限修正独立QA

实际读取R08/R09材白原件；本次不以此前内存试验代替保存态。R09仅两CASE_handle_leg的根帽各16点（偶数0..30）world Z下降0.01100003719329834，XY精确不变；object矩阵不变，其余顶点与其他229对象不动，全部UV不变。原6相机、灯/world、材质节点、旧可见性相同，新增DIAG_case_handle_mount，总231mesh/7cam。

全体单体非流形0、面面积<1e-12退化0、体积正。材白继承5个人台球体索引排序差，但实际世界顶点多重集、loop-triangle坐标、逐面坐标/UV关联排序后，全部231对象精确同。不能说原始索引hash全部相同。

两保存模式接触结果一致：两根实际最低worldZ1.1790000200271606，最高1.25。两杆→箱连续三角距离0、BVH各32对；横杆链距离0，左27、右31对，右相对原29改变，不能等同接触面积不变。全场AABB候选及实际表面关系只有箱体与横杆，新增仅箱体，没有第三方包含/交叠候选。箱体→桌仍有0.007499992847442627正间隙、BVH0，未修其他瓶/珠/钟等旧问题。不证明Boolean焊合、承载或真实来源柄形。

两GLB从空场实际回导，231mesh/7cam齐，双向最近世界顶点误差≤4.76837158203125e-7；1192×671同画幅归一视框方向误差≤5.960464477539063e-8。逐相机矩阵数值在JSON。仅本次坐标与相机回导范围，不声称逐导出三角法线/全材质渲染完全等价。

4张1192×671原图与2crop已逐张实看、全记录核对。四图是R08基线材白和R09当前材白，仅一个人工近景机位。当前图可见所摄单根杆末端延到箱面；材质有噪声，白模对比低，杆顶裁切，不覆盖另一根全周或整个箱体。图像不构成来源直接叠图或整场验收。来源仍FAILED。

4图SHA/bytes/modelSHA/尺寸全匹配记录，记录均64samples/no denoise/同相机参数。两个原矩形[350,280,830,550]上下拼接crop全数组误差0、SHA匹配。没有重渲或修改生产文件。

精确当前原件：
- R09_material.blend SHA256 c8b3cc51e321438e3a1439efaa4ee3ea163cb483e5212d96f774d09105971627
- R09_material.glb SHA256 f1ec1e0154f0830a1a5372d68e1f5420cd0596218eb38795793ae828bdb5149e
- R09_white.blend SHA256 25523c6b24acc44ec1d9cfa326f399a7a5fe7790a3ec5fcec2a72b9935fcb6b2
- R09_white.glb SHA256 ddefb968fd9e8ec2852cc58a11c5870dd08b606bd952e84c40b78cd8678577ca

证据：R09-diff-check.json、R09-transforms.json、R09-shared-surface-check.json、R09-saved-contacts.json、R09-glb-projection-check.json、R09-images.json及对应独立脚本/log。线程覆盖更正另见independent-backstage-mannequin-qa-20261104/R07-thread-correction-addendum.zh.md，不修改旧冻结报告。
