# Haixuan DiffBench 榜单（精度赛道）

规格版本 0.1.0（sha256 `3d6ecebe82b2ba79…`）。CPU 赛道；无综合分、无排名，逐指标列出原始数值。

## 环境与版本

- **brax_generalized**：brax 0.14.2, jax 0.10.2 (CPU, generalized pipeline)
- **drake**：drake 1.51.1 (point contact, discrete)
- **mjx**：mujoco-mjx 3.17.0, jax 0.10.2 (CPU)
- **mujoco**：mujoco 3.17.0
- **mujoco_warp**：mujoco_warp 3.16.0, mujoco 3.17.0, warp 1.18.0 (CPU device)
- **newton_mujoco**：newton 1.7.0, warp 1.18.0 (CPU)
- **newton_xpbd**：newton 1.7.0, warp 1.18.0 (CPU)
- **nexus_diffrigid**：nexus-f2ca9e94428b90e2
- **nexus_pgs**：nexus-f2ca9e94428b90e2
- 结果包 `bundles` 2026-11-02T09:41:15.952466Z · CPU INTEL(R) XEON(R) PLATINUM 8581C CPU @ 2.30GHz ×4 · sha256 `04b12d9542b71f77…`
- 结果包 `bundles` 2026-11-02T09:42:08.512208Z · CPU INTEL(R) XEON(R) PLATINUM 8581C CPU @ 2.30GHz ×4 · sha256 `121292568edb0c9a…`
- 结果包 `bundles` 2026-10-24T09:58:47.972094Z · CPU INTEL(R) XEON(R) PLATINUM 8581C CPU @ 2.30GHz ×4 · sha256 `5450c5078fed8275…`
- 结果包 `bundles` 2026-11-02T09:48:38.075808Z · CPU INTEL(R) XEON(R) PLATINUM 8581C CPU @ 2.30GHz ×4 · sha256 `68b2f0ee1892c987…`
- 结果包 `bundles` 2026-11-02T09:46:22.425611Z · CPU INTEL(R) XEON(R) PLATINUM 8581C CPU @ 2.30GHz ×4 · sha256 `6db73bc89e8ed86f…`
- 结果包 `bundles` 2026-11-02T09:53:55.289779Z · CPU INTEL(R) XEON(R) PLATINUM 8581C CPU @ 2.30GHz ×4 · sha256 `722f72444e42aad1…`
- 结果包 `bundles` 2026-11-02T09:39:48.225004Z · CPU INTEL(R) XEON(R) PLATINUM 8581C CPU @ 2.30GHz ×4 · sha256 `8507972e6e81e030…`
- 结果包 `bundles` 2026-11-02T09:46:00.780785Z · CPU INTEL(R) XEON(R) PLATINUM 8581C CPU @ 2.30GHz ×4 · sha256 `a4c22f043fe9f9e5…`
- 结果包 `bundles` 2026-11-02T09:59:01.027825Z · CPU INTEL(R) XEON(R) PLATINUM 8581C CPU @ 2.30GHz ×4 · sha256 `c275830f5a2a8b12…`
- 结果包 `bundles` 2026-11-02T09:58:08.804284Z · CPU INTEL(R) XEON(R) PLATINUM 8581C CPU @ 2.30GHz ×4 · sha256 `f033d6b3728453c7…`

## 自由落体（`free_fall`，dt=1/240）

| 引擎 | 位置最大误差 (m) | 速度最大误差 (m/s) |
|---|---|---|
| *公开容差* | 0.001 | 0.01 |
| brax_generalized | 0.02044 ✗ | 1.28e-05 ✓ |
| drake | 0.02044 ✗ | 2.13e-14 ✓ |
| mjx | 0.02044 ✗ | 1.28e-05 ✓ |
| mujoco | 0.02044 ✗ | 2.13e-14 ✓ |
| mujoco_warp | 0.02044 ✗ | 1.28e-05 ✓ |
| newton_mujoco | 0.02044 ✗ | 1.28e-05 ✓ |
| newton_xpbd | 0.02044 ✗ | 1.28e-05 ✓ |
| nexus_diffrigid | 1.09e-13 ✓ | 2.82e-13 ✓ |
| nexus_pgs | 8.16e-15 ✓ | 3.73e-14 ✓ |

## 抛射+匀速自旋球（`projectile_spin`，dt=1/240）

