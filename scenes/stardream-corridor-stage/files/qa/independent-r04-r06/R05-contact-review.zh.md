# R05支承接触有限审查

模型材质版 SHA9396214c4cbbf84d76990517a10be5c4cf52db7b2f295509b2721ebf8f52687b。实际calc_loop_triangles世界三角、BVH面交叠和全feature连续三角最小距离（点面/边边/边穿面，AABB仅作距离下界剪枝），并非仅bounds估计。只读单线程，不渲染不改模型。

8灯wall_plate→对应主墙最小表面距离全.00800013542175293，0面交叠；其中y0两plate实际与WALL_BATTEN交叠38对，其他6plate在全场BVH对照仅与bracket相交。不能把y0支撑推广到全部8灯。

两DOOR_handle→独立门叶最小距离.02249908447265625，均与所有其它mesh无BVH表面交叠。是实际位置间隙，尺寸为假设工作单位，不是真实米制测量。

8bracket→roof距离.02609086036682129，0面交叠；但bracket实际同时接diffuser和金属rib（左rib3、右rib0），不是“只接玻璃”。进一步所接rib→roof最小距离全0、左11/右12面交叠对。由此存在plate→bracket→rib→roof几何接触链，不能因缺少直接bracket→roof就称灯冠独立悬浮；亦不要求为此随意改源外观。该接触链不代表机械合理、焊合、真实连接结构或承载验收。

全场BVH查询只对plate/bracket/handle目标进行，未作全面其它物体间碰撞、自交、包含关系或机械结构测试。正距离不能单独排除一个物体被完全包含的情形；本处结合实际已知外置位置/三角几何，报告指定组件相互表面间隙，不泛化全场无支承。

原始完整结果R05-contact-check.json；新增rib→roof链验证R05-contact-check-with-rib.json；两实际脚本和日志均留存。所有来源语义/未知尺寸与23-S3失败不因本项改变。
