# R07线程证据更正附录

原R07-review.zh.md与R07-executed-state-check.json保留不改。旧检查通过Blender CLI -t 1启动，两份执行态的render.threads均读为1。旧报告把脚本设定6线程与该次实际读取混写，因此旧JSON不能独立证明实际6线程。这是证据表述错误，现明确更正。

新脚本check_thread_override.py不渲染、不保存模型，分别新进程不带-t、带-t1、带-t6，读取R07保存态和R06应用原preview_r06.py对应设置后的状态：
- 无CLI线程覆盖：材白两版本均FIXED6，全部所核RNA状态相同。
- CLI -t1：即使脚本执行threads=6，实际RNA仍均FIXED1；其余状态相同。
- CLI -t6：均FIXED6，全部状态相同。

因此实际确认CLI线程数覆盖Scene线程RNA。新无覆盖检查支持R07保存6线程及R06脚本预期6线程的相同状态，旧-t1文件只证明覆盖条件下两态相同。制作方提供历史实际渲染命令-t6；本次不重演渲染，也不从脚本或PNG反推历史实际CPU调度。视觉相关场景/相机/样本/尺寸等相同性结论未被此线程覆盖推翻，但不能将任一线程数量等同CPU实际利用率。

新证据：R07-thread-override-no-cli.json、R07-thread-override-cli1.json、R07-thread-override-cli6.json及thread-no-cli.log/thread-cli1.log/thread-cli6.log。原件与原图均未改。