| 引擎 | 位置最大误差 (m) | 速度最大误差 (m/s) | 角速度最大误差 (rad/s) |
|---|---|---|---|
| *公开容差* | 0.001 | 0.01 | 0.001 |
| brax_generalized | 0.02043 ✗ | 7.21e-06 ✓ | 7.99e-06 ✓ |
| drake | 0.02044 ✗ | 2.04e-14 ✓ | 0 ✓ |
| mjx | 0.02043 ✗ | 7.21e-06 ✓ | 5.22e-06 ✓ |
| mujoco | 0.02044 ✗ | 1.24e-14 ✓ | 1.15e-14 ✓ |
| mujoco_warp | 0.02043 ✗ | 7.21e-06 ✓ | 3.65e-06 ✓ |
| newton_mujoco | 0.02043 ✗ | 7.21e-06 ✓ | 4.08e-04 ✓ |
| newton_xpbd | 0.02043 ✗ | 7.21e-06 ✓ | 1.78e-04 ✓ |
| nexus_diffrigid | 1.03e-13 ✓ | 4.62e-14 ✓ | 0 ✓ |
| nexus_pgs | 2.58e-14 ✓ | 2.22e-14 ✓ | 0 ✓ |

## 无力矩非对称刚体（中间轴翻转）（`torque_free_asym`，dt=1/240）

| 引擎 | 姿态最大误差 (°) | 能量漂移(相对) | 角动量漂移(相对) | 质心漂移 (m) |
|---|---|---|---|---|
| *公开容差* | 2 | 0.001 | 0.001 | 1.00e-06 |
| brax_generalized | 3.418 ✗ | 0.03347 ✗ | 0.01908 ✗ | 0 ✓ |
| drake | 3.378 ✗ | 0.03347 ✗ | 0.01909 ✗ | 0 ✓ |
| mjx | 3.418 ✗ | 0.03347 ✗ | 0.01908 ✗ | 0 ✓ |
| mujoco | 3.418 ✗ | 0.03347 ✗ | 0.01908 ✗ | 0 ✓ |
| mujoco_warp | 3.418 ✗ | 0.03347 ✗ | 0.01908 ✗ | 0 ✓ |
| newton_mujoco | 3.335 ✗ | 0.03163 ✗ | 0.01823 ✗ | 0 ✓ |
| newton_xpbd | 3.409 ✗ | 0.03361 ✗ | 0.01915 ✗ | 0 ✓ |
| nexus_diffrigid | 0.2435 ✓ | 0.002336 ✗ | 0.001343 ✗ | 0 ✓ |
| nexus_pgs | 0.01244 ✓ | 1.69e-05 ✓ | 4.48e-05 ✓ | 0 ✓ |

## 库仑滑行停距（`coulomb_slide`，dt=1/240）

| 引擎 | 停距相对误差 | 残余速度 (m/s) | 高度最大误差 (m) |
|---|---|---|---|
| *公开容差* | 0.02 | 0.01 | 0.002 |
| brax_generalized | 0.009963 ✓ | 1.15e-06 ✓ | 0.001107 ✓ |
| drake | 0.4859 ✗ | 0.03961 ✗ | 0.04275 ✗ |
| mjx | 0.009756 ✓ | 3.55e-05 ✓ | 0.005361 ✗ |
| mujoco | 0.009727 ✓ | 2.52e-10 ✓ | 0.005361 ✗ |
| mujoco_warp | 0.009728 ✓ | 6.31e-07 ✓ | 0.005361 ✗ |
| newton_mujoco | 0.009729 ✓ | 6.31e-07 ✓ | 0.005361 ✗ |
| newton_xpbd | 0.01017 ✓ | 0 ✓ | 2.08e-05 ✓ |
| nexus_diffrigid | 6.54e-04 ✓ | 3.08e-04 ✓ | 1.90e-05 ✓ |
| nexus_pgs | 0.005078 ✓ | 1.97e-18 ✓ | 6.18e-07 ✓ |

## 斜面滑动（重力分解，μ<tanθ）（`incline_slide`，dt=1/240）

