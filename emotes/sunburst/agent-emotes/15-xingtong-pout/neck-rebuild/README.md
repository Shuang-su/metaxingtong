# 颈肩与双拳重制：第 17 帧官方 Images API 掩膜试修（进行中）

本目录与上一版 `neck-follow/` 分开保存，尚未替换任何已交付 GIF。用户认为上一版动作突兀，并要求改用 API 重做；最新要求同时去掉头顶右上角蓝白挂件，保留紫色发箍和头发。

## 当前事实

- 已准备原版星瞳第 17 帧，等比放大至 1024×1024；奶绿真实同帧作为第二输入。
- `sources/mask-17-1024.png` 为同尺寸 RGBA PNG；透明区域可编辑，覆盖颈肩、完整双拳和袖口；面部最大皮肤连通域及周边一像素明确保护。`mask-review.jpg` 的红色为开放范围。
- 输入像素映射、SHA、掩膜多边形和开放像素数见 `prepared-input.json`。
- `edit_frame17.py --check` 已实际执行通过。非 check 模式已实际执行；因为当前运行阶段没有 `OPENAI_API_KEY`，在发请求前以退出码 2 停止。没有伪造官方 PNG、request ID 或成功回执。
- 已检查当前云机配置：HTTP 网络策略已生效且允许出站，未配置任何 Secret。默认沙箱无法连接继承的代理，经过允许的沙箱外只读探测可到达 `https://api.openai.com/v1/models`，无凭据返回 401。这不是编辑权限或余额验证。
- 当前工具集中未提供 `cloud_environment.request_changes`。已请用户通过本云任务环境设置绑定既有凭据，不新建密钥，不从原本机配置复制，不经 Git 中转。

## 已保存的内置接口参考试片

`sources/api-keys.png` 为内置 `image_gen.imagegen` 的实际返回 PNG；`sources/api-keys-no-mascot.png` 为其后去掉蓝白挂件的实际编辑结果。二者均通过工具返回的 PNG 字节保存，非官方 Images API 的成功凭据，不能用来声称 `POST /v1/images/edits` 已打通。内置工具未报告可用的模型名、request ID 或 savedPath，因此不填写这些字段。

`internal_preview.py` 可重建实际试片的局部合成；其头饰和衣领边缘仍有可见接缝，未达到成品标准，不用于替换 GIF。已通过 89 个特征点内点配准，掩膜外像素精确保持原版调色图。官方掩膜试修将解决这种跨图直接拼接的问题。

试片是三格关键姿势参考（11、17、25）；还没有把它们的重绘脸部用于成品。`sources/api-reference.png` 顶行为原版星瞳经既有调色的三姿势，底行为真实同帧奶绿。用户最新指定的官方路线改为单张 1024px 掩膜试修，以原帧为底合回。

## 官方单帧调用

```bash
python prepare.py           # 在本任务 venv 中运行，需 OpenCV
python edit_frame17.py --check
python edit_frame17.py      # 仅在现有 OPENAI_API_KEY 已绑定到当前运行阶段后运行
python compose_frame17.py   # 仅在实际返回并保存 frame17-api.png 后运行
```

请求固定为 `POST https://api.openai.com/v1/images/edits`、`gpt-image-2.6-sunburst`、`1024x1024`、`quality=medium`、`output_format=png`、`n=1`、180s 超时、零自动重试。不使用未经确认的代理占位密钥；HTTP 网络 Secret 绑定若被选用，必须先确认其实际绑定和文档中的客户端用法再适配。

合成脚本只导入 mask 的可编辑像素，并在 768px 尺寸再次合回原帧的掩膜外像素，防止缩放导致头脸变化。每次真正成功后生成输入、输出 SHA 与 request ID 回执，失败只记状态码/安全错误类型，不打印密钥、原始响应或认证头。

单帧审看通过后才扩到 11–25 帧短段：使用原版每帧身体为底，颈肩与左右完整拳袖分开处理，不再用首帧整体贴片，也不再用肤色阈值逐帧硬抬整个身体。再覆盖全部 54 帧及原时值表。官方 GIF 输出不用于此路线。

官方接法由原任务提供：
- https://developers.openai.com/api/docs/models/gpt-image-2.6-sunburst
- https://developers.openai.com/api/reference/resources/images/methods/edit
- https://developers.openai.com/api/docs/guides/image-generation
