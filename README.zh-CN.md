# Haixuan DiffBench（v0.1，精度赛道）

[English](README.md) · [榜单](site/index.html) · [场景](docs/SCENARIOS.md) · [协议](docs/PROTOCOL.zh-CN.md) · [局限](docs/LIMITATIONS.md)

面向刚体物理引擎的**开放、可复现精度基准**。所有场景都有解析或高精度数值真值，评分代码完全公开，引擎只返回状态轨迹、**无法影响评分口径**。**不设综合分、不做排名**：逐场景逐指标公开原始数值与固定的公开容差，包括对维护方不利的结果。

> **利益冲突披露**：DiffBench 由杭州海轩云智科技有限公司维护，该公司同时开发参赛引擎之一（Nexus）。请先阅读 [GOVERNANCE.md](GOVERNANCE.md) 与 [docs/LIMITATIONS.md](docs/LIMITATIONS.md)。欢迎独立审计与复现。

## 开放与不开放
开放：基准规格与 10 个场景及容差、真值与评分代码、隐藏集生成器、MuJoCo/MJX/MuJoCo-Warp/Newton/Brax/Drake 适配器与 Nexus **HTTP 客户端**、签名结果包、历史记录、榜单站点与报告生成器。
**不开放**：Nexus 引擎源码与托管 API 的服务端实现。Nexus 仅通过返回状态的托管 API 参赛，由同一份公开评分器在本地评分。

## 快速开始
```bash
pip install -e . && pip install mujoco
python -m unittest discover -s tests
python -m diffbench.runner --engines mujoco,drake --out results/run1 --raw
python -m diffbench.report --bundles 'results/*/bundle.json' --out report/ --lang zh
python -m diffbench.verify results/run1/bundle.json --rescore results/run1
# Nexus：export DIFFBENCH_NEXUS_URL=https://www.openaethos.com; --engines nexus_pgs --nexus http
```

## 首批结果怎么读
公开集、dt=1/240、CPU 赛道，10 个场景中全部指标均在公开容差内的场景数：Nexus PGS 10、Nexus DiffRigid 9（二者均为厂商自配入口）；MuJoCo / MJX / MuJoCo-Warp / Newton-XPBD / Newton-MuJoCo 各 5；Brax 4；Drake 3。
这只是便利性汇总，**不是排名**：容差刻意严格，默认一阶积分器在部分场景会按设计失败，反映的是对闭式真值的精度，不代表引擎整体质量、速度、鲁棒性、功能或适用性。Nexus 在我们的单环境 CPU 测量中慢于 MuJoCo（0.04–0.94×），梯度赛道与 GPU 赛道尚未建立。

许可证：代码 Apache-2.0；规格文本、文档、数据与结果包 CC-BY-4.0（见 LICENSE-DOCS，使用时请署名 Haixuan DiffBench）；第三方名称归其所有者（见 [TRADEMARKS.md](TRADEMARKS.md)）。