| 引擎 | 沿斜面位移相对误差 | 高度最大误差 (m) |
|---|---|---|
| *公开容差* | 0.02 | 0.002 |
| brax_generalized | 0.03521 ✗ | 4.18e-04 ✓ |
| drake | 0.9704 ✗ | 0.005402 ✗ |
| mjx | 0.007314 ✓ | 5.51e-04 ✓ |
| mujoco | 0.007314 ✓ | 5.51e-04 ✓ |
| mujoco_warp | 0.007326 ✓ | 5.52e-04 ✓ |
| newton_mujoco | 0.007311 ✓ | 5.51e-04 ✓ |
| newton_xpbd | 0.01263 ✓ | 2.09e-05 ✓ |
| nexus_diffrigid | 0.01421 ✓ | 1.35e-05 ✓ |
| nexus_pgs | 0.002147 ✓ | 4.55e-07 ✓ |

## 静置盒体（接触平衡）（`box_rest`，dt=1/240）

| 引擎 | 高度最大误差 (m) | 横向漂移 (m) | 静置最大速度 (m/s) |
|---|---|---|---|
| *公开容差* | 0.001 | 0.001 | 0.01 |
| brax_generalized | 3.09e-04 ✓ | 4.13e-07 ✓ | 2.03e-06 ✓ |
| drake | 1.19e-04 ✓ | 0 ✓ | 3.17e-09 ✓ |
| mjx | 3.09e-04 ✓ | 3.70e-05 ✓ | 4.33e-05 ✓ |
| mujoco | 3.09e-04 ✓ | 2.53e-19 ✓ | 8.02e-13 ✓ |
| mujoco_warp | 3.09e-04 ✓ | 9.80e-10 ✓ | 6.31e-07 ✓ |
| newton_mujoco | 3.09e-04 ✓ | 9.80e-10 ✓ | 6.31e-07 ✓ |
| newton_xpbd | 2.22e-05 ✓ | 0 ✓ | 0 ✓ |
| nexus_diffrigid | 1.92e-06 ✓ | 3.06e-08 ✓ | 3.08e-04 ✓ |
| nexus_pgs | 5.54e-07 ✓ | 2.60e-18 ✓ | 2.95e-18 ✓ |

## 盒体下落（静止高度，非弹性）（`box_drop`，dt=1/240）

| 引擎 | 终态高度误差 (m) | 终态速度 (m/s) | 最大回弹 (m) |
|---|---|---|---|
| *公开容差* | 0.002 | 0.01 | 0.02 |
| brax_generalized | 1.71e-05 ✓ | 1.93e-06 ✓ | 0.001666 ✓ |
| drake | 1.96e-05 ✓ | 1.08e-09 ✓ | 0.001666 ✓ |
| mjx | 1.71e-05 ✓ | 3.57e-05 ✓ | 0.001666 ✓ |
| mujoco | 1.71e-05 ✓ | 2.21e-13 ✓ | 0.001666 ✓ |
| mujoco_warp | 1.71e-05 ✓ | 6.31e-07 ✓ | 0.001666 ✓ |
| newton_mujoco | 1.71e-05 ✓ | 6.31e-07 ✓ | 0.001666 ✓ |
| newton_xpbd | 2.05e-05 ✓ | 0 ✓ | 0.001666 ✓ |
| nexus_diffrigid | 1.92e-06 ✓ | 3.08e-04 ✓ | 3.00e-05 ✓ |
| nexus_pgs | 5.11e-07 ✓ | 4.16e-18 ✓ | 0 ✓ |

## 球体滑动→纯滚动（摩擦力矩耦合）（`sphere_slide_to_roll`，dt=1/240）

| 引擎 | 末速度相对误差 | 滚动约束残差(相对) | 末位置相对误差 |
|---|---|---|---|
| *公开容差* | 0.03 | 0.03 | 0.03 |
| brax_generalized | 3.30e-04 ✓ | 3.39e-04 ✓ | 9.15e-04 ✓ |
| drake | 5.59e-05 ✓ | 9.81e-05 ✓ | 7.74e-04 ✓ |
| mjx | 4.40e-04 ✓ | 3.36e-04 ✓ | 0.001016 ✓ |
| mujoco | 4.41e-04 ✓ | 3.40e-04 ✓ | 0.001014 ✓ |
| mujoco_warp | 4.42e-04 ✓ | 3.40e-04 ✓ | 0.001016 ✓ |
| newton_mujoco | 4.28e-04 ✓ | 3.40e-04 ✓ | 0.001005 ✓ |
| newton_xpbd | 0.005288 ✓ | 8.84e-04 ✓ | 0.003522 ✓ |
| nexus_diffrigid | 2.76e-04 ✓ | 9.65e-04 ✓ | 2.40e-05 ✓ |
| nexus_pgs | 1.71e-15 ✓ | 1.55e-16 ✓ | 4.07e-04 ✓ |

## 五层盒体堆叠静置（`stack5`，dt=1/240）

| 引擎 | 顶层高度最大误差 (m) | 横向漂移 (m) | 静置最大速度 (m/s) |
|---|---|---|---|
| *公开容差* | 0.005 | 0.005 | 0.05 |
| brax_generalized | 0.006926 ✗ | 8.65e-04 ✓ | 0.003211 ✓ |
| drake | 0.5196 ✗ | 0.004875 ✓ | 0.1731 ✗ |
| mjx | 0.003008 ✓ | 1.17e-04 ✓ | 1.45e-04 ✓ |
| mujoco | 0.001452 ✓ | 5.67e-16 ✓ | 1.96e-12 ✓ |
| mujoco_warp | 0.003008 ✓ | 3.39e-08 ✓ | 0.0436 ✓ |
| newton_mujoco | 0.003008 ✓ | 2.87e-08 ✓ | 0.004945 ✓ |
| newton_xpbd | 0.005775 ✗ | 0 ✓ | 0 ✓ |
| nexus_diffrigid | 5.21e-04 ✓ | 7.90e-05 ✓ | 0.003498 ✓ |
| nexus_pgs | 7.20e-05 ✓ | 1.65e-16 ✓ | 1.90e-09 ✓ |

## 铰链复摆（水平释放，大摆幅）（`pendulum_hinge`，dt=1/240）

| 引擎 | 质心位置最大误差 (m) | 能量漂移(相对) |
|---|---|---|
| *公开容差* | 0.005 | 0.01 |
| brax_generalized | 0.005644 ✗ | 0.007038 ✓ |
| drake | 0.005644 ✗ | 0.007039 ✓ |
| mjx | 0.005644 ✗ | 0.007039 ✓ |
| mujoco | 0.005644 ✗ | 0.007039 ✓ |
| mujoco_warp | 0.005644 ✗ | 0.007039 ✓ |
| newton_mujoco | 0.005645 ✗ | 0.00704 ✓ |
| newton_xpbd | 0.4147 ✗ | 0.3101 ✗ |
| nexus_diffrigid | 5.71e-04 ✓ | 3.47e-04 ✓ |
| nexus_pgs | 0.002814 ✓ | 0.003504 ✓ |

## 自由落体（隐藏变体）（`free_fall~h`，dt=1/240）

| 引擎 | 位置最大误差 (m) | 速度最大误差 (m/s) |
|---|---|---|
| *公开容差* | 0.001 | 0.01 |
| mujoco | 0.02044 ✗ | 2.13e-14 ✓ |
| nexus_diffrigid | 2.98e-14 ✓ | 1.47e-13 ✓ |
| nexus_pgs | 9.77e-15 ✓ | 3.73e-14 ✓ |

## 抛射+匀速自旋球（隐藏变体）（`projectile_spin~h`，dt=1/240）

| 引擎 | 位置最大误差 (m) | 速度最大误差 (m/s) | 角速度最大误差 (rad/s) |
|---|---|---|---|
| *公开容差* | 0.001 | 0.01 | 0.001 |
| mujoco | 0.02044 ✗ | 1.02e-14 ✓ | 9.33e-15 ✓ |
| nexus_diffrigid | 7.11e-14 ✓ | 4.62e-14 ✓ | 0 ✓ |
| nexus_pgs | 2.53e-14 ✓ | 2.22e-14 ✓ | 0 ✓ |

## 无力矩非对称刚体（中间轴翻转）（隐藏变体）（`torque_free_asym~h`，dt=1/240）

| 引擎 | 姿态最大误差 (°) | 能量漂移(相对) | 角动量漂移(相对) | 质心漂移 (m) |
|---|---|---|---|---|
| *公开容差* | 2 | 0.001 | 0.001 | 1.00e-06 |
| mujoco | 3.95 ✗ | 0.0376 ✗ | 0.0213 ✗ | 0 ✓ |
| nexus_diffrigid | 0.2821 ✓ | 0.002617 ✗ | 0.001498 ✗ | 0 ✓ |
| nexus_pgs | 0.01772 ✓ | 2.11e-05 ✓ | 5.70e-05 ✓ | 0 ✓ |

## 库仑滑行停距（隐藏变体）（`coulomb_slide~h`，dt=1/240）

| 引擎 | 停距相对误差 | 残余速度 (m/s) | 高度最大误差 (m) |
|---|---|---|---|
| *公开容差* | 0.02 | 0.01 | 0.002 |
| mujoco | 0.0103 ✓ | 4.28e-11 ✓ | 0.001538 ✓ |
| nexus_diffrigid | 8.77e-04 ✓ | 3.32e-04 ✓ | 9.67e-06 ✓ |
| nexus_pgs | 0.005348 ✓ | 9.21e-19 ✓ | 4.98e-07 ✓ |

## 斜面滑动（重力分解，μ<tanθ）（隐藏变体）（`incline_slide~h`，dt=1/240）

| 引擎 | 沿斜面位移相对误差 | 高度最大误差 (m) |
|---|---|---|
| *公开容差* | 0.02 | 0.002 |
| mujoco | 0.003854 ✓ | 0.003829 ✗ |
| nexus_diffrigid | 0.001085 ✓ | 1.69e-05 ✓ |
| nexus_pgs | 0.002091 ✓ | 4.11e-07 ✓ |

## 静置盒体（接触平衡）（隐藏变体）（`box_rest~h`，dt=1/240）

| 引擎 | 高度最大误差 (m) | 横向漂移 (m) | 静置最大速度 (m/s) |
|---|---|---|---|
| *公开容差* | 0.001 | 0.001 | 0.01 |
| mujoco | 3.08e-04 ✓ | 7.03e-19 ✓ | 5.63e-13 ✓ |
| nexus_diffrigid | 1.27e-04 ✓ | 3.64e-08 ✓ | 2.97e-04 ✓ |
| nexus_pgs | 3.58e-07 ✓ | 2.59e-18 ✓ | 2.22e-18 ✓ |

## 盒体下落（静止高度，非弹性）（隐藏变体）（`box_drop~h`，dt=1/240）

| 引擎 | 终态高度误差 (m) | 终态速度 (m/s) | 最大回弹 (m) |
|---|---|---|---|
| *公开容差* | 0.002 | 0.01 | 0.02 |
| mujoco | 1.71e-05 ✓ | 1.78e-13 ✓ | 0 ✓ |
| nexus_diffrigid | 1.92e-06 ✓ | 3.08e-04 ✓ | 0.003603 ✓ |
| nexus_pgs | 5.50e-07 ✓ | 4.61e-18 ✓ | 0.003259 ✓ |

## 球体滑动→纯滚动（摩擦力矩耦合）（隐藏变体）（`sphere_slide_to_roll~h`，dt=1/240）

| 引擎 | 末速度相对误差 | 滚动约束残差(相对) | 末位置相对误差 |
|---|---|---|---|
| *公开容差* | 0.03 | 0.03 | 0.03 |
| mujoco | 3.78e-04 ✓ | 2.02e-04 ✓ | 0.001018 ✓ |
| nexus_diffrigid | 2.21e-04 ✓ | 7.73e-04 ✓ | 6.80e-06 ✓ |
| nexus_pgs | 3.68e-15 ✓ | 1.27e-16 ✓ | 4.01e-04 ✓ |

## 五层盒体堆叠静置（隐藏变体）（`stack5~h`，dt=1/240）

| 引擎 | 顶层高度最大误差 (m) | 横向漂移 (m) | 静置最大速度 (m/s) |
|---|---|---|---|
| *公开容差* | 0.005 | 0.005 | 0.05 |
| mujoco | 0.001512 ✓ | 7.90e-16 ✓ | 2.52e-12 ✓ |
| nexus_diffrigid | 8.04e-04 ✓ | 4.42e-05 ✓ | 0.003592 ✓ |
| nexus_pgs | 1.22e-04 ✓ | 2.88e-16 ✓ | 1.36e-07 ✓ |

## 铰链复摆（水平释放，大摆幅）（隐藏变体）（`pendulum_hinge~h`，dt=1/240）

| 引擎 | 质心位置最大误差 (m) | 能量漂移(相对) |
|---|---|---|
| *公开容差* | 0.005 | 0.01 |
| mujoco | 0.006142 ✗ | 0.00647 ✓ |
| nexus_diffrigid | 4.75e-04 ✓ | 2.43e-04 ✓ |
| nexus_pgs | 0.003063 ✓ | 0.003222 ✓ |

## 时间步收敛阶（dt = 1/60, 1/240, 1/1000 的误差对数斜率；越大收敛越快）

| 引擎 | 场景 | 指标 | 阶 |
|---|---|---|---|
| mjx | free_fall | pos_err_max_m | 1.00 |
| mjx | pendulum_hinge | com_pos_err_max_m | 1.00 |
| mujoco_warp | free_fall | pos_err_max_m | 1.00 |
| mujoco_warp | pendulum_hinge | com_pos_err_max_m | 1.00 |
| nexus_pgs | free_fall | pos_err_max_m | -0.58 |
| nexus_pgs | pendulum_hinge | com_pos_err_max_m | 1.00 |
| drake | free_fall | pos_err_max_m | 1.00 |
| drake | pendulum_hinge | com_pos_err_max_m | 1.00 |
| nexus_diffrigid | free_fall | pos_err_max_m | 0.33 |
| nexus_diffrigid | pendulum_hinge | com_pos_err_max_m | -0.00 |
| mujoco | free_fall | pos_err_max_m | 1.00 |
| mujoco | pendulum_hinge | com_pos_err_max_m | 1.00 |
| brax_generalized | free_fall | pos_err_max_m | 1.00 |
| brax_generalized | pendulum_hinge | com_pos_err_max_m | 1.00 |
| newton_mujoco | free_fall | pos_err_max_m | 1.00 |
| newton_mujoco | pendulum_hinge | com_pos_err_max_m | 1.00 |
| newton_xpbd | free_fall | pos_err_max_m | 1.00 |
| newton_xpbd | pendulum_hinge | com_pos_err_max_m | -0.15 |

## 单环境 CPU 步进速度（仅供参考，不属于精度赛道结论；若结果包由多个引擎并行跑出，受 CPU 争用影响，不可比较）

| 引擎 | free_fall | projectile_spin | torque_free_asym | coulomb_slide | incline_slide | box_rest | box_drop | sphere_slide_to_roll | stack5 | pendulum_hinge | free_fall~h | projectile_spin~h | torque_free_asym~h | coulomb_slide~h | incline_slide~h | box_rest~h | box_drop~h | sphere_slide_to_roll~h | stack5~h | pendulum_hinge~h |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| brax_generalized | 178 | 196 | 369 | 89 | 67 | 102 | 79 | 109 | 74 | 398 | — | — | — | — | — | — | — | — | — | — |
| drake | 74665 | 76572 | 72582 | 11168 | 10324 | 14726 | 15634 | 16116 | 2251 | 69944 | — | — | — | — | — | — | — | — | — | — |
| mjx | 773 | 1125 | 1042 | 957 | 671 | 643 | 672 | 981 | 547 | 696 | — | — | — | — | — | — | — | — | — | — |
| mujoco | 262074 | 74084 | 258022 | 194988 | 159537 | 169994 | 208480 | 243107 | 45672 | 446225 | 407495 | 434732 | 412904 | 175327 | 241359 | 192057 | 204272 | 248643 | 31291 | 408789 |
| mujoco_warp | 238 | 250 | 250 | 227 | 208 | 231 | 245 | 224 | 142 | 231 | — | — | — | — | — | — | — | — | — | — |
| newton_mujoco | 229 | 208 | 216 | 156 | 152 | 175 | 168 | 157 | 111 | 238 | — | — | — | — | — | — | — | — | — | — |
| newton_xpbd | 882 | 1071 | 1069 | 254 | 288 | 310 | 317 | 272 | 281 | 939 | — | — | — | — | — | — | — | — | — | — |
| nexus_diffrigid | 378 | 1074 | 381 | 131 | 236 | 135 | 143 | 350 | 3 | 54 | 1021 | 1724 | 425 | 230 | 289 | 225 | 149 | 509 | 4 | 51 |
| nexus_pgs | 16881 | 16881 | 13302 | 3415 | 3748 | 5796 | 5995 | 8697 | 3774 | 7664 | 22406 | 24462 | 17737 | 4617 | 4959 | 5554 | 8658 | 9727 | 4102 | 17409 |

> 速度含各引擎 Python/Node 绑定开销，且 GPU 引擎（MJX/MuJoCo-Warp/Newton）在 CPU 单环境下不处于其设计工况；速度对比需另设性能赛道（分 CPU/GPU）。